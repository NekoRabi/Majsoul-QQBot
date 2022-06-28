import asyncio
import datetime
import math
import os.path
import time
import logging

import aiohttp
import requests
import sqlite3
import random
import json
import yaml
from requests.adapters import HTTPAdapter
from PIL import Image
from utils.text_to_img import text_to_image
from utils.asyrequestpackge import finish_all_asytasks
from utils.cfg_loader import loadcfg_from_file

asytimeout = aiohttp.ClientTimeout(total=60)

levellist = [[1200, 1400, 2000], [2800, 3200, 3600], [4000, 6000, 9000]]

game_map = {
    4: {
        "金东": 8,
        "金": 9,
        "玉东": 11,
        "玉": 12,
        "王座东": 15,
        "王座": 16
    },
    3: {
        "金东": 21,
        "金": 22,
        "玉东": 23,
        "玉": 24,
        "王座东": 25,
        "王座": 26
    }
}

infomodel = dict(基本=['和牌率', '放铳率', '自摸率', '默听率', '流局率', '流听率', '副露率', '立直率', '和了巡数', '平均打点', '平均铳点', '平均顺位', '被飞率'],
                 立直=['立直率', '立直和了', '立直放铳A', '立直放铳B', '立直收支', '立直收入', '立直支出', '先制率', '追立率', '被追率', '立直巡目', '立直流局',
                     '一发率', '振听率', '立直多面', '立直好型'],
                 更多=['最大连庄', '里宝率', '被炸率', '平均被炸点数', '放铳时立直率', '放铳时副露率', '副露后放铳率', '副露后流局率', '副露后和牌率', '打点效率', '铳点损失',
                     '净打点效率'],
                 血统=['役满', '累计役满', '两立直', '流满', '最大累计番数', '平均起手向听'])

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

aiotimeout = aiohttp.ClientTimeout(total=10)

serverErrorHTML = '<html><body><h1>503 Service Unavailable</h1>'
serverErrorCode = 503  # 牌谱屋炸了


