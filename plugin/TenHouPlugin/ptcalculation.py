import json

import asyncio
import random
import time

import aiohttp

__all__ = ['ptcalculation', 'levelmap']

levelmap = {
    0: {'name': '新人', 'maxscore': 20, 'maxscore_old': 30, 'haslower': False, 'losescore': 0},
    1: {'name': '9级', 'maxscore': 20, 'maxscore_old': 30, 'haslower': False, 'losescore': 0},
    2: {'name': '8级', 'maxscore': 20, 'maxscore_old': 30, 'haslower': False, 'losescore': 0},
    3: {'name': '7级', 'maxscore': 20, 'maxscore_old': 60, 'haslower': False, 'losescore': 0},
    4: {'name': '6级', 'maxscore': 40, 'maxscore_old': 60, 'haslower': False, 'losescore': 0},
    5: {'name': '5级', 'maxscore': 60, 'maxscore_old': 60, 'haslower': False, 'losescore': 0},
    6: {'name': '4级', 'maxscore': 80, 'maxscore_old': 90, 'haslower': False, 'losescore': 0},
    7: {'name': '3级', 'maxscore': 100, 'haslower': False, 'losescore': 0},
    8: {'name': '2级', 'maxscore': 100, 'haslower': False, 'losescore': 10},
    9: {'name': '1级', 'maxscore': 100, 'haslower': False, 'losescore': 20},
    10: {'name': '初段', 'maxscore': 400, 'haslower': True, 'losescore': 30},
    11: {'name': '二段', 'maxscore': 800, 'haslower': True, 'losescore': 40},
    12: {'name': '三段', 'maxscore': 1200, 'haslower': True, 'losescore': 50},
    13: {'name': '四段', 'maxscore': 1600, 'haslower': True, 'losescore': 60},
    14: {'name': '五段', 'maxscore': 2000, 'haslower': True, 'losescore': 70},
    15: {'name': '六段', 'maxscore': 2400, 'haslower': True, 'losescore': 80},
    16: {'name': '七段', 'maxscore': 2800, 'haslower': True, 'losescore': 90},
    17: {'name': '八段', 'maxscore': 3200, 'haslower': True, 'losescore': 100},
    18: {'name': '九段', 'maxscore': 3600, 'haslower': True, 'losescore': 110},
    19: {'name': '十段', 'maxscore': 4000, 'haslower': True, 'losescore': 120},
    20: {'name': '天凤', 'maxscore': 1000000, 'haslower': False, 'losescore': 0}
}
###
'playlength 对局长度 1 or 2'
'playerlevel 对局等级? 0 1 2 3'
ptchange = {
    '3': {
        '0': (30, 0),
        '1': (50, 0),
        '2': (70, 0),
        '3': (90, 0)
    },
    'new4': {
        '0': (20, 10, 0),
        '1': (40, 10, 0),
        '2': (50, 20, 0),
        '3': (60, 30, 0)
    },
    'old4': {
        '0': (30, 0, 0),
        '1': (40, 10, 0),
        '2': (50, 20, 0),
        '3': (60, 30, 0)
    }
}

timeout = aiohttp.ClientTimeout(total=10)

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


