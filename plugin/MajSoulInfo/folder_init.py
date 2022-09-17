import os
import sqlite3

from utils.cfg_loader import write_file

if not os.path.exists("./database/MajSoulInfo"):
    os.mkdir("./database/MajSoulInfo")
if not os.path.exists("./config/MajSoulInfo"):
    os.mkdir("./config/MajSoulInfo")
if not os.path.exists("./images/MajSoulInfo"):
    os.mkdir("./images/MajSoulInfo")

if not os.path.exists(r"./config/MajSoulInfo/config.yml"):
    print('未检测到雀魂配置文件,生成初始文件中...')
    cfg = dict(qhpt=True, qhinfo=True, qhsl=True, qhyb=True, qhpaipu=True, broadcast='image', autoquery=True,
               dailydrawcount=3, disptgroup=[0], disinfogroup=[0], disslgroup=[0], disybgroup=[0],
               disautoquerygroup=[0], dispaipugroup=[0])
    write_file(content=cfg, path=r"./config/MajSoulInfo/config.yml")
    print('雀魂配置文件生成完毕')

if not os.path.exists(r"./config/MajSoulInfo/command.yml"):
    print('未检测到雀魂指令模板,生成初始文件中...')
    _cmd = {
        'disable': r'(qhdisable)\s*(\w+)\s*$',
        'enable': r'(qhenable)\s*(\w+)\s*$',
        'qhpt': r'(qhpt|雀魂分数|雀魂pt)\s*(\S+)\s*([34])?\s*([0-9]+)?\s*$',
        'qhpaipu': r'(qhpaipu|雀魂最近对局)\s*(\S+)\s*([34])*\s*([0-9]+)?\s*$',
        'qhinfo': r'(qhinfo|雀魂玩家详情)\s*(\S+)\s*(\d+)\s*(\w+)*\s*(\w+)*\s*$',
        'qhyb': r'(qhyb|雀魂月报)\s*(\S+)\s*([34])?\s*([0-9]{4})?[-]?([0-9]{1,2})?\s*$',
        'qhsl': r'(qhsl|雀魂十连)\s*(\w+)*\s*$',
        'getmyqhsl': r'(getmyqhsl|我的雀魂十连)\s*$',
        'getwatch': r'(qhgetwatch|雀魂获取本群关注)\s*$',
        'addwatch': r'(qhadd|雀魂添加关注)\s*(\S+)\s*$',
        'delwatch': r'(qhdel|雀魂删除关注)\s*(\S+)\s*$',
        'clearwatch': r'(qhclearwatch|雀魂清除本群关注)\s*$',
        'tagon': r'(qhtagon|雀魂添加标记)\s*(\S+)\s*(\S+)\s*$',
        'tagoff': r'(qhtagoff|雀魂删除标记)\s*(\S+)\s*(\S+)?\s*$',
        'taglist': r'(qhtaglist)\s*(\S+)?\s*$',

        'tagopeartion': r'(qhtag)\s*(\S+)\s*(\S+)\s*(\S*)?\s*'
    }
    write_file(content=_cmd, path=r"./config/MajSoulInfo/command.yml")
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
    write_file(content=template, path=r"./config/MajSoulInfo/template.yml")
    print('雀魂模板文件生成完毕')


def db_init():
    cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
    cursor = cx.cursor()
    cursor.execute("create table if not exists paipu("
                   "id integer primary key,"
                   "uuid varchar(50) UNIQUE,"
                   "watchid integer,"
                   "startTime varchar(50),"
                   "endTime varchar(50),"
                   "player1 varcher(50),"
                   "player2 varcher(50),"
                   "player3 varcher(50),"
                   "player4 varcher(50)"
                   ")")
    cursor.execute('create table if not exists watchedplayer ('
                   'id integer primary key,'
                   'watchedgroupcount integer not null default 0,'
                   'playerid integer,'
                   'playername varchar(50) UNIQUE)')
    cursor.execute("create table if not exists QQgroup("
                   "id integer primary key ,"
                   "groupid integer UNIQUE)")
    cursor.execute("create table if not exists group2player("
                   "id integer primary key,"
                   "groupid integer,"
                   "playerid integer,"
                   "playername varchar(50),"
                   'iswatching integer not null default 1,'
                   "UNIQUE(groupid,playerid) ON CONFLICT REPLACE)")
    cursor.execute('create table if not exists qhplayer ('
                   'id integer primary key,'
                   'playerid integer,'
                   'playername varchar(50) UNIQUE)')
    cursor.execute("create table IF NOT EXISTS drawcards("
                   "id integer primary key,"
                   "userid int UNIQUE,"
                   "drawcount int,"
                   "lastdraw varchar(50)"
                   ")")
    cursor.execute("create table if not exists playerdrawcard("
                   "id integer primary key,"
                   "userid integer not null,"
                   "drawtime varchar(50) not null,"
                   "itemlevel int not null,"
                   "itemname TEXT not null"
                   ")")
    cursor.execute("create table if not exists tagnames("
                   "id integer primary key,"
                   "tagname TEXT not null,"
                   "userid integer not null,"
                   "gpid integer not null,"
                   "constraint gp_nickname "
                   "foreign key (gpid) "
                   "references group2player(id)"
                   ")")
    cursor.execute("create view if not exists groupwatches as "
                   "select groupid,"
                   "group_concat(playername) as watchedplayers,"
                   "count(groupid) as watchnums "
                   "from group2player "
                   "where iswatching = 1 "
                   "group by groupid")
    cursor.execute("create view if not exists watchedplayersview as "
                   "select playername,playerid, "
                   "count(groupid) as watchedgroupcount "
                   "from group2player "
                   "where iswatching = 1 "
                   "group by playername")
    cursor.execute("create view if not exists tagnameview as "
                   "select tagname,playername,groupid "
                   "from tagnames as tg join group2player as gp "
                   "where tg.gpid = gp.id "
                   "and gp.iswatching = 1")
    cx.commit()
    cursor.close()
    cx.close()


db_init()