class majsoul:

    def __init__(self):
        self.template = loadcfg_from_file(r"./config/MajSoulInfo/config.yml")

    # qhpt
    def getcertaininfo(self, username: str, selecttype: str = "4", selectindex: int = None):
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=3))
        s.mount('https://', HTTPAdapter(max_retries=3))
        if not selectindex:
            selectindex = 0
        try:
            if selecttype == "3":
                url = f"https://ak-data-1.sapk.ch/api/v2/pl3/search_player/{username}?limit=20"
                typename = "三麻"
            else:
                url = f"https://ak-data-5.sapk.ch/api/v2/pl4/search_player/{username}?limit=20"
                typename = "四麻"
            xhr = s.get(url=url,
                        headers={'User-Agent': random.choice(user_agent_list), "Connection": "close"}, timeout=10)
            # searchresult = finish_all_asytasks([asysearchqh(url)])[0]
            # if searchresult['error']:
            #     return searchresult['msg']
            if xhr.status_code == 503:
                return "牌谱屋似乎离线了"
                # return dict(error=True, offline=True)
            playerinfo = eval(xhr.text)
            if len(playerinfo) == 0:
                return "不存在该玩家"
            elif len(playerinfo) < selectindex:
                return f"序号有误，共查询到{len(playerinfo)}名玩家,序号最大值为{len(playerinfo) - 1}"
            else:
                playerinfo = playerinfo[selectindex]
                if type(playerinfo) == dict:
                    playerid = playerinfo['id']
                    playername = playerinfo['nickname']
                    prtmsg = f"玩家名: {playername}"
                    levelinfo = playerinfo.get("level")
                    level = levelinfo.get("id")
                    score = int(levelinfo.get("score")) + \
                            int(levelinfo.get("delta"))
                    prtmsg += levelswitch(level, score, typename)
                    cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
                    cursor = cx.cursor()
                    cursor.execute(
                        f"select * from qhplayer where playername = '{username}'")
                    if len(cursor.fetchall()) == 0:
                        cursor.execute(
                            "insert into qhplayer(playerid,playername) values(?,?)", (playerid, username))
                    else:
                        cursor.execute(
                            f"update qhplayer set playerid = {playerid} where playername = '{username}'")
                    cx.commit()
                    cx.close()
                    return prtmsg
        except requests.exceptions.ConnectionError as e:
            print(f"查询玩家信息时连接超时\t {e}")
            return "查询玩家信息时连接超时"
        except requests.exceptions.ReadTimeout as e:
            print(f"读取超时\t {e}")
            return "读取超时"

    def getplayerdetail(self, playername: str, selecttype: str, selectlevel: list = None, model='基本') -> dict:
        if model not in ['基本', '更多', '立直', '血统', 'all']:
            return dict(msg="参数输入有误哦，可用的参数为'基本'、'更多'、'立直'、'血统'、'all'", error=True)
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')

        cursor = cx.cursor()
        cursor.execute(
            f"select playerid from qhplayer where playername = '{playername}'")
        playerid = cursor.fetchall()
        cursor.close()
        s = requests.Session()
        if len(playerid) == 0:
            print("数据库中无此用户，请先查询该用户。")
            return dict(msg="查询失败,数据库中无此用户,请先用 qhpt 查询该用户。", error=True)
        playerid = playerid[0][0]
        s.mount('http://', HTTPAdapter(max_retries=3))
        s.mount('https://', HTTPAdapter(max_retries=3))
        headers = {
            'User-Agent': random.choice(user_agent_list), "Connection": "close"}
        nowtime = time.time()
        nowtime = math.floor(nowtime / 10) * 10000 + 9999
        rule = "三麻"
        try:
            if selecttype == "4":
                rule = "四麻"
                url = f"https://ak-data-5.sapk.ch/api/v2/pl4/player_extended_stats/{playerid}/1262304000000/{nowtime}?mode=16.12.9.15.11.8 "
            else:
                url = f"https://ak-data-1.sapk.ch/api/v2/pl3/player_extended_stats/{playerid}/1262304000000/{nowtime}?mode=21.22.23.24.25.26"
            xhr = s.get(url,
                        timeout=5,
                        headers=headers)
        except requests.exceptions.ConnectionError as e:
            print(f"查询发生了错误:\t{e}\n")
            return dict(msg="查询时发生错误,请稍后再试。\tConnectionError", eror=True)
        except requests.exceptions.ReadTimeout as e:
            print(f'读取超时:\t{e}\n')
            return dict(msg="读取超时，请稍后再试。\tReadTimeOut", error=True)
        text = xhr.text.replace("null", "0.0")
        content: dict = eval(text)
        msg = f" 以下是玩家 {playername} 的{rule}数据:\n"
        for (k, v) in content.items():
            if type(v) not in [list, dict]:
                if str(k) in ["id", "count"]:
                    continue
                if model in ['基本', '更多', '血统', '立直']:
                    if str(k) in infomodel.get(model):
                        if type(v) == float:
                            if str(k) not in ['平均起手向听', '立直巡目', '和了巡数']:
                                msg += f"{k:<12} : {v * 100:2.2f}%\n"
                            else:
                                msg += f"{k:<12} : {v:2.2f}\n"
                        else:
                            msg += f"{k} : {v}\n"
                elif model == 'all':
                    if type(v) == float:
                        if str(k) not in ['平均起手向听', '立直巡目', '和了巡数']:
                            msg += f"{k:<12} : {v * 100:2.2f}%\n"
                        else:
                            msg += f"{k:<12} : {v:2.2f}\n"
                    else:
                        msg += f"{k} : {v}\n"
        text_to_image(path=f"MajsoulInfo/detail{playername}.png", text=msg)
        return dict(msg=msg, error=False)

    def getsomeqhpaipu(self, playername: str, type="4", counts=5):
        nowtime = time.time()
        ptupdate = 0
        nowtime = math.floor(nowtime / 10) * 10000 + 9999

        async def asyrecordsrequest(playerid, type, counts) -> list:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=5), timeout=aiotimeout,
                                             headers={'User-Agent': random.choice(user_agent_list)}) as session:

                if type == "4":
                    async with session.get(
                            f"https://ak-data-5.sapk.ch/api/v2/pl4/player_records/{playerid}/{nowtime}/1262304000000?limit={counts}&mode=8,9,11,12,15,16&descending=true") as response:
                        text = await response.text()
                else:
                    async with session.get(
                            f"https://ak-data-1.sapk.ch/api/v2/pl3/player_records/{playerid}/{nowtime}/1262304000000?limit={counts}&mode=21,22,23,24,25,26&descending=true") as response:
                        text = await response.text()
            text = eval(text.replace("false", "False"))
            return text

        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
        cursor = cx.cursor()
        cursor.execute(
            f"select playerid from qhplayer where playername = '{playername}'")
        playerid = cursor.fetchall()
        cursor.close()
        cx.close()
        if len(playerid) == 0:
            print("数据库中无此用户，请先查询该用户。")
            return "查询失败,数据库中无此用户,请先用 qhpt 查询该用户。"
        playerid = playerid[0][0]
        paipuInfo = f"最近{counts}场对局信息如下："
        content = finish_all_asytasks(
            [asyrecordsrequest(playerid=playerid, type=type, counts=counts)])[0]
        for item in content:
            paipuurl = f'https://game.maj-soul.net/1/?paipu={item["uuid"]}'
            startTime = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(item["startTime"]))
            endTime = time.strftime('%Y-%m-%d %H:%M:%S',
                                    time.localtime(item["endTime"]))
            players = item['players']
            paipuInfo += f"\n牌谱链接 : {paipuurl}\n"
            paipuInfo += f"开始时间: {startTime}\n结束时间: {endTime}\n对局玩家:\n"
            for player in players:
                if player['nickname'].strip() == playername.strip():
                    ptupdate += int(player['gradingScore'])
                paipuInfo += f"{player['nickname']} : {player['score']} ({player['gradingScore']})\n"
            paipuInfo += "\n"
        paipuInfo += f"\n总PT变化 : {ptupdate}"
        return paipuInfo
        # s = requests.Session()
        # s.mount('http://', HTTPAdapter(max_retries=3))
        # s.mount('https://', HTTPAdapter(max_retries=3))

    #    headers = {'User-Agent': random.choice(user_agent_list), "Connection": "close"}
    # try:
    #     if type == '3':
    #         url = f"https://ak-data-1.sapk.ch/api/v2/pl3/player_records/{playerid}/{nowtime}/1262304000000?limit={counts}&mode=21,22,23,24,25,26&descending=true"
    #     else:
    #         url = f"https://ak-data-5.sapk.ch/api/v2/pl4/player_records/{playerid}/{nowtime}/1262304000000?limit={counts}&mode=8,9,11,12,15,16&descending=true"
    #     xhr = s.get(url=url, headers=headers, timeout=3)
    #     content = eval(xhr.text)
    #     if len(content) == 0:
    #         return "未查询到对局信息"
    #     for item in content:
    #         paipuurl = f'https://game.maj-soul.net/1/?paipu={item["uuid"]}'
    #         startTime = time.strftime(
    #             '%Y-%m-%d %H:%M:%S', time.localtime(item["startTime"]))
    #         endTime = time.strftime('%Y-%m-%d %H:%M:%S',
    #                                 time.localtime(item["endTime"]))
    #         players = item['players']
    #         paipuInfo += f"\n牌谱链接 : {paipuurl}\n"
    #         paipuInfo += f"开始时间: {startTime}\n结束时间: {endTime}\n对局玩家:\n"
    #         for player in players:
    #             if player['nickname'].strip() == playername.strip():
    #                 ptupdate += int(player['gradingScore'])
    #             paipuInfo += f"{player['nickname']} : {player['score']} ({player['gradingScore']})\n"
    #         paipuInfo += "\n"
    #     paipuInfo += f"\n总PT变化 : {ptupdate}"
    #     return paipuInfo
    # except requests.exceptions.ConnectionError as e:
    #     print(f"查询发生了错误:\t{e}\n")
    #     return "连接失败，请稍后重试 ConnectionError"
    # except requests.exceptions.ReadTimeout as e:
    #     print(f'读取超时:\t{e}\n')
    #     return "读取超时，请稍后重试 ReadTimeOut"

    def getpaipu(self, playerid: str) -> dict:
        nowtime = time.time()
        nowtime = math.floor(nowtime / 10) * 10000 + 9999
        headers = {
            'User-Agent': random.choice(user_agent_list), "Connection": "close"}
        content = dict(p4=[], p3=[])
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=3))
        s.mount('https://', HTTPAdapter(max_retries=3))
        '''四麻查询'''
        # async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=5), timeout=asytimeout,
        #                                  headers={'User-Agent': random.choice(user_agent_list)}) as session:
        #     async with session.get(
        #             f"https://ak-data-5.sapk.ch/api/v2/pl4/player_records/{playerid}/{nowtime}/1262304000000"
        #         "?limit=1&mode=8,9,11,12,15,16&descending=true") as response:
        #         content['p4'] = eval(await response.text())
        try:
            xhr4 = s.get(
                f"https://ak-data-5.sapk.ch/api/v2/pl4/player_records/{playerid}/{nowtime}/1262304000000"
                "?limit=1&mode=8,9,11,12,15,16&descending=true", headers=headers, timeout=3)
            content['p4'] = eval(xhr4.text)
            # print(f'四麻对局信息:{eval(xhr.text)}')
        except requests.exceptions.ConnectionError as e:
            print(f"\n四麻查询发生了错误:\t{e}\n")
            content['e4'] = True
        except requests.exceptions.ReadTimeout as e:
            print(f'\n读取超时:\t{e}\n')
            content['e4'] = True

        '''三麻查询'''
        try:
            xhr3 = s.get(
                f"https://ak-data-1.sapk.ch/api/v2/pl3/player_records/{playerid}/{nowtime}/1262304000000"
                "?limit=1&mode=21,22,23,24,25,26&descending=true", headers=headers, timeout=3)
            content['p3'] = eval(xhr3.text)
            # print(f'三麻对局信息:{eval(xhr.text)}')
        except requests.exceptions.ConnectionError as e:
            print(f"\n三麻查询发生了错误:\t{e}\n")
            content['e3'] = True
        except requests.exceptions.ReadTimeout as e:
            print(f'\n读取超时:\t{e}\n')
            content['e3'] = True
        return content

    def drawcards(self, userid: int, up=False) -> dict:
        if not os.path.exists('./images/MajsoulInfo'):
            os.mkdir('./images/MajsoulInfo')

        today = datetime.datetime.now().strftime("%Y-%m-%d")
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
        cursor = cx.cursor()
        cursor.execute(
            f"select lastdraw,drawcount from drawcards where userid = {userid}")
        user = cursor.fetchall()
        if len(user) == 0:
            cursor.execute(
                f"insert into drawcards(userid,drawcount,lastdraw) values({userid},{3},'{today}')")
            cx.commit()
            cursor.execute(
                f"select lastdraw,drawcount from drawcards where userid = {userid}")
            user = cursor.fetchall()
        lastdraw = user[0][0]
        drawcount = user[0][1]

        if not (lastdraw == today):
            cursor.execute(
                f"update drawcards set drawcount = {3} , lastdraw = '{today}' where userid = {userid}")
            cx.commit()
            drawcount = 3
        if drawcount > 0:
            drawcount = drawcount - 1
            cursor.execute(
                f"update drawcards set drawcount = {drawcount}  where userid = {userid}")
            cx.commit()
        else:
            return dict(resultsmsg=" 你没有抽数惹，每人每天最多抽3次", error=True)
        baodi = False
        drawcounts = {'0gift': 0, '1gift': 0,
                      '2gift': 0, 'person': 0, 'decoration': 0}
        results = []
        resultsmsg = "\n您的抽卡结果依次为:\n"
        with open(r'./config/MajSoulInfo/drawcards.yml', 'r', encoding='utf-8') as f:

            config = yaml.safe_load(f)
            lottery = config['lottery']
            up_person = config['up']['person']
            up_decoration = config['up']['decoration']
            decoration = lottery['decoration']
            gift = lottery['gift']
            person = lottery['person']
            for count in range(10):
                luck = random.random() * 100
                if count == 9 and drawcounts['2gift'] == 0:
                    print("出保底喽")
                    gift_index = random.randint(0, 5) * 3 + 2
                    gf = gift['item'][gift_index]['name']
                    gfrare = gift['item'][gift_index]['rare']
                    drawcounts[str(gfrare) + 'gift'] += 1
                    results.append(gift['item'][gift_index]['url'])
                    resultsmsg += gf
                    resultsmsg += '\n\n已触发保底。'
                    break
                if luck < 5:
                    if up:
                        if random.random() * 100 < 59:
                            person_name = random.choice(up_person)
                            ps = person_name + '\n'
                            drawcounts['person'] += 1
                            results.append(f'./Images/person/{person_name}.png')
                            resultsmsg += ps
                            continue

                    person_index = random.randint(0, person['length'] - 1)
                    ps = person['item'][person_index]['name']
                    drawcounts['person'] += 1
                    results.append(person['item'][person_index]['url'])
                    resultsmsg += ps
                elif luck < 15:
                    if up:
                        if random.random() * 100 < 49:
                            decoration_name = random.choice(up_decoration)
                            dec = decoration_name + '\n'
                            drawcounts['decoration'] += 1
                            results.append(
                                f'./Images/decoration/{decoration_name}.jpg')
                            resultsmsg += dec
                            continue
                    dec_index = random.randint(0, decoration['length'] - 1)
                    dec = decoration['item'][dec_index]['name']
                    drawcounts['decoration'] += 1
                    results.append(decoration['item'][dec_index]['url'])
                    resultsmsg += dec
                else:
                    gift_index = random.randint(0, 7) * 3
                    gifttype = random.randint(0, 10)
                    if gifttype < 3:
                        gift_index += 2
                    # elif gifttype < 9:
                    else:
                        gift_index += 1
                    if count == 9 and drawcounts['2gift'] == 0:
                        if gift['item'][gift_index]['rare'] == 2:
                            break
                        else:
                            print("出保底喽")
                            gift_index = random.randint(0, 5) * 3 + 2
                            resultsmsg += '\n\n已触发保底。'
                    gf = gift['item'][gift_index]['name']
                    gfrare = gift['item'][gift_index]['rare']
                    drawcounts[str(gfrare) + 'gift'] += 1
                    results.append(gift['item'][gift_index]['url'])
                    resultsmsg += gf
                if not count == 9:
                    resultsmsg += '\n'
        return dict(drawcounts=drawcounts, results=results, resultsmsg=resultsmsg, baodi=baodi, error=False)

    def addwatch(self, playername: str, groupid: int):
        print(f'groupid= {groupid},playername= {playername}')
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
        cursor = cx.cursor()
        cx.commit()

        cursor.execute(
            f"select playerid from qhplayer where playername = '{playername}'")
        playerid = cursor.fetchall()
        if len(playerid) == 0:
            print("数据库中无此用户，请先查询该用户。")
            return "添加失败,数据库中无此用户,请先用 qhpt 查询该用户。"
        playerid = playerid[0][0]
        cursor.execute(f'select * from QQgroup where groupid = {groupid}')
        groups = cursor.fetchall()
        if len(groups) > 0:
            print("该群已注册进雀魂观战数据库")
        else:
            cursor.execute(f'insert into QQgroup(groupid) values({groupid})')
            cx.commit()
            print(f"已将群组{groupid}添加到数据库")
        cursor.execute(
            f'select * from watchedplayer where playerid = {playerid}')
        watchedplayers = cursor.fetchall()
        if len(watchedplayers) == 0:
            cursor.execute(
                f'insert into watchedplayer(playerid,playername) values({playerid},"{playername}")')
            cx.commit()
            print(f"已将{playername}添加到雀魂关注数据库")
        cursor.execute(
            f'select * from group2player where groupid = {groupid} and playerid = "{playerid}"')
        groupplayers = cursor.fetchall()
        if len(groupplayers) > 0:
            if groupplayers[0][3] != 1:
                cursor.execute(
                    f'update group2player set iswatching = 1 where groupid = {groupid} and playerid = {playerid}')
                cursor.execute(
                    f'update watchedplayer set watchedgroupcount = watchedgroupcount + 1 where playerid = {playerid}')
                cx.commit()
                print("已更新雀魂群关注")
            else:
                print("该用户已添加进此群的关注列表")
                cursor.close()
                cx.close()
                return "此群已关注该玩家"
        else:
            cursor.execute(
                f'insert into group2player(playerid,playername,groupid) values({playerid},"{playername}",{groupid})')
            cursor.execute(
                f'update watchedplayer set watchedgroupcount = watchedgroupcount + 1 where playerid = {playerid}')
            cx.commit()
            print(f"已将{playername}添加到群聊{groupid}的关注")
        cursor.close()
        cx.close()
        return "添加成功"

    def getmonthreport(self, playername: str, selecttype: str, year: str, month: str) -> dict:
        def getrank(playerinfo: dict):
            return playerinfo['score']

        ptchange = 0
        msg = ""
        if not selecttype:
            selecttype = "4"
        if not year or not month:
            year, month = time.strftime("%Y-%m", time.localtime()).split('-')
        rankdict = {"1": 0, "2": 0, "3": 0, "4": 0, "fly": 0}
        paipumsg = f"玩家{playername}在{year}年{month}月"
        selectmonth = f"{year}-{month}"
        playerslist = []
        if month == "12":
            nextmonth = f"{int(year) + 1}-1"
        else:
            nextmonth = f"{year}-{int(month) + 1}"
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')

        cursor = cx.cursor()
        cursor.execute(
            f"select playerid from qhplayer where playername = '{playername}'")
        playerid = cursor.fetchall()
        cursor.close()
        cx.close()
        if len(playerid) == 0:
            print("数据库中无此用户，请先查询该用户。")
            return dict(msg="查询失败,数据库中无此用户,请先用 qhpt 查询该用户。", error=True)
        playerid = playerid[0][0]
        selectmontht = int(time.mktime(time.strptime(selectmonth, '%Y-%m')) * 1000)
        nextmontht = int(time.mktime(time.strptime(nextmonth, '%Y-%m')) * 1000)
        session_paipu = requests.session()
        session_paipu.mount('http://', HTTPAdapter(max_retries=3))
        session_paipu.mount('https://', HTTPAdapter(max_retries=3))
        session_info = requests.session()
        session_info.mount('http://', HTTPAdapter(max_retries=3))
        session_info.mount('https://', HTTPAdapter(max_retries=3))
        headers = {
            'User-Agent': random.choice(user_agent_list), "Connection": "close"}
        try:
            if selecttype == "4":
                paipuresponse = session_paipu.get(
                    f"https://ak-data-5.sapk.ch/api/v2/pl4/player_records/{playerid}/{nextmontht}/{selectmontht}"
                    "?limit=599&mode=8,9,11,12,15,16&descending=true", headers=headers, timeout=3)
            else:
                paipuresponse = session_paipu.get(
                    f"https://ak-data-1.sapk.ch/api/v2/pl3/player_records/{playerid}/{nextmontht}/{selectmontht}"
                    "?limit=599&mode=21,22,23,24,25,26&descending=true", headers=headers, timeout=3)
            if paipuresponse.status_code == 503:
                return dict(msg="牌谱屋服务器似乎离线了", error=True)
            paipuresponse = eval(paipuresponse.text)
            if len(paipuresponse) == 0:
                return dict(msg='该玩家这个月似乎没有进行过该类型的对局呢', error=True)
            paipumsg += f"总共进行了{len(paipuresponse)}场对局\n共计"
            for players in paipuresponse:
                temp: list = players['players']
                temp.sort(key=getrank)
                playerslist.append(temp)
            for playerrank in playerslist:
                if selecttype == "4":
                    rank = 4
                else:
                    rank = 3
                for player in playerrank:
                    if player['nickname'] == playername:
                        ptchange += player['gradingScore']
                        rankdict[f"{rank}"] += 1
                        if player['score'] < 0:
                            rankdict['fly'] += 1
                        break
                    rank = rank - 1
            averagerank = (rankdict['1'] + rankdict['2'] * 2 +
                           rankdict['3'] * 3 + rankdict['4'] * 4) / len(paipuresponse)
            if selecttype == "4":
                paipumsg += f"{rankdict['1']}次①位,{rankdict['2']}次②位,{rankdict['3']}次③位,{rankdict['4']}次④位,平均顺位:{averagerank:1.2f}\n"
            else:
                paipumsg += f"{rankdict['1']}次①位,{rankdict['2']}次②位,{rankdict['3']}次③位,平均顺位:{averagerank:1.2f}\n"
            if rankdict['fly'] > 0:
                paipumsg += f"其中被飞了{rankdict['fly']}次,"
            paipumsg += f"PT总得失: {ptchange}\n\n"
            msg += paipumsg
        except requests.exceptions.ConnectionError as e:
            print(f"\n牌谱查询超时:\t{e}\n")
            return dict(msg="查询超时,请再试一次", error=True)
        except requests.exceptions.ReadTimeout as e:
            print(f'\n牌谱读取超时:\t{e}\n')
            return dict(msg="查询超时,请再试一次", error=True)

        try:
            if selecttype == "4":
                inforesponse = session_info.get(
                    f"https://ak-data-5.sapk.ch/api/v2/pl4/player_extended_stats/{playerid}/{selectmontht}/{nextmontht}?mode"
                    f"=16.12.9.15.11.8",
                    timeout=3,
                    headers=headers)
            else:
                inforesponse = session_info.get(
                    f"https://ak-data-1.sapk.ch/api/v2/pl3/player_extended_stats/{playerid}/{selectmontht}/{nextmontht}?mode"
                    f"=21.22.23.24.25.26",
                    timeout=3,
                    headers=headers)
            if inforesponse.status_code == 503:
                return dict(msg="牌谱屋服务器似乎离线了", error=True)
            inforesponse = eval(inforesponse.text.replace("null", "0.0"))
            infomsg = f" 立直率: {inforesponse['立直率'] * 100 :2.2f}%\t 副露率: {inforesponse['副露率'] * 100 :2.2f}%\t " \
                      f" 和牌率: {inforesponse['和牌率'] * 100 :2.2f}%\n 放铳率: {inforesponse['放铳率'] * 100 :2.2f}%\t " \
                      f" 默听率: {inforesponse['默听率'] * 100 :2.2f}%\n 平均打点: {inforesponse['平均打点']}\t 平均铳点 : {inforesponse['平均铳点']}"
            msg += infomsg
        except requests.exceptions.ConnectionError as e:
            print(f"\n玩家详情查询超时:\t{e}\n")
            return dict(msg="查询超时,请再试一次", error=True)
        except requests.exceptions.ReadTimeout as e:
            print(f'\n玩家详情读取超时:\t{e}\n')
            return dict(msg="查询超时,请再试一次", error=True)
        text_to_image(path=f"MajsoulInfo/yb{playername}.png", text=msg)
        return dict(msg=msg, error=False, )
        # return dict(msg=msg, error=False, imgbase64=text_to_image(text=msg, needtobase64=True))

    def removewatch(self, playername: str, groupid: int) -> str:
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
        cursor = cx.cursor()
        # cursor.execute(
        #     f"select * from group2player where playername = '{playername}'")
        # player = cursor.fetchall()
        # if len(player) == 0:
        #     return '本群未关注该玩家'
        # if player[0][4] == 1:
        #     cursor.execute(
        #         f"update group2player set iswatching = 0 where playername = '{playername}' and groupid = {groupid}")
        # cx.commit()
        # cursor.execute(
        #     f"select * from group2player where playername = '{playername}' and iswatching = 1")
        # groupplayers = cursor.fetchall()
        # if len(groupplayers) == 0:
        #     cursor.execute(
        #         f"update watchedplayer set watchedgroupcount = 0 where playername = '{playername}'")
        #     cx.commit()
        # cursor.close()
        # cx.close()
        # return "删除成功"

        cursor.execute(
            f"select playerid from qhplayer where playername = '{playername}'")
        playerid = cursor.fetchall()
        if len(playerid) == 0:
            print("数据库中无此用户,删除未进行")
            return "删除成功"
        playerid = playerid[0][0]
        cursor.execute(
            f'select * from group2player where groupid ={groupid} and playerid ={playerid}')
        groupplayers = cursor.fetchall()
        if len(groupplayers) == 0:
            print("未关注该用户")
            return "删除成功"
        cursor.execute(
            f'select * from watchedplayer where playerid = {playerid}')
        watcherplayers = cursor.fetchall()
        if groupplayers[0][3] != 0:
            cursor.execute(
                f"update group2player set iswatching = 0 where playerid = {playerid} and groupid = {groupid}")
            cursor.execute(
                f"update watchedplayer set watchedgroupcount = watchedgroupcount - 1 where playerid = {playerid}")
            print("删除成功")
            cx.commit()
            cursor.close()
            cx.close()
            return "删除成功"
        else:
            print("未关注该用户")
            return "删除成功"

    def getallwatcher(self, groupid: int) -> str:
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
        cursor = cx.cursor()
        cursor.execute(
            f"select watchedplayers,watchnums from groupwatches where groupid = {groupid}")
        players = cursor.fetchall()
        if len(players) == 0:
            return "本群未关注任何玩家"
        msg = f"本群共关注了{players[0][1]}位玩家:\n{players[0][0]}"
        cursor.close()
        cx.close()
        return msg

    def asygetqhpaipu(self):
        nowtime = time.time()
        nowtime = math.floor(nowtime / 10) * 10000 + 9999
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
        cursor = cx.cursor()
        cursor.execute(f"select playerid from watchedplayer where watchedgroupcount > 0")
        res = cursor.fetchall()
        cursor.close()
        cx.close()
        playeridlist = []
        content = []
        for item in res:
            playeridlist.append(item[0])
        results = finish_all_asytasks(
            [paipu_pl3(playeridlist, nowtime), paipu_pl4(playeridlist, nowtime)])
        for result in results:
            content.extend(msganalysis(result))
        return content

    def query(self, username: str, selecttype: str = "", selectindex: int = 0) -> dict:
        userinfo = getinfo(username)
        if userinfo['error']:
            if userinfo['offline']:
                return dict(msg="牌谱屋服务器离线", error=True)
            return dict(msg="查询超时", error=True)
        prtmsg = username
        playerid = userinfo['playerid']
        if playerid:
            pass
        else:
            return dict(msg="该用户不存在", error=True)
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
        cursor = cx.cursor()
        cx.commit()
        cursor.execute(
            f"select playerid from qhplayer where playername = '{username}'")
        if len(cursor.fetchall()) == 0:
            cursor.execute(
                "insert into qhplayer(playerid,playername) values(?,?)", (playerid, username))
            cx.commit()
        cursor.close()
        cx.close()
        """三麻"""
        try:
            if userinfo['muti3']:
                print("查到多位同名三麻玩家，将输出第一个，请确认是否是匹配的用户,精确匹配请增加参数")
                prtmsg += f"\n\n查到多位同名三麻玩家，将输出第一个\n请确认是否是匹配的用户,精确匹配请增加参数\n"
            user_p3_levelinfo = userinfo['pl3']
            user_p3_levelinfo = user_p3_levelinfo.get("level")
            p3_level = user_p3_levelinfo.get("id")
            p3_score = int(user_p3_levelinfo.get("score")) + \
                       int(user_p3_levelinfo.get("delta"))
            prtmsg += levelswitch(p3_level, p3_score, "三麻")

        except AttributeError:
            print("查询不到三麻段位")
            prtmsg += "\n未查询到三麻段位。"
        """四麻"""
        try:
            if userinfo['muti4']:
                print("查到多位同名四麻玩家，将输出第一个，请确认是否是匹配的用户,精确匹配请增加参数")
                prtmsg += f"\n\n查到多位同名四麻玩家，将输出第一个\n请确认是否是匹配的用户,精确匹配请增加参数\n"
            user_p4_levelinfo = userinfo['pl4']
            user_p4_levelinfo = user_p4_levelinfo.get("level")
            p4_level = user_p4_levelinfo.get("id")
            p4_score = int(user_p4_levelinfo.get("score")) + \
                       int(user_p4_levelinfo.get("delta"))
            prtmsg += levelswitch(p4_level, p4_score, "四麻")
        except AttributeError:
            print("查询不到四麻段位")
            prtmsg += "\n未查询到四麻段位。"

        text_to_image(path=f"MajsoulInfo/qhpt{username}.png", text=prtmsg)
        return dict(msg=prtmsg, error=False)

    def tagonplayer(self,playername,tagname,userid,groupid):
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
        cursor = cx.cursor()
        cursor.execute(
            f"select id from group2player where groupid = {groupid} and playername = '{playername}'")
        gpid = cursor.fetchall()
        if len(gpid) > 0:
            gpid = gpid[0][0]
            cursor.execute(
                f"select * from tagnames where gpid = {gpid}")
            gptag = cursor.fetchall()
            if len(gptag) > 0:
                cursor.execute(f"update tagnames set tagname = '{tagname}' and userid = {userid} where gpid = {gpid} ")
            else:
                cursor.execute(f"insert into tagnames(tagname,userid,gpid) values('{tagname}',{userid},{gpid})")
            cx.commit()
            cursor.close()
            cx.close()
            return f"操作成功,{userid}已为玩家{playername}添加标记{tagname}"
        else:
            cx.commit()
            cursor.close()
            cx.close()
            return "添加失败，请先对该玩家添加关注"


