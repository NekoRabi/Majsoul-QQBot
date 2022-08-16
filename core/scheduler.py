from apscheduler.schedulers.asyncio import AsyncIOScheduler
from mirai.bot import Startup, Shutdown

from core import bot

scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")


@bot.on(Startup)
def start_scheduler(_):
    scheduler.start()  # 启动定时器


@bot.on(Shutdown)
def stop_scheduler(_):
    scheduler.shutdown(True)  # 结束定时器
