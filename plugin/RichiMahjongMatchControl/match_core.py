"""
:Author:  NekoRabi
:Create:  2022/10/15 21:19
:Update: /
:Describe: 比赛机器人核心功能
:Version: 0.0.1
"""
import sqlite3


class MatchOperator:

    def __init__(self):
        pass

    @staticmethod
    def register_match(host: int, sourcegroup: int, matchname: str, ddl: str, description: str = None) -> str:
        """
        创建比赛

        Args:
            host:创建人的QQ
            sourcegroup: 由哪个群聊创建
            matchname:比赛名
            ddl: 比赛截止报名时间(YYYY-MM-dd)
            description: 比赛描述

        Returns:

        """
        if description is None:
            description = ''
        cx = sqlite3.connect('./database/RichiMahjongMatchControl/match.sqlite')
        cursor = cx.cursor()
        cursor.execute(f"select * from teamcompetition where name = '{matchname}'")
        if len(cursor.fetchall()) > 0:
            cursor.close()
            cx.close()
            return "创建比赛失败, 已有同名比赛"
        # if description:
        #     sql = f"insert into teamcompetition(name,ddl,description) values('{matchname}','{ddl}','{description}')"
        # else:
        #     sql = f"insert into teamcompetition(name,ddl,description) values('{matchname}','{ddl}')"
        sql = f"insert into teamcompetition(name,ddl,description,host,sourcegroup) values('{matchname}','{ddl}','{description}',{host},{sourcegroup})"
        cursor.execute(sql)
        cx.commit()
        matchid = cursor.execute(f"select id from teamcompetition where name = '{matchname}'").fetchall()
        matchid = matchid[0][0]
        cursor.execute(f"insert into teams(name,matchid) values('{matchname}',{matchid})")
        cx.commit()
        cursor.close()
        cx.close()
        return "比赛创建成功"

    @staticmethod
    def join_match(matchname: str, qqid: int, teamname=None, position=None, playername=None) -> str:
        """
        参加比赛

        Args:
            matchname:要参加的比赛名
            qqid: 参加者的qq号
            position: 报名队伍的位置
            teamname: 报名队伍名字
            playername: 比赛玩家名

        Returns:

        """
        if not teamname:
            teamname = matchname
        cx = sqlite3.connect('./database/RichiMahjongMatchControl/match.sqlite')
        cursor = cx.cursor()
        sql = f"select qq from ptmview where teamname='{teamname}' and matchname = '{matchname}' and playername = '{playername}'"
        if position:
            sql += f" and position = '{position}'"
        qq = cursor.execute(sql).fetchall()
        if len(qq) > 0:
            cursor.close()
            cx.close()
            qq = qq[0][0]
            msg = "加入队伍"
            if position:
                msg += "的该位置"
            if qq == qqid:
                return "你已" + msg
            return "已有同名玩家" + msg
        matchid = cursor.execute(f"select id from teamcompetition where name = '{matchname}'").fetchall()
        if len(matchid) == 0:
            return "比赛不存在"
        else:
            matchid = matchid[0][0]
        teamid = cursor.execute(f"select id from teams where name = '{teamname}' and matchid = {matchid}").fetchall()
        if len(teamid) == 0:
            return "队伍不存在"
        teamid = teamid[0][0]
        if playername == "" or playername is None:
            cursor.execute(f"select id from players where qqid = {qqid}")
        else:
            cursor.execute(f"select id from players where qqid = {qqid} and playername = '{playername}'")
        playerid = cursor.fetchall()
        if len(playerid) > 0:
            playerid = playerid[0][0]
        else:
            sql1 = f"insert into players(qqid,playername) values({qqid},'')"
            sql2 = f"select id from players where qqid = {qqid}"
            if playername:
                sql1 = f"insert into players(qqid,playername) values({qqid},'{playername}')"
                sql2 = f"select id from players where qqid = {qqid} and playername = '{playername}'"
            cursor.execute(sql1)
            cx.commit()
            playerid = cursor.execute(sql2).fetchall()[0][0]
        if not position:
            p = cursor.execute(
                f"select enable from teamplayers where playerid = {playerid} and teamid = {teamid}").fetchall()
            if len(p) > 0:
                if p[0][0] > 0:
                    return '你已加入该队伍,无法重复加入'
                cursor.execute(f"update teamplayers set enable = 1 where playerid = {playerid} and teamid = {teamid}")
                cx.commit()
                cursor.close()
                cx.close()
                return "加入成功"
        else:
            p = cursor.execute(f"select enable from teamplayers where playerid = {playerid} and teamid = {teamid} and "
                               f"position = '{position}'").fetchall()
            if len(p) > 0:
                if p[0][0] > 0:
                    return '你已选择该位置'
                cursor.execute(
                    f"update teamplayers set enable = 1 where playerid = {playerid} and teamid = {teamid} and position = '{position}'")
                cx.commit()
                cursor.close()
                cx.close()
                return "加入成功"
        if position:
            sql = f"insert into teamplayers(playerid,teamid,position) values({playerid},{teamid},'{position}')"
        else:
            sql = f"insert into teamplayers(playerid,teamid) values({playerid},{teamid})"
        cursor.execute(sql)
        cx.commit()
        cursor.close()
        cx.close()
        return "加入成功"

    @staticmethod
    def get_teammembers(matchname, teamname=None) -> list:
        """
        获取队伍成员

        Args:
            matchname: 比赛名
            teamname: 队伍名

        Returns:[(),()]

        """
        if not teamname:
            teamname = matchname
        cx = sqlite3.connect('./database/RichiMahjongMatchControl/match.sqlite')
        cursor = cx.cursor()
        order_rule = "CASE position WHEN '先锋' THEN 1 WHEN '次锋' THEN 2 WHEN '中坚' THEN 3 when '副将' then 4 when '大将' then 5 when '替补' then 6 END, position"
        sql = f'select group_concat(qq) as qq,group_concat(playername) as players,position from ptmview where teamname = "{teamname}" and matchname = "{matchname}" group by position order by {order_rule}'
        result = cursor.execute(sql).fetchall()
        cursor.close()
        cx.close()
        return result

    @staticmethod
    def remove_teammate(matchname, teamname, _id: str or int, position: str = None) -> str:
        """
        删除队员

        Args:
            matchname: 比赛名
            teamname: 队伍名
            _id: QQ号或者玩家名
            position: 玩家的位置

        Returns:

        """
        sql = f'select teamid,playerid from ptmview where teamname = "{teamname}" and matchname = "{matchname}"'
        if isinstance(_id, int):
            sql += f' and qq = {_id}'
        else:
            sql += f' and playername = "{_id}"'
        if position:
            sql += f' and position = "{position}"'
        cx = sqlite3.connect('./database/RichiMahjongMatchControl/match.sqlite')
        cursor = cx.cursor()
        info = cursor.execute(sql).fetchall()
        if len(info) == 0:
            return "删除失败,玩家未加入比赛或队伍"
        teamid, playerid = info[0]
        sql = f"update teamplayers set enable = 0 where teamid = {teamid} and playerid = {playerid}"
        if position:
            sql += f' and position = "{position}"'
        cursor.execute(sql)
        cx.commit()
        cursor.close()
        cx.close()
        return "删除成功"

    @staticmethod
    def create_team(matchname, teamname, description=None, leader=None):
        """
        创建队伍

        Args:
            matchname: 比赛名
            teamname: 队伍名
            description: 队伍描述
            leader: 队长QQ

        Returns:

        """
        cx = sqlite3.connect('./database/RichiMahjongMatchControl/match.sqlite')
        cursor = cx.cursor()
        matchid = cursor.execute(f"select id from teamcompetition where name = '{matchname}'").fetchall()
        if len(matchid) == 0:
            return "比赛不存在"
        else:
            matchid = matchid[0][0]
        team = cursor.execute(f"select id from teams where name = '{teamname}' and matchid = {matchid}").fetchall()
        if len(team) > 0:
            return "队伍已存在"
        field = 'name,matchid'
        values = f"'{teamname}',{matchid}"
        if description:
            field += ',description'
            values += f",'{description}'"
        if leader:
            field += ',leader'
            values += f",'{leader}'"
        sql = f"insert into teams({field}) values({values})"
        cursor.execute(sql)
        cx.commit()
        cursor.close()
        cx.close()
        return "队伍创建成功"
