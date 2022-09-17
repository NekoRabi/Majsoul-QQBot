"""
:Author:  NekoRabi
:Update Time:  2022/8/16 20:02
:Describe: 塔罗牌抽卡
:Version: 0.0.1
"""

import os
import random
import base64
import re
import sqlite3
import time
import yaml
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from mirai import GroupMessage, Plain
from mirai.models import ForwardMessageNode, Forward
from core import bot, commandpre, commands_map
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender
from utils.cfg_loader import write_file

__all__ = ['getsometarots', 'getmytarots', 'tarotcards']


def write_default_cfg():
    interpretation = dict(tarot=[
        dict(name="愚者 (The Fool)",
             positive="从零开始; 好赌运; 不墨守成规; 追求新奇的梦想; 冒险; 放浪形骸; 艺术家的气质; 异于常人; 直攻要害、盲点; 爱情狩猎者; 爱情历经沧桑; 不拘形式的自由恋爱",
             negative="不安定; 孤注一掷会失败; 缺乏责任感; 损失; 脚跟站不稳; 堕落; 没发展; 没计划; 走错路; 行为乖张; 轻浮的恋情; 感情忽冷忽热; 不安定的爱情之旅)",
             imageName="TheFool.jpg"
             ),
        dict(name="魔术师 (The Magician)",
             positive="好的开始; 具独创性; 有发展的; 新计划成功; 想像力丰富或有好点子; 有恋情发生; 拥有默契良好的伴侣; 有新恋人出现; 值得效仿的对象出现",
             negative="失败; 优柔寡断; 才能平庸; 有被欺诈的危险; 技术不足; 过于消极; 没有判断力; 缺乏创造力; 爱情没有进展",
             imageName="The Magician.jpg"),
        dict(name="女祭司 (The High Priestess)",
             positive="知性、优秀的判断力; 具洞察力及先见之明; 强大的战斗意志; 冷静的统率力; 学问、研究等精神方面幸运; 独立自主的女性; 柏拉图式的爱情; 有心灵上交往至深的友人; 冷淡的恋情",
             negative="无知、缺乏理解力; 研究不足; 不理性的态度; 自我封闭; 神经质; 洁癖; 与女性朋友柒争执; 对人冷淡; 晚婚或独身主义; 没有结果的单相思; 气色不好; 不孕",
             imageName="The High Priestess.jpg", )
    ])
    write_file(interpretation, r'./config/Tarot/data.yml')


def file_init():
    if not os.path.exists(r"./images/Tarot"):
        os.mkdir(r"./images/Tarot")
    if not os.path.exists(r'./database/Tarot'):
        os.mkdir(r'./database/Tarot')
    if not os.path.exists(r"./config/Tarot"):
        os.mkdir(r"./config/Tarot")
        write_default_cfg()
    if not os.path.exists(r"./config/Tarot/data.yml"):
        write_default_cfg()
    cx = sqlite3.connect("./database/Tarot/Tarot.sqlite")
    cursor = cx.cursor()
    cursor.execute("create table if not exists playerdrawcard("
                   "id integer primary key,"
                   "userid integer not null,"
                   "drawtime varchar(50) not null,"
                   "cardid integer not null,"
                   "cardposition integer not null"
                   ")")
    cursor.execute("create table if not exists drawtarots("
                   "id integer primary key,"
                   "userid integer not null,"
                   "drawtime varchar(50) not null,"
                   "cardname text not null,"
                   "cardposition text not null"
                   ")")
    cx.commit()
    cx.close()


def addfont(img: Image, text: str, position: tuple = (0, 0), textcolor=(0, 0, 0), size=20):
    textlist = text.split(';')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(
        font='./plugin/Tarot/MiSans-Light.ttf', size=size)
    linetext = []
    temptext0 = ''
    temptext1 = ''
    for item in textlist:
        temptext0 += item.strip() + ';'
        if font.getsize(temptext0)[0] > img.width:
            linetext.append(temptext1.strip())
            temptext0 = item
        temptext1 = temptext0
    if temptext0.strip() != '':
        linetext.append(temptext0.strip())
    for i in range(len(linetext)):
        draw.text((position[0], position[1] + i * (size + 2)), text=linetext[i], font=font, fill=textcolor)


def calculate_allfont_height(text, fontsize, maxwidth=948):
    textlist = text.split(';')
    font = ImageFont.truetype(
        font='./plugin/Tarot/MiSans-Light.ttf', size=fontsize)
    linetext = []
    temptext0 = ''
    temptext1 = ''
    for item in textlist:
        temptext0 += item.strip() + ';'
        if font.getsize(temptext0)[0] > maxwidth:
            linetext.append(temptext1.strip())
            temptext0 = item
        temptext1 = temptext0
    if temptext0.strip() != '':
        linetext.append(temptext0.strip())
    return len(linetext) * (fontsize + 2)


