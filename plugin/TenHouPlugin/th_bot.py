"""
:Author:  NekoRabi
:Create:  2022/9/5 16:45
:Update: /
:Describe: 天凤与机器人交互组件
:Version: 0.0.1
"""
import datetime
import re

from mirai import GroupMessage, Plain

from core import bot, commandpre, commands_map, scheduler
from plugin.TenHouPlugin.TenHou import tenhou
from utils.cfg_loader import read_file

__all__ = ['ranktenhouplayer', 'asyth_all', 'addtenhouwatch', 'deltenhouwatcher', 'cleartenhouwatcher',
           'gettenhouwatcher']

from utils import text_to_image

from utils.MessageChainBuilder import messagechain_builder

from utils.MessageChainSender import messagechain_sender

from utils.bufferpool import *
from utils.get_groupmember_authority import is_having_admin_permission

_cfg = read_file(r'./config/TenHouPlugin/config.yml')


@bot.on(GroupMessage)
async def ranktenhouplayer(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{commands_map['tenhou']['thpt']}", msg.strip())
    if m:
        if not cmdbuffer.updategroupcache(GroupCommand(event.group.id, event.sender.id, 'thpt')):
            return messagechain_sender(event=event,
                                       msg=messagechain_builder(text="你查的太频繁了,休息一下好不好", rndimg=True, at=event.sender.id))
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
        await messagechain_sender(messagechain_builder(imgbase64=result['img64']), event=event, errortext=result['msg'])
        # await bot.send(event, tenhou.getthpt(m.group(2), reset))


@bot.on(GroupMessage)
async def addtenhouwatch(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{commands_map['tenhou']['addwatch']}", msg.strip())
    if m:
        if is_having_admin_permission(event):
            await messagechain_sender(event=event,
                                      msg=messagechain_builder(text=tenhou.addthwatch(m.group(2), event.group.id)))
        else:
            await messagechain_sender(event=event, msg=messagechain_builder(text='抱歉，此权限需要管理员', at=event.sender.id))


@bot.on(GroupMessage)
async def deltenhouwatcher(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{commands_map['tenhou']['delwatch']}", msg.strip())
    if m:
        if is_having_admin_permission(event):
            await bot.send(event,
                           tenhou.removethwatch(playername=m.group(2), groupid=event.group.id))
        else:
            await bot.send(event, messagechain_builder(at=event.sender.id, text=" 抱歉，只有管理员才能这么做哦"))


@bot.on(GroupMessage)
async def cleartenhouwatcher(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{commands_map['tenhou']['clearwatch']}", msg.strip())
    if m:
        if is_having_admin_permission(event):
            await bot.send(event, tenhou.clearthwatch(groupid=event.group.id))
        else:
            await bot.send(event, messagechain_builder(at=event.sender.id, text=" 抱歉，只有管理员才能这么做哦"))


@bot.on(GroupMessage)
async def gettenhouwatcher(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    # 匹配指令
    m = re.match(fr"^{commandpre}{commands_map['tenhou']['getwatch']}", msg.strip())
    if m:
        await bot.send(event, tenhou.getthwatch(event.group.id))


# 添加昵称
# @bot.on(GroupMessage)
# async def thaddtag(event: GroupMessage):
#     msg = "".join(map(str, event.message_chain[Plain]))
#     m = re.match(fr"^{commandpre}{commands_map['tenhou']['tagon']}", msg.strip())
#     if m:
#         if not m.group(3):
#             return await sendMsgChain(event=event, msg=messagechain_builder(text='请输入你要添加tag哦'))
#         if is_havingadmin(event):
#             await bot.send(event,
#                            tenhou.tagonplayer(playername=m.group(2), tagname=m.group(3), userid=event.sender.id,
#                                                groupid=event.group.id))
#         else:
#             await sendMsgChain(event=event, msg=messagechain_builder(at=event.sender.id, text='抱歉，只有管理员才能这么做'))
#
#
#
# # 删除昵称
# @bot.on(GroupMessage)
# async def thdeltag(event: GroupMessage):
#     msg = "".join(map(str, event.message_chain[Plain]))
#     m = re.match(fr"^{commandpre}{commands_map['tenhou']['tagoff']}", msg.strip())
#     if m:
#         if is_havingadmin(event):
#             tagnames = None
#             if m.group(3):
#                 tagnames = m.group(3)
#             await bot.send(event, tenhou.tagoffplayer(playername=m.group(2), groupid=event.group.id,
#                                                        userid=event.sender.id, tagname=tagnames))
#         else:
#             await bot.send(event, messagechain_builder(at=event.sender.id, text='抱歉，只有管理员才能这么做'))
#
#
# # 昵称操作
# @bot.on(GroupMessage)
# async def thtagoperate(event: GroupMessage):
#     msg = "".join(map(str, event.message_chain[Plain]))
#     m = re.match(fr"^{commandpre}{commands_map['tenhou']['tagopeartion']}", msg.strip())
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
#             await sendMsgChain(messagechain_builder(text=result), event)
#
#
# # 获取所有tag
#
# @bot.on(GroupMessage)
# async def thlisttag(event: GroupMessage):
#     msg = "".join(map(str, event.message_chain[Plain]))
#     m = re.match(fr"^{commandpre}{commands_map['tenhou']['taglist']}", msg.strip())
#     if m:
#         target = m.group(2)
#         searchtype = 'playername'
#         if target:
#             if target.startswith('tag=') or target.startswith('tagname='):
#                 target = target.split('=', 2)[1]
#                 searchtype = 'tagname'
#         await sendMsgChain(event=event, msg=messagechain_builder(
#             text=tenhou.getalltags(event.group.id, target=target, searchtype=searchtype)))


async def asyth_all():
    print("开始查询天凤信息")
    result = await tenhou.asythquery()
    # print(result)
    for msgobj in result:
        for group in msgobj['groups']:
            b64 = text_to_image(text=msgobj['msg'], needtobase64=True)
            # await bot.send_group_message(group, msgobj['msg'])
            await messagechain_sender(grouptarget=group, msg=messagechain_builder(imgbase64=b64))
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
