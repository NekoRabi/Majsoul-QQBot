"""
:Author:  NekoRabi
:Create:  2022/9/23 14:07
:Update: /
:Describe: 亲亲群友
:Version: 0.0.1
"""
import re
import numpy
import aiohttp
import os

from PIL import Image as IMG
from PIL import ImageDraw
from mirai import GroupMessage, Plain, At
from moviepy.editor import ImageSequenceClip as imageclip
from io import BytesIO
from core import bot, commands_map, commandpre, blacklist
from utils import read_file
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender

if not os.path.exists("./images/ImgGenerator/KissKiss"):
    os.mkdir("./images/ImgGenerator/KissKiss")

__all__ = ['on_kiss']

_cfg = read_file(r'./config/ImgGenerator/config.yml')


async def save_gif(gif_frames, dest, fps=10):
    clip = imageclip(gif_frames, fps=fps)
    clip.write_gif(dest, logger=None, program='ffmpeg')
    clip.close()


async def kiss_make_frame(operator, target, i):
    operator_x = [92, 135, 84, 80, 155, 60, 50, 98, 35, 38, 70, 84, 75]
    operator_y = [64, 40, 105, 110, 82, 96, 80, 55, 65, 100, 80, 65, 65]
    target_x = [58, 62, 42, 50, 56, 18, 28, 54, 46, 60, 35, 20, 40]
    target_y = [90, 95, 100, 100, 100, 120, 110, 100, 100, 100, 115, 120, 96]
    bg = IMG.open(f"./plugin/ImgGenerator/KissKiss/KissFrames/{i}.png")
    gif_frame = IMG.new('RGB', (200, 200), (255, 255, 255))
    gif_frame.paste(bg, (0, 0))
    gif_frame.paste(target, (target_x[i - 1], target_y[i - 1]), target)
    gif_frame.paste(operator, (operator_x[i - 1], operator_y[i - 1]), operator)
    return numpy.array(gif_frame)


async def kiss(operator_id, target_id) -> None:
    operator_url = f'http://q1.qlogo.cn/g?b=qq&nk={operator_id}&s=640'
    target_url = f'http://q1.qlogo.cn/g?b=qq&nk={target_id}&s=640'
    gif_frames = []
    async with aiohttp.ClientSession() as session:
        async with session.get(url=operator_url) as resp:
            operator_img = await resp.read()
    operator = IMG.open(BytesIO(operator_img))

    async with aiohttp.ClientSession() as session:
        async with session.get(url=target_url) as resp:
            target_img = await resp.read()
    target = IMG.open(BytesIO(target_img)).convert("RGBA")

    operator = operator.resize((40, 40), IMG.ANTIALIAS)
    size = operator.size
    r2 = min(size[0], size[1])
    circle = IMG.new('L', (r2, r2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, r2, r2), fill=255)
    alpha = IMG.new('L', (r2, r2), 255)
    alpha.paste(circle, (0, 0))
    operator.putalpha(alpha)

    target = target.resize((50, 50), IMG.ANTIALIAS)
    size = target.size
    r2 = min(size[0], size[1])
    circle = IMG.new('L', (r2, r2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, r2, r2), fill=255)
    alpha = IMG.new('L', (r2, r2), 255)
    alpha.paste(circle, (0, 0))
    target.putalpha(alpha)

    for i in range(1, 14):
        gif_frames.append(await kiss_make_frame(operator, target, i))
    await save_gif(gif_frames, f'./images/ImgGenerator/KissKiss/tempKiss-{operator_id}-{target_id}.gif', fps=25)


# 亲亲

@bot.on(GroupMessage)
async def on_kiss(event: GroupMessage):
    if not _cfg.get('Kiss', True):
        return
    if event.sender.id in blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{commands_map['reply']['kisskiss']}", msg.strip())
    if m:
        if At in event.message_chain:
            operator_id = event.sender.id
            target_id = event.message_chain.get_first(At).target
            if operator_id == target_id:
                # return await bot.send(event, await messagechain_builder(text="请不要自交", rndimg=True))
                return await messagechain_sender(event=event, msg=await messagechain_builder(text="请不要自交", rndimg=True,
                                                                                             at=event.sender.id))
            else:
                await kiss(operator_id=operator_id, target_id=target_id)
                # await bot.send(event, await messagechain_builder(
                #     imgpath=f'./images/ImgGenerator/KissKiss/tempKiss-{operator_id}-{target_id}.gif'))
                return await messagechain_sender(event=event, msg=await messagechain_builder(
                    imgpath=f'./images/ImgGenerator/KissKiss/tempKiss-{operator_id}-{target_id}.gif'))
