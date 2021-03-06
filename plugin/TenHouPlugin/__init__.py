import os
import sqlite3

from plugin.TenHouPlugin.TenHou import tenhouobj as tenhou

if not os.path.exists("./database/TenHouPlugin"):
    os.mkdir("./database/TenHouPlugin")

if not os.path.exists("./data/TenHouPlugin"):
    os.mkdir("./data/TenHouPlugin")

cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
cursor = cx.cursor()
cursor.execute('create table if not exists watchedplayer ('
               'id integer primary key,'
               'watchedgroupcount integer not null default 0,'
               'playername varchar(50) UNIQUE)')
cursor.execute("create table if not exists QQgroup("
               "id integer primary key ,"
               "groupid integer UNIQUE)")
cursor.execute("create table IF NOT EXISTS group2player("
               "id integer primary key,"
               "groupid integer,"
               "playername varchar(50),"
               "iswatching integer not null default 1,"
               "UNIQUE(groupid,playername) ON CONFLICT REPLACE)")
cursor.execute("create table if not exists paipu("
               "id integer primary key,"
               "startTime varchar(50),"
               "model varchar(50),"
               "duration varchar(50),"
               "player1 varcher(50),"
               "player2 varcher(50),"
               "player3 varcher(50),"
               "player4 varcher(50)"
               ")")
cursor.execute("create table if not exists isgaming("
               "playername varchar(50),"
               "url varchar(20)"
               ")")

cursor.execute("create view if not exists groupwatches as "
               "select groupid,"
               "group_concat(playername) as watchedplayers,"
               "count(groupid) as watchnums "
               "from group2player "
               "where iswatching = 1 "
               "group by groupid")

cursor.execute("create view if not exists watchedplayersview as "
               "select playername,"
               "count(groupid) as watchedgroupcount "
               "from group2player "
               "where iswatching = 1 "
               "group by playername")
cx.commit()
cursor.close()
cx.close()
