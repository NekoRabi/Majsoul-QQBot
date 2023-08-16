"""
:Author:  NekoRabi
:Create:  2022/9/23 14:08
:Update: 2023/6/16
:Describe: 群成员图片制作
:Version: 0.0.1
"""
import datetime
import random

from utils import root_logger, read_file
from utils.MessageChainBuilder import messagechain_builder
from mirai import GroupMessage, At, Plain
from core import bot, blacklist, commandpre, admin, bot_cfg
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw

import aiohttp
import re
import os
import base64

from utils.MessageChainSender import messagechain_sender

if not os.path.exists("./images/ImgGenerator"):
    os.mkdir("./images/ImgGenerator")

__all__ = ['xka', 'daiburen', 'diuren', 'chiren', 'juren', 'marry_random_group_member', 'marry_group_member']

_cfg = read_file(r'./config/ImgGenerator/config.yml')


def img_to_base64(img: Image):
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    b_content = img_bytes.getvalue()
    imgcontent = base64.b64encode(b_content)
    return imgcontent


def addfont(img: Image, text, position=(0, 0), fontcolor=(0, 0, 0), fontsize=None, maxsize: tuple = None, center=True):
    pos_x, pos_y = position
    if not fontsize:
        fontsize = img.width // len(text)
        if maxsize:
            maxs = min(maxsize)
            fontsize = min(maxs, fontsize)
    draw = ImageDraw.Draw(img)
    fontstyle = ImageFont.truetype(
        font='./plugin/ImgGenerator/MiSans-Bold.ttf', size=fontsize)
    if center:
        pxlength = fontstyle.getsize(text)[0]
        pos_x = (img.width - pxlength) // 2
    draw.text((pos_x, pos_y), text=text, font=fontstyle, fill=fontcolor)
    return fontsize


def circle_corner(img, radii=50):  # 将矩形圆角化
    """
    圆角处理
    :param img: 源图象。
    :param radii: 半径，如：30。
    :return: 返回一个圆角处理后的图象。
    """

    # 画圆（用于分离4个角）
    circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建一个黑色背景的画布
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 画白色圆形

    # 原图
    img = img.convert("RGBA")
    w, h = img.size

    # 画4个角（将整圆分离为4个部分）
    alpha = Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))  # 右上角
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii))  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))  # 左下

    img.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见
    return img


async def get_head_sculpture(userid) -> Image:
    url = f'http://q1.qlogo.cn/g?b=qq&nk={userid}&s=640'
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            img_content = await resp.read()
    return Image.open(BytesIO(img_content)).convert("RGBA")


async def makedaibu(userid):
    avatar = await get_head_sculpture(userid)
    ima = avatar.resize((130, 130), Image.ANTIALIAS)
    bgk = Image.open('./plugin/ImgGenerator/image/daibu.png').convert("RGBA")
    bgk.paste(ima, (68, 85, 68 + ima.width, 85 + ima.height))
    return img_to_base64(bgk)


async def makesmalllove(userid, username, sex: str = None):
    avatar = await get_head_sculpture(userid)
    userimg = avatar.resize((200, 200), Image.ANTIALIAS)

    bgk = Image.new('RGB', (300, 300), (255, 255, 255))
    bgk.paste(userimg, (50, 50, 50 + userimg.width, 50 + userimg.height))
    if sex == 'MALE':
        sex = '他'
    else:
        sex = '她'
    if random.random() < 0.5:
        addfont(bgk, text=f'你们看到{sex}了吗?', maxsize=(300, 30))
    else:
        addfont(bgk, text=f'你们看到{username}了吗?', maxsize=(300, 30))
    addfont(bgk, text=f'非常可爱,简直就是小天使', maxsize=(50, 20), position=(0, 250))
    addfont(bgk, text=f'{sex}没失踪也没怎么样,我只是觉得你们都该看一下', position=(0, 280))
    bgk.save(fp=f'./images/ImgGenerator/xiaokeai_{userid}.png')


async def throwpeople(userid):
    headimg = await get_head_sculpture(userid)
    headimg = circle_corner(headimg.resize((160, 160), Image.ANTIALIAS), 80)
    bgk = Image.open('./plugin/ImgGenerator/image/diu.png').convert("RGBA")
    bgk.paste(headimg, (10, 170, 10 + headimg.width, 170 + headimg.height), mask=headimg.split()[3])
    return img_to_base64(bgk)


