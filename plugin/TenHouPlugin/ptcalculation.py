'''

时间分界线  2017.10.24  1508774400

等级映射表
level: name maxscore haslower 4pt 3pt
'''
import asyncio
import random
import time

import aiohttp

levelmap = {
    0: {'name': '新人', 'maxscore': 20, 'haslower': False, 'losescore': 0},
    1: {'name': '9级', 'maxscore': 20, 'haslower': False, 'losescore': 0},
    2: {'name': '8级', 'maxscore': 20, 'haslower': False, 'losescore': 0},
    3: {'name': '7级', 'maxscore': 20, 'haslower': False, 'losescore': 0},
    4: {'name': '6级', 'maxscore': 40, 'haslower': False, 'losescore': 0},
    5: {'name': '5级', 'maxscore': 60, 'haslower': False, 'losescore': 0},
    6: {'name': '4级', 'maxscore': 80, 'haslower': False, 'losescore': 0},
    7: {'name': '3级', 'maxscore': 100, 'haslower': False, 'losescore': 0},
    8: {'name': '2等', 'maxscore': 100, 'haslower': False, 'losescore': 10},
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
    20: {'name': '天凤', 'maxscore': 100000, 'haslower': False, 'losescore': 0}
}
'playlength 对局长度 1/2'
'playerlevel 对局等级? 0 1 2 3'
ptchange = {
    '3': {
        '0': (30, 0),
        '1': (50, 0),
        '2': (70, 0),
        '3': (100, 0)
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
        self.playtimes = {3: 0, 4: 0}

    def scorechange(self, playernum: int, sc: int):
        rk = self.rank[playernum]
        maxsc = levelmap[rk]['maxscore']

        return

    def addscore(self, playernum: int, score: int, magnification: int = 1):
        rk = self.rank[playernum]
        mxsc = levelmap[rk]['maxscore']
        self.score[playernum] = self.score[playernum] + score * magnification
        if self.score[playernum] >= mxsc:
            self.rank[playernum] += 1
            if 9 < self.rank[playernum] < 21:
                self.score[playernum] = int(levelmap[self.rank[playernum]]['maxscore'] / 2)
            else:
                self.score[playernum] = 0
        self.updatehistory()

    def updatehistory(self):
        if self.rank[3] > self.maxrk[3]:
            self.maxrk[3] = self.rank[3]
            self.maxsc[3] = self.score[3]
        elif self.rank[3] == self.maxrk[3]:
            if self.maxsc[3] < self.score[3]:
                self.maxsc[3] = self.score[3]

        if self.rank[4] > self.maxrk[4]:
            self.maxrk[4] = self.rank[4]
            self.maxsc[4] = self.maxsc[4]
        elif self.rank[4] == self.maxrk[4]:
            if self.maxsc[4] < self.score[4]:
                self.maxsc[4] = self.score[4]

    def reducescore(self, playernum: int, magnification: int = 1):
        rk = self.rank[playernum]
        reducescore = levelmap[rk]['losescore'] * magnification
        self.score[playernum] = self.score[playernum] - reducescore
        if self.score[playernum] <= 0:
            if 9 < self.rank[playernum] < 20:
                self.rank[playernum] = self.rank[playernum] - 1
                self.score[playernum] = int(levelmap[self.rank[playernum]]['maxscore'] / 2)
            else:
                self.score[playernum] = 0

    def showrank(self):
        playername = self.playername
        p3 = f'三麻段位:{levelmap[self.rank[3]]["name"]} {int(self.score[3])}pt'
        p4 = f'四麻段位:{levelmap[self.rank[4]]["name"]} {int(self.score[4])}pt'
        # p3 = f'三麻段位:' \
        #      f'当前段位: {levelmap[self.rank[3]]["name"]} {int(self.score[3])}pt 历史最高:{levelmap[self.maxrk[3]]["name"]} {int(self.maxsc[3])}pt'
        # p4 = f'四麻段位:' \
        #      f'当前段位: {levelmap[self.rank[4]]["name"]} {int(self.score[4])}pt 历史最高:{levelmap[self.maxrk[4]]["name"]} {int(self.maxsc[4])}pt'
        return f'{playername}\n{p3}\n{p4}\n *个室对战等会影响数据统计，目前还在研究。'


async def getthpt(playername: str):
    url = f'https://nodocchi.moe/api/listuser.php?name={playername}'
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=timeout,
                                     headers={'User-Agent': random.choice(user_agent_list)}) as session:
        async with session.get(url=url, allow_redirects=True) as response:
            listenerjson = await response.text()
            if listenerjson in [False,'false']:
                return {'list':[]}
            listenerjson = eval(listenerjson)
    return listenerjson


def readlevel(listenerjson: dict, playername: str) -> str:
    dt = time.mktime(time.strptime('2017:10:24', '%Y:%m:%d'))
    ps = playerscore(playername)
    level = listenerjson.get('list')
    if len(level) == 0:
        return "未查询到该玩家"
    for item in level:
        magnification = 1  # 倍率,南风场的倍率乘1.5
        oldP = False
        # print(item)
        if item['sctype'] not in ['b','c']:
            # print('非段位战')
            continue
        position = 1
        # print(time.strftime('%Y:%m:%d %H:%M', time.localtime(int(item['starttime']))), end='\t')
        if item['playlength'] == '2':
            magnification = 1.5
        # print(magnification, end='\t')
        if item['playernum'] == '4':
            # print('4麻', end='\t')
            for i in range(1, 5):
                if item[f'player{i}'] == ps.playername:
                    position = i
            # print(f'posi_{position}', end='\t')
            if int(item['starttime']) >= int(dt):
                # print('new 牌谱')
                pass
            else:
                # print('old 牌谱')
                oldP = True
            if oldP:
                useptrull = ptchange['old4']
            else:
                useptrull = ptchange['new4']
            if position == 4:
                ps.reducescore(4, magnification=magnification)
            else:
                ps.addscore(4, useptrull[f"{item['playerlevel']}"][position - 1], magnification=magnification)
        else:
            # print('3麻', end='\t')
            useptrull = ptchange['3']
            for i in range(1, 4):
                if item[f'player{i}'] == ps.playername:
                    position = i
            if position == 3:
                ps.reducescore(3, magnification=magnification)
            else:
                ps.addscore(3, useptrull[f"{item['playerlevel']}"][position - 1], magnification=magnification)

    return ps.showrank()


def ptcalculation(playername) -> str:
    try:
        tasks = [
            asyncio.ensure_future(getthpt(playername))
        ]
        loop = asyncio.get_event_loop()
        tasks = asyncio.gather(*tasks)
        loop.run_until_complete(tasks)
        content = ''
        for results in tasks.result():
            content = readlevel(results, playername)
        return content
    except asyncio.exceptions.TimeoutError as e:
        print(f'天凤PT查询超时{e}')
        return '查询超时,请再试一次'