def getinfo(username: str, selecttype: str = "4", selectindex: int = 0) -> dict:
    muti3 = False
    muti4 = False
    headers = {
        'User-Agent': random.choice(user_agent_list), "Connection": "close"}
    s3 = requests.Session()
    s3.mount('http://', HTTPAdapter(max_retries=3))
    s3.mount('https://', HTTPAdapter(max_retries=3))
    s4 = requests.Session()
    s4.mount('https://', HTTPAdapter(max_retries=3))
    s4.mount('https://', HTTPAdapter(max_retries=3))

    try:
        xhr3 = s3.get(
            f"https://ak-data-1.sapk.ch/api/v2/pl3/search_player/{username}?limit=20",
            headers=headers, timeout=10)
        if xhr3.status_code == 503:
            return dict(error=True, offline=True)
        pl3 = json.loads(xhr3.text)

        xhr4 = s4.get(
            f"https://ak-data-5.sapk.ch/api/v2/pl4/search_player/{username}?limit=20",
            headers=headers, timeout=10)
        pl4 = json.loads(xhr4.text)
        if len(pl3) > 0:
            if len(pl4) > 1:
                muti3 = True
            pl3 = pl3[0]
        else:
            pl3 = None
        if len(pl4) > 0:
            if len(pl4) > 1:
                muti4 = True
            pl4 = pl4[0]
        else:
            pl4 = None
        if pl3:
            playerid = pl3['id']
            playername = pl3['nickname']
        elif pl4:
            playerid = pl4['id']
            playername = pl4['nickname']
        else:
            playerid = None
            playername = None
        return dict(pl3=pl3, pl4=pl4, playerid=playerid, playername=playername, error=False, muti3=muti3, muti4=muti4,
                    offline=False)
    except requests.exceptions.ConnectionError:
        print("查询玩家信息时连接超时")
        return dict(error=True, muti3=muti3, muti4=muti4, offline=False)
    except requests.exceptions.ReadTimeout:
        print("查询玩家时读取超时")
        return dict(error=True, muti3=muti3, muti4=muti4, offline=False)