class playerscore:
    def __init__(self, playername: str):
        self.rank = {3: 0, 4: 0}
        self.score = {3: 0, 4: 0}
        self.playername = playername
        self.maxrk = {3: 0, 4: 0}
        self.maxsc = {3: 0, 4: 0}
        self.maxsctime = {3: 0, 4: 0}
        self.playtimes = {3: 0, 4: 0}
        self.poslist = {3: [], 4: []}
        self.lastplaytime = 0

    def scorechange(self, playernum: int, sc: int):
        rk = self.rank[playernum]
        maxsc = levelmap[rk]['maxscore']

        return

    def addscore(self, playernum: int, score: int, magnification: int = 1, matchtime=0, is_old=False):
        rk = self.rank[playernum]
        mxsc = levelmap[rk]['maxscore']
        if is_old and rk <= 6:
            mxsc = levelmap[rk]['maxscore_old']
        self.lastplaytime = matchtime
        self.score[playernum] = self.score[playernum] + int(score * magnification)
        if self.score[playernum] >= mxsc:
            self.rank[playernum] += 1
            # print(f'{playernum}人麻将 在{time.strftime("%Y-%m-%d %H:%M ",time.localtime(matchtime))}升段到了{levelmap.get(self.rank[playernum]).get("name")},此前分数{self.score[playernum]}')
            if 9 < self.rank[playernum] < 21:
                self.score[playernum] = levelmap[self.rank[playernum]]['maxscore'] // 2
            else:
                self.score[playernum] = 0
        self.updatehistory(playernum, matchtime)

    def updatehistory(self, playernum=3, matchtime=None):
        # if playernum == 3:
        if self.rank[playernum] > self.maxrk[playernum]:
            self.maxrk[playernum] = self.rank[playernum]
            self.maxsc[playernum] = self.score[playernum]
            self.maxsctime[playernum] = matchtime
        elif self.rank[playernum] == self.maxrk[playernum]:
            if self.maxsc[playernum] < self.score[playernum]:
                self.maxsc[playernum] = self.score[playernum]
                self.maxsctime[playernum] = matchtime

    def reducescore(self, playernum: int, magnification: int = 1, matchtime=0):
        rk = self.rank[playernum]
        self.lastplaytime = matchtime
        reducescore = int(levelmap[rk]['losescore'] * magnification)
        self.score[playernum] = self.score[playernum] - reducescore
        if self.score[playernum] < 0:
            # print(f'{playernum}人麻将 在{time.strftime("%Y-%m-%d %H:%M",time.localtime(matchtime))}降段到了{levelmap.get(self.rank[playernum]).get("name")},此前分数{self.score[playernum]}')
            if 9 < self.rank[playernum] < 20:
                self.rank[playernum] = self.rank[playernum] - 1
                self.score[playernum] = levelmap[self.rank[playernum]]['maxscore'] // 2
            else:
                self.score[playernum] = 0

    def reset(self):
        self.rank = {3: 0, 4: 0}
        self.score = {3: 0, 4: 0}
        self.maxrk = {3: 0, 4: 0}
        self.maxsc = {3: 0, 4: 0}
        self.maxsctime = {3: 0, 4: 0}
        self.playtimes = {3: 0, 4: 0}
        self.lastplaytime = 0
        self.poslist = {3: [], 4: []}

    def showrank(self):
        playername = self.playername
        if self.rank[3] == 20:
            p3 = f'三麻段位:{levelmap[self.rank[3]]["name"]}'
        else:
            p3 = f'三麻段位:{levelmap[self.rank[3]]["name"]} [{self.score[3]}/{levelmap[self.rank[3]]["maxscore"]}]'
        if self.rank[4] == 20:
            p4 = f'四麻段位:{levelmap[self.rank[4]]["name"]}'
        else:
            p4 = f'四麻段位:{levelmap[self.rank[4]]["name"]} [{self.score[4]}/{levelmap[self.rank[4]]["maxscore"]}]'

        if 9 <= self.rank[3] < 20:
            p3 += f' 历史最高:{levelmap[self.maxrk[3]]["name"]} [{self.maxsc[3]}/{levelmap[self.maxrk[3]]["maxscore"]}]'
            p3 += f'\n达成时间: {time.strftime("%Y-%m-%d %H:%M", time.localtime(self.maxsctime[3]))}'
        if 9 <= self.rank[4] < 20:
            p4 += f' 历史最高:{levelmap[self.maxrk[4]]["name"]} [{self.maxsc[4]}/{levelmap[self.maxrk[4]]["maxscore"]}]'
            p4 += f'\n达成时间: {time.strftime("%Y-%m-%d %H:%M", time.localtime(self.maxsctime[4]))}'

        return f'{playername}\n{p3}\n{p4}\n{self.recentXposition(returnErr=False)}'

    def recentXposition(self, num=5, returnErr=True):
        """
        返回一个玩家最近 num 场对局的顺位
        """
        success = 0
        msg = f'{self.playername} 最近 {num} 局顺位如下:\n'
        if self.rank[3] > 0:
            msg += '三麻顺位: '
            if num > len(self.poslist.get(3)):
                msg += f'{self.poslist.get(3)}'[1:-1]
            else:
                msg += f'{self.poslist.get(3)[-num:]}'[1:-1] + '\n'
        else:
            success += 1
        if self.rank[4] > 0:
            msg += '四麻顺位: '
            if num > len(self.poslist.get(4)):
                msg += f'{self.poslist.get(4)}'[1:-1]
            else:
                msg += f'{self.poslist.get(4)[-num:]}'[1:-1]
        else:
            success += 1
        if success == 2:
            if returnErr:
                msg = f'玩家 {self.playername}没有进行过对局'
            else:
                msg = ''
        return msg


