"""
:Author:  NekoRabi
:Create:  2022/9/5 16:46
:Update: /
:Describe: 天凤功能插件
:Version: 0.0.1
"""
import base64
import gzip
import datetime
import os
import random
import sqlite3
from decimal import Decimal

import aiohttp
import pytz
import re
from plugin.TenHouPlugin.ptcalculation import ptcalculation, levelmap, get_tenhou_month_report
from utils import text_to_image, read_file, write_file

TIME_FORMAT = "%Y-%m-%d %H:%M "

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
        2: " %player% 悄悄拿二,韬光养晦",
        3: " %player% 忍痛吃三，太苦了"
    }
}
# 修正了牌桌类型的获取，但不常见的牌桌类型（右四）对应数字依然未知
_matchtype = {
    "41": "四特南喰赤",
    "97": "四特東喰赤速",
    "169": "四鳳南喰赤",
    "225": "四鳳東喰赤速",
    "57": "三特南喰赤",
    "185": "三鳳南喰赤",
}
timeout = aiohttp.ClientTimeout(total=30)

_cfg = read_file(r'./config/TenHouPlugin/config.yml')


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


# 精算点还原点数
def format_players(players):
    offset = [-10000, 20000, 40000, 50000] if len(players) == 4 else [5000, 40000, 60000]
    for order, player in enumerate(players):
        raw_point = int(Decimal(re.match(r'.+?\(([+\-]?\d+?\.\d+?)\)$', player).group(1)) * 1000) + offset[order]
        players[order] = re.sub(r"(.+?)(\([+\-]?\d+?\.\d+?\))$", f"\\1 {raw_point}\\2", player)
    return players


