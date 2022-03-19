import gzip
import datetime
import random

import pytz
import re
import sqlite3
import os

import requests

user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) Gecko/20100101 Firefox/61.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
]

# 解压gz
def un_gz(file_name):
    """ungz zip file"""
    f_name = file_name.replace(".gz", "")
    # 获取文件的名称，去掉
    g_file = gzip.GzipFile(file_name)
    # 创建gzip对象
    open(f_name, "wb").write(g_file.read())
    # gzip对象用read()打开后，写入open()建立的文件里。
    g_file.close()
    # 关闭gzip对象

# 自动抓取天风对局
def autoget_th_match()->list:
    # tz = pytz.timezone('Asia/Tokyo')
    tz= pytz.timezone('Asia/Shanghai')
    nowtime = datetime.datetime.now(tz=tz).strftime("%Y%m%d%H")
    # daytime = time.strftime("%Y-%m-%d", time.localtime())
    daytime = datetime.datetime.now(tz=tz).strftime("%Y-%m-%d")
    msglist = []

    response = requests.get(f'https://tenhou.net/sc/raw/dat/scb{nowtime}.log.gz',
                            headers={'User-Agent': random.choice(user_agent_list)}, allow_redirects=True)
    open(f'./data/TenHouPlugin/scb{nowtime}.log.gz', 'wb').write(response.content)
    un_gz(f'./data/TenHouPlugin/scb{nowtime}.log.gz')
    os.remove(f'./data/TenHouPlugin/scb{nowtime}.log.gz')
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()
    cx.commit()
    cursor.execute("select playername from watchedplayer")
    result = cursor.fetchall()
    playername = []
    for player in result:
        playername.append(player[0])
    print(playername)
    with open(f'./data/TenHouPlugin/scb{nowtime}.log', 'r', encoding='utf-8') as f:
    # with open(f'./scb2022031811.log', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            datas = line.split('|')
            startTime = datas[0].strip()
            duration = datas[1].strip()
            model = datas[2].strip()
            players = datas[3].strip()
            plname = re.sub("[(\d+\.\-)]", "", players)
            plname = plname.split(' ')
            players = players.split(' ')
            for p in plname:
                if p in playername:
                    print(f"{datas}\n")
                    cursor.execute(f"select * from paipu where player1 = '{players[0]}' and startTime = '{daytime} {startTime}'")
                    record = cursor.fetchall()
                    if len(record) > 0:
                        print("该记录已存在")
                        break
                    print(f"检测到{p}新的对局信息")
                    msg = "检测到新的对局信息:\n"
                    msg += f"{model}\n"
                    msg += f"结束时间: {daytime} {startTime} , 对局时长: {duration}\n"
                    msg += datas[3].strip()
                    if len(players) == 3:
                        cursor.execute(
                            f'insert into paipu(startTime,duration,model,player1,player2,player3,player4) values("{daytime} {startTime}","{duration}","{model}","{players[0]}","{players[1]}","{players[2]}","Null")')
                    else:
                        cursor.execute(
                            f'insert into paipu(startTime,duration,model,player1,player2,player3,player4) values("{daytime} {startTime}","{duration}","{model}","{players[0]}","{players[1]}","{players[2]}","{players[3]}")')
                    cx.commit()
                    msglist.append(dict(playername=p,msg=msg))
                    break
    os.remove(f'./data/TenHouPlugin/scb{nowtime}.log')
    cursor.close()
    cx.close()
    print(msglist)
    return forwardmessage(msglist)


def forwardmessage(msglist:list) ->list:
    messageChainList = []
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()
    for item in msglist:
        groupids = []
        cursor.execute(f'''select groupid from group2player where playername = "{item['playername']}"''')
        for g in cursor.fetchall():
            groupids.append(g[0])
        messageChainList.append(dict(groups = groupids,msg = item['msg']))
    cursor.close()
    cx.close()
    return messageChainList


# 添加关注
def addthwatch(playername:str,groupid:int):
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()

    cursor.execute(f'select * from watchedplayer where playername = "{playername}"')
    if len(cursor.fetchall())>0:
        print("该用户已添加进关注列表")
    else:
        cursor.execute(f'insert into watchedplayer(playername) values("{playername}")')
        cx.commit()
        print(f"已将{playername}添加到数据库")

    cursor.execute(f'select * from QQgroup where groupid = {groupid}')
    if len(cursor.fetchall())>0:
        print("该群已注册进列表")
    else:
        cursor.execute(f'insert into QQgroup(groupid) values({groupid})')
        cx.commit()
        print(f"已将群组{groupid}添加到数据库")

    cursor.execute(f'select * from group2player where groupid = {groupid} and playername = "{playername}"')
    if len(cursor.fetchall())>0:
        print("该用户已添加进此群的关注列表")
        return "该用户已添加进此群的关注列表,无需重复添加"
    else:
        cursor.execute(f'insert into group2player(playername,groupid) values("{playername}",{groupid})')
        cx.commit()
        print(f"已将{playername}添加到群聊{groupid}的关注")

    cursor.close()
    cx.close()
    return "添加成功"


def removethwatch(playername:str,groupid:int):
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()

    cursor.execute(f'select * from watchedplayer where playername = "{playername}"')
    if len(cursor.fetchall()) ==0:
        print("未关注该用户")
        return "未关注该用户"
    else:
        cursor.execute(f'select * from group2player where groupid = {groupid} and playername = "{playername}"')
        if len(cursor.fetchall()) > 0:
            cursor.execute(f"delete from group2player where playername = '{playername}' and groupid = {groupid}")
            cx.commit()
        else:
            print("此群未关注该用户")
            return "此群未关注该用户"
        cursor.execute(f'select * from group2player where playername = "{playername}"')
        if len(cursor.fetchall()) == 0:
            cursor.execute(f"delete from watchedplayer where playername = '{playername}'")
            cx.commit()
        print(f"将{playername}从群聊{groupid}的关注中删除成功")
        return "删除成功"


def getthwatch(groupid :int) ->str:
    msg = "本群关注的天凤玩家有:\n"
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()

    cursor.execute(f'select playername from group2player where groupid = {groupid}')
    result = cursor.fetchall()
    for player in result:
        msg+= player[0] + " "
    return msg


