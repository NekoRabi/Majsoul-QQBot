"""
:Author:  NekoRabi
:Create:  2022/10/16 20:31
:Update: /
:Describe: 时钟功能核心
:Version: 0.0.1
"""
import sqlite3
import time

from core import scheduler
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender


class Clock:

    @staticmethod
    def add_group_clock(scheduledtime: str, group: int, creator: int, at: list, description: str):
        """
        添加闹钟

        Args:
            scheduledtime: 计划时间
            group: 群组
            creator: 创建人
            at: at的对象
            description: 描述

        Returns: 是否成功的消息

        """
        ats = []
        nowtime = time.time()
        d_time = int(time.mktime(time.strptime(scheduledtime, '%Y-%m-%d %H:%M:%S'))) - nowtime
        if d_time <= 0:
            return f"添加失败，计划时间必须在将来"
        elif d_time > 3600 * 24 * 14:
            return f"添加失败,最多支持未来14天的安排"
        for _at in at:
            ats.append(int(_at))
        if len(at) > 0:
            at = f'{at}'.replace('"', '').replace("'", "")
        else:
            at = '[]'
        cx = sqlite3.connect('./database/AlarmClock/clock.sqlite')
        cursor = cx.cursor()
        sql_select = f"select enable,scheduledtime from groupclock where creator = {creator} and description = '{description}'"
        task = cursor.execute(sql_select).fetchall()
        if len(task) > 0:
            task = task[0]
            task_time = task[1]
            task_enable = task[0]
            if int(time.mktime(time.strptime(task_time, '%Y-%m-%d %H:%M:%S'))) > time.time():
                sql_update = f"update groupclock set scheduledtime = '{scheduledtime}' and enable = 1 where description = '{description}' and creator = {creator}"
                scheduler.add_job(send_remind, 'date', run_date=scheduledtime, args=[group, description, ats])
                cursor.execute(sql_update)
            elif task_enable == 0:
                sql_update = f"update groupclock set enable = 1 where description = '{description}' and creator = {creator}"
                cursor.execute(sql_update)
                scheduler.add_job(send_remind, 'date', run_date=scheduledtime, args=[group, description, ats])
        else:
            sql = f"insert into groupclock(creator,at,target,description,scheduledtime) values({creator},'{at[1:-1]}',{group},'{description}','{scheduledtime}')"
            cursor.execute(sql)
            scheduler.add_job(send_remind, 'date', run_date=scheduledtime, args=[group, description, ats])
        cx.commit()
        cursor.close()
        cx.close()
        return f"计划时间:{scheduledtime},创建人:{creator},{'目标:' if len(at) > 0 else ''}{ats if len(at) > 0 else ''},描述={description}"

    @staticmethod
    def start_all_clock():
        """启动所有闹钟"""
        all_clock = get_all_active_clock()
        for clock in all_clock:
            ats = []
            for at in clock[3].split(','):
                ats.append(int(at))
            scheduler.add_job(send_remind, 'date', run_date=clock[1], args=[clock[0], clock[2], ats])
        print("已自动设置所有闹钟")


def get_all_active_clock() -> list:
    """
    返回所有有效闹钟

    Returns:
        list[tuple(int, str, str, str)]
        [(groupid, scheduledtime, description, at) , ......]

    """
    cx = sqlite3.connect('./database/AlarmClock/clock.sqlite')
    cursor = cx.cursor()
    sql_select = f"select target,scheduledtime,description,at from groupclock where date(scheduledtime) > date('now') and enable = 1 "
    all_clock = cursor.execute(sql_select).fetchall()
    cursor.close()
    cx.close()
    return all_clock


async def send_remind(groupid: int, message: str, at: list or int = None):
    return await messagechain_sender(grouptarget=groupid, msg=await messagechain_builder(text=message, at=at))
