import datetime

from core import bot, scheduler, config, bot_cfg
from utils.MessageChainBuilder import messagechain_builder

__all__ = ['group_fixed_clock']

_alarmclockgroup: list = config['alarmclockgroup']

_botname = bot_cfg.get('nickname')

if 0 in _alarmclockgroup:
    _alarmclockgroup.remove(0)


async def group_fixed_clock():
    # 时分秒
    hour_now = datetime.datetime.now().hour
    for groupid in _alarmclockgroup:
        if groupid != 0 and type(groupid) == int:
            await bot.send_group_message(groupid,
                                         messagechain_builder(
                                             text=f"准点报时: {datetime.datetime.now().hour}:00",
                                             rndimg=True))
            if hour_now == 22:
                await bot.send_group_message(groupid,
                                             messagechain_builder(text=f"晚上10点了，大家可以休息了,{_botname}也要休息了", rndimg=True))

if len(_alarmclockgroup) > 0:
    scheduler.add_job(group_fixed_clock, 'cron', hour='8-22')
    print(f' |--- 已为群组{_alarmclockgroup}添加准点报时')
