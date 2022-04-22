import asyncio
import base64
import gzip
import datetime
import random

import aiohttp
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

bordercast_temple = {
    4: {
        1: " %player% 轻松拿下一位,实在太强啦",
        2: " %player% 悄悄拿下二位,稳稳上分",
        3: " %player% 精准避四，避开重大损失",
        4: " %player% 被安排了一个四位,库鲁西~"
    },
    3: {
        1: " %player% 轻松拿下一位,实在太强啦",
        2: " %player% 悄悄拿二,默默上分",
        3: " %player% 忍痛吃三，太苦了"
    }
}

timeout = aiohttp.ClientTimeout(total=330)


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


# 自动抓取天风结算 - 普通爬虫
def autoget_th_match() -> list:
    jptz = pytz.timezone('Asia/Tokyo')
    zhtz = pytz.timezone('Asia/Shanghai')
    minute = datetime.datetime.now(tz=zhtz).strftime("%M")
    zhnowtime = datetime.datetime.now(tz=zhtz).strftime("%Y%m%d%H")
    jpnowtime = datetime.datetime.now(tz=jptz).strftime("%Y%m%d%H")
    zhdaytime = datetime.datetime.now(tz=zhtz).strftime("%Y-%m-%d")
    jpdaytime = datetime.datetime.now(tz=jptz).strftime("%Y-%m-%d")

    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()
    if int(minute) <= 10:
        timelist = [dict(nowtime=zhnowtime, daytime=zhdaytime)]
    else:
        timelist = [dict(nowtime=zhnowtime, daytime=zhdaytime), dict(nowtime=jpnowtime, daytime=jpdaytime)]

    msglist = []
    for usetime in timelist:
        response = requests.get(f'https://tenhou.net/sc/raw/dat/scb{usetime["nowtime"]}.log.gz',
                                headers={'User-Agent': random.choice(user_agent_list)}, allow_redirects=True)
        open(f'./data/TenHouPlugin/scb{usetime["nowtime"]}.log.gz', 'wb').write(response.content)
        un_gz(f'./data/TenHouPlugin/scb{usetime["nowtime"]}.log.gz')
        os.remove(f'./data/TenHouPlugin/scb{usetime["nowtime"]}.log.gz')
        cursor.execute("select playername from watchedplayer")
        result = cursor.fetchall()
        playername = []
        for player in result:
            playername.append(player[0])
        with open(f'./data/TenHouPlugin/scb{usetime["nowtime"]}.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                datas = line.split('|')
                startTime = datas[0].replace('－ ', '')
                duration = datas[1].strip()
                model = datas[2].replace('－', '').strip()
                players = datas[3].strip()
                plname = re.sub(r"[(\d+\.\-)]", "", players)
                plname = plname.split(' ')
                players = players.split(' ')
                for p in plname:
                    if p in playername:
                        print(f"{datas}\n")
                        cursor.execute(
                            f"select * from paipu where player1 = '{players[0]}' and startTime = '{usetime['daytime']} {startTime}'")
                        record = cursor.fetchall()
                        if len(record) > 0:
                            print("该记录已存在")
                            break
                        print(f"检测到{p}新的对局信息")
                        # msg = "检测到新的对局信息:\n"
                        msg = ""
                        msg += f"{model}\n"
                        msg += f"{usetime['daytime']} {startTime} , 对局时长: {duration}\n"
                        order = get_matchorder(playerlist=players, playername=p)
                        if len(players) == 4:
                            msg += f"{bordercast_temple[4][order]}\n\n".replace('%player%', p)
                        else:
                            msg += f"{bordercast_temple[3][order]}\n\n".replace('%player%', p)
                        for item in players:
                            msg += f"{item}\n"
                        if len(players) == 3:
                            cursor.execute(
                                f'''insert into paipu(startTime,duration,model,player1,player2,player3,player4) values("{usetime['daytime']} {startTime}","{duration}","{model}","{players[0]}","{players[1]}","{players[2]}","Null")''')
                        else:
                            cursor.execute(
                                f'''insert into paipu(startTime,duration,model,player1,player2,player3,player4) values("{usetime['daytime']} {startTime}","{duration}","{model}","{players[0]}","{players[1]}","{players[2]}","{players[3]}")''')
                        cx.commit()
                        msglist.append(dict(playername=p, msg=msg))
                        break
        os.remove(f'./data/TenHouPlugin/scb{usetime["nowtime"]}.log')
        print(msglist)
    cursor.close()
    cx.close()
    return forwardmessage(msglist)


# 自动抓取天风结算 - 异步爬虫
async def asyautoget_th_match() -> list:
    jptz = pytz.timezone('Asia/Tokyo')
    zhtz = pytz.timezone('Asia/Shanghai')
    minute = datetime.datetime.now(tz=zhtz).strftime("%M")
    zhnowtime = datetime.datetime.now(tz=zhtz).strftime("%Y%m%d%H")
    jpnowtime = datetime.datetime.now(tz=jptz).strftime("%Y%m%d%H")
    zhdaytime = datetime.datetime.now(tz=zhtz).strftime("%Y-%m-%d")
    jpdaytime = datetime.datetime.now(tz=jptz).strftime("%Y-%m-%d")

    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()
    if int(minute) <= 10:
        timelist = [dict(nowtime=zhnowtime, daytime=zhdaytime)]
    else:
        timelist = [dict(nowtime=zhnowtime, daytime=zhdaytime), dict(nowtime=jpnowtime, daytime=jpdaytime)]

    msglist = []
    for usetime in timelist:
        # response = requests.get(f'https://tenhou.net/sc/raw/dat/scb{usetime["nowtime"]}.log.gz',
        #                         headers={'User-Agent': random.choice(user_agent_list)}, allow_redirects=True)
        # open(f'./data/TenHouPlugin/scb{usetime["nowtime"]}.log.gz', 'wb').write(response.content)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=timeout,
                                         headers={'User-Agent': random.choice(user_agent_list)}) as session:
            async with session.get(url=f'https://tenhou.net/sc/raw/dat/scb{usetime["nowtime"]}.log.gz',
                                   allow_redirects=True) as response:
                filedata = await response.read()
        open(f'./data/TenHouPlugin/scb{usetime["nowtime"]}.log.gz', 'wb').write(filedata)
        un_gz(f'./data/TenHouPlugin/scb{usetime["nowtime"]}.log.gz')
        os.remove(f'./data/TenHouPlugin/scb{usetime["nowtime"]}.log.gz')
        cursor.execute("select playername from watchedplayer")
        result = cursor.fetchall()
        playername = []
        for player in result:
            playername.append(player[0])
        with open(f'./data/TenHouPlugin/scb{usetime["nowtime"]}.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                datas = line.split('|')
                startTime = datas[0].replace('－ ', '')
                duration = datas[1].strip()
                model = datas[2].replace('－', '').strip()
                players = datas[3].strip()
                plname = re.sub(r"[(\d+\.\-)]", "", players)
                plname = plname.split(' ')
                players = players.split(' ')
                for p in plname:
                    if p in playername:
                        print(f"{datas}\n")
                        cursor.execute(
                            f"select * from paipu where player1 = '{players[0]}' and startTime = '{usetime['daytime']} {startTime}'")
                        record = cursor.fetchall()
                        if len(record) > 0:
                            print("该记录已存在")
                            break
                        print(f"检测到{p}新的对局信息")
                        # msg = "检测到新的对局信息:\n"
                        msg = ""
                        msg += f"{model}\n"
                        msg += f"{usetime['daytime']} {startTime} , 对局时长: {duration}\n"
                        order = get_matchorder(playerlist=players, playername=p)
                        if len(players) == 4:
                            msg += f"{bordercast_temple[4][order]}\n\n".replace('%player%', p)
                        else:
                            msg += f"{bordercast_temple[3][order]}\n\n".replace('%player%', p)
                        for item in players:
                            msg += f"{item}\n"
                        if len(players) == 3:
                            cursor.execute(
                                f'''insert into paipu(startTime,duration,model,player1,player2,player3,player4) values("{usetime['daytime']} {startTime}","{duration}","{model}","{players[0]}","{players[1]}","{players[2]}","Null")''')
                        else:
                            cursor.execute(
                                f'''insert into paipu(startTime,duration,model,player1,player2,player3,player4) values("{usetime['daytime']} {startTime}","{duration}","{model}","{players[0]}","{players[1]}","{players[2]}","{players[3]}")''')
                        cx.commit()
                        msglist.append(dict(playername=p, msg=msg))
                        break
        os.remove(f'./data/TenHouPlugin/scb{usetime["nowtime"]}.log')
        print(msglist)
    cursor.close()
    cx.close()
    return forwardmessage(msglist)


# 自动抓取天风对局 - 普通爬虫
def autoget_th_matching() -> list:
    gamingplayer = get_gaming_thplayers()
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()
    cursor.execute("select playername from watchedplayer")
    result = cursor.fetchall()
    watchedplayers = set()
    for player in result:
        watchedplayers.add(player[0])

    response = requests.get('https://mjv.jp/0/wg/0.js', headers={'User-Agent': random.choice(user_agent_list)},
                            allow_redirects=True)
    text = response.text

    text = text[6:-4]
    text = text.replace('\r\n', '').replace('",', '";').replace('"', '').split(';')
    nowmatches = []
    for infos in text:
        info = infos.split(',')
        duijuurl = info[0]
        type = info[1]
        time = info[2]
        numberX = info[3]
        players = []
        for i in range(4, len(info), 3):
            dstr = base64.b64decode(info[i]).decode('utf-8')
            info[i] = dstr
            player = dict(playername=info[i], playerlevel=info[i + 1], playerrank=info[i + 2])
            players.append(player)
        duiju = dict(url=duijuurl, type=type, time=time, numberX=numberX, players=players)
        nowmatches.append(duiju)

    eligible_Matches = []
    for match in nowmatches:
        matchplayer = get_thmatch_player(match)
        player_t = ishaving_player_in_list(player_list=matchplayer, target_list=watchedplayers)
        if player_t:
            for gameplayer in gamingplayer:
                if player_t == gameplayer['playername'] and gameplayer['url'] == match['url']:
                    # tempmatch = dict(playername=player_t, match=match)
                    # tempmatch = dict(playername=player_t, msg=matching2string(tempmatch))
                    # eligible_Matches.append(tempmatch)
                    gameplayer['isgaming'] = 1
                    break
            else:
                gamingplayer.append(dict(playername=player_t, url=match['url'], isgaming=2))
                tempmatch = dict(playername=player_t, match=match)
                tempmatch = dict(playername=player_t, msg=matching2string(tempmatch))
                eligible_Matches.append(tempmatch)
    print(eligible_Matches)
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()
    print(gamingplayer)
    for item in gamingplayer:
        if item['isgaming'] == 2:
            cursor.execute(f'''insert into isgaming(playername,url) values ("{item['playername']}","{item['url']}")''')
        elif item['isgaming'] == 0:
            cursor.execute(
                f'''delete from isgaming where playername = '{item["playername"]}' and url = "{item['url']}" ''')
    cx.commit()
    cursor.close()
    cx.close()
    msglist = forwardmessage(eligible_Matches)
    return msglist


# 自动抓取天风对局 - 异步爬虫
async def asyautoget_th_matching() -> list:
    gamingplayer = get_gaming_thplayers()
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()
    cursor.execute("select playername from watchedplayer")
    result = cursor.fetchall()
    watchedplayers = set()
    for player in result:
        watchedplayers.add(player[0])

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=timeout,
                                     headers={'User-Agent': random.choice(user_agent_list)}) as session:
        async with session.get(url='https://mjv.jp/0/wg/0.js', allow_redirects=True) as response:
            text = await response.text()

    text = text[6:-4]
    text = text.replace('\r\n', '').replace('",', '";').replace('"', '').split(';')
    nowmatches = []
    for infos in text:
        info = infos.split(',')
        duijuurl = info[0]
        type = info[1]
        time = info[2]
        numberX = info[3]
        players = []
        for i in range(4, len(info), 3):
            dstr = base64.b64decode(info[i]).decode('utf-8')
            info[i] = dstr
            player = dict(playername=info[i], playerlevel=info[i + 1], playerrank=info[i + 2])
            players.append(player)
        duiju = dict(url=duijuurl, type=type, time=time, numberX=numberX, players=players)
        nowmatches.append(duiju)

    eligible_Matches = []
    for match in nowmatches:
        matchplayer = get_thmatch_player(match)
        player_t = ishaving_player_in_list(player_list=matchplayer, target_list=watchedplayers)
        if player_t:
            for gameplayer in gamingplayer:
                if player_t == gameplayer['playername'] and gameplayer['url'] == match['url']:
                    # tempmatch = dict(playername=player_t, match=match)
                    # tempmatch = dict(playername=player_t, msg=matching2string(tempmatch))
                    # eligible_Matches.append(tempmatch)
                    gameplayer['isgaming'] = 1
                    break
            else:
                gamingplayer.append(dict(playername=player_t, url=match['url'], isgaming=2))
                tempmatch = dict(playername=player_t, match=match)
                tempmatch = dict(playername=player_t, msg=matching2string(tempmatch))
                eligible_Matches.append(tempmatch)
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()
    print(gamingplayer)
    for item in gamingplayer:
        if item['isgaming'] == 2:
            cursor.execute(f'''insert into isgaming(playername,url) values ("{item['playername']}","{item['url']}")''')
        elif item['isgaming'] == 0:
            cursor.execute(
                f'''delete from isgaming where playername = '{item["playername"]}' and url = "{item['url']}" ''')
    cx.commit()
    cursor.close()
    cx.close()
    msglist = forwardmessage(eligible_Matches)
    return msglist


