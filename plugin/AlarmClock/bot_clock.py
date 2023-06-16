import datetime
import re

from mirai import GroupMessage, Plain, At  # , Startup

from core import bot, scheduler, config, bot_cfg, commandpre
from plugin.AlarmClock.file_init import *
from plugin.AlarmClock.clock_core import Clock
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender
from utils.TimeCheckUtil import *
from utils.cfg_loader import read_file

__all__ = ['group_fixed_clock']

_alarmclockgroup: list = config['alarmclockgroup']

_botname = bot_cfg.get('nickname')

_clocksetting = read_file("./config/AlarmClock/config.yml")

if 0 in _alarmclockgroup:
    _alarmclockgroup.remove(0)


@bot.on(GroupMessage)
async def addclock(event: GroupMessage):
    """添加闹钟"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(
        fr"^{commandpre}添加提醒\s*(at|@[\d,，]+)?\s*(\d{{4}}-\d{{1,2}}-\d{{1,2}})\s*(\d{{1,2}}:\d{{1,2}}:\d{{1,2}})?\s*(\w+)$",
        msg.strip())
    if m:
        if _clocksetting.get("enable", False):
            at = m.group(1)
            if at is None:
                at = ""
            else:
                at = re.findall(r"\d+", at)
            if At in event.message_chain:
                msg = []
                at = event.message_chain[At]
                for _at in at:
                    msg.append(f"{_at.target}")
                at = msg
            date = m.group(2)
            time = m.group(3)
            description = m.group(4)
            info = date_check(date)
            if not info.get('effective'):
                # return await bot.send(event, await messagechain_builder(text=info.get('error')))
                return await messagechain_sender(event=event, msg=await messagechain_builder(text=info.get('error')))
            if m.group(3):
                info = time_check(time)
                if not info.get('effective'):
                    # return await bot.send(event, await messagechain_builder(text=info.get('error')))
                    return await messagechain_sender(event=event,
                                                     msg=await messagechain_builder(text=info.get('error')))
            else:
                time = '00:00:00'
            groupid = event.group.id
            msg = Clock.add_group_clock(group=groupid, creator=event.sender.id, scheduledtime=f'{date} {time}', at=at,
                                        description=description)

            return await messagechain_sender(event=event, msg=await messagechain_builder(text=msg))


# @bot.on(Startup)
# async def start_allclock():
#     Clock.start_all_clock()


async def group_fixed_clock():
    # 时分秒
    hour_now = datetime.datetime.now().hour
    for groupid in _alarmclockgroup:
        if groupid != 0 and type(groupid) == int:
            # await bot.send_group_message(groupid,
            #                              await messagechain_builder(
            #                                  text=f"准点报时: {datetime.datetime.now().hour}:00",
            #                                  rndimg=True))
            await messagechain_sender(grouptarget=groupid,
                                      msg=await messagechain_builder(text=f"准点报时: {datetime.datetime.now().hour}:00",
                                                                     rndimg=True))
            if hour_now == 22:
                # await bot.send_group_message(groupid,
                #                              await messagechain_builder(text=f"晚上10点了，大家可以休息了,{_botname}也要休息了",
                #                                                         rndimg=True))
                await messagechain_sender(grouptarget=groupid,
                                          msg=await messagechain_builder(text=f"晚上10点了，大家可以休息了,{_botname}也要休息了",
                                                                         rndimg=True))


if len(_alarmclockgroup) > 0:
    scheduler.add_job(group_fixed_clock, 'cron', hour='8-22')
    print(f' |--- 已为群组{_alarmclockgroup}添加准点报时')
