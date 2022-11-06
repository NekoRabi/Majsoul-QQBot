import os
import random
import re

from mirai import GroupMessage, Plain

from core import bot, config
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender
from utils.cfg_loader import read_file

__all__ = ['dragon_img']

_setting = config['settings']
_silencegroup = config['silencegroup']
_blacklist = config['blacklist']

longtufiles = os.listdir('./plugin/LocalImageAutoSender/Image/Dragon/')

_enable = read_file("./config/LocalImageAutoSender/config.yml").get("dragonimg", True)


@bot.on(GroupMessage)
async def dragon_img(event: GroupMessage):
    """
    其他网站找来的龙图
    """
    if not _enable:
        return
    if not _setting['silence']:
        if event.group.id in _silencegroup:
            return

        if event.sender.id in _blacklist:
            return
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(r'^来?.?龙图', msg.strip())
        if m:
            return await messagechain_sender(event=event,
                                             msg=await messagechain_builder(
                                                 imgpath=f'./plugin/LocalImageAutoSender/Image/Dragon/{random.choice(longtufiles)}'))
