"""
:Author:  NekoRabi
:Create:  2022/8/16 17:23
:Update: /
:Describe: BiliBili相关
:Version: 0.0.1
"""
import os
import random
import re

import aiohttp
import mirai.exceptions
from mirai import GroupMessage

from core import bot, config
from utils import write_file, read_file
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender

last_bvid = {}

settings = config['settings']
silencegroup = config['silencegroup']
_blacklist = config.get('blacklist', [])
__all__ = ['bili_resolve']
if not os.path.exists(r"./config/BilibiliPlugin"):
    os.mkdir(r"./config/BilibiliPlugin")
if not os.path.exists(r"./config/BilibiliPlugin/config.yml"):
    print('未检测到B站解析配置文件,生成初始文件中...')
    cfg = dict(videolink_resolve=True)
    write_file(content=cfg, path=r"./config/BilibiliPlugin/config.yml")
    print('B站解析配置文件生成完毕')

_cfg = read_file(r"./config/BilibiliPlugin/config.yml")
if _cfg is None:
    _cfg = {'videolink_resolve': True}


user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) Gecko/20100101 Firefox/61.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
]

@bot.on(GroupMessage)
async def bili_resolve(event: GroupMessage):
    """bilibili链接解析"""
    if not _cfg:
        return
    if not _cfg.get("videolink_resolve", True):
        return
    if not settings['silence']:
        if event.group.id not in silencegroup:
            if event.sender.id in _blacklist:
                return
            global last_bvid
            text = str(event.message_chain.as_mirai_code)
            text = text.replace('\\n', '').replace('\\', '')
            if 'b23.tv/' in text:
                b23_url = re.findall('b23.tv/[A-Za-z0-9]+', text)[0]
                url = f'https://{b23_url}'
                async with aiohttp.ClientSession() as session:
                    async with session.get(url=url, allow_redirects=False) as resp:
                        text = await resp.text()
            if 'BV' in text:
                bvid = re.findall('BV[A-Za-z0-9]+', text)[0]
            else:
                return
            if event.group.id in last_bvid.keys():
                if bvid == last_bvid[event.group.id]:
                    return
            # if event.message_chain.has("www.bilibili.com/video"):
            #     bvid = re.findall('BV[A-Za-z0-9]',"".join(map(str, event.message_chain[Plain])).strip())[0]
            last_bvid[event.group.id] = bvid
            bv_url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
            async with aiohttp.ClientSession(headers={'User-Agent': random.choice(user_agent_list)}) as session:
                async with session.get(url=bv_url) as resp:
                    data = await resp.json()
            if data['code'] != 0:
                return
            img_url = data['data']['pic']
            author = data['data']['owner']['name']
            title = data['data']['title']
            msg = f'{bvid}\nUP主:{author}\n标题:{title}'

            '''if event.message_chain[1].type == 'App':
                app = event.message_chain[1].as_json()
                url = app['meta']['detail_1']['preview']
                img_url = f'https://{url}'''
            message_chain = await messagechain_builder(imgurl=img_url, text=msg)
            try:
                # await bot.send(event, message_chain)
                await messagechain_sender(event=event,msg =message_chain)
            except mirai.exceptions.ApiError as _e:
                print(f'视频封面发送失败 {_e.args}')
    return
