from plugin.MajSoulInfo.majsoulinfo import *
from plugin.MajSoulInfo.mergeimgs import *
import os

if not os.path.exists("./database/MajSoulInfo"):
    os.mkdir("./database/MajSoulInfo")
if not os.path.exists("./config/MajSoulInfo"):
    os.mkdir("./config/MajSoulInfo")

if not os.path.exists("./images/MajSoulInfo"):
    os.mkdir("./images/MajSoulInfo")

cx = sqlite3.connect('./database/MajSoulInfo/majsoul.sqlite')
cursor = cx.cursor()
cursor.execute("create table IF NOT EXISTS paipu("
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
cursor.execute('create table IF NOT EXISTS watchedplayer ('
               'id integer primary key,'
               'watchedgroupcount integer not null default 0,'
               'playerid integer,'
               'playername varchar(50) UNIQUE)')
cursor.execute("create table IF NOT EXISTS QQgroup("
               "id integer primary key ,"
               "groupid integer UNIQUE)")
cursor.execute("create table IF NOT EXISTS group2player("
               "id integer primary key,"
               "groupid integer,"
               "playerid integer,"
               "playername varchar(50),"
               'iswatching integer not null default 1,'
               "UNIQUE(groupid,playerid) ON CONFLICT REPLACE)")
cursor.execute('create table IF NOT EXISTS qhplayer ('
               'id integer primary key,'
               'playerid integer,'
               'playername varchar(50) UNIQUE)')
cursor.execute("create table IF NOT EXISTS drawcards("
               "id integer primary key,"
               "userid int UNIQUE,"
               "drawcount int,"
               "lastdraw varchar(50)"
               ")")
cx.commit()
cursor.close()
cx.close()
