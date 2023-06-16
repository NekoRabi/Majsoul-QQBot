"""
:Author:  NekoRabi
:Update Time:  2022/8/16 19:31
:Describe: 生成摸头gif
:Version: 0.0.2
"""
import random
import re

import numpy
import aiohttp
import os
from PIL import Image as IMG, ImageOps
from moviepy.editor import ImageSequenceClip
from io import BytesIO
from mirai import MessageChain, Plain, Image, GroupMessage, At
from mirai.models import NudgeEvent
from core import bot, config, replydata, commandpre, commands_map
from utils import root_logger
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender

blacklist = config.get('blacklist', [])
__all__ = ['nudge_petpet']

if not os.path.exists("./images/PetPet"):
    os.mkdir("./images/PetPet")

_settings = config.get('settings')
_silencegroup = config['silencegroup']
_nudgeconfig = config['nudgeconfig']
_admin = config['admin']


async def petpet_generator(qqnumber: int):
    if not os.path.exists("./images/PetPet"):
        os.mkdir("./images/PetPet")
    if not os.path.exists("./images/PetPet/temp"):
        os.mkdir("./images/PetPet/temp")
    await petpet(member_id=qqnumber)
    return


frame_spec = [
    (27, 31, 86, 90),
    (22, 36, 91, 90),
    (18, 41, 95, 90),
    (22, 41, 91, 91),
    (27, 28, 86, 91)
]

squish_factor = [
    (0, 0, 0, 0),
    (-7, 22, 8, 0),
    (-8, 30, 9, 6),
    (-3, 21, 5, 9),
    (0, 0, 0, 0)
]

squish_translation_factor = [0, 20, 34, 21, 0]

frames = tuple([f'./plugin/Petpet/PetPetFrames/frame{i}.png' for i in range(5)])


async def save_gif(gif_frames, dest, fps=10):
    """生成 gif
    将输入的帧数据合并成视频并输出为 gif
    参数
    gif_frames: list<numpy.ndarray>
    为每一帧的数据
    dest: str
    为输出路径
    fps: int, float
    为输出 gif 每秒显示的帧数
    返回
    None
    但是会输出一个符合参数的 gif
    """
    # clip = ImageSequenceClip(gif_frames, fps=fps)
    # clip.write_gif(dest, program='ffmpeg', logger=None, logger=None)  # 使用 imageio
    # clip.close()
    with ImageSequenceClip(gif_frames, fps=fps) as clip:
        clip.write_gif(dest, program='ffmpeg', logger=None)


# 生成函数（非数学意味）
async def make_frame(avatar, i, squish=0, flip=False):
    """生成帧
    将输入的头像转变为参数指定的帧，以供 make_gif() 处理
    参数
    avatar: PIL.Image.Image
    为头像
    i: int
    为指定帧数
    squish: float
    为一个 [0, 1] 之间的数，为挤压量
    flip: bool
    为是否横向反转头像
    返回
    numpy.ndarray
    为处理完的帧的数据
    """
    # 读入位置
    spec = list(frame_spec[i])
    # 将位置添加偏移量
    for j, s in enumerate(spec):
        spec[j] = int(s + squish_factor[i][j] * squish)
    # 读取手
    hand = IMG.open(frames[i])
    # 反转
    if flip:
        avatar = ImageOps.mirror(avatar)
    # 将头像放缩成所需大小
    avatar = avatar.resize((int((spec[2] - spec[0]) * 1.2), int((spec[3] - spec[1]) * 1.2)), IMG.ANTIALIAS)
    # 并贴到空图像上
    gif_frame = IMG.new('RGB', (112, 112), (255, 255, 255))
    gif_frame.paste(avatar, (spec[0], spec[1]))
    # 将手覆盖（包括偏移量）
    gif_frame.paste(hand, (0, int(squish * squish_translation_factor[i])), hand)
    # 返回
    return numpy.array(gif_frame)


