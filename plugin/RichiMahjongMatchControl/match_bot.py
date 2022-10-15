"""
:Author:  NekoRabi
:Create:  2022/10/15 21:19
:Update: /
:Describe: 比赛机器人
:Version: 0.0.1
"""

import re

from mirai import GroupMessage, Plain, FriendMessage
from mirai.bot import Startup

from core import bot, commandpre, scheduler
from plugin.RichiMahjongMatchControl.match_core import MatchOperator
from utils import text_to_image
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender
from utils.cfg_loader import write_file, read_file
from utils.get_groupmember_authority import is_having_admin_permission

__all__ = ['create_match', 'join_match', 'get_teammembers', 'remove_teammate']


@bot.on(GroupMessage)
async def create_match(event: GroupMessage):
    """创建比赛"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}创建比赛\s*(\w+)\s*(\d{{4}}-\d{{2}}-\d{{2}})\s*(\w+)?$", msg.strip())
    if m:
        if not is_having_admin_permission(event):
            return await bot.send(event, await messagechain_builder(text="仅管理员可以创建新比赛", at=event.sender.id))
        if m.group(2):
            description = m.group(3)
        else:
            description = ""
        res = MatchOperator.register_match(matchname=m.group(1), ddl=m.group(2), description=description)
        await bot.send(event, await messagechain_builder(text=res))


@bot.on(GroupMessage)
async def join_match(event: GroupMessage):
    """加入比赛"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}加入比赛\s*(\w+)\s*(\w+)?\s*(\w+)?\s*(\w+)?$", msg.strip())
    if m:
        matchname = m.group(1)
        teamname = m.group(2)
        position = m.group(3)
        playername = m.group(4)
        if not m.group(2):
            teamname = matchname
        res = MatchOperator.join_match(matchname=m.group(1), qqid=event.sender.id, teamname=teamname,
                                       position=position, playername=playername)
        await bot.send(event, await messagechain_builder(text=res))


@bot.on(GroupMessage)
async def get_teammembers(event: GroupMessage):
    """获取队伍成员"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}查询队伍\s*(\w+)\s*(\w+)?$", msg.strip())
    if m:
        matchname = m.group(1)
        teamname = m.group(2)
        msg = f"{matchname}的{teamname}参赛名单:\n"
        if not m.group(2):
            teamname = matchname
            msg = f"{matchname}的参赛名单:\n"
        res = MatchOperator.get_teammembers(matchname=m.group(1), teamname=teamname)
        for item in res:
            qq, playername, position = item
            if position is None:
                position = ''
            else:
                position += ' : '
            if playername == '':
                try:
                    memberinfo = await bot.get_group_member(group=event.group.id, id_=qq)
                    playername = memberinfo.member_name
                    msg += f"{position}{playername}\n"
                except Exception:
                    msg += f"{position}{qq}\n"
            else:
                msg += f"{position}{playername}\n"
        await bot.send(event, await messagechain_builder(text=msg[:-1]))


@bot.on(GroupMessage)
async def remove_teammate(event: GroupMessage):
    """删除队员"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}移除队员\s*(\w+)\s*(\w+)?\s*(%playername%=)?\s*(\w+)$", msg.strip())
    if m:
        matchname = m.group(1)
        teamname = m.group(2)
        if not teamname:
            teamname = matchname
        id = m.group(4)
        if not m.group(3):
            try:
                id = int(id)
            except ValueError:
                msg = "请输入正确的qq,如需输入玩家名,请在玩家名前加上'%playername%='"
                return await bot.send(event, await messagechain_builder(text=msg))
        res = MatchOperator.remove_teammate(matchname=matchname, teamname=teamname, id=id)
        return await bot.send(event, await messagechain_builder(text=res))
