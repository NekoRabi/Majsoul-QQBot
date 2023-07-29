"""
:Author:  NekoRabi
:Create:  2023/6/16 1:50
:Update: /
:Describe: CS击杀制作
:Version: 0.0.1
"""
import os
import re

from PIL import Image as IMG, ImageDraw, ImageFont
from mirai import GroupMessage, Plain, Image

from core import bot, commandpre, blacklist

from utils.cfg_loader import read_file

__all__ = ['bwimg']

from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender

if not os.path.exists("./images/ImgGenerator"):
    os.mkdir("./images/ImgGenerator")

_cfg = read_file(r'./config/ImgGenerator/config.yml')


def makebwimg(imgname, text: str = ""):
    filename = os.path.splitext(imgname)[0]
    suffixname = os.path.splitext(imgname)[-1]
    if suffixname == '.jpg':
        suffixname = '.jpeg'
    img = IMG.open(f'./images/tempimg/{filename}{suffixname}').convert('L')
    width = img.width
    height = img.height
    if width > height:
        fontsize = height // 10
    else:
        fontsize = width // 10
    textlength = len(text)
    if textlength == 0:
        textlength = 1
    if fontsize > width / textlength:
        fontsize = width // textlength
    font = ImageFont.truetype(
        font='./plugin/ImgGenerator/MiSans-Bold.ttf', size=fontsize)
    bgimg = IMG.new('RGB', (width, height + 30 + fontsize), (0, 0, 0))
    bgimg.paste(img, (0, 0, width, height))
    textdraw = ImageDraw.Draw(bgimg)
    textdraw.text(((width - font.getsize(text)[0]) / 2, height + 10), text=f'{text}', font=font, fill=(255, 255, 255))
    bgimg.save(f'./images/ImgGenerator/{filename}{os.path.splitext(imgname)[-1]}')


def deletesource(imgname):
    filename = os.path.splitext(imgname)[0]
    suffixname = os.path.splitext(imgname)[-1]
    if suffixname == '.jpg':
        suffixname = '.jpeg'
    if os.path.exists(f'./images/ImgGenerator/{filename}{suffixname}'):
        os.remove(f'./images/ImgGenerator/{filename}{suffixname}')
    if os.path.exists(f'./images/ImgGenerator/{imgname}'):
        os.remove(f'./images/ImgGenerator/{imgname}')


@bot.on(GroupMessage)
async def bwimg(event: GroupMessage):
    if not _cfg.get('BW_img', False):
        return
    if event.sender.id in blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(
        fr"^{commandpre}\s*bw\s*(\S+)\s*$", msg.strip())
    if m and event.message_chain.has(Image):
        # try:
        img = event.message_chain.get_first(Image)
        imgname = img.image_id
        await img.download(filename=f'./images/tempimg/{imgname}')
        makebwimg(imgname, m.group(1))
        # await bot.send(event, await messagechain_builder(imgpath=f'./images/ImgGenerator/{imgname}'))
        await messagechain_sender(event=event,
                                  msg=await messagechain_builder(imgpath=f'./images/ImgGenerator/{imgname}'))
        deletesource(imgname)
        # except Exception as e:
        #     print(e)
        #     rootLogger.exception(e)
