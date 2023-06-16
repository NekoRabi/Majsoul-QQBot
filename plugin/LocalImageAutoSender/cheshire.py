"""
:Author:  NekoRabi
:Create:  2023/6/16 1:59
:Update: /
:Describe: 从本地发生柴郡图
:Version: 0.0.1
"""
import os
import random
import re

from mirai import GroupMessage, Plain

from core import bot, config
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender
from utils.cfg_loader import read_file

__all__ = ['send_chai_jun']

_setting = config['settings']
_silencegroup = config['silencegroup']
_blacklist = config['blacklist']

longtufiles = os.listdir('./plugin/LocalImageAutoSender/Image/Cheshire/')

_enable = read_file("./config/LocalImageAutoSender/config.yml").get("cheshireimg", True)


@bot.on(GroupMessage)
async def send_chai_jun(event: GroupMessage):
    """
    发送柴郡
    """
    if not _enable:
        return
    if not _setting['silence']:
        if event.group.id in _silencegroup:
            return

        if event.sender.id in _blacklist:
            return
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(r'^来?[张点份]?(柴郡|cheshire)[图]?', msg.strip())
        if m:
            return await messagechain_sender(event=event,
                                             msg=await messagechain_builder(
                                                 imgpath=f'./plugin/LocalImageAutoSender/Image/Cheshire/{random.choice(longtufiles)}'))