async def eatpeople(userid):
    headimg = await get_head_sculpture(userid)
    headimg = circle_corner(headimg.resize((160, 160), Image.ANTIALIAS), 80)
    bgkimg = Image.open('./plugin/ImgGenerator/image/eat.png').convert("RGBA")
    bgk = Image.new('RGB', bgkimg.size, (255, 255, 255))
    bgk.paste(headimg, (90, 350, 90 + headimg.width, 350 + headimg.height), mask=headimg.split()[3])
    bgk.paste(bgkimg, (0, 0), mask=bgkimg.split()[3])
    return img_to_base64(bgk)


async def holdup(userid):
    headimg = await get_head_sculpture(userid)
    headimg = circle_corner(headimg.resize((240, 240), Image.ANTIALIAS), 120)
    bgkimg = Image.open('./plugin/ImgGenerator/image/ju.png').convert("RGBA")
    bgk = Image.new('RGB', bgkimg.size, (255, 255, 255))
    bgk.paste(headimg, (80, 10, 80 + headimg.width, 10 + headimg.height), mask=headimg.split()[3])
    bgk.paste(bgkimg, (0, 0), mask=bgkimg.split()[3])
    return img_to_base64(bgk)


@bot.on(GroupMessage)
async def daiburen(event: GroupMessage):
    """生成逮捕图"""
    if not _cfg.get('Arrest', False):
        return
    if event.sender.id in blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(
        fr"^逮捕(\w*)", msg.strip())
    userid = None
    if m:
        if m.group(1):
            if m.group(1) in ['我', '我自己', '自己']:
                userid = event.sender.id
        elif At in event.message_chain:
            userid = event.message_chain.get_first(At).target
        if userid:
            # await makedaibu(userid)
            # return bot.send(event, await messagechain_builder(imgpath=f'./images/ImgGenerator/daibu_{userid}.png'))
            return await messagechain_sender(event=event,
                                             msg=await messagechain_builder(imgbase64=await makedaibu(userid)))


@bot.on(GroupMessage)
async def xka(event: GroupMessage):
    if not _cfg.get('SmallLove', False):
        return
    if event.sender.id in blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(
        fr"^(我是)?小可爱$", msg.strip())
    userid = None
    if m:
        if m.group(1):
            userid = event.sender.id
        elif At in event.message_chain:
            userid = event.message_chain.get_first(At).target
        if userid:
            try:
                member_profile = await bot.member_profile.get(event.group.id, userid)
                memberinfo = await bot.get_group_member(group=event.group.id, id_=userid)
                if memberinfo:
                    await makesmalllove(userid, memberinfo.member_name, member_profile.sex)
                else:
                    await makesmalllove(userid, member_profile.nickname, member_profile.sex)
                # await bot.send(event,
                #                await messagechain_builder(imgpath=f'./images/ImgGenerator/xiaokeai_{userid}.png'))
                await messagechain_sender(event=event,
                                          msg=await messagechain_builder(
                                              imgpath=f'./images/ImgGenerator/xiaokeai_{userid}.png'))
            except Exception as e:
                print(e)
                root_logger.error(f"制作并发生'小可爱'时发生了错误\n{e}")
    return


@bot.on(GroupMessage)
async def diuren(event: GroupMessage):
    """丢人制作"""
    if not _cfg.get('Throw', False):
        return
    if event.sender.id in blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^丢(\w+)?$", msg.strip())
    if m:
        userid = None
        if m.group(1):
            if m.group(1) in ['我', '我自己', '自己']:
                userid = event.sender.id
        elif At in event.message_chain:
            userid = event.message_chain.get_first(At).target
        if userid:
            img = await throwpeople(userid)
            # await bot.send(event, await messagechain_builder(imgbase64=img))
            await messagechain_sender(event=event, msg=await messagechain_builder(imgbase64=img))
        # else:
        #     await bot.send(event, await messagechain_builder(text='请At要丢的人哦~'))
    return


@bot.on(GroupMessage)
async def chiren(event: GroupMessage):
    """吃掉头像"""
    if not _cfg.get('Eat', False):
        return
    if event.sender.id in blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^吃掉?$", msg.strip())
    if m:
        if At in event.message_chain:
            userid = event.message_chain.get_first(At).target
            img = await eatpeople(userid)
            await messagechain_sender(event=event, msg=await messagechain_builder(imgbase64=img))
    return


