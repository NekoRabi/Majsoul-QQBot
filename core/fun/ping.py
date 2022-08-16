"""
:Author:  NekoRabi
:Create:  2022/8/16 20:32
:Update: /
:Describe: 一些私聊消息发送
:Version: 0.0.1
"""
import re

from mirai import FriendMessage, Plain
from core import bot, commands_map, commandpre, admin
from utils.MessageChainSender import sendMsgChain

__all__ = ['ping', 'sayhello']


@bot.on(FriendMessage)
async def ping(event: FriendMessage):
    if event.sender.id in admin:
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(
            fr"^{commandpre}{commands_map['sys']['ping']}", msg.strip())
        if m:
            await bot.send(event, "pong!")
    return


@bot.on(FriendMessage)
async def sayhello(event: FriendMessage):
    if str(event.message_chain) == '你好':
        return sendMsgChain(event=event, msg='Hello, World!')
