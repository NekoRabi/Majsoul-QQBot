"""
:Author:  NekoRabi
:Create:  2022/8/16 17:44
:Update: /
:Describe: 机器人管理员控制器
:Version: 0.0.1
"""

import re

from mirai import FriendMessage, Plain, GroupMessage

from core import bot, master, commandpre, commands_map, config, admin
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import sendMsgChain
from utils.bufferpool import cmdbuffer, groupcommand
from utils.cfg_loader import w_cfg_to_file

_whitelist = config['whitelist']

_black_list = dict(user=config['blacklist'], group=config['mutegrouplist'])

__all__ = ['addblacklist', 'addwhitelist', 'addadmin', 'deladmin', 'delblacklist', 'getbotinfo', 'getsyslog',
           'tell_to_master']


@bot.on(FriendMessage)
async def addadmin(event: FriendMessage):
    if event.sender.id == master:
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(
            fr"^{commandpre}{commands_map['sys']['addadmin']}", msg.strip())
        if m:
            qqid = int(m.group(1))
            if qqid not in admin:
                admin.append(qqid)
                w_cfg_to_file(content=config, path=r'./config/config.yml')
                await sendMsgChain(event=event, msg=f"已将 {m.group(1)} 添加为机器人管理员")
            else:
                await sendMsgChain(event=event, msg=f"{m.group(1)} 已经是管理员了")

    else:
        await sendMsgChain(event=event, msg=messagechain_builder(text="抱歉,您无权这么做哦", rndimg=True))

    return


@bot.on(FriendMessage)
async def deladmin(event: FriendMessage):
    if event.sender.id == master:
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(
            fr"^{commandpre}{commands_map['sys']['deladmin']}", msg.strip())
        if m:
            qqid = int(m.group(1))
            if qqid in admin:
                admin.remove(qqid)
                w_cfg_to_file(content=config, path=r'./config/config.yml')
                return await sendMsgChain(event=event, msg=f"已将 {m.group(1)} 从机器人管理员中移出")
            else:
                return await sendMsgChain(event=event, msg=f"{m.group(1)} 不是再管理员了")
    else:
        await bot.send(event, messagechain_builder(text="抱歉,您无权这么做哦", rndimg=True))
    return


@bot.on(FriendMessage)
async def getbotinfo(event: FriendMessage):
    """获取bot信息"""
    msg = "".join(map(str, event.message_chain[Plain]))
    userid = event.sender.id
    m = re.match(fr"^{commandpre}{commands_map['sys']['getbotinfo']}", msg.strip())
    if m:
        if userid in admin:
            return await bot.send(event,
                                  f"机器人设置:{config}\n白名单用户:{_whitelist}\n黑名单用户:{_black_list['user']}\n屏蔽群组:{_black_list['group']}")


@bot.on(GroupMessage)
async def addwhitelist(event: GroupMessage):
    """添加白名单,目前没用"""
    msg = "".join(map(str, event.message_chain[Plain]))
    userid = event.sender.id
    m = re.match(fr"^{commandpre}{commands_map['sys']['addwhitelist']}", msg.strip())
    if m:
        if userid in admin and userid not in _whitelist:

            _whitelist.append(int(m.group(1)))
            w_cfg_to_file(content=config, path=r'./config/config.yml')
            print(m)
            return await bot.send(event, "添加成功")
        else:
            return await bot.send(event, "添加失败,用户已存在")


@bot.on(FriendMessage)
async def addblacklist(event: FriendMessage):
    """添加黑名单,目前没用"""
    msg = "".join(map(str, event.message_chain[Plain]))
    userid = event.sender.id
    m = re.match(fr"^{commandpre}{commands_map['sys']['addblacklist']}", msg.strip())
    if m:
        if userid in admin:
            if int(m.group(1)) in admin:
                return await bot.send(event, "请不要将管理员加入黑名单")
            _black_list['user'].append(int(m.group(1)))

            w_cfg_to_file(content=config, path=r'./config/config.yml')
            print(m)
            return await bot.send(event, "添加成功")
        else:
            return await bot.send(event, "添加失败,用户已存在")


@bot.on(FriendMessage)
async def delblacklist(event: FriendMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    userid = event.sender.id
    m = re.match(fr"^{commandpre}{commands_map['sys']['delblacklist']}", msg.strip())
    if m:
        if userid in admin:
            delperson = int(m.group(1))
            if delperson in _black_list['user']:
                _black_list['user'].remove(delperson)

                w_cfg_to_file(content=config, path=r'./config/config.yml')
                return await bot.send(event, "删除成功")
            else:
                return await bot.send(event, "删除失败,用户不存在")


@bot.on(FriendMessage)
async def getsyslog(event: FriendMessage):
    if event.sender.id in admin:
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(
            fr"^{commandpre}{commands_map['sys']['log']}", msg.strip())
        if m:
            return await bot.send(event, "日志功能开发中")


@bot.on(GroupMessage or FriendMessage)
async def tell_to_master(event: FriendMessage or GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(
        fr"^{commandpre}{commands_map['sys']['tell_master']}", msg.strip())
    qqid = event.sender.id
    if m:
        if qqid in _black_list:
            return await bot.send(event, messagechain_builder(text='你已被列入黑名单,禁止使用该功能'))
        if master != 0:
            if event is GroupMessage:
                if not cmdbuffer.updategroupcache(groupcommand(event.group.id, event.sender.id, 'tell_master')):
                    return bot.send(event, messagechain_builder(text="该功能已进入CD", at=event.sender.id))
            message = m.group(1)
            await bot.send_friend_message(master, messagechain_builder(text=f'qq为{qqid}的人说:{message}'))
            await bot.send(event, messagechain_builder(text='已转告主人'))