@bot.on(GroupMessage)
async def juren(event: GroupMessage):
    """举高高"""
    if not _cfg.get('HoldUp', False):
        return
    if event.sender.id in blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^举(\w+)?$", msg.strip())
    if m:
        userid = None
        if m.group(1):
            if m.group(1) in ['我', '我自己', '自己']:
                userid = event.sender.id
        elif At in event.message_chain:
            userid = event.message_chain.get_first(At).target
        if userid:
            img = await holdup(userid)
            await bot.messagechain_sender(event=event, msg=await messagechain_builder(imgbase64=img))
    return


@bot.on(GroupMessage)
async def marry_random_group_member(event: GroupMessage):
    """每日找对象"""
    if not _cfg.get('Marry', False):
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(
        fr"^{commandpre}\s*(娶群友|找对象)\s*$", msg.strip())
    if m:
        if At in event.message_chain:
            at = event.message_chain.get_first(At)
            avatar = await get_head_sculpture(at.target)
            userimg = avatar.resize((200, 200), Image.ANTIALIAS)
            userimg = img_to_base64(userimg)
            return await messagechain_sender(event=event, msg=await messagechain_builder(at=event.sender.id,
                                                                                         text=f'你今天的老婆是 {at.display}',
                                                                                         imgbase64=userimg))
        else:
            time = datetime.datetime.now().strftime('%Y%m%d')
            seed = int(time) + event.sender.id
            random.seed(seed)
            memberlist = await bot.member_list.get(event.group.id)
            memberlist = memberlist.data
            member = memberlist[random.randint(0, len(memberlist) - 1)]
            if member.id == event.sender.id:
                return await messagechain_sender(event=event, msg=await messagechain_builder(at=event.sender.id,
                                                                                             text=f'倒霉的你今天没有对象'))
            if member.id == bot.qq:
                if not _cfg.get('bot_married', False):
                    if event.sender.id in admin:
                        return await messagechain_sender(event=event, msg=await messagechain_builder(at=event.sender.id,
                                                                                                     text=f'Lucky! '
                                                                                                          f'你今天的老婆是我这个小可爱 {bot_cfg.get("nickname")} 哦'))
                return await messagechain_sender(event=event, msg=await messagechain_builder(at=event.sender.id,
                                                                                             text=f'今天你不许娶群友'))
            avatar = await get_head_sculpture(member.id)
            userimg = avatar.resize((200, 200), Image.ANTIALIAS)
            userimg = img_to_base64(userimg)
            return await messagechain_sender(event=event, msg=await messagechain_builder(at=event.sender.id,
                                                                                         text=f'你今天的老婆是 {member.member_name}',
                                                                                         imgbase64=userimg))


@bot.on(GroupMessage)
async def marry_group_member(event: GroupMessage):
    """和指定群友结婚"""
    if not _cfg.get('Marry', False):
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(
        fr"^{commandpre}\s*(结婚|娶)\s*$", msg.strip())
    if m:
        if At in event.message_chain:
            at = event.message_chain.get_first(At)
            avatar = await get_head_sculpture(at.target)
            userimg = avatar.resize((200, 200), Image.ANTIALIAS)
            userimg = img_to_base64(userimg)
            count = random.random() * 100
            if count < 1:
                pass
            else:
                pass
            if at.target == event.sender.id:
                return await messagechain_sender(event=event, msg=await messagechain_builder(at=event.sender.id,
                                                                                             text=f'请不要自交!'))
            if at.target == bot.qq:
                if not _cfg.get('bot_married', False):
                    if event.sender.id in admin:
                        return await messagechain_sender(event=event, msg=await messagechain_builder(at=event.sender.id,
                                                                                                     text=f'Lucky! 你的小可爱 {bot_cfg.get("nickname")} 来了'))
                    return await messagechain_sender(event=event, msg=await messagechain_builder(at=event.sender.id,
                                                                                                 text=f'不许娶我'))
                return await messagechain_sender(event=event, msg=await messagechain_builder(at=event.sender.id,
                                                                                             text=f'小可爱 {bot_cfg.get("nickname")} 来了'))
            member = await bot.get_group_member(event.group.id, at.target)
            if member is None:
                return await messagechain_sender(event=event, msg=await messagechain_builder(text=f'Error,未找到此群友'))
            return await messagechain_sender(event=event, msg=await messagechain_builder(at=event.sender.id,
                                                                                         text=f'恭喜你和 {member.member_name} 结婚',
                                                                                         imgbase64=userimg))