async def petpet(member_id, flip=False, squish=0, fps=15) -> None:
    """生成PetPet
    将输入的头像生成为所需的 PetPet 并输出
    参数
    path: str
    为头像路径
    flip: bool
    为是否横向反转头像
    squish: float
    为一个 [0, 1] 之间的数，为挤压量
    fps: int
    为输出 gif 每秒显示的帧数
    返回
    bool
    但是会输出一个符合参数的 gif
    """

    if not os.path.exists("./images/PetPet/temp"):
        os.mkdir("./images/PetPet/temp")
    if os.path.exists(f'./images/PetPet/temp/tempPetPet-{member_id}.gif'):
        os.remove(f'./images/PetPet/temp/tempPetPet-{member_id}.gif')
    url = f'http://q1.qlogo.cn/g?b=qq&nk={str(member_id)}&s=640'
    gif_frames = []
    # 打开头像
    # avatar = Image.open(path)
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            img_content = await resp.read()

    avatar = IMG.open(BytesIO(img_content)).convert("RGBA")

    size = avatar.size
    # 因为是要圆形，所以需要正方形的图片
    r2 = min(size[0], size[1])
    ima = avatar
    if size[0] != size[1]:
        ima = avatar.resize((r2, r2), IMG.ANTIALIAS)
    bgk = IMG.open('./plugin/Petpet/baseimg.png').convert('RGBA').resize((r2, r2))
    r, g, b, a = bgk.split()
    ima.paste(bgk, (0, 0, r2, r2), mask=a)
    # 生成每一帧
    for i in range(5):
        gif_frames.append(await make_frame(ima, i, squish=squish, flip=flip))
    # 输出
    await save_gif(gif_frames, f'./images/PetPet/temp/tempPetPet-{member_id}.gif', fps=fps)


@bot.on(NudgeEvent)
async def nudge_petpet(event: NudgeEvent):
    """检测戳一戳事件"""
    sender = event.from_id
    if sender == bot.qq:
        return
    if sender in blacklist:
        return
    if (not _settings['silence']) or _settings['nudgereply']:
        if event.subject.kind == 'Group':
            if not (event.subject.id in _silencegroup or event.subject.id in _nudgeconfig['disnudgegroup']):
                target = event.target
                if target == bot.qq:
                    if sender in _admin:
                        await messagechain_sender(grouptarget=event.subject.id, msg=await messagechain_builder(
                            reply_choices=replydata['nudgedata']['admin']))
                        await petpet(target)
                        await messagechain_sender(grouptarget=event.subject.id, msg=await messagechain_builder(
                            imgpath=f'./images/PetPet/temp/tempPetPet-{target}.gif'))
                    else:
                        if random.random() < _nudgeconfig['sendnudgechance']:
                            if random.random() < _nudgeconfig['supersendnudgechance']:
                                await messagechain_sender(grouptarget=event.subject.id, msg=await messagechain_builder(
                                    reply_choices=replydata['nudgedata']['supernudgereply'],
                                    rndimg=True))
                                for i in range(_nudgeconfig['supernudgequantity']):
                                    await bot.send_nudge(subject=event.subject.id, target=sender, kind='Group')
                                return
                            else:
                                await bot.send_nudge(subject=event.subject.id, target=sender, kind='Group')
                                return await messagechain_sender(grouptarget=event.subject.id,
                                                                 msg=await messagechain_builder(
                                                                     reply_choices=replydata['nudgedata']['nudgereply'],
                                                                     rndimg=True))
                        else:
                            return await messagechain_sender(grouptarget=event.subject.id,
                                                             msg=random.choice(replydata['nudgedata']['other']))
                else:
                    await petpet(target)
                    await messagechain_sender(grouptarget=event.subject.id, msg=MessageChain(Image(path=f'./images/PetPet/temp/tempPetPet-{target}.gif')))
    return


@bot.on(GroupMessage)
async def touchhead(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{commands_map['reply']['touchhead']}", msg.strip())
    if m:
        if At in event.message_chain:
            target = event.message_chain.get_first(At).target
            await petpet(target)
            if await messagechain_sender(event=event, msg=MessageChain(
                    Image(path=f'./images/PetPet/temp/tempPetPet-{target}.gif'))) == -1:
                print('摸头发送失败')
                root_logger.error('摸头发送失败')
        # else:
        #     target = m.group(2)
        #     await petpet(target)
        #     await bot.send(event, MessageChain(Image(path=f'./images/PetPet/temp/tempPetPet-{target}.gif')))
