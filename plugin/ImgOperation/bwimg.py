import os
import re

from PIL import Image as IMG, ImageDraw, ImageFont
from mirai import GroupMessage, Plain, Image, MessageChain

# from plugin.preinit.create_bot import bot
from core import bot, commandpre, commands_map

if not os.path.exists("./images/ImgOperation"):
    os.mkdir("./images/ImgOperation")


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
        font='./plugin/ImgOperation/MiSans-Bold.ttf', size=fontsize)
    bgimg = IMG.new('RGB', (width, height + 30 + fontsize), (0, 0, 0))
    bgimg.paste(img, (0, 0, width, height))
    textdraw = ImageDraw.Draw(bgimg)
    textdraw.text(((width - font.getsize(text)[0]) / 2, height + 10), text=f'{text}', font=font, fill=(255, 255, 255))
    bgimg.save(f'./images/ImgOperation/{filename}{os.path.splitext(imgname)[-1]}')


def deletesource(imgname):
    filename = os.path.splitext(imgname)[0]
    suffixname = os.path.splitext(imgname)[-1]
    if suffixname == '.jpg':
        suffixname = '.jpeg'
    if os.path.exists(f'./images/ImgOperation/{filename}{suffixname}'):
        os.remove(f'./images/ImgOperation/{filename}{suffixname}')
    if os.path.exists(f'./images/ImgOperation/{imgname}'):
        os.remove(f'./images/ImgOperation/{imgname}')


@bot.on(GroupMessage)
async def bwimg(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(
        fr"^{commandpre}{commands_map['imgoperation']['bw']}", msg.strip())
    if m and event.message_chain.has(Image):
        # try:
        img = event.message_chain.get_first(Image)
        imgname = img.image_id
        await img.download(filename=f'./images/tempimg/{imgname}')
        makebwimg(imgname, m.group(1))
        await bot.send(event, MessageChain([Image(path=f'./images/ImgOperation/{imgname}')]))
        deletesource(imgname)
        # except Exception as e:
        #     print(e)
        #     rootLogger.exception(e)