async def paipu_pl3(playeridlist, nowtime):
    contentlist = []
    if len(playeridlist) >= 25:
        timeout = aiohttp.ClientTimeout(total=15)
    else:
        timeout = asytimeout
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=5), timeout=timeout,
                                     headers={'User-Agent': random.choice(user_agent_list)}) as session:
        for playerid in playeridlist:
            try:
                async with session.get(
                        f"https://ak-data-1.sapk.ch/api/v2/pl3/player_records/{playerid}/{nowtime}/1262304000000"
                        "?limit=1&mode=21,22,23,24,25,26&descending=true") as response:
                    text: list = eval(await response.text())
                    if len(text) > 0:
                        contentlist.append(
                            dict(playerid=playerid, content=text[0]))
                    else:
                        contentlist.append(
                            dict(playerid=playerid, content=text))
            except asyncio.TimeoutError as e:
                logging.getLogger().exception(e)
            except Exception as e:
                logging.getLogger().exception(e)
    return contentlist

    # 返回一个 list，内容为 [{groupid:groupid,msg:msg}]


async def paipu_pl4(playeridlist, nowtime) -> list:
    contentlist = []
    if len(playeridlist) >= 25:
        timeout = aiohttp.ClientTimeout(total=15)
    else:
        timeout = asytimeout
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=5), timeout=timeout,
                                     headers={'User-Agent': random.choice(user_agent_list)}) as session:
        for playerid in playeridlist:
            try:
                async with session.get(
                        f"https://ak-data-5.sapk.ch/api/v2/pl4/player_records/{playerid}/{nowtime}/1262304000000"
                        "?limit=1&mode=8,9,11,12,15,16&descending=true") as response:
                    text: list = eval(await response.text())
                    if len(text) > 0:
                        contentlist.append(
                            dict(playerid=playerid, content=text[0]))
                    else:
                        contentlist.append(dict(playerid=playerid, content={}))
            except asyncio.TimeoutError as e:
                logging.getLogger().exception(e)
            except Exception as e:
                logging.getLogger().exception(e)

    return contentlist


