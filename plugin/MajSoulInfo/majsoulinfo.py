"""
:Author:  NekoRabi
:Update Time:  2022/8/28 3:14
:Describe: 牌谱屋链接更新
:Version: 0.6.5
"""

import asyncio
import datetime
import json
import logging
import math
import os.path
import random
import time

import aiohttp
import yaml
from PIL import Image
from mirai import MessageChain

from plugin.MajSoulInfo.folder_init import *
from utils.MessageChainBuilder import messagechain_builder
from utils.cfg_loader import read_file
from utils.text_to_img import text_to_image

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

aiotimeout = aiohttp.ClientTimeout(total=25)

serverErrorHTML = '<html><body><h1>503 Service Unavailable</h1>'
serverErrorCode = 503  # 牌谱屋炸了


# aiohttp.TCPConnector(ssl=False, limit=10) = aiohttp.TCPConnector(ssl=False, limit=10)

def get_qhpturl(playername, searchtype=3):
    if int(searchtype) == 3:
        url = f"https://2.data.amae-koromo.com/api/v2/pl3/search_player/{playername}?limit=20&tag=all"
    else:
        url = f"https://2.data.amae-koromo.com/api/v2/pl4/search_player/{playername}?limit=20&tag=all"
    return url


def get_player_records_url(playerid, searchtype, end_time, start_time=None):
    if not start_time:
        start_time = 1262304000000
    if int(searchtype) == 4:
        url = f"https://2.data.amae-koromo.com/api/v2/pl4/player_records/{playerid}/{end_time}/{start_time}?limit=599&mode=8,9,11,12,15,16&descending=true"
    else:
        url = f"https://2.data.amae-koromo.com/api/v2/pl3/player_records/{playerid}/{end_time}/{start_time}?limit=599&mode=21,22,23,24,25,26&descending=true"
    return url


def get_paipuurl(playerid, searchtype, count):
    nowtime = time.time()
    nowtime = math.floor(nowtime / 10) * 10000 + 9999
    if int(searchtype) == 4:
        url = f"https://2.data.amae-koromo.com/api/v2/pl4/player_records/{playerid}/{nowtime}/1262304000000?limit={count}&mode=8,9,11,12,15,16&descending=true"
    else:
        url = f"https://2.data.amae-koromo.com/api/v2/pl3/player_records/{playerid}/{nowtime}/1262304000000?limit={count}&mode=21,22,23,24,25,26&descending=true"
    return url


def get_player_extended_stats_url(playerid, searchtype, end_time=None, start_time=None):
    if not (start_time or end_time):
        nowtime = time.time()
        nowtime = math.floor(nowtime / 10) * 10000 + 9999
        start_time = 1262304000000
        end_time = nowtime
    if int(searchtype) == 4:
        url = f'https://2.data.amae-koromo.com/api/v2/pl4/player_extended_stats/{playerid}/{start_time}/{end_time}?mode=8.9.11.12.15.16'
    else:
        url = f'https://2.data.amae-koromo.com/api/v2/pl3/player_extended_stats/{playerid}/{start_time}/{end_time}?mode=21.22.23.24.25.26'
    return url


_template = read_file(r"./config/MajSoulInfo/template.yml")
_config = read_file(r"./config/MajSoulInfo/config.yml")


