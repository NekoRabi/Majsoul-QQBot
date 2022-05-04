import random

import aiohttp
import os
import asyncio

from utils.asyrequestpackge import finish_all_asytasks
'''
r18	int	0	0为非 R18，1为 R18，2为混合（在库中的分类，不等同于作品本身的 R18 标识）
num	int	1	一次返回的结果数量，范围为1到100；在指定关键字或标签的情况下，结果数量可能会不足指定的数量
uid	int[]		返回指定uid作者的作品，最多20个
keyword	string		返回从标题、作者、标签中按指定关键字模糊匹配的结果，大小写不敏感，性能和准度较差且功能单一，建议使用tag代替
tag	string[]		返回匹配指定标签的作品，详见下文
size	string[]	["original"]	返回指定图片规格的地址，详见下文
proxy	string	i.pixiv.cat	设置图片地址所使用的在线反代服务，详见下文
dateAfter	int		返回在这个时间及以后上传的作品；时间戳，单位为毫秒
dateBefore	int		返回在这个时间及以前上传的作品；时间戳，单位为毫秒
dsc	boolean	false

'''

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


def keyword_transform(keywords: str, value):
    if keywords in ["r18", "num", "uid", "keyword", "size"]:
        return f"{keywords}={value}"
    elif keywords == "tag":
        tag = ""
        for v in value:
            tag += f"{value}"
        return tag


async def getsetuinfo(tag: str) -> dict:
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=5), timeout=timeout,
                                     headers={'User-Agent': random.choice(user_agent_list)}) as session:

        if tag:
            async with session.get(f"https://api.lolicon.app/setu/v2?tag={tag}") as response:
                text = await response.text()
        else:
            async with session.get(f"https://api.lolicon.app/setu/v2") as response:
                text = await response.text()
    text = eval(text.replace("false", "False"))
    return text


def getsetu(tag: str = "",r18:bool=False) -> dict:
    content = finish_all_asytasks([getsetuinfo(tag)])
    response = content[0]
    print(response)
    if len(response['data']) == 0:
        imginfo = dict(notFound=True)
    else:
        imginfo: dict = response['data'][0]
        imginfo['notFound'] = False
        imginfo['url'] = imginfo['urls']['original'].replace("cat",  "re")
    return imginfo