def jiexi(paipu: dict, playerid: int) -> list:
    hasNewPaipu = False
    # paipuInfo = "检测到新的对局信息:\n"
    paipuInfo = ""
    cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')

    cursor = cx.cursor()
    cx.commit()
    allpaipuinfo = []
    for item in paipu['p4']:
        paipuurl = f'https://game.maj-soul.net/1/?paipu={item["uuid"]}'
        startTime = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(item["startTime"]))
        endTime = time.strftime('%Y-%m-%d %H:%M:%S',
                                time.localtime(item["endTime"]))
        players = item['players']
        try:
            cursor.execute(
                "insert into paipu(uuid,watchid,startTime,endTime,player1,player2,player3,player4) values(?,?,?,?,?,?,?,?)",
                (item['uuid'], playerid, startTime, endTime, f"{players[0]['nickname']}:{players[0]['score']}",
                 f"{players[1]['nickname']}:{players[1]['score']}", f"{players[2]['nickname']}:{players[2]['score']}",
                 f"{players[3]['nickname']}:{players[3]['score']}"))
            cx.commit()
            paipuInfo += f"牌谱链接 : {paipuurl}\n"
            paipuInfo += f"开始时间: {startTime}\n结束时间: {endTime}\n对局玩家:\n"
            for info in players:
                paipuInfo += f"{info['nickname']}:{info['score']} ({info['gradingScore']})\n"
            hasNewPaipu = True
        except sqlite3.IntegrityError:
            # print(f"存在uuid={item['uuid']}的记录")
            pass
    for item in paipu['p3']:
        paipuurl = f'https://game.maj-soul.net/1/?paipu={item["uuid"]}'
        startTime = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(item["startTime"]))
        endTime = time.strftime('%Y-%m-%d %H:%M:%S',
                                time.localtime(item["endTime"]))
        players = item['players']

        try:
            cursor.execute(
                "insert into paipu(uuid,watchid,startTime,endTime,player1,player2,player3,player4) values(?,?,?,?,?,?,?,?)",
                (item['uuid'], playerid, startTime, endTime, f"{players[0]['nickname']}:{players[0]['score']}",
                 f"{players[1]['nickname']}:{players[1]['score']}", f"{players[2]['nickname']}:{players[2]['score']}",
                 f"Null"))
            cx.commit()
            paipuInfo += f"牌谱链接 : {paipuurl}\n"
            paipuInfo += f"开始时间: {startTime}\n结束时间: {endTime}\n对局玩家:\n"
            for info in players:
                paipuInfo += f"{info['nickname']}:{info['score']} ({info['gradingScore']})\n"
            hasNewPaipu = True
        except sqlite3.IntegrityError:
            # print(f"存在uuid={item['uuid']}的记录")
            pass
    allpaipuinfo.append(
        dict(paipuInfo=paipuInfo, hasNewPaipu=hasNewPaipu))
    cursor.close()
    cx.close()
    return allpaipuinfo


