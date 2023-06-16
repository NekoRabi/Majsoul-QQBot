"""
:Author:  NekoRabi
:Create:  2023/6/15 3:03
:Update: /
:Describe: Bot群状态监控工具
:Version: 0.0.1
"""

from mirai.models import BotLeaveEventKick, BotMuteEvent, BotUnmuteEvent, BotJoinGroupEvent

from core import bot, master
from utils import root_logger
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender

__all__ = ['bot_muted', 'bot_unmuted', 'bot_leave_group', 'bot_join_group']


@bot.on(BotLeaveEventKick)
async def bot_leave_group(event: BotLeaveEventKick):
    """Bot被踢出群"""
    try:
        await messagechain_sender(friendtarget=master, msg=await messagechain_builder(text=f"Bot被踢出群{event.group.id}"))
        root_logger.error(f'Bot被踢出群聊{event.group.id}')
    except Exception as _e:
        print(f'Bot被踢出出群聊时发生错误\n{_e}')
        root_logger.error(f'Bot被踢出出群聊时发生错误\n{_e}')
    return


@bot.on(BotMuteEvent)
async def bot_muted(event: BotMuteEvent):
    """Bot在x群被禁言"""
    try:
        await messagechain_sender(friendtarget=master, msg=await messagechain_builder(text=f"Bot被群{event.group.id}禁言了"))
        root_logger.error(f'Bot被群聊 {event.group.id} 禁言')
    except Exception as _e:
        print(f'Bot在被{event.group.id}被禁言时发生错误\n{_e}')
        root_logger.error(f'Bot在被{event.group.id}被禁言时发生错误\n{_e}')
    return


@bot.on(BotUnmuteEvent)
async def bot_unmuted(event: BotUnmuteEvent):
    """Bot在x群被解除禁言"""
    try:
        await messagechain_sender(friendtarget=master,
                                  msg=await messagechain_builder(text=f"Bot在{event.group.id}群解除禁言"))
        root_logger.error(f'Bot被群聊 {event.group.id} 解除禁言')
    except Exception as _e:
        print(f'Bot在群{event.group.id}时被解除禁言发生错误\n{_e}')
        root_logger.error(f'Bot在群{event.group.id}时被解除禁言发生错误\n{_e}')
    return

@bot.on(BotJoinGroupEvent)
async def bot_join_group(event: BotJoinGroupEvent):
    """Bot加入群"""
    try:
        await messagechain_sender(friendtarget=master,
                                  msg=await messagechain_builder(text=f"Bot加入群聊 {event.group.id}"))
        root_logger.error(f"Bot加入群聊 {event.group.id}")
    except Exception as _e:
        print(f'Bot加入群聊 {event.group.id} 时发生错误\n{_e}')
        root_logger.error(f'Bot加入群聊 {event.group.id} 时发生错误\n{_e}')
    return