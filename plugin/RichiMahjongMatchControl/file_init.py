import os
import sqlite3


def folder_init():
    if not os.path.exists("./database/RichiMahjongMatchControl"):
        os.mkdir("./database/RichiMahjongMatchControl")
    if not os.path.exists("./config/RichiMahjongMatchControl"):
        os.mkdir("./config/RichiMahjongMatchControl")


def db_init():
    cx = sqlite3.connect('./database/RichiMahjongMatchControl/match.sqlite')
    cursor = cx.cursor()
    cursor.execute("create table if not exists teamcompetition("
                   "id integer primary key,"
                   "name text not null unique,"
                   "host integer not null,"
                   "sourcegroup integer not null,"
                   "ddl text not null,"
                   "description text"
                   ")")

    cursor.execute("create table if not exists teams("
                   "id integer primary key,"
                   "name text not null,"
                   "matchid integer not null,"
                   "leader integer,"
                   "description text,"
                   "constraint fk_matchid "
                   "foreign key (matchid) "
                   "references teamcompetition(id),"
                   "UNIQUE(name,matchid) ON CONFLICT REPLACE"
                   ")")

    cursor.execute("create table if not exists remind("
                   "id integer primary key,"
                   "QQid text not null,"
                   "remindtime text not null,"
                   "description text"
                   ")")

    cursor.execute("create table if not exists players("
                   "id integer primary key,"
                   "qqid integer not null,"
                   "playername text"
                   ")")

    cursor.execute("create table if not exists teamplayers("
                   "id integer primary key,"
                   "teamid integer not null,"
                   "playerid integer not null,"
                   "position text,"
                   "score integer not null default 0,"
                   "enable integer not null default 1,"
                   "constraint fk_teamid "
                   "foreign key (teamid) "
                   "references teamcompetition(id),"
                   "constraint fk_playerid "
                   "foreign key (playerid) "
                   "references players(id)"
                   ")")
    cursor.execute("create view if not exists teamview as select teams.id as teamid, "
                   "teams.name as teamname, "
                   "teamcompetition.name as matchname "
                   "from teams "
                   "left join teamcompetition "
                   "on teams.matchid = teamcompetition.id")
    cursor.execute("create view if not exists playerteamview as SELECT players.id as playerid,"
                   "players.qqid as qq, "
                   "players.playername, "
                   "teamplayers.teamid, "
                   "teamplayers.position "
                   "FROM players "
                   "LEFT JOIN "
                   "teamplayers ON players.id = teamplayers.playerid "
                   "WHERE teamplayers.enable > 0"
                   )
    cursor.execute("create view if not exists ptmview as "
                   "SELECT teamview.teamid,teamname,playerteamview.playerid,playername,qq,matchname,position "
                   "FROM teamview "
                   "LEFT JOIN playerteamview "
                   "ON teamview.teamid = playerteamview.teamid")
    cx.commit()
    cursor.close()
    cx.close()


folder_init()
db_init()
