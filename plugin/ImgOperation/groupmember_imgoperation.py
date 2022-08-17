import random

from utils.MessageChainBuilder import *
from mirai import GroupMessage, At, Plain
# from plugin.preinit.create_bot import bot
from core import bot
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw

import aiohttp
import re
import os
import base64

if not os.path.exists("./images/ImgOperation"):
    os.mkdir("./images/ImgOperation")

__all__ = ['xka', 'daiburen']


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
        font='./plugin/ImgOperation/MiSans-Bold.ttf', size=fontsize)
    if center:
        pxlength = fontstyle.getsize(text)[0]
        pos_x = (img.width - pxlength) // 2
    draw.text((pos_x, pos_y), text=text, font=fontstyle, fill=fontcolor)
    return fontsize


async def get_head_sculpture(userid) -> Image:
    url = f'http://q1.qlogo.cn/g?b=qq&nk={userid}&s=640'
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            img_content = await resp.read()
    return Image.open(BytesIO(img_content)).convert("RGBA")


async def makedaibu(userid):
    avatar = await get_head_sculpture(userid)
    ima = avatar.resize((130, 130), Image.ANTIALIAS)
    bgk = Image.open('./plugin/ImgOperation/image/daibu.png').convert("RGBA")
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
    bgk.save(fp=f'./images/ImgOperation/xiaokeai_{userid}.png')


@bot.on(GroupMessage)
async def daiburen(event: GroupMessage):
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
            # return bot.send(event, messagechain_builder(imgpath=f'./images/ImgOperation/daibu_{userid}.png'))
            return await bot.send(event, messagechain_builder(imgbase64=await makedaibu(userid)))


@bot.on(GroupMessage)
async def xka(event: GroupMessage):
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
                await bot.send(event, messagechain_builder(imgpath=f'./images/ImgOperation/xiaokeai_{userid}.png'))
            except Exception as e:
                print(e)
                pass
            return
