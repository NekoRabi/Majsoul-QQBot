"""
:Author:  NekoRabi
:Create:  2022/8/18 2:19
:Update: /
:Describe: 获取机器人帮助，或者说是呼出指令面板
:Version: 0.0.1
"""

import re
from mirai import MessageEvent, Plain
from core import bot, commandpre, commands_map, config
from utils.MessageChainBuilder import messagechain_builder

_settings = config.get('settings')

__all__ = ['getsyshelp', 'getprojectlink']


@bot.on(MessageEvent)
async def getsyshelp(event: MessageEvent):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(
        fr"^{commandpre}{commands_map['sys']['help']}", msg.strip())
    if m and _settings['help']:
        # if not cmdbuffer.updategroupcache(groupcommand(event.group.id, event.sender.id, 'help')):
        #     return bot.send(event, await messagechain_builder()(text="帮助文档刚刚才发过哦~", rndimg=True, at=event.sender.id))
        return await bot.send(event, await messagechain_builder(imgpath="./images/grouphelp.png"))


@bot.on(MessageEvent)
async def getprojectlink(event: MessageEvent):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}项目地址\s*$", msg.strip())
    if m:
        return await bot.send(event, await messagechain_builder(text="Github : https://github.com/NekoRabi/Majsoul-QQBot\n"
                                                               "如果觉得好可以点个star⭐"))

        # 与机器人互动