def levelswitch(level, score, type):
    stage_level = int(str(level)[2]) - 3
    score_level = int(str(level)[4]) - 1
    maxscore = 2000
    msg = "\n"
    if stage_level < 3:
        maxscore = levellist[stage_level][score_level]

    # 升段
    if score >= maxscore:
        score_level += 1
        if stage_level < 4:
            if score_level > 2:
                score_level = 0
                stage_level += 1
        if stage_level == 3:
            stage_level += 1
        if stage_level < 3:
            maxscore = levellist[stage_level][score_level]
        else:
            maxscore = 2000
        score = maxscore // 2

    # 掉段
    if score <= 0:
        score_level -= 1
        if score_level < 0:
            score_level = 2
            stage_level -= 1
        if stage_level == 3:
            stage_level -= 1
        if stage_level < 3:
            maxscore = levellist[stage_level][score_level]
        else:
            maxscore = 2000
        score = maxscore // 2

    if stage_level < 0:
        # msg += type + "段位:  雀士"
        msg += type + ":" + "  雀士"
    elif stage_level < 4:
        # msg += type + "段位: " + prtlevelmsg(stage_level, score_level) + " \t" + type + "分数: " + str(
        #     score) + "/" + str(maxscore)
        msg += type + ":" + prtlevelmsg(stage_level, score_level) + " \t [" + str(
            score) + "/" + str(maxscore) + "]"
    else:
        # msg += type + "段位: " + prtlevelmsg(stage_level, score_level) + " \t" + type + "分数: " + str(
        #     score / 100) + "/" + str(maxscore / 100)
        msg += type + ":" + prtlevelmsg(stage_level, score_level) + " \t [" + str(
            score / 100) + "/" + str(maxscore / 100) + "]"
    return msg


