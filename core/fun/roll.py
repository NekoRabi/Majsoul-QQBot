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

from core import bot, commandpre, commands_map, blacklist, add_help
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender


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
    # if len(items) ==1:
    #     return "不可以只roll一个东西哦"
    # item_list = list(set(items))
    # if len(item_list) != items:
    #     return "roll的选项概率要公平哦"
    return random.choice(items)


@bot.on(GroupMessage)
@bot.on(FriendMessage)
async def roll_item(event: GroupMessage or FriendMessage):
    """roll"""
    msg = "".join(map(str, event.message_chain[Plain]))
    roll_re = commands_map.get('sys', dict()).get('roll', r'roll\s*([\s\S]+)?')
    m = re.match(
        fr"^{commandpre}{roll_re}", msg.strip())
    if event.sender.id in blacklist:
        return
    if m:
        content = m.group(1)
        if content:
            content = content.strip()
            if len(content) > 0:
                if content in ['-h', '-help', 'help']:
                    from utils.text_to_img import text_to_image
                    return await messagechain_sender(event=event, msg=await messagechain_builder(
                        imgbase64=text_to_image(text=_roll_help, needtobase64=True)))
                m1 = re.match(r'^(\d+)$', content)
                if m1:
                    return await messagechain_sender(event=event, msg=await messagechain_builder(
                        text=f'{_random_int_general(upper=m1.group(1))}'))
                m2 = re.match(r'^(\d+)\s*[\-~]\s*(\d+)$', content)
                if m2:
                    return await messagechain_sender(event=event, msg=await messagechain_builder(
                        text=f'{_random_int_general(m2.group(1), m2.group(2))}'))
                m3 = re.match(r'(\d+)?[Dd](\d+)$', content)
                if m3:
                    counts = m3.group(1)
                    if counts:
                        counts = int(counts)
                    else:
                        counts = 1
                    if counts < 1:
                        counts = 1
                    elif counts > 100:
                        return await messagechain_sender(event=event, msg=await messagechain_builder(at=event.sender.id, text='我累了'))
                    dice = int(m3.group(2))
                    if dice < 1 or dice > 100:
                        return await messagechain_sender(event=event, msg=await messagechain_builder(at=event.sender.id, text='我没有这样的骰子'))
                    elif dice % 2 == 1 and dice > 9:
                        return await messagechain_sender(event=event, msg=await messagechain_builder(at=event.sender.id, text='我只有10面以下的奇数面骰子~'))
                    each_rnd = _random_int_general(dn=dice)
                    sum = each_rnd
                    rnd_str = f'{each_rnd}'
                    for i in range(counts):
                        if i == 0:
                            continue
                        each_rnd = _random_int_general(dn=dice)
                        sum += each_rnd
                        rnd_str += f' + {each_rnd}'
                    rnd_str += f' = {sum}'

                    return await messagechain_sender(event=event, msg=await messagechain_builder(
                        text=f'{rnd_str}'))
                m4 = content.split(' ')
                return await messagechain_sender(event=event, msg=await messagechain_builder(text=_random_item(m4)))
        return await messagechain_sender(event=event, msg=await messagechain_builder(text=f'{_random_int_general()}'))


_roll_help = [
    "roll : 返回 0-100的随机整数",
    "roll 正整数a : 返回 0-a 的随机整数 ",
    "roll a-b : 返回 a-b 之间的随机整数",
    "roll itemA itemB …… : 返回随机一个元素",
    "roll ndn: 投掷n次n面骰"
]
add_help('group', [
    'roll 返回100以内的随机整数',
    'roll -help : 获取roll的更多使用方法'
])
