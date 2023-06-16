"""
:Author:  NekoRabi
:Update Time:  2022/8/16 16:17
:Describe: 重开图片生成
:Version: 0.0.2
"""
import base64
import os
import re
from io import BytesIO

import numpy
from PIL import ImageDraw, ImageFont, Image as IMG
from mirai import GroupMessage, Plain, MessageChain, Image

from core import bot, commandpre, add_help, config
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender
from utils.bufferpool import *
from utils.cfg_loader import read_file

if not os.path.exists("./images/Remake"):
    os.mkdir("./images/Remake")

score = 0
_remake_member = dict()
__all__ = ['getremakeimg']
_blackuser = config.get('blacklist', [])
_cfg = read_file(r'./config/Remake/config.yml')


def getattribute() -> list:
    """
    随机人物属性

    Returns:

    """
    global score
    attributelist = []
    for i in range(6):
        choice = numpy.random.randint(4, dtype=int)
        attributelist.append(choice)
        if choice == 0:
            score += 10
        else:
            score = score + 25 - i * 25
    return attributelist


def getstart(worlddifficulty: str = None, worldtype: str = None) -> list:
    """

    开始游戏

    Args:
        worlddifficulty: 世界难度
        worldtype: 世界类型

    Returns:

    """
    global score
    startlist = []
    for i in range(5):
        choice = numpy.random.randint(5, dtype=int)
        if i == 1:
            if choice == 0:
                score += 10
            elif choice == 2:
                score = score - 5
            elif score == 3:
                score = score - 15
            elif score == 4:
                score = score - 30
        elif i == 2:
            if worlddifficulty in ['peace', 'p', '0', '理想乡', '和平']:
                score = score - 50
                startlist.append(4)
                continue
            elif worlddifficulty in ['easy', 'e', '1', '桃园', '简单']:
                score = score - 25
                startlist.append(3)
                continue
            elif worlddifficulty in ['normal', 'common', '2', '普通', '一般']:
                startlist.append(2)
                continue
            elif worlddifficulty in ['hard', 'h', 'difficult', '3', '严酷', '困难']:
                score = score + 10
                startlist.append(1)
                continue
            elif worlddifficulty in ['Purgatory', 'Infernal', 'hell', 'vh', '4', '炼狱', '地狱', '超难']:
                score = score + 20
                startlist.append(0)
                continue
            else:
                score += choice * 25 - 50
        elif i > 2:
            score += 10 - 5 * choice
        else:
            if choice < 2:
                score += 20 - 10 * choice
            else:
                score += choice * 25 - 50
        startlist.append(choice)
    return startlist


def addfont(img: IMG, senderid):
    """
    添加文字

    :param img: PIL.Image
    :param senderid: 发消息的用户id，用来生成图片的uid
    :return:
    """
    draw = ImageDraw.Draw(img)
    h1font = ImageFont.truetype(
        font='./data/fonts/MiSans-Bold.ttf', size=40)
    h4font = ImageFont.truetype(
        font='./data/fonts/MiSans-Light.ttf', size=20)
    titlefont = ImageFont.truetype(
        font='./data/fonts/MiSans-Bold.ttf', size=60)

    _time = time.strftime('%Y-%m-%d', time.localtime())
    draw.text((10, 10), text=f'No.{senderid}', font=h4font, fill=(0, 0, 0))
    draw.text((710, 10), text=f'{_time}', font=h4font, fill=(0, 0, 0))
    draw.text((300, 10), text='重生档案', font=titlefont, fill=(0, 0, 0))

    draw.text((10, 80), text='基础能力', font=h1font, fill=(0, 0, 0))
    draw.text((190, 100), text='(力量/魔力/智力/体质/魅力/运气)', font=h4font, fill=(0, 0, 0))

    draw.text((10, 400), text='世界设定', font=h1font, fill=(0, 0, 0))
    draw.text((190, 420), text='(种族/性别/局势/开局/审美)', font=h4font, fill=(0, 0, 0))


def create_remakeimg(senderid: int, basic_score: int = 30, worlddifficulty: str = None, worldtype: str = None) -> IMG:
    """
    生成重开图片

    :param senderid: 发送人id
    :param basic_score: 基础分
    :param worlddifficulty: 世界难度
    :param worldtype: 世界类型
    :return:
    """
    bgk = IMG.new('RGB', (900, 800), (230, 220, 210))
    img = IMG.open('./plugin/Remake/remake.jpg').convert("RGBA")
    count = 0
    for i in getattribute():
        temp = img.crop((150 + 145 * i, 1915 + 245 * count,
                         295 + 145 * i, 2165 + 245 * count))
        bgk.paste(temp, (145 * count, 150, 145 *
                         count + temp.width, 150 + temp.height))
        count += 1
    count = 0
    for i in getstart(worlddifficulty):
        if count == 2:
            temp = img.crop((35 + 146 * i, 120 + 364 * count,
                             190 + 146 * i, 390 + 364 * count))
        elif count == 3:
            temp = img.crop((35 + 144 * i, 90 + 364 * count,
                             190 + 144 * i, 380 + 364 * count))
        else:
            temp = img.crop((35 + 146 * i, 90 + 364 * count,
                             190 + 146 * i, 360 + 364 * count))
        bgk.paste(temp, (145 * count, 460, 145 *
                         count + temp.width, 460 + temp.height))
        count += 1

    addfont(bgk, senderid=senderid)
    # bgk.save(fp=f'./images/Remake/{senderid}.png')
    return img_to_base64(bgk)


def img_to_base64(PILimg: IMG):
    """
    图片转换为base64的格式

    Args:
        PILimg: PIL的图片

    Returns:base64的图片

    """
    img_bytes = BytesIO()

    PILimg.save(img_bytes, format='PNG')
    b_content = img_bytes.getvalue()
    imgcontent = base64.b64encode(b_content)
    return imgcontent


@bot.on(GroupMessage)
async def getremakeimg(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_cfg['command']}", msg.strip())
    if m:
        senderid = event.sender.id
        if senderid in _blackuser:
            return await messagechain_sender(event=event, msg=await messagechain_builder(text='你已被列入黑名单', at=senderid))
        if not cmdbuffer.updategroupcache(GroupCommand(event.group.id, senderid, 'remake')):
            return await messagechain_sender(event=event, msg=await messagechain_builder(text="好快的重开", at=senderid))
        _today = time.strftime('%Y%m%d', time.localtime())
        if _remake_member.get(senderid, None) is None:
            _remake_member[senderid] = dict(time=_today, remakecount=0)
        member_info = _remake_member.get(senderid)
        if member_info['time'] != _today:
            _remake_member[senderid] = dict(time=_today, remakecount=1)
        else:
            if member_info['remakecount'] >= _cfg['remake_perday']:
                return await messagechain_sender(event=event,
                                                 msg=await messagechain_builder(text=f'每天只能重开{_cfg["remake_perday"]}次哦',
                                                                                at=senderid))
            member_info['remakecount'] += 1
        if m.group(2):
            basic_score = int(m.group(2))
        else:
            basic_score = 30
        if m.group(3):
            worlddifficulty = m.group(3)
        else:
            worlddifficulty = None
        b64 = create_remakeimg(senderid, basic_score=basic_score,
                               worlddifficulty=worlddifficulty)
        # await messagechain_sender(event=)(eventmsg=, MessageChain(Image(path=f'./images/Remake/{senderid}.png')))
        await messagechain_sender(event=event, msg=MessageChain(Image(base64=b64)))
    return


add_help('group', "重开 / remake : 异世界转生\n")