async def asyautoget_th_match() -> list:
    """使用aiohttp编写的自动抓取天风结算 - 异步爬虫"""
    jptz = pytz.timezone('Asia/Tokyo')
    now = datetime.datetime.now(tz=jptz)
    before = now - datetime.timedelta(hours=1)
    hour_before = before.strftime("%Y%m%d%H")
    hour_now = now.strftime("%Y%m%d%H")
    date_before = before.strftime("%Y-%m-%d")
    date_now = now.strftime("%Y-%m-%d")

    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()
    if now.minute <= 7:  # 本程序基于如下假设：一个半庄最快不少于2分钟，最慢不超过 (55分钟-查询间隔)，观战延迟为5分钟
        timelist = [dict(date_hour=hour_before, date=date_before)]
    else:
        timelist = [dict(date_hour=hour_before, date=date_before),
                    dict(date_hour=hour_now, date=date_now)]

    msglist = []
    for usetime in timelist:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=timeout,
                                         headers={'User-Agent': random.choice(user_agent_list)}) as session:
            async with session.get(url=f'https://tenhou.net/sc/raw/dat/scb{usetime["date_hour"]}.log.gz',
                                   allow_redirects=True) as response:
                filedata = await response.read()
        open(
            f'./data/TenHouPlugin/scb{usetime["date_hour"]}.log.gz', 'wb').write(filedata)
        un_gz(f'./data/TenHouPlugin/scb{usetime["date_hour"]}.log.gz')
        os.remove(f'./data/TenHouPlugin/scb{usetime["date_hour"]}.log.gz')
        # cursor.execute("select playername from watchedplayer where watchedgroupcount > 0")
        cursor.execute("select playername from watchedplayersview")
        result = cursor.fetchall()
        playername = []
        for player in result:
            playername.append(player[0])
        with open(f'./data/TenHouPlugin/scb{usetime["date_hour"]}.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            datas = line.split('|')
            startTime = datas[0].replace('－ ', '')
            duration = datas[1].strip()
            model = datas[2].replace('－', '').strip()
            players = datas[3].strip()
            plname = re.sub(r"\([+\-]?\d+?\.\d+?\)", "", players)
            plname = plname.split(' ')
            players = format_players(players.split(' '))
            for p in playername:
                if p in plname:
                    print(f"{datas}\n")
                    cursor.execute(
                        f"select * from paipu where player1 = '{players[0]}' and startTime = '{usetime['date']} {startTime}'")
                    record = cursor.fetchall()
                    if len(record) > 0:
                        print("该记录已存在")
                        break
                    print(f"检测到{p}新的对局信息")
                    # msg = "检测到新的对局信息:\n"
                    msg = ""
                    msg += f"{model}\n"
                    localtime = jptz.localize(datetime.datetime.strptime(f"{usetime['date']} {startTime}", TIME_FORMAT)) \
                        .astimezone().strftime(TIME_FORMAT)
                    msg += f"{localtime}，对局时长: {duration}\n"
                    order = get_matchorder(
                        playerlist=plname, playername=p)
                    if len(players) == 4:
                        msg += f"{bordercast_temple[4][order]}\n".replace(
                            '%player%', p)
                    else:
                        msg += f"{bordercast_temple[3][order]}\n".replace(
                            '%player%', p)
                    for item in players:
                        msg += f"{item}\n"
                    msg = msg[:-1]
                    if len(players) == 3:
                        cursor.execute(
                            f'''insert into paipu(startTime,duration,model,player1,player2,player3,player4) values("{usetime['date']} {startTime}","{duration}","{model}","{players[0]}","{players[1]}","{players[2]}","Null")''')
                    else:
                        cursor.execute(
                            f'''insert into paipu(startTime,duration,model,player1,player2,player3,player4) values("{usetime['date']} {startTime}","{duration}","{model}","{players[0]}","{players[1]}","{players[2]}","{players[3]}")''')
                    cx.commit()
                    msglist.append(dict(playername=p, msg=msg))
                    break
        os.remove(f'./data/TenHouPlugin/scb{usetime["date_hour"]}.log')
        # print(msglist)
    cursor.close()
    cx.close()
    return forwardmessage(msglist)


async def asyautoget_th_matching() -> list:
    """自动抓取天风对局 - 异步爬虫"""
    gamingplayer = get_gaming_thplayers()
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()
    cursor.execute("select playername from watchedplayersview")
    result = cursor.fetchall()
    watchedplayers = set()
    for player in result:
        watchedplayers.add(player[0])

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=timeout,
                                     headers={'User-Agent': random.choice(user_agent_list)}) as session:
        async with session.get(url='https://mjv.jp/0/wg/0.js', allow_redirects=True) as response:
            text = await response.text()

    text = text[6:-4]
    text = text.replace('\r', '').replace('\n', '').replace(
        '",', '";').replace('"', '').split(';')
    nowmatches = []
    for infos in text:
        info = infos.split(',')
        _duijuurl = info[0]  # 对局链接
        _type = info[3]  # 对局类型
        _time = info[2]  # 对局时间
        _numberX = info[1]
        players = []
        for i in range(4, len(info), 3):  # 将玩家名用base64进行解码
            dstr = base64.b64decode(info[i]).decode('utf-8')
            info[i] = dstr
            player = dict(
                playername=info[i], playerlevel=info[i + 1], playerrank=info[i + 2])
            players.append(player)
        _duiju = dict(url=_duijuurl, type=_type, time=_time, numberX=_numberX, players=players)
        nowmatches.append(_duiju)

    eligible_Matches = []  # 合法比赛list
    for match in nowmatches:
        matchplayer = get_thmatch_player(match)
        _target_player = ishaving_player_in_list(
            player_list=matchplayer, target_list=watchedplayers)
        if _target_player:
            for gameplayer in gamingplayer:
                if _target_player == gameplayer['playername'] and gameplayer['url'] == match['url']:
                    # tempmatch = dict(playername=_target_player, match=match)
                    # tempmatch = dict(playername=_target_player, msg=matching2string(tempmatch))
                    # eligible_Matches.append(tempmatch)
                    gameplayer['isgaming'] = 1
                    break
            else:
                gamingplayer.append(
                    dict(playername=_target_player, url=match['url'], isgaming=2))
                tempmatch = dict(playername=_target_player, match=match)
                tempmatch = dict(playername=_target_player,
                                 msg=matching2string(tempmatch), url=match['url'])
                eligible_Matches.append(tempmatch)
    # print('eligible_Matches: ', eligible_Matches)
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()
    if not _cfg.get('silence_CLI', False):
        if len(gamingplayer) > 0:
            print('正在天凤对局的玩家:', gamingplayer)
    for item in gamingplayer:
        if item['isgaming'] == 2:
            cursor.execute(
                f'''insert into isgaming(playername,url) values ("{item['playername']}","{item['url']}")''')
        elif item['isgaming'] == 0:
            cursor.execute(
                f'''delete from isgaming where playername = '{item["playername"]}' and url = "{item['url']}" ''')
    cx.commit()
    cursor.close()
    cx.close()
    msglist = forwardmessage(eligible_Matches)
    return msglist


