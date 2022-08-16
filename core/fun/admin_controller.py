"""
:Author:  NekoRabi
:Create:  2022/8/16 17:44
:Update: /
:Describe: 机器人管理员控制器
:Version: 0.0.1
"""


import re

from mirai import FriendMessage, Plain

from core import bot, master, commandpre, commands_map, config, admin
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import sendMsgChain
from utils.cfg_loader import w_cfg_to_file


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
