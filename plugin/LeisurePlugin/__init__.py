from plugin.LeisurePlugin.leisure import *
from plugin.LeisurePlugin.tarot import TarotCards,TarotCard
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
cursor.execute('create table IF NOT EXISTS tarot ('
               'id integer primary key,'
               'cardsid integer,'
               'cardname varchar(40) not null,'
               'position int not null default 1 )')
cx.commit()
cx.close()
