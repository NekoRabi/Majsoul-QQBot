import sqlite3
import time
import os

if not os.path.exists("./database/LeisurePlugin"):
    os.mkdir("./database/LeisurePlugin")


def siginin(userid: int) -> str:
    singinmsg = "签到成功,积分+1\n当前积分 : "
    cx = sqlite3.connect("./database/LeisurePlugin/leisure")
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
        singinmsg += "1"
    elif today != user[0][1]:
        cursor.execute(f"update userinfo set lastsignin = '{today}',score = {user[0][0] + 1} where userid = {userid}")
        cx.commit()
        singinmsg += str(user[0][0] + 1)
    else:
        singinmsg = "一天只能签到一次哦~"
    cursor.close()
    cx.close()
    return singinmsg


def getscore(userid: int):
    score = 0
    cx = sqlite3.connect("./database/LeisurePlugin/leisure")
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
