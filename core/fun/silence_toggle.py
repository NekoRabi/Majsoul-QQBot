"""
:Author:  NekoRabi
:Update Time:  2022/8/16 16:01
:Describe: 机器人沉默模式切换
"""
import re

from mirai import GroupMessage, Plain, FriendMessage

from core import bot, config, commandpre, commands_map
from utils.cfg_loader import write_file

settings = config.get('settings')
admin = config['admin']
silencegroup = config['silencegroup']

__all__ = ['be_silence_from_friend', 'be_groupsilence_from_group']


@bot.on(FriendMessage)
async def be_silence_from_friend(event: FriendMessage):
    """
    全局沉默
    :param event:
    :return:
    """
    if event.sender.id in admin:
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['sys']['silence_all']}", msg.strip())
        if m:
            if m.group(1).lower() == 'on' or m.group(1).lower() == 'true':
                settings['silence'] = True
                write_file(content=config, path=r'./config/config.yml')
            else:
                settings['silence'] = False
                write_file(content=config, path=r'./config/config.yml')


# 单群沉默 - 从群聊沉默

@bot.on(GroupMessage)
async def be_groupsilence_from_group(event: GroupMessage):
    """
    群沉默
    :param event:
    :return:
    """
    msg = "".join(map(str, event.message_chain[Plain]))
    userid = event.sender.id
    if userid in admin:
        m = re.match(fr"^{commandpre}{commands_map['sys']['silence_group']}", msg.strip())
        if m:
            if m.group(1).lower() == 'on' or m.group(1).lower() == 'true':
                if event.group.id not in silencegroup:
                    silencegroup.append(event.group.id)
                    write_file(content=config, path=r'./config/config.yml')
            else:
                if event.group.id in silencegroup:
                    silencegroup.remove(event.group.id)
                    write_file(content=config, path=r'./config/config.yml')
