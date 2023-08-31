# -*- coding: utf-8 -*-
import datetime
import re
import time

import psutil
from PIL import Image as IMG
from PIL import ImageDraw, ImageFont
from httpx import AsyncClient
from mirai import GroupMessage, Plain, Image

from core import bot, admin

@bot.on(GroupMessage)
async def sysinfo(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^sysinfo$", msg.strip())
    if m is None:
        return
    if event.sender.id not in admin:
        return
    cpu_percent = round((psutil.cpu_percent()), 2)  # cpu使用率
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('C:/')
    total_nc = round((float(memory.total) / 1024 / 1024))  # 总内存
    used_nc = round((float(memory.used) / 1024 / 1024))  # 已用内存
    percent_nc = memory.percent  # 内存使用率
    total_disk = round((float(disk.total) / 1024 / 1024 / 1024), 2)
    used_disk = round((float(disk.used) / 1024 / 1024 / 1024), 2)
    percent_disk = disk.percent
    now = time.time()
    boot = psutil.boot_time()
    boottime = datetime.datetime.fromtimestamp(boot).strftime("%Y-%m-%d %H:%M:%S")
    up_time = str(
        datetime.datetime.utcfromtimestamp(now).replace(microsecond=0)
        - datetime.datetime.utcfromtimestamp(boot).replace(microsecond=0)
    )
    try:
        async with AsyncClient(
            timeout=10,
            proxies="http://127.0.0.1:10809",
            follow_redirects=True,
        ) as client:
            start = time.time()
            resp = await client.get("https://www.pixiv.net/")
            delay = (time.time() - start) * 1000
            pixiv_connection = f'pixiv:{round(delay)}ms'
            if delay < 2000:
                percent_pixiv = 100-delay/20
    except Exception as e:
        pixiv_connection = 'pixiv:timeout'
        percent_pixiv = 0
    try:
        async with AsyncClient(
            timeout=10,
            proxies="http://127.0.0.1:10809",
            follow_redirects=True,
        ) as client:
            start = time.time()
            resp = await client.get("https://www.google.com/")
            delay = (time.time() - start) * 1000
            google_connection = f'google:{round(delay)}ms'
    except Exception as e:
        google_connection = 'google:timeout'
    '''
    img = IMG.new('RGB', (1080, 1280), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle((48,78,352,282),fill='white',outline=(17,125,187),width=4)
    draw.rectangle((48,378,352,582),fill='white',outline=(139,18,174),width=4)
    draw.rectangle((48,678,352,882),fill='white',outline=(77,166,12),width=4)
    draw.rectangle((48,978,352,1182),fill='white',outline=(167,79,1),width=4)
    font = ImageFont.truetype('msyh.ttc', 80)
    draw.text((400,50),text='CPU',font=font,fill=(0, 0, 0))
    draw.text((400,350),text='内存',font=font,fill=(0, 0, 0))
    draw.text((400,650),text='磁盘(C:)',font=font,fill=(0, 0, 0))
    draw.text((400,950),text='以太网',font=font,fill=(0, 0, 0))
    '''
    img = IMG.open(r'./plugin/SystemInfo/cpu.jpg')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('msyh.ttc', 60)
    draw.text((400,150),text=f'{cpu_percent}% 2.50 GHZ\n{up_time}',font=font,fill=(0, 0, 0))
    draw.text((400,450),text=f'{used_nc}/{total_nc}MB\n{percent_nc}%',font=font,fill=(0, 0, 0))
    draw.text((400,750),text=f'{used_disk}/{total_disk}GB\n{percent_disk}%',font=font,fill=(0, 0, 0))
    draw.text((400,1050),text=f'{google_connection}\n{pixiv_connection}',font=font,fill=(0, 0, 0))
    draw.rectangle((48,280-round(cpu_percent)*2,352,282-round(cpu_percent)*2),fill=(17,125,187))
    draw.rectangle((48,580-round(percent_nc)*2,352,582-round(percent_nc)*2),fill=(139,18,174))
    draw.rectangle((48,880-round(percent_disk)*2,352,882-round(percent_disk)*2),fill=(77,166,12))
    draw.rectangle((48,1180-round(percent_pixiv)*2,352,1182-round(percent_pixiv)*2),fill=(167,79,1))
    img.save(r'./plugin/SystemInfo/now_cpu.jpg')
    path = r'./plugin/SystemInfo/now_cpu.jpg'
    return await bot.send(event,Image(path=r'./plugin/SystemInfo/now_cpu.jpg'))