class TenHou:

    def __init__(self):
        self.template = bordercast_temple

    @staticmethod
    async def asythquery():
        return await asyautoget_th_matching() + await asyautoget_th_match()
        # return finish_all_asytasks([asyautoget_th_matching(), asyautoget_th_match()], mergelist=True)

    # 添加关注
    @staticmethod
    def addthwatch(playername: str, groupid: int, isadmin=False):
        """
        通过玩家id查询月报

        Args:
            playername: 玩家名
            groupid: 添加关注的群组id
            isadmin: 是否为管理员

        Returns:

        """
        auth_groups = _cfg.get("authenticationgroup", [])
        if _cfg.get("admincontrol", True) or groupid in auth_groups:
            if isadmin is False:
                return "添加失败,本群该功能需要管理员"
        cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
        cursor = cx.cursor()
        cursor.execute(f'select * from QQgroup where groupid = {groupid}')
        groups = cursor.fetchall()
        newplayer = False
        if len(groups) > 0:
            print("该群已注册进天凤观战数据库")
        else:
            cursor.execute(f'insert into QQgroup(groupid) values({groupid})')
            cx.commit()
            print(f"已将群组{groupid}添加到数据库")
        cursor.execute(
            f'select * from watchedplayer where playername = "{playername}"')
        watchedplayers = cursor.fetchall()
        if len(watchedplayers) == 0:
            #     if watchedplayers[0][1] != 1:
            #         cursor.execute(
            #             f'update watchedplayer set iswatching = 1 where playername = "{playername}"')
            #         cx.commit()
            #         print("已更新天凤关注")
            #     else:
            #         print("该用户已添加进关注列表")
            # else:
            newplayer = True
            cursor.execute(
                f'insert into watchedplayer(playername) values("{playername}")')
            cx.commit()
            print(f"已将{playername}添加到天风关注数据库")
        cursor.execute(
            f'select * from group2player where groupid = {groupid} and playername = "{playername}"')
        groupplayers = cursor.fetchall()
        if len(groupplayers) > 0:
            if groupplayers[0][3] != 1:
                cursor.execute(
                    f'update group2player set iswatching = 1 where groupid = {groupid} and playername = "{playername}"')
                if newplayer:
                    cursor.execute(
                        f'update watchedplayer set watchedgroupcount = 1 where playername = "{playername}"')
                else:
                    cursor.execute(
                        f'update watchedplayer set watchedgroupcount = watchedgroupcount + 1 where playername = "{playername}"')
                cx.commit()
                print("已更新天凤群关注")
            else:
                print("该用户已添加进此群的关注列表")
                cursor.close()
                cx.close()
                return "此群已关注该玩家"
        else:
            cursor.execute(
                f'insert into group2player(playername,groupid) values("{playername}",{groupid})')
            if newplayer:
                cursor.execute(
                    f'update watchedplayer set watchedgroupcount = 1 where playername = "{playername}"')
            else:
                cursor.execute(
                    f'update watchedplayer set watchedgroupcount = watchedgroupcount + 1 where playername = "{playername}"')
            cx.commit()
            print(f"已将{playername}添加到群聊{groupid}的关注")
        cursor.close()
        cx.close()
        return "添加成功"

    @staticmethod
    def removethwatch(playername: str, groupid: int, isadmin=False):
        """
        移除关注
        Args:
            playername: 玩家名
            groupid:群id
            isadmin: 是否为管理员

        Returns:

        """

        auth_groups = _cfg.get("authenticationgroup", [])
        if _cfg.get("admincontrol", True) or groupid in auth_groups:
            if isadmin is False:
                return "删除失败,本群该功能需要管理员"
        cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
        cursor = cx.cursor()
        cursor.execute(
            f'select * from group2player where groupid ={groupid} and playername ="{playername}"')
        groupplayers = cursor.fetchall()
        if len(groupplayers) == 0:
            print("未关注该用户")
            return "删除成功"
        cursor.execute(
            f'select * from watchedplayer where playername = "{playername}"')
        if groupplayers[0][3] != 0:
            cursor.execute(
                f"update group2player set iswatching = 0 where playername = '{playername}' and groupid = {groupid}")
            cursor.execute(
                f"update watchedplayer set watchedgroupcount = watchedgroupcount - 1 where playername = '{playername}'")
            print("删除成功")
            cx.commit()
            cursor.close()
            cx.close()
            return "删除成功"
        else:
            print("未关注该用户")
            return "删除成功"

    @staticmethod
    def clearthwatch(groupid: int):
        """清除群组关注"""
        cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
        cursor = cx.cursor()
        print(f'开始执行清除群聊{groupid}的天凤关注')
        cursor.execute(
            f"update watchedplayer set watchedgroupcount = watchedgroupcount -1 where watchedgroupcount > 0 and playername in (select playername from group2player where groupid = {groupid} and iswatching = 1)")
        cursor.execute(f'update group2player set iswatching = 0 where groupid = {groupid}')
        cx.commit()
        cursor.close()
        cx.close()
        return "清除成功"

    @staticmethod
    def getthwatch(groupid: int) -> str:
        """获取某个群全部关注"""
        cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
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

    @staticmethod
    async def getthpt(playername: str, reset=True) -> dict:
        """
        thpt 相关功能

        Args:
            playername: 天凤玩家名
            reset: 是否自动重置(即180天不打)

        Returns:

        """
        result = await ptcalculation(playername, reset)
        return dict(msg=result, img64=text_to_image(text=result, needtobase64=True))

    @staticmethod
    async def getthyb(playername: str, searchtype=3, year=None, month=None) -> dict:
        """
        thyb 相关功能

        Args:
            playername: 天凤玩家名

        Returns:

        """
        result = await get_tenhou_month_report(playername, searchtype, year, month)
        return dict(msg=result, img64=text_to_image(text=result, needtobase64=True))

    @staticmethod
    def authentication_controller(groupid: int, enable: bool):
        groups: list = _cfg.get("authenticationgroup", [])
        msgchain ="操作成功"
        if enable:
            if groupid not in groups:
                groups.append(groupid)
                _cfg['authenticationgroup'] = groups
                write_file(_cfg, r"./config/MajSoulInfo/config.yml")
            else:
                msgchain = "操作失败,已设置权限"
        else:
            if groupid in groups:
                groups.remove(groupid)
                _cfg['authenticationgroup'] = groups
                write_file(_cfg, r"./config/MajSoulInfo/config.yml")
        return msgchain

    @staticmethod
    def power_control_switch(enable:bool, isadmin = False):
        """
        天凤群聊权限模式切换
        Args:
            enable: 目标模式
            isadmin: 用户权限

        Returns:

        """
        powercontrol = _cfg.get("powercontrol",True)
        if isadmin:
            if enable != powercontrol:
                _cfg['powercontrol'] = enable
                write_file(_cfg, r"./config/MajSoulInfo/config.yml")
                return "操作成功"
        else:
            return "操作失败, 该功能仅机器人管理员可用"