class MajsoulQuery:

    def __init__(self):
        self.template = _template
        self.config = _config

    async def getplayerdetail(self, playername: str, selecttype: str, selectlevel: list = None,
                              model='基本') -> MessageChain:
        """
        获取玩家详情
        @param playername: 玩家名
        @param selecttype: 查询类别
        @param selectlevel: 查询场况
        @param model: 查询模式
        @return:
        """
        if model not in ['基本', '更多', '立直', '血统', 'all']:
            return messagechain_builder(text="参数输入有误哦，可用的参数为'基本'、'更多'、'立直'、'血统'、'all'")
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')

        cursor = cx.cursor()
        cursor.execute(
            f"select playerid from qhplayer where playername = '{playername}'")
        playerid = cursor.fetchall()
        cursor.close()
        cx.close()
        if len(playerid) == 0:
            print("数据库中无此用户，请先查询该用户。")
            return messagechain_builder(text="查询失败,数据库中无此用户,请先用 qhpt 查询该用户。")
        playerid = playerid[0][0]
        rule = "三麻"
        try:
            url = get_player_extended_stats_url(playerid, selecttype)
            # nowtime = time.time()
            # nowtime = math.floor(nowtime / 10) * 10000 + 9999
            if selecttype == "4":
                rule = "四麻"
            #     url = f"https://ak-data-5.sapk.ch/api/v2/pl4/player_extended_stats/{playerid}/1262304000000/{nowtime}?mode=16.12.9.15.11.8"
            # else:
            #     url = f"https://ak-data-1.sapk.ch/api/v2/pl3/player_extended_stats/{playerid}/1262304000000/{nowtime}?mode=21.22.23.24.25.26"
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=10), timeout=aiotimeout,
                                             headers={'User-Agent': random.choice(user_agent_list)}) as session:
                async with session.get(url) as response:
                    if response.status == 503:
                        print('牌谱屋似乎离线了')
                        return messagechain_builder(text="牌谱屋似乎离线了~")
                    content = await response.json()
        except asyncio.exceptions.TimeoutError as e:
            print(f"查询超时:\t{e}\n")
            return messagechain_builder(text="查询超时,请稍后再试")

        except aiohttp.client.ClientConnectorError as _e:
            print(f"发生了意外的错误,类别为aiohttp.client.ClientConnectorError,可能的原因是连接达到上限,可以尝试关闭代理:\n{_e}")
            return messagechain_builder(text="查询超时,请稍后再试")
        msg = f" 以下是玩家 {playername} 的{rule}数据:\n"
        for (k, v) in content.items():
            if type(v) not in [list, dict]:
                if str(k) in ["id", "count"]:
                    continue
                if model in ['基本', '更多', '血统', '立直']:
                    if str(k) in infomodel.get(model):
                        if type(v) == float:
                            if str(k).endswith('率'):
                                msg += f"{k:<12} : {v * 100:2.2f}%\n"
                            else:
                                msg += f"{k:<12} : {v:2.2f}\n"
                        else:
                            msg += f"{k:<12} : {v if v else 0}\n"
                elif model == 'all':
                    if type(v) == float:
                        if str(k).endswith('率'):
                            msg += f"{k:<12} : {v * 100:2.2f}%\n"
                        else:
                            msg += f"{k:<12} : {v:2.2f}\n"
                    else:
                        msg += f"{k:<12} : {v if v else 0}\n"
        if _config.get('broadcast', 'image') in ['txt', 'text', 'str']:
            return messagechain_builder(text=msg)
        else:
            return messagechain_builder(imgbase64=text_to_image(text=msg, needtobase64=True))

    async def getsomeqhpaipu(self, playername: str, type="4", counts=5) -> MessageChain:
        ptupdate = 0
        ERROR = False

        async def asyrecordsrequest(_playerid, _type, _counts) -> list:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=10), timeout=aiotimeout,
                                             headers={'User-Agent': random.choice(user_agent_list)}) as session:
                # nowtime = time.time()
                # nowtime = math.floor(nowtime / 10) * 10000 + 9999
                # if type == "4":
                #     async with session.get(
                #             f"https://ak-data-5.sapk.ch/api/v2/pl4/player_records/{playerid}/{nowtime}/1262304000000?limit={counts}&mode=8,9,11,12,15,16&descending=true") as response:
                #         text = await response.json()
                # else:
                #     async with session.get(
                #             f"https://ak-data-1.sapk.ch/api/v2/pl3/player_records/{playerid}/{nowtime}/1262304000000?limit={counts}&mode=21,22,23,24,25,26&descending=true") as response:
                #         text = await response.json()
                async with session.get(get_paipuurl(_playerid, _type, _counts)) as response:
                    text = await response.json()
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
            return messagechain_builder(text="查询失败,数据库中无此用户,请先用 qhpt 查询该用户。")
        playerid = playerid[0][0]
        paipuInfo = f"最近{counts}场对局信息如下："
        # content = finish_all_asytasks(
        #     [asyrecordsrequest(playerid=playerid, type=type, counts=counts)])[0]
        try:
            content = await asyrecordsrequest(playerid, type, counts)
            for item in content:
                # paipuurl = f'https://game.maj-soul.net/1/?paipu={item["uuid"]}'
                paipuuid = f'{item["uuid"]}'
                startTime = time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.localtime(item["startTime"]))
                endTime = time.strftime('%Y-%m-%d %H:%M:%S',
                                        time.localtime(item["endTime"]))
                players = item['players']
                if _config.get('broadcast', 'image') in ['txt', 'text', 'str']:
                    paipuInfo += f"\n牌谱连接: https://game.maj-soul.net/1/?paipu={paipuuid}\n"
                else:
                    paipuInfo += f"\n牌谱UID: {paipuuid}\n"
                paipuInfo += f"开始时间: {startTime}\n结束时间: {endTime}\n对局玩家:\n"
                for player in players:
                    if player['nickname'].strip() == playername.strip():
                        ptupdate += int(player['gradingScore'])
                    paipuInfo += f"{player['nickname']} : {player['score']} ({player['gradingScore']})\n"
                paipuInfo += "\n"
            paipuInfo += f"\n总PT变化 : {ptupdate}"
        except asyncio.TimeoutError as e:
            print(e)
            ERROR = True
            paipuInfo = '牌谱查询超时,请稍后再试'
        result = messagechain_builder(text=paipuInfo)
        if not ERROR:

            if _config.get('broadcast', 'image') in ['txt', 'text', 'str']:
                return messagechain_builder(text=paipuInfo)
            else:
                # text_to_image(path=f"MajsoulInfo/qhpt{username}.png", text=prtmsg)
                return messagechain_builder(imgbase64=text_to_image(text=paipuInfo, needtobase64=True))
            # result['img64'] = text_to_image(text=paipuInfo, needtobase64=True)
        return result

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
                f"insert into drawcards(userid,drawcount,lastdraw) values({userid},{self.config.get('dailydrawcount', 3)},'{today}')")
            cx.commit()
            cursor.execute(
                f"select lastdraw,drawcount from drawcards where userid = {userid}")
            user = cursor.fetchall()
        lastdraw = user[0][0]
        drawcount = user[0][1]

        if not (lastdraw == today):
            cursor.execute(
                f"update drawcards set drawcount = {self.config.get('dailydrawcount', 3)} , lastdraw = '{today}' where userid = {userid}")
            cx.commit()
            drawcount = self.config.get('dailydrawcount', 3)
        if drawcount > 0:
            drawcount = drawcount - 1
            cursor.execute(
                f"update drawcards set drawcount = {drawcount}  where userid = {userid}")
            cx.commit()
        else:
            return dict(resultsmsg=f" 你没有抽数惹，每人每天最多抽{self.config.get('dailydrawcount', 3)}次", error=True)
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

        drawtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        random.seed()
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
                cursor.execute(
                    f'''insert into playerdrawcard(userid,drawtime,itemlevel,itemname) values({userid},'{drawtime}',{gfrare},'{gf}')''')
                break
            if luck < 5:
                if up:
                    if random.random() * 100 < 59:
                        person_name = random.choice(up_person)
                        ps = person_name + '\n'
                        drawcounts['person'] += 1
                        cursor.execute(
                            f'''insert into playerdrawcard(userid,drawtime,itemlevel,itemname) values({userid},'{drawtime}',4,'{ps}')''')
                        results.append(f'./Images/person/{person_name}.png')
                        resultsmsg += ps
                        continue
                person_index = random.randint(0, person['length'] - 1)
                ps = person['item'][person_index]['name']
                drawcounts['person'] += 1
                # psrare = person['item'][person_index]['rare']
                results.append(person['item'][person_index]['url'])
                resultsmsg += ps
                cursor.execute(
                    f'''insert into playerdrawcard(userid,drawtime,itemlevel,itemname) values({userid},'{drawtime}',4,'{ps}')''')
            elif luck < 15:
                if up:
                    if random.random() * 100 < 49:
                        decoration_name = random.choice(up_decoration)
                        dec = decoration_name + '\n'
                        drawcounts['decoration'] += 1
                        cursor.execute(
                            f'''insert into playerdrawcard(userid,drawtime,itemlevel,itemname) values({userid},'{drawtime}',3,'{dec}')''')
                        results.append(
                            f'./Images/decoration/{decoration_name}.jpg')
                        resultsmsg += dec
                        continue
                dec_index = random.randint(0, decoration['length'] - 1)
                dec = decoration['item'][dec_index]['name']
                cursor.execute(
                    f'''insert into playerdrawcard(userid,drawtime,itemlevel,itemname) values({userid},'{drawtime}',3,'{dec}')''')
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
                cursor.execute(
                    f'''insert into playerdrawcard(userid,drawtime,itemlevel,itemname) values({userid},'{drawtime}',{gfrare},'{gf}')''')
                resultsmsg += gf
            if not count == 9:
                resultsmsg += '\n'
        cx.commit()
        cursor.close()
        cx.close()
        return dict(drawcounts=drawcounts, results=results, resultsmsg=resultsmsg, baodi=baodi, error=False)

    def getmycard(self, userid):
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
        cursor = cx.cursor()
        cursor.execute(
            f"select itemlevel,count(itemlevel) from playerdrawcard where userid = {userid} group by itemlevel order by itemlevel")
        result = cursor.fetchall()
        msg = "你总共抽到了这些:\n"
        if len(result) > 0:
            for row in result:
                if row[0] == 0:
                    msg += f"{row[1]}个绿礼物,"
                elif row[0] == 1:
                    msg += f"{row[1]}个蓝礼物,"
                elif row[0] == 2:
                    msg += f"{row[1]}个紫礼物,"
                elif row[0] == 3:
                    msg += f"{row[1]}个饰品,"
                elif row[0] == 4:
                    msg += f"{row[1]}个人物,"
        else:
            msg = "你还没有抽过卡哦~"
        cursor.close()
        cx.close()
        return msg

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

    async def getmonthreport(self, playername: str, selecttype: str = None, year: str = None,
                             month: str = None) -> MessageChain:
        def getrank(playerinfo: dict):
            return playerinfo['score']

        ptchange = 0
        msg = ""
        getrecent=False
        if not selecttype:
            selecttype = "4"
        if not year or not month:
            year, month = time.strftime("%Y-%m", time.localtime()).split('-')
            paipumsg = f"{playername} 最近一个月 的对局报告\n"
            getrecent = True
        else:
            paipumsg = f"{playername} {year}-{month} 的对局报告\n"
        selectmonth = f"{year}-{month}"
        rankdict = {"1": 0, "2": 0, "3": 0, "4": 0, "fly": 0}
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
            return messagechain_builder(text="查询失败,数据库中无此用户,请先用 qhpt 查询该用户。")
        playerid = playerid[0][0]
        selectmontht = int(time.mktime(time.strptime(selectmonth, '%Y-%m')) * 1000)
        if getrecent:
            nextmontht = int(time.time()*1000)
            selectmontht = nextmontht - 2592000 * 1000
        else:
            nextmontht = int(time.mktime(time.strptime(nextmonth, '%Y-%m')) * 1000)

        try:
            # if selecttype == "4":
            #     url = f"https://ak-data-5.sapk.ch/api/v2/pl4/player_records/{playerid}/{nextmontht}/{selectmontht}?limit=599&mode=8,9,11,12,15,16&descending=true"
            # else:
            #     url = f"https://ak-data-1.sapk.ch/api/v2/pl3/player_records/{playerid}/{nextmontht}/{selectmontht}?limit=599&mode=21,22,23,24,25,26&descending=true"
            url = get_player_records_url(playerid, selecttype, nextmontht, selectmontht)
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=10), timeout=aiotimeout,
                                             headers={'User-Agent': random.choice(user_agent_list)}) as session:
                async with session.get(url) as response:
                    if response.status == 503:
                        return messagechain_builder(text='牌谱屋似乎离线了')
                    paipuresponse = await response.json()

            if len(paipuresponse) == 0:
                return messagechain_builder(text='该玩家这个月似乎没有进行过该类型的对局呢')
            paipumsg += f"总对局数: {len(paipuresponse)}\n其中"
            for players in paipuresponse:
                temp = players['players']
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
                paipumsg += f"{rankdict['1']}次①位,{rankdict['2']}次②位,{rankdict['3']}次③位,{rankdict['4']}次④位"
            else:
                paipumsg += f"{rankdict['1']}次①位,{rankdict['2']}次②位,{rankdict['3']}次③位"
            if rankdict['fly'] > 0:
                paipumsg += f",被飞了{rankdict['fly']}次"
            paipumsg += f",平均顺位:{averagerank:1.2f}\nPT总得失: {ptchange}\n\n"
            msg += paipumsg
        except asyncio.exceptions.TimeoutError as e:
            print(f'\n牌谱读取超时:\t{e}\n')
            return messagechain_builder(text="查询超时,请稍后再试")

        except aiohttp.client.ClientConnectorError as _e:
            print(f"发生了意外的错误,类别为aiohttp.client.ClientConnectorError,可能的原因是连接达到上限,可以尝试关闭代理:\n{_e}")
            return messagechain_builder(text="查询超时,请稍后再试")
        try:
            # if selecttype == "4":
            #     url = f"https://ak-data-5.sapk.ch/api/v2/pl4/player_extended_stats/{playerid}/{selectmontht}/{nextmontht}?mode=16.12.9.15.11.8"
            # else:
            #     url = f"https://ak-data-1.sapk.ch/api/v2/pl3/player_extended_stats/{playerid}/{selectmontht}/{nextmontht}?mode=21.22.23.24.25.26"
            url = get_player_extended_stats_url(playerid, selecttype, end_time=nextmontht, start_time=selectmontht)
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=10), timeout=aiotimeout,
                                             headers={'User-Agent': random.choice(user_agent_list)}) as session:
                async with session.get(url) as response:
                    if response.status == 503:
                        return messagechain_builder(text='牌谱屋似乎离线了')
                    inforesponse: dict = await response.json()
            infomsg = f" 立直率: {inforesponse.get('立直率', None) * 100 if inforesponse.get('立直率', None) else 0:2.2f}%\t"
            infomsg += f" 副露率: {inforesponse.get('副露率', None) * 100 if inforesponse.get('副露率', None) else 0:2.2f}%\t"
            infomsg += f" 和牌率: {inforesponse.get('和牌率', None) * 100 if inforesponse.get('和牌率', None) else 0:2.2f}%\n"
            infomsg += f" 放铳率: {inforesponse.get('放铳率', None) * 100 if inforesponse.get('放铳率', None) else 0:2.2f}% "
            if inforesponse.get('默听率', None):
                infomsg += f"\t 默听率: {inforesponse.get('默听率', 0) * 100 :2.2f}%\n"
            else:
                infomsg += '\t'
            infomsg += f" 平均打点: {inforesponse.get('平均打点') if inforesponse.get('平均打点') else 0}\t 平均铳点 : {inforesponse.get('平均铳点') if inforesponse.get('平均铳点') else 0}"
            msg += infomsg
        except asyncio.exceptions.TimeoutError as e:
            print(f'\n玩家详情读取超时:\t{e}\n')
            return messagechain_builder(text="查询超时,请稍后再试")
        except aiohttp.client.ClientConnectorError as _e:
            print(f"发生了意外的错误,类别为aiohttp.client.ClientConnectorError,可能的原因是连接达到上限,可以尝试关闭代理:\n{_e}")
            return messagechain_builder(text="查询超时,请稍后再试")
        if _config.get('broadcast', 'image') in ['text', 'txt', 'str']:
            return messagechain_builder(text=msg)
        return messagechain_builder(imgbase64=text_to_image(text=msg, needtobase64=True))

    def removewatch(self, playername: str, groupid: int) -> str:
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
        cursor = cx.cursor()
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
        # watcherplayers = cursor.fetchall()
        if groupplayers[0][3] != 0:
            cursor.execute(
                f"update group2player set iswatching = 0 where playerid = {playerid} and groupid = {groupid}")
            cursor.execute(
                f"update watchedplayer set watchedgroupcount = watchedgroupcount - 1 where playerid = {playerid}")
            print("删除成功")
            cx.commit()
            cursor.close()
            cx.close()
            self.tagoffplayer(playername=playername, groupid=groupid)
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

    def clearallwatch(self, groupid: int):
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
        cursor = cx.cursor()
        print(f'开始执行清除群聊{groupid}的雀魂关注')
        cursor.execute(
            f"update watchedplayer set watchedgroupcount = watchedgroupcount -1 where watchedgroupcount > 0 and playername in (select playername from group2player where groupid = {groupid} and iswatching = 1)")
        cursor.execute(f'update group2player set iswatching = 0 where groupid = {groupid}')
        cx.commit()
        cursor.close()
        cx.close()
        self.tagoffplayer(groupid=groupid)
        return "清除成功"

    async def asygetqhpaipu(self):
        nowtime = time.time()
        nowtime = math.floor(nowtime / 10) * 10000 + 9999
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
        cursor = cx.cursor()
        cursor.execute(f"select playerid from watchedplayer where watchedgroupcount > 0")
        res = cursor.fetchall()
        cursor.close()
        cx.close()
        playeridlist = []
        for item in res:
            playeridlist.append(item[0])
        results = await paipu_pl3(playeridlist, nowtime) + await paipu_pl4(playeridlist, nowtime)
        return msganalysis(results)

    async def query(self, username: str, selecttype: str = "", selectindex: int = 1) -> MessageChain:
        userinfo = await asyqhpt(username)
        if userinfo['error']:
            if userinfo['offline']:
                return messagechain_builder(text='牌谱屋似乎离线了')
                # return dict(msg="牌谱屋服务器离线", error=True)
            return messagechain_builder(text='查询超时,请稍后再试')
            # return dict(msg="查询超时,请稍后再试", error=True)
        prtmsg = username
        playerid = userinfo.get('playerid', None)
        if not playerid:
            return messagechain_builder(text='该玩家不存在或未进行金之间及以上对局')
            # return dict(msg="该用户不存在", error=True)
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
                print("查到多位同名玩家，将输出第一个，请确认是否是匹配的用户,精确匹配请增加参数")
                prtmsg += f"\n\n查到多位同名玩家，将输出第一个\n请确认是否是匹配的用户,精确匹配请增加参数\n"
            user_p3_levelinfo: dict = userinfo.get('pl3')
            user_p3_levelinfo = user_p3_levelinfo.get("level")
            p3_level = user_p3_levelinfo.get("id")
            p3_score = int(user_p3_levelinfo.get("score")) + int(user_p3_levelinfo.get("delta"))
            prtmsg += levelswitch(p3_level, p3_score, "三麻")

        except AttributeError:
            print("查询不到三麻段位")
            prtmsg += "\n未查询到三麻段位。"
        """四麻"""
        try:
            if userinfo['muti4']:
                print("查到多位同名玩家，将输出第一个，请确认是否是匹配的用户,精确匹配请增加参数")
                prtmsg += f"\n\n查到多位同名玩家，将输出第一个\n请确认是否是匹配的用户,精确匹配请增加参数\n"
            user_p4_levelinfo = userinfo['pl4']
            user_p4_levelinfo = user_p4_levelinfo.get("level")
            p4_level = user_p4_levelinfo.get("id")
            p4_score = int(user_p4_levelinfo.get("score")) + int(user_p4_levelinfo.get("delta"))
            prtmsg += levelswitch(p4_level, p4_score, "四麻")
        except AttributeError:
            print("查询不到四麻段位")
            prtmsg += "\n未查询到四麻段位。"
        if _config.get('broadcast', 'image') in ['txt', 'text', 'str']:
            return messagechain_builder(text=prtmsg)
        else:
            # text_to_image(path=f"MajsoulInfo/qhpt{username}.png", text=prtmsg)
            return messagechain_builder(imgbase64=text_to_image(text=prtmsg, needtobase64=True))
        # return dict(msg=prtmsg, error=False)

    async def getcertaininfo(self, username: str, selecttype: str = "4", selectindex: int = 1) -> MessageChain:
        """

        Args:
            username:   玩家名
            selecttype:  查询类别  3/4 代表三麻或者四麻
            selectindex:  查询序号,于 0.6.4 改成 下标从1开始

        Returns:

        """
        if not selectindex:
            selectindex = 1
        selectindex = int(selectindex) - 1 if int(selectindex) > 0 else 0
        if selecttype == 3:
            # url = f"https://ak-data-1.sapk.ch/api/v2/pl3/search_player/{username}?limit=20"
            url = get_qhpturl(username, 3)
            typename = "三麻"
        else:
            # url = f"https://ak-data-5.sapk.ch/api/v2/pl4/search_player/{username}?limit=20"
            url = get_qhpturl(username, 4)
            typename = "四麻"
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=10), timeout=aiotimeout,
                                             headers={'User-Agent': random.choice(user_agent_list)}) as session:
                async with session.get(url) as response:
                    if response.status == 503:
                        return messagechain_builder(text="牌谱屋似乎离线了")
                    playerinfo = await response.json()
        except asyncio.exceptions.TimeoutError as e:
            print(f"查询超时\t {e}")
            return messagechain_builder(text="查询超时,请稍后再试")

        except aiohttp.client.ClientConnectorError as _e:
            print(f"发生了意外的错误,类别为aiohttp.client.ClientConnectorError,可能的原因是连接达到上限,可以尝试关闭代理:\n{_e}")
            return messagechain_builder(text="查询超时,请稍后再试")
        if len(playerinfo) == 0:
            return messagechain_builder(text="不存在该玩家")
        elif len(playerinfo) < selectindex:
            return messagechain_builder(text=f"序号有误，共查询到{len(playerinfo)}名玩家,序号最大值为{len(playerinfo)}")
        elif selectindex < 0:
            return messagechain_builder(text=f"序号有误，序号大于0")
        else:
            playerinfo = playerinfo[selectindex]
        if playerinfo:
            playerid = playerinfo['id']
            playername = playerinfo['nickname']
            prtmsg = f"玩家名: {playername}"
            levelinfo = playerinfo.get("level")
            level = levelinfo.get("id")
            if level > 20000 and selecttype == 4:
                prtmsg = f"未查询到四麻玩家,查询到三麻玩家\n玩家名: {playername}"
            elif level < 20000 and selecttype == 3:
                prtmsg = f"未查询到三麻玩家,查询到四麻玩家\n玩家名: {playername}"
            score = int(levelinfo.get("score")) + int(levelinfo.get("delta"))
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
            if _config.get('broadcast', 'image') in ['txt', 'text', 'str']:
                return messagechain_builder(text=prtmsg)
            else:
                # text_to_image(path=f"MajsoulInfo/qhpt{username}.png", text=prtmsg)
                return messagechain_builder(imgbase64=text_to_image(text=prtmsg, needtobase64=True))

    def tagonplayer(self, playername, tagname, userid, groupid):
        opertaionMsg = '添加成功'
        if len(tagname) > 10:
            return 'Tag太长啦，短一点短一点'
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
        cursor = cx.cursor()
        cursor.execute(
            f"select id from group2player where groupid = {groupid} and playername = '{playername}' and iswatching = 1")
        gpid = cursor.fetchall()
        if len(gpid) > 0:
            gpid = gpid[0][0]
            cursor.execute(
                f"select * from tagnames where gpid = {gpid} and tagname = '{tagname}'")
            gptag = cursor.fetchall()
            if len(gptag) > 0:
                # cursor.execute(f"update tagnames set tagname = '{tagname}' and userid = {userid} where gpid = {gpid} ")
                pass
            else:
                cursor.execute(f"insert into tagnames(tagname,userid,gpid) values('{tagname}',{userid},{gpid})")
                cx.commit()
                opertaionMsg = f"操作成功,{userid} 已为玩家 {playername} 添加tag: {tagname}"
        else:
            opertaionMsg = "添加失败，请先在本群内对该玩家添加关注"
        cursor.close()
        cx.close()
        return opertaionMsg

    def tagoffplayer(self, groupid, playername=None, userid=None, tagname=None):
        deletemsg = '删除成功'
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
        cursor = cx.cursor()
        if playername:
            cursor.execute(
                f"select id from group2player where groupid = {groupid} and playername = '{playername}'")
            gpid = cursor.fetchall()
            if len(gpid) > 0:
                gpid = gpid[0][0]
                if tagname:
                    deletemsg = f"操作成功,已成功删除玩家 {playername} 的tag: {tagname}"
                    cursor.execute(f"delete from tagnames where tagname = '{tagname}' and gpid = {gpid} ")
                else:
                    cursor.execute(
                        f"delete from tagnames where gpid = {gpid} ")
                    deletemsg = f"操作成功,已成功删除玩家 {playername} 的所有tag"
            # return "删除失败，本群未关注该玩家"  # 其实应该有有一个else，用来处理没有本群关注人的情况
        else:
            cursor.execute(
                f"delete from tagnames where gpid in (select id from group2player where groupid = {groupid} ) ")
            deletemsg = f"操作成功,已成功删除群 {groupid} 的所有tag"
        cx.commit()
        cursor.close()
        cx.close()
        return deletemsg

    def tag_C_operation(self, groupid, source_playername, target_playername, operation_type: str = 'COPY'):
        opertaionMsg = '操作成功!'
        operation_type = operation_type.lower()
        if operation_type in ['cut', 'copy']:
            cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
            cursor = cx.cursor()
            source_id = cursor.execute(
                f"select id from group2player where groupid = {groupid} and playername = '{source_playername}'").fetchall()
            target_id = cursor.execute(
                f"select id from group2player where groupid = {groupid} and playername = '{target_playername}'").fetchall()
            if len(source_id) == 0 or len(target_id) == 0:
                opertaionMsg = "操作失败，请先在本群内对该玩家添加关注"
            else:
                target_id = target_id[0][0]
                source_id = source_id[0][0]
                cursor.execute(
                    f"insert into tagnames(tagname,userid,gpid) select tagname,userid,{target_id} from tagnames where gpid = {source_id}")
                if operation_type == 'cut':
                    cursor.execute(
                        f"delete from tagnames where gpid = {source_id} ")
                cx.commit()
            cursor.close()
            cx.close()
        return opertaionMsg

    def getalltags(self, groupid, target=None, searchtype='playername'):
        querytable = f'''{'玩家名':^10}|{'tag':^10}\n'''
        cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
        cursor = cx.cursor()
        sql = f'select playername,tagname from tagnameview where groupid = {groupid}'
        if target:
            sql += f' and {searchtype} = "{target}"'
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) > 0:
            for row in result:
                querytable += f'''{row[0]:^10} {row[1]}\n'''
        else:
            querytable = '本群没有为任何玩家添加tag'
        cursor.close()
        cx.close()
        return querytable


