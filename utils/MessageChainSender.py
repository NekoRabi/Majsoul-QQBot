"""
:Author:  NekoRabi
:Create:  2022/8/16 16:15
:Update: /
:Describe: 消息链发送工具
:Version: 0.0.1
"""


from typing import Union

from mirai import MessageChain, MessageEvent
from mirai.models import MessageComponent

from core import bot, bot_cfg
from utils.MessageChainBuilder import messagechain_builder

__all__ = ['sendMsgChain']

async def sendMsgChain(msg: Union[MessageChain, str, MessageComponent], event: MessageEvent = None,
                       grouptarget: int = None, friendtarget: int = None, errortext: str = None) -> int:
    res = 0
    if msg is not MessageChain:
        msg = MessageChain(msg)
    errtext = "消息发送失败"
    imgSendErrText = f"图片发送失败,这肯定不是{bot_cfg.get('nickname')}的问题!"
    if errortext:
        errtext = errortext
        imgSendErrText = errortext
    onlyImg = False
    msgComponentTypeList = []

    for component in msg:
        msgComponentTypeList.append(component.type)
    if msgComponentTypeList == ['Image']:
        onlyImg = True
    if event:
        res = await bot.send(event, msg)
        if res == -1 and not onlyImg:
            # if Image in msg and not onlyImg :
            #     msg[Image] = None
            await bot.send(event, errtext)

    elif grouptarget:
        res = await bot.send_group_message(grouptarget, msg)
        if res == -1 and not onlyImg:
            await bot.send_group_message(grouptarget, errtext)
        # errtext += f'消息类型:GroupMessageEvent,消息目标:{grouptarget}'
    elif friendtarget:
        res = await bot.send_friend_message(friendtarget, msg)
        if res == -1 and not onlyImg:
            await bot.send_group_message(friendtarget, errtext)
        # errtext += f'消息类型:FriendMessageEvent,消息目标:{friendtarget}'
    if res == -1 and onlyImg:
        if grouptarget:
            await bot.send_group_message(grouptarget, messagechain_builder(text=imgSendErrText, rndimg=True))
        elif event:
            await bot.send(event, messagechain_builder(text=imgSendErrText, rndimg=True))
        elif friendtarget:
            await bot.send_friend_message(friendtarget, messagechain_builder(text=imgSendErrText, rndimg=True))

    return res