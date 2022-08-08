import os
from utils.cfg_loader import w_cfg_to_file

if not os.path.exists("./database/MajSoulInfo"):
    os.mkdir("./database/MajSoulInfo")
if not os.path.exists("./config/MajSoulInfo"):
    os.mkdir("./config/MajSoulInfo")
if not os.path.exists("./images/MajSoulInfo"):
    os.mkdir("./images/MajSoulInfo")

if not os.path.exists("./config/MajSoulInfo/config,yml"):
    print('生成雀魂配置文件中')
    cfg = dict(qhsettings=dict(qhpt=True, qhinfo=True, qhsl=True, qhyb=True, qhpaipu=True, disptgroup=[0],
                               disinfogroup=[0], disslgroup=[0], disybgroup=[0], disautoquerygroup=[0],
                               dispaipugroup=[0]))
    w_cfg_to_file(content=cfg, path="./config/MajSoulInfo/config,yml")
    print('雀魂配置文件生成完毕')

if not os.path.exists("./config/MajSoulInfo/template,yml"):
    print('生成雀魂模板文件中')
    template = dict(qhpt=" 玩家名: %playername%\n三麻: %pl3% \n四麻: %pl4% ",
                    qhyb=dict(
                        pl3="玩家%playername%在%Y年%m月共进行了%counts%场对局,共计%1st%次①位,%2nd%次②位,%3rd%次③位,%4th%次④位,"
                            "平均顺位:%averank%,%flycount%,PT得失:%ptchange%\n",
                        pl4="玩家%playername%在%Y年%m月共进行了%counts%场对局,共计%1st%次①位,%2nd%次②位,%3rd%次③位,平均顺位:%averank%,"
                            "%flycount%,PT得失:%ptchange%\n",
                        infomsg="立直率: %立直率%\n 副露率: %副露率%\n 和牌率: %和牌率%\n 放铳率: %放铳率%\n 默听率: %默听率%\n 平均打点: %平均打点%\n "
                                "平均铳点: %平均铳点%"),
                    qhsl=dict(maxdraw=3),
                    qhinfo=dict(format="%k% : %v% \n"),
                    qhpaipu=dict(head="玩家%playername%最近%counts%场对局如下:",
                                 format="牌谱链接:%paipuurl% \n开始时间:%startTime% \n结束时间:%endTime% \n对局玩家:%players% \n",
                                 footer="总PT收支:%ptupdate%"),
                    endboardcast=dict(head="检测到新的对局:\n",
                                      format="牌谱链接:%paipuurl% \n开始时间:%startTime% \n结束时间:%endTime% \n对局玩家:%players%",
                                      sort=False)
                    )
    print('雀魂模板文件生成完毕')
