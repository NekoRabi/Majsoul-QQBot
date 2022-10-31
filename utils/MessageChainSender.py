"""
:Author:  NekoRabi
:Create:  2022/8/16 16:15
:Update: /
:Describe: 消息链发送工具
:Version: 0.0.1
"""
import logging
import time
from typing import Union

import mirai.exceptions
from mirai import MessageChain, MessageEvent
from mirai.models import MessageComponent

from core import bot, bot_cfg, master
from utils.MessageChainBuilder import messagechain_builder

__all__ = ['messagechain_sender']

_last_error_message = dict(groupmessage=dict(), friendmessage=dict(), other=dict())


async def messagechain_sender(msg: Union[MessageChain, str, MessageComponent], event: MessageEvent = None,
                              grouptarget: int = None, friendtarget: int = None, errortext: str = None) -> int:
    """
    消息链发送工具\n
    event,grouptarget,friendtarget三者有一个就行

    Args:
        msg: 消息,可以是字符串、消息组件、消息链
        event: 群聊事件 或 私聊事件
        grouptarget: 发送群消息的群号
        friendtarget: 发送好友消息的QQ号
        errortext: 发送失败时,尝试发送错误提示文本

    Returns:
        消息ID , 发送失败时返回 -1
    """
    res = 0
    if not isinstance(msg, MessageChain):
        if not isinstance(msg, list):
            msg = [msg]
        msg = MessageChain(msg)
    errtext = "消息发送失败"
    imgSendErrText = f"图片发送失败,这肯定不是{bot_cfg.get('nickname')}的问题!"
    if errortext:
        errtext = errortext
        imgSendErrText = errortext
    onlyImg = False
    msgComponentTypeList = []
    target = None
    for component in msg:
        msgComponentTypeList.append(component.type)
    if msgComponentTypeList == ['Image']:
        onlyImg = True
    try:
        if event:
            res = await bot.send(event, msg)
            target = event
            if res == -1 and not onlyImg:
                # if Image in msg and not onlyImg :
                #     msg[Image] = None
                await bot.send(event, errtext)
        elif grouptarget:
            target = grouptarget
            res = await bot.send_group_message(grouptarget, msg)
            if res == -1 and not onlyImg:
                await bot.send_group_message(grouptarget, errtext)
            # errtext += f'消息类型:GroupMessageEvent,消息目标:{grouptarget}'
        elif friendtarget:
            target = friendtarget
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
    except mirai.exceptions.ApiError as _e:
        # 消息发送失败时，进行日志记录，并尝试告诉机器人主人，每次发送CD 3600 s
        nowtime = int(time.time())
        last_time = _last_error_message.get('groupmessage').get('time', 0)
        if _e.code == 20:
            if nowtime - last_time > 3600:
                _last_error_message['groupmessage'] = dict(time=nowtime, target=target, message=msg,
                                                           error='Bot被禁言')
                await bot.send_friend_message(master, f"在{target.group.id}群消息发送失败,疑似被禁言")
            print('Bot被禁言')
            logging.warning('Bot发送消息失败,Bot被禁言')
        else:
            if nowtime - last_time > 3600:
                _last_error_message['groupmessage'] = dict(time=nowtime, target=target, message=msg, error=_e)
                await bot.send_friend_message(master, f"群消息发送失败,可能被群消息风控")
            print(f'Bot发送消息失败,MiraI错误码{_e}')
            logging.error(f'Bot发送消息失败,Mirai错误码{_e}')
        res = -1
    return res
