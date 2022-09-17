"""
:Author:  NekoRabi
:Create:  2022/9/18 3:13
:Update: /
:Describe: 签到功能，也是系统数据库
:Version: 0.0.1
"""
import datetime
import os
import re
import sqlite3
import time

from mirai import GroupMessage, Plain
from core import bot, commandpre, commands_map
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender

if not os.path.exists("./database/sys"):
    os.mkdir("./database/sys")

usetarot = False

if os.path.exists(r'./plugin/Tarot/tarot.py'):
    usetarot = True


def db_init():
    cx = sqlite3.connect("./database/sys/sys.sqlite")
    cursor = cx.cursor()
    cursor.execute('create table IF NOT EXISTS userinfo('
                   'id integer primary key,'
                   'userid integer UNIQUE,'
                   'score integer default 0,'
                   'lastsignin varchar(50),'
                   'keepsigndays integer not null default 1'
                   ')')
    cx.commit()
    cx.close()


__all__ = ['sign_In', 'getuserscore']


def sign_in(userid: int) -> tuple:
    singinmsg = "签到成功,积分+1\n当前积分 : "
    cx = sqlite3.connect("./database/sys/sys.sqlite")
    cursor = cx.cursor()
    today = time.strftime('%Y-%m-%d', time.localtime())
    td_stamp = int(time.mktime(time.strptime(today, "%Y-%m-%d")))
    cursor.execute(f"select score,lastsignin,keepsigndays from userinfo where userid = {userid}")
    user = cursor.fetchall()
    if len(user) == 0:
        cursor.execute(f"insert into userinfo(userid,score,lastsignin) values({userid},1,'{today}')")
        cx.commit()
        singinmsg += "1\n这是你今天的塔罗牌"
        return True, singinmsg
    lastday_stamp = int(time.mktime(time.strptime(user[0][1], "%Y-%m-%d")))
    differ = (datetime.datetime.fromtimestamp(td_stamp) - datetime.datetime.fromtimestamp(lastday_stamp)).days
    if today != user[0][1]:
        if differ == 1:
            singinmsg += f"{user[0][0] + 1},你已连续签到{user[0][2] + 1}天\n这是你今天的塔罗牌"
            cursor.execute(
                f"update userinfo set lastsignin = '{today}',score = score + 1,keepsigndays = keepsigndays + 1 where userid = {userid}")
        else:
            singinmsg += f"{user[0][0] + 1},连续签到中断惹~\n这是你今天的塔罗牌"
            cursor.execute(
                f"update userinfo set lastsignin = '{today}',score = score + 1 ,keepsigndays = 1 where userid = {userid}")
        cx.commit()
    else:
        return False, "一天只能签到一次哦~"
    cursor.close()
    cx.close()
    return True, singinmsg


def getscore(userid: int):
    score = 0
    cx = sqlite3.connect("./database/sys/sys.sqlite")
    cursor = cx.cursor()
    cursor.execute(f"select score from userinfo where userid = {userid}")
    user = cursor.fetchone()
    if len(user) == 0:
        cursor.execute(f"insert into userinfo(userid,score,lastsignin) values({userid},0,'0')")
        cx.commit()
    else:
        score = user[0]
    cursor.close()
    cx.close()
    return f"当前积分 : {score}"

# 签到获取积分

@bot.on(GroupMessage)
async def sign_In(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{commands_map['sys']['signin']}", msg.strip())
    if m:
        success, signmsg = sign_in(event.sender.id)
        if success:
            if usetarot:
                from plugin.Tarot.tarot import tarotcards
                card = tarotcards.drawcards(userid=event.sender.id)[0]
                return await bot.send(event,
                                      messagechain_builder(at=event.sender.id, text=signmsg, imgbase64=card.imgcontent))
            else:
                return await messagechain_sender(messagechain_builder(at=event.sender.id, text=signmsg))
        else:
            return await bot.send(event, messagechain_builder(at=event.sender.id, text=signmsg, rndimg=True))


# 查询积分

@bot.on(GroupMessage)
async def getuserscore(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{commands_map['sys']['getscore']}", msg.strip())
    if m:
        scoremsg = getscore(
            userid=event.sender.id)
        return await bot.send(event, messagechain_builder(text=scoremsg, rndimg=True))


db_init()
