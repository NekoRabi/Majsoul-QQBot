"""
:Author:  NekoRabi
:Create:  2022/8/16 16:14
:Update: /
:Describe: 消息链构造工具
:Version: 0.0.1
"""

import random
from mirai import MessageChain, At, Plain, AtAll, Image
from core import load_replydata

replydata = load_replydata()
enable_countenance = False  # 表情是否启用
if len(replydata.get('img')) > 0:
    enable_countenance = True

__all__ = ['messagechain_builder']


def messagechain_builder(reply_choices: list = None, text: str = None, imgpath: str = None, rndimg=False,
                         imgurl: str = None, imgbase64=None, at: int = None, atall=False) -> MessageChain:
    """
    通过给定参数来快速构造一个合法消息链

    Args:
        reply_choices: 一个全部是 str 的 list, 会随机从中抽取一个str
        text: 普通的字符串
        imgpath: 从本地路径发送图片
        rndimg: 随机发送一张表情包 ( 如果config中给了表情包路径才有用 )
        imgurl: 从网络url获取一张图片并发送,有可能超时或者tx不让发
        imgbase64: 将图片进行base64化的后的值
        at: At对象的QQ号
        atall: 是否At全体成员 . 请注意，每个账号的At全体成员的次数每天是有限的，并且是所有群共享的次数

    Returns:一个合法消息链

    """
    msgchain = []
    if at:
        msgchain.append(At(at))
        msgchain.append(Plain(" "))
    elif atall:
        msgchain.append(AtAll())
        msgchain.append(Plain(" "))
    if reply_choices:
        msgchain.append(Plain(random.choice(reply_choices)))
    elif text:
        msgchain.append(Plain(text))
    if reply_choices or text:
        msgchain.append(Plain(' '))
    if rndimg:
        if enable_countenance:
            msgchain.append(Plain("\n"))
            msgchain.append(
                Image(path=f"./data/reply/img/{replydata['replyimgpath']}/{random.choice(replydata['img'])}"))
    if imgpath:
        if reply_choices or text:
            msgchain.append(Plain("\n"))
        msgchain.append(
            Image(path=f"{imgpath}"))
    if imgbase64:
        if reply_choices or text:
            msgchain.append(Plain("\n"))
        msgchain.append(Image(base64=imgbase64))
    if imgurl:
        if reply_choices or text:
            msgchain.append(Plain("\n"))
        msgchain.append(Image(url=imgurl))
    return MessageChain(msgchain)