async def getthpt(playername: str):
    url = f'https://nodocchi.moe/api/listuser.php?name={playername}'
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=timeout,
                                     headers={'User-Agent': random.choice(user_agent_list)}) as session:
        async with session.get(url=url, allow_redirects=True) as response:
            listenerjson = await response.text()
            if listenerjson in [False, 'false']:
                return {'list': []}
            listenerjson = json.loads(listenerjson)
    return listenerjson


def readlevel(listenerjson: dict, playername: str, reset=True) -> str:
    dt = 1508792400  # 天凤pt改版时间点，与天凤水表网一致，2017-10-24 05:00（北京时间凌晨）
    deadtime = 86400 * 180
    ps = playerscore(playername)
    matches = listenerjson.get('list')
    matchcount = 0
    if len(matches) == 0:
        return "未查询到该玩家"
    for item in matches:

        starttime = int(item['starttime'])
        if starttime - ps.lastplaytime > deadtime:  # 超过180天未打则重置
            # if ps.maxrk[3] > 16 or ps.maxrk[4] > 16:  # 判断不了这个账号是否收费，因此我把7段以下的召唤会进行重置
            if reset:  # 还是手动决定是否重置
                ps.reset()
                matchcount = 0

        if item.get('lobby', None):
            # print("个室对战")
            continue
        # playernameList = [item.get('player1'), item.get('player2'), item.get('player3'), item.get('player4')]
        # if 'NoName' in playernameList:
        #     continue
        magnification = 1  # 倍率,南风场的倍率乘1.5
        oldP = False
        if starttime >= dt:
            # print('new 牌谱')
            pass
        else:
            # print('old 牌谱')
            oldP = True
        position = 1
        # print(time.strftime('%Y:%m:%d %H:%M', time.localtime(starttime)), end='\t')
        if item['playlength'] == '2':
            magnification = 1.5
        # print(magnification, end='\t')
        if item['playernum'] == '4':
            # print('4麻', end='\t')
            for i in range(1, 5):
                if item[f'player{i}'] == ps.playername:
                    position = i
            ps.poslist.get(4).append(position)
            # print(f'posi_{position}', end='\t')
            if oldP:
                useptrule = ptchange['old4']
            else:
                useptrule = ptchange['new4']
            if position == 4:
                ps.reducescore(4, magnification=magnification, matchtime=starttime)
            else:
                ps.addscore(4, useptrule[f"{item['playerlevel']}"][position - 1], magnification=magnification,
                            matchtime=starttime, is_old=oldP)
        else:
            # print('3麻', end='\t')
            useptrule = ptchange['3']
            for i in range(1, 4):
                if item[f'player{i}'] == ps.playername:
                    position = i
            ps.poslist.get(3).append(position)
            if position == 3:
                ps.reducescore(3, magnification=magnification, matchtime=starttime)
            else:
                ps.addscore(3, useptrule[f"{item['playerlevel']}"][position - 1], magnification=magnification,
                            matchtime=starttime, is_old=oldP)
        matchcount += 1
    # print(matchcount)

    return ps.showrank()


async def ptcalculation(playername, reset) -> str:
    try:
        results = await getthpt(playername)
        content = readlevel(results, playername, reset=reset)
        return content
    except asyncio.exceptions.TimeoutError as e:
        print(f'天凤PT查询超时{e}')
        return '查询超时,请再试一次'
