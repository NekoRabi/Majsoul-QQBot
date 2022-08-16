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
enable_countenance = False # 表情是否启用
if len(replydata.get('img')) > 0:
    enable_countenance = True

__all__ = ['messagechain_builder']

def messagechain_builder(reply_choices: list = None, text: str = None, imgpath: str = None, rndimg=False,
                         imgurl: str = None, imgbase64=None,
                         at: int = None, atall=False) -> MessageChain:
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
