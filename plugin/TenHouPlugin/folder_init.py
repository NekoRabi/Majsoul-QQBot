import os
import sqlite3
from utils.cfg_loader import write_file, read_file


def file_init():
    if not os.path.exists("./database/TenHouPlugin"):
        os.mkdir("./database/TenHouPlugin")

    if not os.path.exists("./config/TenHouPlugin"):
        os.mkdir("./config/TenHouPlugin")

    if not os.path.exists(r'./config/TenHouPlugin/config.yml'):
        _cfg = dict(thpt=True, searchfrequency=6, autoquery=True, broadcast='image')
        write_file(content=_cfg, path=r'./config/TenHouPlugin/config.yml')

    if not os.path.exists(r'./config/TenHouPlugin/template.yml'):
        _template = {
            'result': {
                4: {
                    1: " %player% 轻松拿下一位,实在太强啦",
                    2: " %player% 悄悄拿下二位,稳稳上分",
                    3: " %player% 精准避四，避开重大损失",
                    4: " %player% 被安排了一个四位,库鲁西~"
                },
                3: {
                    1: " %player% 轻松拿下一位,实在太强啦",
                    2: " %player% 悄悄拿二,韬光养晦",
                    3: " %player% 忍痛吃三，太苦了"
                },
                "header": r"检测到新的对局信息\n",
                "main": r" %model% \n开始时间: %starttime% 对局时长:%duration%\n %players%"
            },
            'matching': r"%target% 正在天凤对局,速来围观: %url%\n %players%"
        }
        write_file(content=_template, path=r'./config/TenHouPlugin/template.yml')

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

    commands = read_file(r'./config/command.yml')
    thcmds = {
        "thpt": r"(thpt|天凤pt|天凤分数)\s*(\S+)\s*(\S+)?\s*$",
        "addwatch": r"(thadd|天凤添加关注)\s*(\S+)\s*$",
        "delwatch": r"(thdel|天凤删除关注)\s*(\S+)\s*$",
        "getwatch": r"(thgetwatch|天凤获取本群关注)\s*$",
        "clearwatch": r"(thclearwatch|天凤清除本群关注)\s*$",
        "tagon": r"(thtagon|天凤添加标记)\s*(\S+)\s*(\S+)\s*$",
        "tagoff": r"(thtagoff|天凤删除标记)\s*(\S+)\s*(\S+)?\s*$",
        "taglist": r"(qhtaglist)\s*(\S+)?\s*$"
    }
    if commands.get('tenhou', None):
        for key in ['thpt', 'addwatch', 'delwatch', 'getwatch', 'clearwatch', 'tagon', 'tagoff', 'taglist']:
            if key not in commands.get('tenhou').keys():
                commands['tenhou'] = thcmds
                write_file(commands, path=r'./config/command.yml')
                break
    else:
        commands['tenhou'] = thcmds
        write_file(commands, path=r'./config/command.yml')


    # if not os.path.exists(r'./config/TenHouPlugin/command.yml'):
    #     w_cfg_to_file(thcmds, path=r'./config/command.yml')
    # else:
    #     commands = loadcfg_from_file(r'./config/TenHouPlugin/command.yml')
    #     for key in ['thpt', 'addwatch', 'delwatch', 'getwatch', 'clearwatch', 'tagon', 'tagoff', 'taglist']:
    #         if key not in commands.keys():
    #             commands['tenhou'] = thcmds
    #             w_cfg_to_file(commands, path=r'./config/command.yml')
    #             break

file_init()
