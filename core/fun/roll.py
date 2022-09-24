"""
:Author:  NekoRabi
:Create:  2022/9/24 19:38
:Update: /
:Describe: roll Roll ROLL !!!
:Version: 0.0.1
"""
import random
import re

from mirai import GroupMessage, FriendMessage, Plain

from core import bot, commandpre, commands_map
from utils.MessageChainBuilder import messagechain_builder


def _random_int_general(lower: int or str = None, upper: int or str = None, dn: int = None) -> int:
    """
    随机生成一个lower-upper之间的整数,支持Dn掷筛

    Args:
        lower: 下限
        upper: 上限

    Returns: 下限到上限之间的一个整数

    """
    if dn:
        return random.randint(1, dn)
    else:
        if lower is None:
            lower = 0
        if upper is None:
            upper = 0
        lower = int(lower)
        upper = int(upper)
        if lower > upper:
            _temp = lower
            lower = upper
            upper = _temp
        if upper == 0:
            upper = 100
        return random.randint(lower, upper)


def _random_item(items: list):
    """
    从list中随机返回一个元素
    Args:
        items: 一个list

    Returns: list的一个元素

    """
    return random.choice(items)


@bot.on(GroupMessage)
@bot.on(FriendMessage)
async def roll_item(event: GroupMessage or FriendMessage):
    """roll"""
    msg = "".join(map(str, event.message_chain[Plain]))
    roll_re = commands_map.get('sys', dict()).get('roll', r'roll\s*([\s\S]+)?')
    m = re.match(
        fr"^{commandpre}{roll_re}", msg.strip())
    if m:
        content = m.group(1)
        if content:
            content = content.strip()
            if len(content) > 0:
                m1 = re.match(r'^(\d+)$', content)
                if m1:
                    return await bot.send(event, messagechain_builder(text=f'{_random_int_general(upper=m1.group(1))}'))
                m2 = re.match(r'^(\d+)\s*[\-~]\s*(\d+)$', content)
                if m2:
                    return await bot.send(event,
                                          messagechain_builder(text=f'{_random_int_general(m2.group(1), m2.group(2))}'))
                m3 = re.match(r'[Dd](\d+)$', content)
                if m3:
                    dice = int(m3.group(1))
                    if dice < 2 or dice > 100:
                        return await bot.send(event, messagechain_builder(text='没有这样的骰子'))
                    return await bot.send(event,
                                          messagechain_builder(text=f'{_random_int_general(dn=dice)}'))
                m4 = content.split(' ')
                return await bot.send(event, messagechain_builder(text=_random_item(m4)))
        return await bot.send(event, messagechain_builder(text=f'{_random_int_general()}'))
