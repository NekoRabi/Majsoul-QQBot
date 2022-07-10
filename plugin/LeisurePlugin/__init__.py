from plugin.LeisurePlugin.leisure import *
from plugin.LeisurePlugin.tarot import cards as tarotcards
import os

if not os.path.exists("./database/LeisurePlugin"):
    os.mkdir("./database/LeisurePlugin")

if not os.path.exists("./images/tarot"):
    os.mkdir("./images/tarot")

cx = sqlite3.connect("./database/LeisurePlugin/leisure.sqlite")
cursor = cx.cursor()
cursor.execute('create table IF NOT EXISTS userinfo('
               'id integer primary key,'
               'userid integer UNIQUE,'
               'score integer default 0,'
               'lastsignin varchar(50),'
               'keepsigndays integer not null default 1'
               ')')

cursor.execute("create table if not exists playerdrawcard("
               "id integer primary key,"
               "userid integer not null,"
               "drawtime varchar(50) not null,"
               "cardid integer not null,"
               "cardposition integer not null"
               ")")

cursor.execute("create table if not exists drawtarots("
               "id integer primary key,"
               "userid integer not null,"
               "drawtime varchar(50) not null,"
               "cardname text not null,"
               "cardposition text not null"
               ")")

cx.commit()
cx.close()
