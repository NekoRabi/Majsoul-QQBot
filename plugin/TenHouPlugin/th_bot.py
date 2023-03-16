"""
:Author:  NekoRabi
:Create:  2022/9/5 16:45
:Update: /
:Describe: 天凤与机器人交互组件
:Version: 0.0.3
"""
import asyncio
import datetime
import re

from mirai import GroupMessage, Plain, FriendMessage

from core import bot, commandpre, scheduler, add_help
from plugin.TenHouPlugin.TenHou import tenhou
from utils.cfg_loader import read_file
from utils import text_to_image
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender
from utils.bufferpool import *
from utils.get_groupmember_authority import is_having_admin_permission

add_help('group', [
    "thpt / 天凤pt / 天凤分数 [玩家名] : 查询玩家的天凤pt \n",
    "thyb / 天凤月报 [玩家名] [3/4] [yyyy-mm] : 查询天凤月报\n",
    "thadd / 天凤添加关注 [玩家名] :将一个玩家添加指天凤的自动查询，有新对局会广播\n",
    "thdel / 天凤删除关注 [玩家名] :将一个玩家从天凤自动查询中移除，不再自动广播对局记录\n",
    "thgetwatch / 天凤获取本群关注 :获取本群所有的天凤关注的玩家\n",
    "牌理[114514p1919m810s4z] : 天凤一般型牌理分析\n"
])
__all__ = ['ranktenhouplayer', 'asyth_all', 'addtenhouwatch', 'deltenhouwatcher', 'cleartenhouwatcher',
           'gettenhouwatcher', 'thmonthreport', 'thgroupauthentication', 'friend_cleartenhouwatcher']

_cfg = read_file(r'./config/TenHouPlugin/config.yml')

_cmd = read_file(r'./config/TenHouPlugin/command.yml')


@bot.on(GroupMessage)
async def ranktenhouplayer(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_cmd.get('thpt')}", msg.strip())
    if m:
        if not cmdbuffer.updategroupcache(GroupCommand(event.group.id, event.sender.id, 'thpt')):
            return messagechain_sender(event=event,
                                       msg=await messagechain_builder(text="你查的太频繁了,休息一下好不好", rndimg=True,
                                                                      at=event.sender.id))
        reset = True
        if m.group(3):
            reset = m.group(3)
            if reset.lower().startswith('reset=') and len(reset) > 6:
                reset = reset[6:-1]
                if reset.lower() == 'true':
                    reset = True
                else:
                    reset = False
            else:
                reset = False
        result = await tenhou.getthpt(m.group(2), reset)
        await messagechain_sender(await messagechain_builder(imgbase64=result['img64']), event=event,
                                  errortext=result['msg'])
        # await bot.send(event, tenhou.getthpt(m.group(2), reset))


@bot.on(GroupMessage)
async def addtenhouwatch(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_cmd.get('addwatch')}", msg.strip())
    if m:
        if is_having_admin_permission(event):
            await messagechain_sender(event=event,
                                      msg=await messagechain_builder(
                                          text=tenhou.addthwatch(m.group(2), event.group.id,
                                                                 isadmin=is_having_admin_permission(event))))
        else:
            await messagechain_sender(event=event,
                                      msg=await messagechain_builder(text='抱歉，此权限需要管理员', at=event.sender.id))


@bot.on(GroupMessage)
async def deltenhouwatcher(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_cmd.get('delwatch')}", msg.strip())
    if m:
        if is_having_admin_permission(event):
            await bot.send(event,
                           tenhou.removethwatch(playername=m.group(2), groupid=event.group.id,
                                                isadmin=is_having_admin_permission(event)))
        else:
            await bot.send(event, await messagechain_builder(at=event.sender.id, text=" 抱歉，只有管理员才能这么做哦"))


@bot.on(GroupMessage)
async def cleartenhouwatcher(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_cmd.get('clearwatch')}", msg.strip())
    if m:
        if is_having_admin_permission(event):
            await bot.send(event, tenhou.clearthwatch(groupid=event.group.id))
        else:
            await bot.send(event, await messagechain_builder(at=event.sender.id, text=" 抱歉，只有管理员才能这么做哦"))


