"""
:Author:  NekoRabi
:Create:  2023/6/16 1:22
:Update: /
:Describe: 计时器模块,本来还想做一个检测更新的
:Version: 0.0.1
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from mirai.bot import Startup, Shutdown
# import logging
# import aiohttp
# import asyncio
# from bs4 import BeautifulSoup

from core import bot



__all__ = ['scheduler', 'start_scheduler', 'stop_scheduler']

scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")

# scheduler.add_job(majsoul.set_link_node, 'cron', hour='0')

_version = 'v0.7.0'

@bot.on(Startup)
def start_scheduler(_):
    scheduler.start()  # 启动定时器


@bot.on(Shutdown)
def stop_scheduler(_):
    scheduler.shutdown(True)  # 结束定时器


# async def _auto_update() -> bool:
#     """
#     自动检查有无版本更新
#     Returns:
#
#     """
#     try:
#         async with aiohttp.ClientSession(
#                 connector=aiohttp.TCPConnector(ssl=False), timeout=aiohttp.ClientTimeout(total=25),headers={'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}) as session:
#             async with session.get('https://github.com/NekoRabi/Majsoul-QQBot/releases') as response:
#                 if response.status == 503:
#                     return False
#                 html = response.text()
#
#     except aiohttp.client.ClientConnectorError as _e:
#         logging.warning('检测更新时发生了意外的错误,类别为aiohttp.client.ClientConnectorError,可能的原因是连接达到上限,可以尝试关闭代理:\n{_e}')
#         return False
#     bs = BeautifulSoup(html)
#     return