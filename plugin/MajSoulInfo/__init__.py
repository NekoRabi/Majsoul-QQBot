from plugin.MajSoulInfo.folder_init import *
from plugin.MajSoulInfo.majsoulinfo import majsoulobj as majsoul
from plugin.MajSoulInfo.mergeimgs import *
import sqlite3

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
