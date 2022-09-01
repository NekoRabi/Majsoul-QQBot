import os
from utils.cfg_loader import w_cfg_to_file

if not os.path.exists("./database/MajSoulInfo"):
    os.mkdir("./database/MajSoulInfo")
if not os.path.exists("./config/MajSoulInfo"):
    os.mkdir("./config/MajSoulInfo")
if not os.path.exists("./images/MajSoulInfo"):
    os.mkdir("./images/MajSoulInfo")

if not os.path.exists(r"./config/MajSoulInfo/config.yml"):
    print('未检测到雀魂配置文件,生成初始文件中...')
    cfg = dict(
        qhsettings=dict(qhpt=True, qhinfo=True, qhsl=True, qhyb=True, qhpaipu=True, autoquery=True, disptgroup=[0],
                        disinfogroup=[0], disslgroup=[0], disybgroup=[0], disautoquerygroup=[0],
                        dispaipugroup=[0]))
    w_cfg_to_file(content=cfg, path=r"./config/MajSoulInfo/config.yml")
    print('雀魂配置文件生成完毕')

if not os.path.exists(r"./config/MajSoulInfo/template.yml"):
    print('生成雀魂播报模板文件中...')
    template = dict(qhpt=r" 玩家名: %playername%<br>三麻: %pl3% <br>四麻: %pl4% ",
                    qhyb=dict(
                        pl3=r"玩家%playername%在%Y年%m月共进行了%counts%场对局,共计%1st%次①位,%2nd%次②位,%3rd%次③位,%4th%次④位,平均顺位:%averank%,%flycount%,PT得失:%ptchange%<br>",
                        pl4=r"玩家%playername%在%Y年%m月共进行了%counts%场对局,共计%1st%次①位,%2nd%次②位,%3rd%次③位,平均顺位:%averank%,%flycount%,PT得失:%ptchange%<br>",
                        infomsg=r"立直率: %立直率%<br> 副露率: %副露率%<br> 和牌率: %和牌率%<br> 放铳率: %放铳率%<br> 默听率: %默听率%<br> 平均打点: %平均打点%<br> 平均铳点: %平均铳点%"),
                    qhsl=dict(maxdraw=3),
                    qhinfo=dict(format=r"%k% : %v% <br>"),
                    qhpaipu=dict(head=r"玩家%playername%最近%counts%场对局如下:",
                                 format=r"牌谱链接:%paipuurl% <br>开始时间:%startTime% <br>结束时间:%endTime% <br>对局玩家:%players% <br>",
                                 footer=r"总PT收支:%ptupdate%"),
                    endboardcast=dict(head=r"检测到新的对局:<br>",
                                      format=r"牌谱链接:%paipuurl% <br>开始时间:%startTime% <br>结束时间:%endTime% <br>对局玩家:%players%",
                                      sort=False)
                    )
    w_cfg_to_file(content=template, path=r"./config/MajSoulInfo/template.yml")
    print('雀魂模板文件生成完毕')