def get_matchorder(playerlist: list, playername: str) -> int:
    """
    从玩家list中获取指定玩家的顺位

    Args:
        playerlist: 玩家list
        playername: 目标玩家名

    Returns:

    """
    for i in range(4):
        if playername == playerlist[i]:
            return i + 1

    return 0


def get_thmatch_player(match: dict) -> list:
    players = list()
    for player in match['players']:
        players.append(player['playername'])
    return players


def ishaving_player_in_list(player_list: list, target_list: set):
    """
    是否有玩家在目标集合中

    Args:
        player_list: 可能有目标玩家的list
        target_list: 目标集合

    Returns:

    """
    for player in player_list:
        if player in target_list:
            return player
    return None


def matching2string(eligiblematch: dict) -> str:
    """
    将比赛信息转换为合法输出

    计划以后支持自定义模板

    Args:

        eligiblematch: 合法比赛

    Returns:
        比赛信息字符串

    """
    # 以下为一个eligiblematch:
    # {'playername': 'RAYMOK', 'match': {'url': '064E45DB', 'type': '1414', 'time': '15:10', 'numberX': '41',
    # 'players': [{'playername': 'miku618', 'playerlevel': '15', 'playerrank': '2016.09'}, {'playername': 'RAYMOK',
    # 'playerlevel': '14', 'playerrank': '1908.20'}, {'playername': '浦飯幽助', 'playerlevel': '14', 'playerrank':
    # '1934.99'}, {'playername': '石丸電 化', 'playerlevel': '14', 'playerrank': '1906.34'}]}}

    playername = eligiblematch['playername']
    match = eligiblematch['match']
    # msg = f"{playername}正在{_matchtype[match['type']]}乱杀，快来围观:\n"
    msg = f"{playername}正在{_matchtype.get(match['type'], '天凤')}{random.choice(['乱杀', '对局'])} 快来围观:\n"
    # print(f'eligiblematch:{eligiblematch}')
    msg += f"https://tenhou.net/3/?wg={match['url']}\n"
    # msg += f"https://tenhou.net/3/?wg={match['url']} , 开始时间: {match['time']}\n"
    players = match['players']
    for player in players:
        # print(player["playerrank"], type(player["playerrank"]))
        msg += f'{levelmap.get(int(player["playerlevel"])).get("name")}R{player["playerrank"]} {player["playername"]}\n'
    return msg[:-1]