@bot.on(FriendMessage)
async def friend_cleartenhouwatcher(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}thclearwatch\s*(\d+)\s*$", msg.strip())
    if m:
        if is_having_admin_permission(event):
            if m.group(1):
                await bot.send(event, tenhou.clearthwatch(groupid=int(m.group(1))))
            else:
                await bot.send(event, "指令执行错误")


@bot.on(GroupMessage)
async def gettenhouwatcher(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    # 匹配指令
    m = re.match(fr"^{commandpre}{_cmd.get('getwatch')}", msg.strip())
    if m:
        await bot.send(event, tenhou.getthwatch(event.group.id))


@bot.on(GroupMessage)
async def thmonthreport(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_cmd.get('thyb')}", msg.strip())
    if m:
        if not cmdbuffer.updategroupcache(GroupCommand(event.group.id, event.sender.id, 'thpt')):
            return messagechain_sender(event=event,
                                       msg=await messagechain_builder(text="你查的太频繁了,休息一下好不好", rndimg=True,
                                                                      at=event.sender.id))
        searchtype = m.group(3)
        year = m.group(5)
        month = m.group(6)
        if searchtype:
            searchtype = int(searchtype)
        result = await tenhou.getthyb(m.group(2), searchtype, year, month)
        await messagechain_sender(await messagechain_builder(imgbase64=result['img64']), event=event,
                                  errortext=result['msg'])


@bot.on(GroupMessage)
async def thgroupauthentication(event: GroupMessage):
    """天凤群组权限控制"""
    msg = "".join(map(str, event.message_chain[Plain]))
    defaultcmd = r'thauthority\s*(\w+)\s*$'
    m = re.match(
        fr"^{commandpre}{_cmd.get('thauthority', defaultcmd)}", msg.strip())
    if m:
        if not is_having_admin_permission(event=event):
            return await messagechain_sender(event=event, msg=await messagechain_builder(text='抱歉, 只有管理员有权限这么做'))
        enable = m.group(1).lower()

        if enable in ['enable', 'true', 'open']:
            enable = True
        elif enable in ['disable', 'false', 'cross', 'close']:
            enable = False
        else:
            return await messagechain_sender(event=event, msg=await messagechain_builder(text='指令有误'))

        await messagechain_sender(event=event, msg=await tenhou.authentication_controller(event.group.id, enable))
    return


# 添加昵称
# @bot.on(GroupMessage)
# async def thaddtag(event: GroupMessage):
#     msg = "".join(map(str, event.message_chain[Plain]))
#     m = re.match(fr"^{commandpre}{_cmd.get('tagon')}", msg.strip())
#     if m:
#         if not m.group(3):
#             return await sendMsgChain(event=event, msg=await messagechain_builder(text='请输入你要添加tag哦'))
#         if is_havingadmin(event):
#             await bot.send(event,
#                            tenhou.tagonplayer(playername=m.group(2), tagname=m.group(3), userid=event.sender.id,
#                                                groupid=event.group.id))
#         else:
#             await sendMsgChain(event=event, msg=await messagechain_builder(at=event.sender.id, text='抱歉，只有管理员才能这么做'))
#
#
#
# # 删除昵称
# @bot.on(GroupMessage)
# async def thdeltag(event: GroupMessage):
#     msg = "".join(map(str, event.message_chain[Plain]))
#     m = re.match(fr"^{commandpre}{_cmd.get('tagoff')}", msg.strip())
#     if m:
#         if is_havingadmin(event):
#             tagnames = None
#             if m.group(3):
#                 tagnames = m.group(3)
#             await bot.send(event, tenhou.tagoffplayer(playername=m.group(2), groupid=event.group.id,
#                                                        userid=event.sender.id, tagname=tagnames))
#         else:
#             await bot.send(event, await messagechain_builder(at=event.sender.id, text='抱歉，只有管理员才能这么做'))
#
#
# # 昵称操作
# @bot.on(GroupMessage)
# async def thtagoperate(event: GroupMessage):
#     msg = "".join(map(str, event.message_chain[Plain]))
#     m = re.match(fr"^{commandpre}{_cmd.get('tagopeartion')}", msg.strip())
#     ope_type = 'add'
#     p1 = 'xyshu'
#     p2 = '帅哥'
#     if m:
#         if is_havingadmin(event):
#             if m.group(2):
#                 ope_type = m.group(2).lower()
#             print(ope_type)
#             if ope_type not in ['cut', 'copy']:
#                 return
#             if m.group(3):
#                 p1 = m.group(3)
#             if m.group(4):
#                 p2 = m.group(4)
#             # result = majsoul.tagonplayer(playername=p1, tagname=p2, userid=event.sender.id,
#             #                     groupid=event.group.id)
#             result = tenhou.tag_C_operation(event.group.id, p1, p2, ope_type)
#             await sendMsgChain(await messagechain_builder(text=result), event)
#
#
# # 获取所有tag
#
# @bot.on(GroupMessage)
# async def thlisttag(event: GroupMessage):
#     msg = "".join(map(str, event.message_chain[Plain]))
#     m = re.match(fr"^{commandpre}{_cmd.get('taglist')}", msg.strip())
#     if m:
#         target = m.group(2)
#         searchtype = 'playername'
#         if target:
#             if target.startswith('tag=') or target.startswith('tagname='):
#                 target = target.split('=', 2)[1]
#                 searchtype = 'tagname'
#         await sendMsgChain(event=event, msg=await messagechain_builder(
#             text=tenhou.getalltags(event.group.id, target=target, searchtype=searchtype)))


async def asyth_all():
    if not _cfg.get('silence_CLI', False):
        print("开始查询天凤信息")
    result = await tenhou.asythquery()
    # print(result)
    index = 0
    broadcast_type = _cfg.get('broadcast', 'img').lower()
    if broadcast_type in ['mix', 'mixed']:
        for msgobj in result:
            for group in msgobj['groups']:
                index += 1
                if index % 10 == 0:
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(0.005)
                b64 = text_to_image(text=msgobj['msg'], needtobase64=True)
                # await bot.send_group_message(group, msgobj['msg'])
                if msgobj.get('url', None):
                    await messagechain_sender(grouptarget=group,
                                              msg=await messagechain_builder(imgbase64=b64,
                                                                             text=f"https://tenhou.net/3/?wg={msgobj['url']}"))
                else:
                    await messagechain_sender(grouptarget=group, msg=await messagechain_builder(imgbase64=b64))
    elif broadcast_type in ['str', 'txt', 'text']:
        for msgobj in result:
            for group in msgobj['groups']:
                index += 1
                if index % 10 == 0:
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(0.005)
                await messagechain_sender(grouptarget=group, msg=await messagechain_builder(text=msgobj['msg']))
    else:
        for msgobj in result:
            for group in msgobj['groups']:
                index += 1
                if index % 10 == 0:
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(0.005)
                b64 = text_to_image(text=msgobj['msg'], needtobase64=True)
                # await bot.send_group_message(group, msgobj['msg'])
                await messagechain_sender(grouptarget=group, msg=await messagechain_builder(imgbase64=b64))

    if not _cfg.get('silence_CLI', False):
        print(
            f'天凤自动查询结束,当前时间:{datetime.datetime.now().hour}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}')
    return


if _cfg.get('autoquery', True):
    _searchfrequency = _cfg.get('searchfrequency', 6)
    if int(_searchfrequency) < 1:
        print('查询频率不能为0,将自动设置为6')
        _searchfrequency = 6
    scheduler.add_job(asyth_all, 'cron', hour='*', minute=f'0/{_searchfrequency}')
    print(f' |---已添加定时任务 "天凤自动查询",查询周期{_searchfrequency}分钟')
