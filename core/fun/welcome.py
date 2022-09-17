"""
:Author:  NekoRabi
:Create:  2022/8/16 17:29
:Update: /
:Describe: 欢迎新成员入群,群名字太长可能会显示不全
:Version: 0.0.1
"""

import os.path
import random

from mirai.models import MemberJoinEvent

from core import bot, config
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender

settings = config.get('settings')
admin = config.get('admin',[])

__all__ = ['welcome']


@bot.on(MemberJoinEvent)
async def welcome(event: MemberJoinEvent) -> None:
    if settings['autowelcome']:
        personid = event.member.id
        personname = event.member.member_name
        groupname = event.member.group.name
        groupid = event.member.group.id
        info: str = random.choice(config['welcomeinfo'])
        info = info.replace('%ps%', personname).replace('%gn%', groupname)
        await messagechain_sender(
            messagechain_builder(text=info, at=personid), grouptarget=event.member.group.id)
        if os.path.exists(r'./plugin/Petpet/gif.py'):
            from plugin.Petpet.gif import petpet
            await petpet(personid)
            await messagechain_sender(grouptarget=groupid,
                                      msg=messagechain_builder(imgpath=f'./images/PetPet/temp/tempPetPet-{personid}.gif'))
        return
