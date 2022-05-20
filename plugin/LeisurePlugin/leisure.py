import sqlite3
import time
import os
from mirai import MessageChain
from utils.MessageChainBuilder import buildmessagechain
from plugin.LeisurePlugin.tarot import TarotCards

if not os.path.exists("./database/LeisurePlugin"):
    os.mkdir("./database/LeisurePlugin")


def signup(userid: int) -> tuple:
    singinmsg = "签到成功,积分+1\n当前积分 : "
    cx = sqlite3.connect("./database/LeisurePlugin/leisure.sqlite")
    cursor = cx.cursor()
    cursor.execute('create table IF NOT EXISTS userinfo('
                   'id integer primary key,'
                   'userid integer UNIQUE,'
                   'score integer default 0,'
                   'lastsignin varchar(50)'
                   ')')
    cx.commit()
    today = time.strftime('%Y-%m-%d', time.localtime())
    cursor.execute(f"select score,lastsignin from userinfo where userid = {userid}")
    user = cursor.fetchall()
    if len(user) == 0:
        cursor.execute(f"insert into userinfo(userid,score,lastsignin) values({userid},1,'{today}')")
        cx.commit()
        singinmsg += "1\n这是你今天的塔罗牌"
    elif today != user[0][1]:
        cursor.execute(f"update userinfo set lastsignin = '{today}',score = {user[0][0] + 1} where userid = {userid}")
        cx.commit()
        singinmsg += f"{user[0][0] + 1}\n这是你今天的塔罗牌"
    else:
        return False, "一天只能签到一次哦~"
    cursor.close()
    cx.close()
    return True, singinmsg


def getscore(userid: int):
    score = 0
    cx = sqlite3.connect("./database/LeisurePlugin/leisure.sqlite")
    cursor = cx.cursor()
    cursor.execute('create table IF NOT EXISTS userinfo('
                   'id integer primary key,'
                   'userid integer UNIQUE,'
                   'score integer default 0,'
                   'lastsignin varchar(50)'
                   ')')
    cx.commit()
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


def startfishing(userid: int) -> dict:
    msg = ""
    errmsg = ""
    return dict(success=True, msg=msg, errmsg=errmsg)


def endfishing(userid: int) -> dict:
    msg = ""
    errmsg = ""
    return dict(success=True, msg=msg, errmsg=errmsg)