class TarotCard:

    def __init__(self, config):
        self.imgcontent = None
        self.position = config['position']
        self.imageName = config['imageName']
        if self.position == 'positive':
            self.effective = config['positive']
            self.name = '正位 ' + config['name']
        else:
            self.effective = config['negative']
            self.name = '逆位 ' + config['name']
        self.buildcard()

    def buildcard(self, path=None):
        if not path:
            path = f'./plugin/Tarot/Images/{self.imageName}'
        source_card = Image.open(path).convert("RGBA")
        width, height = source_card.size
        if self.position == 'negative':
            source_card = source_card.rotate(180)
        new_height = calculate_allfont_height(self.effective, 20, width) + calculate_allfont_height(self.name, 20,
                                                                                                    width) + 20
        bgk = Image.new('RGB', (width, height + new_height), (255, 255, 255))
        bgk.paste(source_card, (0, 0, width, height))
        addfont(bgk, text=self.name, position=(0, height))
        addfont(bgk, text=self.effective, position=(0, height + 30))
        img_bytes = BytesIO()

        bgk.save(img_bytes, format='JPEG')
        b_content = img_bytes.getvalue()
        self.imgcontent = base64.b64encode(b_content)


class TarotCards:

    def __init__(self):
        with open('./config/Tarot/data.yml', 'r', encoding='utf-8') as cfg:
            tarotdata = yaml.safe_load(cfg)
        self.imgdata = tarotdata['tarot']

    def drawcards(self, count=1, userid=None):
        cardslist = []
        for i in range(count):
            cardinfo = random.choice(self.imgdata)
            if random.random() < 0.5:
                position = 'negative'
            else:
                position = 'positive'
            cardinfo['position'] = position
            if userid:
                self.dboperation(
                    sql=f'''insert into drawtarots(userid,drawtime,cardname,cardposition) values({userid},"{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}","{cardinfo['name']}","{cardinfo['position']}")''',
                    update=True)
            cardslist.append(TarotCard(cardinfo))
        return cardslist

    def getmydrawcardsinfo(self, userid):
        result = self.dboperation(
            sql=f'''select count(cardname),cardname as drawcounts from drawtarots where userid = {userid} group by cardname''',
            col_sep='张')
        msg = f"你总共抽了{result}"
        return msg

    @staticmethod
    def dboperation(sql, update=False, colindex=None, col_sep="", row_sep=",", optsource=False):
        try:
            cx = sqlite3.connect("./database/Tarot/Tarot.sqlite")
            cursor = cx.cursor()
            cursor.execute(sql)
            if update:
                cx.commit()
                opt = "操作成功"
            else:
                fetchall = cursor.fetchall()
                if optsource:
                    opt = fetchall
                else:
                    opt = ""
                    if colindex is None:
                        colindex = -1
                    elif type(colindex) is int:
                        colindex = [colindex]
                    elif type(colindex) is list:
                        pass
                    else:
                        colindex = -1
                        print(f'colindex输入有误,自动变为获取所有')
                    for item in fetchall:
                        if colindex == -1:
                            for i in item:
                                opt += f'{i}{col_sep}'
                        else:
                            for index in colindex:
                                opt += f'{item[index]}{col_sep}'
                        opt = opt[:-1] + f'{row_sep}'
            cursor.close()
            cx.close()
            return opt
        except Exception as e:
            print(e)
            return f'{e}'


file_init()

tarotcards = TarotCards()


@bot.on(GroupMessage)
async def getsometarots(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{commands_map['sys']['tarot']}", msg.strip())
    if m:
        if m.group(1):
            num = int(m.group(1))
            if 0 < num < 10:
                cards = tarotcards.drawcards(count=num, userid=event.sender.id)
                msgC = []
                for card in cards:
                    fmn = ForwardMessageNode(
                        sender_id=event.sender.id,
                        sender_name=event.sender.get_name(),
                        message_chain=messagechain_builder(
                            imgbase64=card.imgcontent)
                    )
                    # fmn = ForwardMessageNode.create(event.sender,MessageChain([Image(base64=card.imgcontent)]))
                    msgC.append(fmn)
                    # msgC.append(Image(base64=card.imgcontent))
                # ForwardMessageNode(event.sender,MessageChain(msgC))
                return await bot.send(event, Forward(node_list=msgC))
            else:
                return await messagechain_sender(event=event, msg=messagechain_builder(text='每次只能抽1-9张塔罗牌哦', rndimg=True))
        else:
            card = tarotcards.drawcards(userid=event.sender.id)[0]
            return await bot.send(event, messagechain_builder(imgbase64=card.imgcontent))


# 获取塔罗牌抽卡记录

@bot.on(GroupMessage)
async def getmytarots(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{commands_map['sys']['getmytarot']}", msg.strip())
    if m:
        msg = tarotcards.getmydrawcardsinfo(event.sender.id)
        return await bot.send(event, messagechain_builder(text=msg))
