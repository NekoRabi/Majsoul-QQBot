import os
import sqlite3

from core import add_help
from utils import write_file

if not os.path.exists("./database/AlarmClock"):
    os.mkdir("./database/AlarmClock")

if not os.path.exists("./config/AlarmClock"):
    os.mkdir("./config/AlarmClock")


def _db_init():
    cx = sqlite3.connect('./database/AlarmClock/clock.sqlite')
    cursor = cx.cursor()
    cursor.execute("create table if not exists groupclock("
                   "id integer primary key,"
                   "type text not null default 'group',"
                   "creator integer not null,"
                   "at text not null default '',"
                   "target integer not null,"
                   "description text not null,"
                   "scheduledtime text not null,"
                   "enable integer not null default 1"
                   ")")
    cx.commit()
    cursor.close()
    cx.close()


def _cfg_init():
    if not os.path.exists("./config/AlarmClock/config.yml"):
        write_file(content=dict(enable=True), path="./config/AlarmClock/config.yml")


_db_init()
_cfg_init()

add_help('group', ["添加提醒 @xx YYYY-mm-DD HH:MM:ss 备注 ： 设置一个闹钟"])