# 异步的qhpt

async def asyqhpt(username: str, selecttype: str = None, selectindex: int = None) -> dict:
    muti3 = False
    muti4 = False
    if not selectindex:
        selectindex = 0
    urlp3 = get_qhpturl(username, 3)
    urlp4 = get_qhpturl(username, 4)
    if selecttype:
        return dict()
        # if selecttype == "3":
        #     url = urlp3
        #     typename = "三麻"
        # else:
        #     url = urlp4
        #     typename = "四麻"
        # try:
        #     async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=10), timeout=aiotimeout,
        #                                      headers={'User-Agent': random.choice(user_agent_list)}) as session:
        #         async with session.get(url) as response:
        #             if response.status == 503:
        #                 return dict(error=True, offline=True)
        #             playerinfo = await response.json()
        # except asyncio.exceptions.TimeoutError as e:
        #     print(f"qhpt查询超时,{e}")
        #     return dict(error=True, muti3=muti3, muti4=muti4, offline=False)
        # except aiohttp.client.ClientConnectorError as _e:
        #     print(f"发生了意外的错误,类别为aiohttp.client.ClientConnectorError,可能的原因是连接达到上限,可以尝试关闭代理:\n{_e}")
        #     return dict(error=True, muti3=muti3, muti4=muti4, offline=False)
        # if len(playerinfo) == 0:
        #     print("不存在该玩家")
        #     return dict(error=True, muti3=muti3, muti4=muti4, offline=False)
        # elif len(playerinfo) < selectindex:
        #     print(f"序号有误，共查询到{len(playerinfo)}名玩家,序号最大值为{len(playerinfo) - 1}")
        #     return dict(error=True, muti3=muti3, muti4=muti4, offline=False)
        # else:
        #     playerinfo = playerinfo[selectindex]
        #     if type(playerinfo) == dict:
        #         playerid = playerinfo['id']
        #         playername = playerinfo['nickname']
        #         prtmsg = f"玩家名: {playername}"
        #         levelinfo = playerinfo.get("level")
        #         level = levelinfo.get("id")
        #         score = int(levelinfo.get("score")) + int(levelinfo.get("delta"))
        #         prtmsg += levelswitch(level, score, typename)
        #         cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
        #         cursor = cx.cursor()
        #         cursor.execute(
        #             f"select * from qhplayer where playername = '{username}'")
        #         if len(cursor.fetchall()) == 0:
        #             cursor.execute(
        #                 "insert into qhplayer(playerid,playername) values(?,?)", (playerid, username))
        #         else:
        #             cursor.execute(
        #                 f"update qhplayer set playerid = {playerid} where playername = '{username}'")
        #         cx.commit()
        #         cx.close()
        #         return prtmsg

    else:
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=10), timeout=aiotimeout,
                                             headers={'User-Agent': random.choice(user_agent_list)}) as session:
                async with session.get(urlp3) as response:
                    if response.status == 503:
                        return dict(error=True, offline=True)
                    pl3 = await response.json()
                async with session.get(urlp4) as response:
                    if response.status == 503:
                        return dict(error=True, offline=True)
                    pl4 = await response.json()

        except asyncio.exceptions.TimeoutError as e:
            print(f"qhpt查询超时,{e}")
            return dict(error=True, muti3=muti3, muti4=muti4, offline=False)
        except aiohttp.client.ClientConnectorError as _e:
            print(f"发生了意外的错误,类别为aiohttp.client.ClientConnectorError,可能的原因是连接达到上限,可以尝试关闭代理:\n{_e}")
            return dict(error=True, muti3=muti3, muti4=muti4, offline=False)
        pl3info = None
        pl4info = None
        if len(pl3) > 0:
            if len(pl3) > 1:
                muti3 = True
            for _pl in pl3:
                if _pl.get('level').get('id') > 20000:
                    pl3info = _pl
                    break
            # else:
            #     pl3info = None
        if len(pl4) > 0:
            if len(pl4) > 1:
                muti4 = True
            pl4info = None
            for _pl in pl4:
                if _pl.get('level').get('id') < 20000:
                    pl4info = _pl
                    break
            # else:
            #     pl4 = None
        playerid = None
        playername = None
        if pl3info:
            # if pl3info['nickname'] == username:
            playerid = pl3info['id']
            playername = pl3info['nickname']
        elif pl4info:
            # if pl4info['nickname'] == username :
            playerid = pl4info['id']
            playername = pl4info['nickname']
        else:
            muti3 = False
            muti4 = False
        return dict(pl3=pl3info, pl4=pl4info, playerid=playerid, playername=playername, error=False, muti3=muti3,
                    muti4=muti4,
                    offline=False)


