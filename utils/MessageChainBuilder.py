"""
:Author:  NekoRabi
:Create:  2022/8/16 16:14
:Update: /
:Describe: 消息链构造工具
:Version: 0.0.1
"""

import random
from typing import Union

from mirai import MessageChain, At, Plain, AtAll, Image
from core import load_replydata

replydata = load_replydata()
enable_countenance = False  # 表情是否启用
if len(replydata.get('img')) > 0:
    enable_countenance = True

__all__ = ['messagechain_builder', 'MessageChainBuilder']


class MessageChainBuilder:
    """ 写一个类似 builder 的构造器提供给喜欢用builder模式的人 """
    replyChoices: list = []
    text: str = ''
    imgPath: list = []
    rndImg = False
    imgUrl: list = []
    imgBase64 = []
    at: list = []
    atAll = False

    def __init__(self):
        self._messageChain = []
        self.text = ''
        self.at = []
        self.rndImg = False
        self.imgPath = []
        self.imgUrl = []
        self.imgBase64 = []
        self.atAll = False

    def setReplyChoice(self, data):
        """设置一个 可迭代集合 ，从中随机选择一个作为回复"""
        self.replyChoices = data
        return self

    def addText(self, data: str):
        """增加回复字符串"""
        self.text += data
        return self

    def addAt(self, _id: Union[list, int]):
        """
        增加 at 的对象
        Args:
            _id:

        Returns:

        """
        if isinstance(_id, int):
            self.at.append(_id)
        elif isinstance(_id, list):
            self.at.extend(_id)
        return self

    def setAtAll(self, data=True):
        """
        设置是否 At全体成员
        Args:
            data: True or False

        Returns:

        """
        self.atAll = data
        return self

    def setRndImg(self, data=True):
        """
        是否使用随机表情回复

        Args:
            data:

        Returns:

        """
        self.rndImg = data
        return self

    def addImgPath(self, path: Union[str, list]):
        """添加本地图片地址"""
        if isinstance(path, str):
            self.imgPath.append(path)
        elif isinstance(path, list):
            self.imgPath.extend(path)
        return self

    def addImgUrl(self, url: Union[str, list]):
        """
        添加网络图片地址

        Args:
            url: 网络图片URL

        Returns:

        """
        if isinstance(url, str):
            self.imgPath.append(url)
        elif isinstance(url, list):
            self.imgPath.extend(url)
        return self

    def addImgBase64(self, imgbase64: Union[str, list]):
        """
        添加 base64化后的图片

        Args:
            imgbase64: base64化后的图片，可以是 list 或者 str

        Returns:

        """
        if isinstance(imgbase64, str):
            self.imgPath.append(imgbase64)
        elif isinstance(imgbase64, list):
            self.imgPath.extend(imgbase64)
        return self

    def getMessaheChain(self):
        return self._messageChain

    async def build(self) -> MessageChain:
        """ 构建消息链 """
        messageChain = []
        if self.atAll:
            messageChain.append(AtAll())
            messageChain.append("\n")
        if len(self.at) > 0:
            for _at in self.at:
                messageChain.append(At(_at))
            messageChain.append("\n")
        if len(self.replyChoices)>0:
            messageChain.append(random.choice(self.replyChoices))
        if len(self.text) > 0:
            messageChain.append(self.text)
        if len(self.imgBase64) > 0:
            for b64 in self.imgBase64:
                messageChain.append(Image(base64=b64))
        if len(self.imgPath) > 0:
            for path in self.imgPath:
                messageChain.append(await Image.from_local(filename=f"{path}"))
        if len(self.imgUrl) > 0:
            for url in self.imgUrl:
                messageChain.append(Image(url=url))
        if self.rndImg:
            if enable_countenance:
                self._messageChain.append(
                    await Image.from_local(
                        filename=f"./data/reply/img/{replydata['replyimgpath']}/{random.choice(replydata['img'])}"))
        if len(self._messageChain) > 0:
            return MessageChain(self._messageChain)
        else:
            raise ValueError("消息链为空")


async def messagechain_builder(reply_choices: list = None, text: str = None, imgpath: Union[str, list] = None,
                               rndimg=False,
                               imgurl: str = None, imgbase64=None, at: Union[list, int] = None,
                               atall=False) -> MessageChain:
    """
    通过给定参数来快速构造一个合法消息链

    Args:
        reply_choices: 一个全部是 str 的 list, 会随机从中抽取一个str
        text: 普通的字符串
        imgpath: 从本地路径发送图片
        rndimg: 随机发送一张表情包 ( 如果config中给了表情包路径才有用 )
        imgurl: 从网络url获取一张图片并发送,有可能超时或者tx不让发
        imgbase64: 将图片进行base64化的后的值
        at: At对象的QQ号或QQ号列表
        atall: 是否At全体成员 . 请注意，每个账号的At全体成员的次数每天是有限的，并且是所有群共享的次数

    Returns:一个合法消息链

    """
    msgchain = []
    if at:
        if type(at) == int:
            msgchain.append(At(at))
            msgchain.append(Plain(" "))
        else:
            for _at in at:
                msgchain.append(At(_at))
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
                await Image.from_local(
                    filename=f"./data/reply/img/{replydata['replyimgpath']}/{random.choice(replydata['img'])}"))
    if imgbase64:
        if reply_choices or text:
            msgchain.append(Plain("\n"))
        msgchain.append(Image(base64=imgbase64))
    if imgpath:
        if reply_choices or text:
            msgchain.append(Plain("\n"))
        if isinstance(imgpath, str):
            msgchain.append(
                await Image.from_local(filename=f"{imgpath}"))
        elif isinstance(imgpath, list):
            for path in imgpath:
                msgchain.append(
                    await Image.from_local(filename=f"{path}"))
    if imgurl:
        if reply_choices or text:
            msgchain.append(Plain("\n"))
        msgchain.append(Image(url=imgurl))
    return MessageChain(msgchain)