def prtlevelmsg(stagelevel, scorelevel):
    msg = ""
    if stagelevel == 0:
        msg += "杰"
    elif stagelevel == 1:
        msg += "豪"
    elif stagelevel == 2:
        msg += "圣"
    else:
        msg += "魂"

    msg += str(scorelevel + 1)
    if stagelevel < 0:
        msg = "雀士"
    return msg


def mergeimg(imgurls: list) -> Image:
    for url in imgurls:
        img = Image.open(f"./plugin/MajSoulInfo/Images/{url}")
    return


def forwardmessage(msglist: list) -> list:
    messageChainList = []
    cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
    cursor = cx.cursor()
    for item in msglist:
        groupids = []
        cursor.execute(
            f'''select groupid,playername from group2player where playerid = {item['playerid']} and iswatching = 1''')
        results = cursor.fetchall()
        for g in results:
            groupids.append(g[0])
        messageChainList.append(
            dict(groups=groupids, msg=item['msg'], playerid=item['playerid'], playername=results[0][1]))
    cursor.close()
    cx.close()
    return messageChainList


'''
{'_id': '8R4hmIkLAfZ', 
'modeId': 12, 
'uuid': '220331-59b46bb1-1177-4843-9f0b-6125fe9ae5ba', 
'startTime': 1648656045, 'endTime': 1648658431, 
'players': [
{'accountId': 73438605, 'nickname': 'ドルオーラ', 'level': 10401, 'score': 27200, 'gradingScore': 63}, 
{'accountId': 8560870, 'nickname': '云游水', 'level': 10401, 'score': 4600, 'gradingScore': -200}, 
{'accountId': 71424576, 'nickname': 'シュウ4', 'level': 10501, 'score': 51200, 'gradingScore': 152},
 {'accountId': 12728158, 'nickname': '兔子甲', 'level': 10401, 'score': 17000, 'gradingScore': -13}
 ]}
'''