def get_gaming_thplayers() -> list:
    """获取数据库中记录的正在对局的天凤玩家"""
    gamingplayer = []
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')

    cursor = cx.cursor()
    cursor.execute(f"select * from isgaming")
    for item in cursor.fetchall():
        gamingplayer.append(dict(playername=item[0], url=item[1], isgaming=0))
    cursor.close()
    cx.commit()
    return gamingplayer


#
#  {playername,msg} -> {groupids,msg,playername}
def forwardmessage(msglist: list) -> list:
    """
    转发消息，封装为 向 groupid 群聊 发送 msg 的格式

    Args:
        msglist: [ {playername:xxx, msg:aaa} ]

    Returns: [ {playername:xxx, msg:aaa, groups:iii} ]

    """
    messageChainList = []
    cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
    cursor = cx.cursor()
    for item in msglist:
        groupids = []
        cursor.execute(
            f'''select groupid from group2player where playername = "{item['playername']}" and iswatching = 1''')
        for g in cursor.fetchall():
            groupids.append(g[0])
        data = dict(groups=groupids, msg=item['msg'], playername=item['playername'])
        if item.get('url', None):
            data['url'] = item['url']
        messageChainList.append(data)
    cursor.close()
    cx.close()
    return messageChainList


tenhou = TenHou()