def asygetTH():
    tasks = [
        asyncio.ensure_future(asyautoget_th_match()),
        asyncio.ensure_future(asyautoget_th_matching())
    ]
    loop = asyncio.get_event_loop()
    tasks = asyncio.gather(*tasks)
    loop.run_until_complete(tasks)
    content = []
    for results in tasks.result():
        content.extend(results)
    return content


# 转发消息，封装为 向 groupid 群聊 发送 msg 的格式
#  {playername,msg} -> {groupids,msg,playername}
def forwardmessage(msglist: list) -> list:
    messageChainList = []
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()
    for item in msglist:
        groupids = []
        cursor.execute(f'''select groupid from group2player where playername = "{item['playername']}"''')
        for g in cursor.fetchall():
            groupids.append(g[0])
        messageChainList.append(dict(groups=groupids, msg=item['msg'], playername=item['playername']))
    cursor.close()
    cx.close()
    return messageChainList


# 添加关注
def addthwatch(playername: str, groupid: int):
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()

    cursor.execute(f'select * from watchedplayer where playername = "{playername}"')
    if len(cursor.fetchall()) > 0:
        print("该用户已添加进关注列表")
    else:
        cursor.execute(f'insert into watchedplayer(playername) values("{playername}")')
        cx.commit()
        print(f"已将{playername}添加到数据库")

    cursor.execute(f'select * from QQgroup where groupid = {groupid}')
    if len(cursor.fetchall()) > 0:
        print("该群已注册进列表")
    else:
        cursor.execute(f'insert into QQgroup(groupid) values({groupid})')
        cx.commit()
        print(f"已将群组{groupid}添加到数据库")

    cursor.execute(f'select * from group2player where groupid = {groupid} and playername = "{playername}"')
    if len(cursor.fetchall()) > 0:
        print("该用户已添加进此群的关注列表")
        return "该用户已添加进此群的关注列表,无需重复添加"
    else:
        cursor.execute(f'insert into group2player(playername,groupid) values("{playername}",{groupid})')
        cx.commit()
        print(f"已将{playername}添加到群聊{groupid}的关注")

    cursor.close()
    cx.close()
    return "添加成功"