def msganalysis(infos: list) -> list:
    def getScore(e):
        return e['score']

    content = []
    cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
    cursor = cx.cursor()
    for item in infos:
        msgitem = item['content']
        if len(msgitem) == 0:
            continue
        paipuInfo = ""
        paipuurl = f'https://game.maj-soul.net/1/?paipu={msgitem["uuid"]}'
        startTime = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(msgitem["startTime"]))
        endTime = time.strftime('%Y-%m-%d %H:%M:%S',
                                time.localtime(msgitem["endTime"]))
        players: list = msgitem['players']
        players.sort(key=getScore, reverse=True)
        try:
            if len(players) == 3:
                cursor.execute(
                    "insert into paipu(uuid,watchid,startTime,endTime,player1,player2,player3,player4) values(?,?,?,?,?,?,?,?)",
                    (msgitem['uuid'], item['playerid'], startTime, endTime,
                     f"{players[0]['nickname']}:{players[0]['score']}",
                     f"{players[1]['nickname']}:{players[1]['score']}",
                     f"{players[2]['nickname']}:{players[2]['score']}",
                     f"Null"))
            else:
                cursor.execute(
                    "insert into paipu(uuid,watchid,startTime,endTime,player1,player2,player3,player4) values(?,?,?,?,?,?,?,?)",
                    (msgitem['uuid'], item['playerid'], startTime, endTime,
                     f"{players[0]['nickname']}:{players[0]['score']}",
                     f"{players[1]['nickname']}:{players[1]['score']}",
                     f"{players[2]['nickname']}:{players[2]['score']}",
                     f"{players[3]['nickname']}:{players[3]['score']}"))
            cx.commit()
            paipuInfo += f"牌谱链接 : {paipuurl}\n"
            paipuInfo += f"开始时间: {startTime}\n结束时间: {endTime}\n对局玩家:\n"
            for player in players:
                paipuInfo += f"{player['nickname']}:{player['score']} ({player['gradingScore']})\n"
            content.append(dict(playerid=item['playerid'], msg=paipuInfo))
        except sqlite3.IntegrityError:
            # print(f"存在uuid={item['uuid']}的记录")
            pass
    return forwardmessage(content)


async def asysearchqh(url, type="3"):
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=5), timeout=aiotimeout,
                                         headers={'User-Agent': random.choice(user_agent_list)}) as session:
            async with session.get(url) as response:
                text = await response.text()
                return dict(msg=json.loads(text), error=False)
    except asyncio.exceptions.TimeoutError as e:
        print(f"查询超时,{e}")
        return dict(msg="查询超时，请再试一次", error=True)


majsoulobj = majsoul()
