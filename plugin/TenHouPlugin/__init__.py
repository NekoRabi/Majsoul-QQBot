import os
import sqlite3

from plugin.TenHouPlugin.TenHou import asyautoget_th_matching, addthwatch, asyautoget_th_match, removethwatch, \
    getthwatch, asygetTH,getthpt

if not os.path.exists("./database/TenHouPlugin"):
    os.mkdir("./database/TenHouPlugin")

if not os.path.exists("./data/TenHouPlugin"):
    os.mkdir("./data/TenHouPlugin")

cx = sqlite3.connect('./database/TenHouPlugin/TenHou.sqlite')
cursor = cx.cursor()
cursor.execute('create table IF NOT EXISTS watchedplayer ('
               'id integer primary key,'
               'playername varchar(50) UNIQUE)')
cursor.execute("create table IF NOT EXISTS QQgroup("
               "id integer primary key ,"
               "groupid integer UNIQUE)")
cursor.execute("create table IF NOT EXISTS group2player("
               "id integer primary key,"
               "groupid integer,"
               "playername varchar(50),"
               "UNIQUE(groupid,playername) ON CONFLICT REPLACE)")
cursor.execute("create table IF NOT EXISTS paipu("
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

cx.commit()
cursor.close()
cx.close()