def removethwatch(playername: str, groupid: int):
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()

    cursor.execute(f'select * from watchedplayer where playername = "{playername}"')
    if len(cursor.fetchall()) == 0:
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


def getthwatch(groupid: int) -> str:
    msg = "本群关注的天凤玩家有:\n"
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()

    cursor.execute(f'select playername from group2player where groupid = {groupid}')
    result = cursor.fetchall()
    for player in result:
        msg += player[0] + " "
    cursor.close()
    cx.close()
    return msg


def get_matchorder(playerlist: list, playername: str) -> int:
    # def get_score(e):
    #     return e['score']
    #
    # playerwithscore = []
    # for p in playerlist:
    #     player, score = p.replace(')', '').split('(')
    #     playerwithscore.append(dict(playername=playername, score=int(score)))
    #
    # playerwithscore.sort(key=get_score, reverse=True)

    for i in range(4):
        # if playername == playerwithscore[i]['playername']:
        if playername == playerlist[i].split('(')[0]:
            return i + 1

    return 0


def get_thmatch_player(match: dict) -> list:
    players = list()
    for player in match['players']:
        players.append(player['playername'])
    return players


def ishaving_player_in_list(player_list: list, target_list: set):
    for player in player_list:
        for target in target_list:
            if player == target:
                return player
    return None


def matching2string(eligiblematch: dict) -> str:
    playername = eligiblematch['playername']
    match = eligiblematch['match']
    # msg = f"{playername}正在{match['type']}乱杀，快来围观:\n"
    msg = f"{playername}正在天凤乱杀，快来围观:\n"
    msg += f"https://tenhou.net/3/?wg={match['url']}\n"
    # msg += f"https://tenhou.net/3/?wg={match['url']} , 开始时间: {match['time']}\n"
    for player in get_thmatch_player(match):
        msg += f'{player}  '
    return msg


def get_gaming_thplayers() -> list:
    gamingplayer = []
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')

    cursor = cx.cursor()
    cursor.execute(f"select * from isgaming")
    for item in cursor.fetchall():
        gamingplayer.append(dict(playername=item[0], url=item[1], isgaming=0))
    cursor.close()
    cx.commit()
    return gamingplayer