async def paipu_pl3(playeridlist, nowtime) -> list:
    contentlist = []
    if len(playeridlist) >= 25:
        timeout = aiohttp.ClientTimeout(total=15)
    else:
        timeout = asytimeout
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=10), timeout=timeout,
                                     headers={'User-Agent': random.choice(user_agent_list)}) as session:
        for playerid in playeridlist:
            try:
                #  url =f"https://ak-data-1.sapk.ch/api/v2/pl3/player_records/{playerid}/{nowtime}/1262304000000?limit=1&mode=21,22,23,24,25,26&descending=true"
                url = get_player_records_url(playerid, 3, nowtime)
                async with session.get(url) as response:

                    text: list = json.loads(await response.text())
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
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=10), timeout=timeout,
                                     headers={'User-Agent': random.choice(user_agent_list)}) as session:
        for playerid in playeridlist:
            try:
                # url = f"https://ak-data-5.sapk.ch/api/v2/pl4/player_records/{playerid}/{nowtime}/1262304000000?limit=1&mode=8,9,11,12,15,16&descending=true"
                url = get_player_records_url(playerid, 4, nowtime)
                async with session.get(url) as response:
                    text: list = json.loads(await response.text())
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
    # cmdopt = []
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
        # paipuurl = f'https://game.maj-soul.net/1/?paipu={msgitem["uuid"]}'
        paipuurl = f'{msgitem["uuid"]}'
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
            paipuInfo += f"{paipuurl}\n"
            paipuInfo += f"{startTime} ~ {endTime}\n对局玩家:\n"
            for player in players:
                paipuInfo += f"{player['nickname']}:{player['score']} ({player['gradingScore']})\n"
            content.append(dict(playerid=item['playerid'], msg=paipuInfo))
        except sqlite3.IntegrityError:
            # print(f"存在uuid={item['uuid']}的记录")
            pass
    return forwardmessage(content)



majsoul = MajsoulQuery()
