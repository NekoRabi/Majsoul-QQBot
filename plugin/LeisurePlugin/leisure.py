import sqlite3
import time, datetime
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
    today = time.strftime('%Y-%m-%d', time.localtime())
    td_stamp = int(time.mktime(time.strptime(today, "%Y-%m-%d")))
    cursor.execute(f"select score,lastsignin,keepsigndays from userinfo where userid = {userid}")
    user = cursor.fetchall()
    if len(user) == 0:
        cursor.execute(f"insert into userinfo(userid,score,lastsignin) values({userid},1,'{today}')")
        cx.commit()
        singinmsg += "1\n这是你今天的塔罗牌"
        return True,singinmsg
    lastday_stamp = int(time.mktime(time.strptime(user[0][1], "%Y-%m-%d")))
    differ = (datetime.datetime.fromtimestamp(td_stamp) - datetime.datetime.fromtimestamp(lastday_stamp)).days
    if today != user[0][1]:
        if differ == 1:
            singinmsg += f"{user[0][0] + 1},你已连续签到{user[0][2] + 1}天\n这是你今天的塔罗牌"
            cursor.execute(
                f"update userinfo set lastsignin = '{today}',score = {user[0][0] + 1},keepsigndays = {user[0][2]+1} where userid = {userid}")
        else:
            singinmsg += f"{user[0][0] + 1},连续签到中断惹~\n这是你今天的塔罗牌"
            cursor.execute(f"update userinfo set lastsignin = '{today}',score = {user[0][0] + 1},keepsigndays = 1 where userid = {userid}")
        cx.commit()
    else:
        return False, "一天只能签到一次哦~"
    cursor.close()
    cx.close()
    return True, singinmsg


def getscore(userid: int):
    score = 0
    cx = sqlite3.connect("./database/LeisurePlugin/leisure.sqlite")
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


def startfishing(userid: int) -> dict:
    msg = ""
    errmsg = ""
    return dict(success=True, msg=msg, errmsg=errmsg)


def endfishing(userid: int) -> dict:
    msg = ""
    errmsg = ""
    return dict(success=True, msg=msg, errmsg=errmsg)
