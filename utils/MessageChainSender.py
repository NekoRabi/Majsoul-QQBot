"""
:Author:  NekoRabi
:Create:  2022/8/16 16:15
:Update: /
:Describe: 消息链发送工具
:Version: 0.0.2
"""
import time
import traceback
from typing import Union

import mirai.exceptions
from mirai import MessageChain, MessageEvent, GroupMessage, FriendMessage
from mirai.models import MessageComponent
from mirai.models.api import MessageResponse

from core import bot, bot_cfg, master
from utils import root_logger
from utils.MessageChainBuilder import messagechain_builder

__all__ = ['messagechain_sender']

_last_error_message = dict(groupmessage=dict(), friendmessage=dict(), other=dict())

# _mahversion = await bot.about()  # 获取MAH的版本
# _mahversion = _mahversion.data.get('version')[:3]  # MAH的版本我只取前三位，如'2.4','2.9'


#
# class MessageChainSender:
#     target: str
#     targetId: int
#     messageChain: MessageChain
#     recall: int
#     errorText: str
#
#     def __init__(self):
#         self.target = ''

async def messagechain_sender(msg: Union[MessageChain, str, MessageComponent], event: MessageEvent = None,
                              grouptarget: int = None, friendtarget: int = None, errortext: str = None) -> int:
    """
    消息链发送工具\n
    event,grouptarget,friendtarget三者有一个就行\n

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
            if isinstance(event, GroupMessage):
                grouptarget = event.group.id
            elif isinstance(event, FriendMessage):
                friendtarget = event.sender.id
            # res = await bot.send(event, msg)
            # target = event
            # if res == -1 and not onlyImg:
            #     # if Image in msg and not onlyImg :
            #     #     msg[Image] = None
            #     await bot.send(event, errtext)
        if grouptarget:
            target = grouptarget
            if bot.get_group(target):
                res = await bot.send_group_message(grouptarget, msg)
                # if isinstance(res, MessageResponse):
                #     res = res.message_id
                if res == -1 and not onlyImg:
                    await bot.send_group_message(grouptarget, errtext)
                # errtext += f'消息类型:GroupMessageEvent,消息目标:{grouptarget}'
            else:
                print(f"尝试向群聊{target}发送消息失败, bot不在群聊 {target} 中")
                root_logger.error(f"尝试向群聊{target}发送消息失败, bot不在群聊 {target} 中")
        elif friendtarget:
            target = friendtarget
            if bot.get_friend(target):
                res = await bot.send_friend_message(friendtarget, msg)
                # if isinstance(res, MessageResponse):
                #     res = res.message_id
                if res == -1 and not onlyImg:
                    await bot.send_group_message(friendtarget, errtext)
                # errtext += f'消息类型:FriendMessageEvent,消息目标:{friendtarget}'
            else:
                print(f"尝试向好友{target}发送消息失败, {target} 不是bot的好友")
                root_logger.error(f"尝试向好友{target}发送消息失败, {target} 不是bot的好友")
        if res == -1 and onlyImg:
            if grouptarget:
                await bot.send_group_message(grouptarget, await messagechain_builder(text=imgSendErrText, rndimg=True))
            elif event:
                await bot.send(event, await messagechain_builder(text=imgSendErrText, rndimg=True))
            elif friendtarget:
                await bot.send_friend_message(friendtarget,
                                              await messagechain_builder(text=imgSendErrText, rndimg=True))
    except mirai.exceptions.ApiError as _e:
        # 消息发送失败时，进行日志记录，并尝试告诉机器人主人，每次发送CD 3600 s
        nowtime = int(time.time())
        last_time = _last_error_message.get('groupmessage').get('time', 0)
        if _e.code == 20:
            if nowtime - last_time > 3600:
                _last_error_message['groupmessage'] = dict(time=nowtime, target=target, message=msg,
                                                           error='Bot被禁言')
                await bot.send_friend_message(master, f"向 {target} 发送消息失败,可能被禁言")
            print(f"向 {target} 发送消息失败,可能被禁言")
            root_logger.error(f"向 {target} 发送消息失败,可能被禁言")
        elif _e.code == 6:
            if nowtime - last_time > 3600:
                await bot.send_friend_message(master, f"向 {target} 发送消息失败,指定图片不存在")
            print(f"向 {target} 发送消息失败,指定图片不存在")
            root_logger.error(f"向 {target} 发送消息失败,指定图片不存在\n{_e.args}")
        else:
            if nowtime - last_time > 3600:
                _last_error_message['groupmessage'] = dict(time=nowtime, target=target, message=msg, error=_e)
                await bot.send_friend_message(master, f"群消息发送失败,可能被群消息风控\n{_e}")
            print(f'Bot发送消息失败,MiraI错误码{_e}')
            root_logger.error(f'Bot发送消息失败,Mirai错误码{_e}')
        res = -1
    except Exception as _e:
        traceback.print_exc()
        root_logger.error(f'出现未知错误:{_e}')
        nowtime = int(time.time())
        last_time = _last_error_message.get('groupmessage').get('time', 0)
        if nowtime - last_time > 3600:
            _last_error_message['groupmessage'] = dict(time=nowtime, target=target, message=msg, error=_e)
        await bot.send_friend_message(master, f"发生未知错误消息发送失败,请到后台查看错误!")
    return res
