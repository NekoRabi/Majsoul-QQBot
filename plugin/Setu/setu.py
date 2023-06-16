"""
:Author:  NekoRabi
:Create:  2023/6/16 2:11
:Update: /
:Describe: 从 liliconAPI 搜索色图
:Version: 0.0.1
"""
import asyncio
import base64
import os.path
import random
import re
import yaml
import aiohttp
import json

# from io import BytesIO

# from PIL.Image import Image
from mirai import GroupMessage, Plain
from core import bot, commandpre, commands_map, config
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender
from utils.bufferpool import *
from utils.cfg_loader import write_file

###
# r18	int	0	0为非 R18，1为 R18，2为混合（在库中的分类，不等同于作品本身的 R18 标识）
# num	int	1	一次返回的结果数量，范围为1到100；在指定关键字或标签的情况下，结果数量可能会不足指定的数量
# uid	int[]		返回指定uid作者的作品，最多20个
# keyword	string		返回从标题、作者、标签中按指定关键字模糊匹配的结果，大小写不敏感，性能和准度较差且功能单一，建议使用tag代替
# tag	string[]		返回匹配指定标签的作品，详见下文
# size	string[]	["original"]	返回指定图片规格的地址，详见下文
# proxy	string	i.pixiv.cat	设置图片地址所使用的在线反代服务，详见下文
# dateAfter	int		返回在这个时间及以后上传的作品；时间戳，单位为毫秒
# dateBefore	int		返回在这个时间及以前上传的作品；时间戳，单位为毫秒
# dsc	boolean	false
###

__all__ = ['getsomesetu', 'enablesetu', 'disablesetu']
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

if not os.path.exists("./config/Setu"):
    os.mkdir("./config/Setu")
if not os.path.exists(r'./config/Setu/config.yml'):
    cfg = dict(r18enable=False, enable=False, allowsearchself=False, setugroups=[0], r18groups=[0],
               recalltime=50, err_opt=True)
    write_file(content=cfg, path=r'./config/Setu/config.yml')


async def download_setu_base64_from_url(userid):
    url = f'http://q1.qlogo.cn/g?b=qq&nk={userid}&s=640'
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            img_content = await resp.read()

    pic_base64 = base64.b64encode(img_content)
    print(pic_base64)
    return pic_base64


# async def download_setu_base64_from_url(url):
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url=url) as resp:
#             img_content = await resp.read()
#
#     # 将图片转换为 base64
#     img_bytes = BytesIO(img_content)
#     b_content = img_bytes.getvalue()
#     imgcontent = base64.b64encode(b_content)
#     return imgcontent


async def getsetuinfo(description: str, num: int) -> dict:
    tag = description
    r18 = False
    if tag:
        tag = tag.replace('的', '')
        if 'r18' in tag:
            tag = tag.replace('r18', '', 1).strip()
            r18 = True
        elif 'R18' in tag:
            tag = tag.replace('R18', '', 1).strip()
            r18 = True
    keyword = {}
    url = f"https://api.lolicon.app/setu/v2?num={num}"
    if tag and tag != '':
        keyword['tag'] = tag
    if r18:
        keyword['r18'] = 1
    if len(keyword) > 0:
        for k, v in keyword.items():
            url += f'&{k}={v}'
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=5),
                                     timeout=aiohttp.ClientTimeout(total=10),
                                     headers={'User-Agent': random.choice(user_agent_list)}) as session:
        async with session.get(f"{url}") as response:
            text = await response.text()
    text = json.loads(text)
    print('色图结果:', text.get('data'))
    return text


def keyword_transform(keywords: str, value):
    if keywords in ["r18", "num", "uid", "keyword", "size"]:
        return f"{keywords}={value}"
    elif keywords == "tag":
        tag = ""
        for v in value:
            tag += f"{v}"
        return tag


class SetuFinder:
    recalltime = 30

    def __init__(self, botname, _config: dict):
        self.r18enable = _config.get('r18enable', False)
        self.r18groups = _config.get('r18groups', [])
        self.allowsearchself = _config.get('allowsearchself', False)
        self.recalltime = _config.get('recalltime', 30)
        self.botname = botname
        self.err_opt = _config.get('err_opt', True)

    async def getsetu(self, description, groupid, num=1) -> dict:
        if not num:
            num = 1
        if description:
            if 'r18' in description or 'R18' in description:
                if groupid not in self.r18groups:
                    imginfo = dict(FoundError=True, ErrorMsg="本群未开启R18")
                    return imginfo
            if self.botname in description and not self.allowsearchself:
                return dict(FoundError=True, ErrorMsg="不许搜咱的图")

        # content = finish_all_asytasks([getsetuinfo(description, num)])
        response = await getsetuinfo(description, num)
        # response = content[0]
        if len(response['data']) == 0:
            # imginfo = dict(FoundError=True, ErrorMsg="没找到这样的图片呢")
            imginfo = dict(FoundError=True, ErrorMsg="你的XP太奇怪了")
        else:
            imginfo: dict = response['data'][0]
            imginfo['FoundError'] = False
            imginfo['url'] = imginfo['urls']['original'].replace("cat", "re")
        return imginfo


admin = config.get('admin', [])
blackuser = config.get('blacklist', [])

with open(r'./config/Setu/config.yml', 'r', encoding='utf-8') as f:
    setu_config = yaml.safe_load(f)
stfinder = SetuFinder(config['botconfig']['botname'], setu_config)


@bot.on(GroupMessage)
async def enablesetu(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(
        fr"^{commandpre}{commands_map['setu']['enable']}", msg.strip())
    if m:
        if event.sender.id in admin:
            groupid = event.group.id
            if groupid in setu_config.get('setugroups'):
                await messagechain_sender(event=event, msg=await messagechain_builder(text="本群已开启色图"))
            else:
                setu_config.get('setugroups').append(groupid)
                # with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                #     yaml.dump(config, file, allow_unicode=True)
                # w_cfg_to_file(content=config, path=r'./config/config.yml')
                write_file(content=setu_config, path=r'./config/Setu/config.yml')
                await messagechain_sender(event=event, msg=await messagechain_builder(text="色图开启成功"))


@bot.on(GroupMessage)
async def disablesetu(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))

    m = re.match(
        fr"^{commandpre}{commands_map['setu']['disable']}", msg.strip())
    if m:
        if event.sender.id in admin:
            groupid = event.group.id
            if groupid in setu_config.get('setugroups'):
                setu_config.get('setugroups').remove(groupid)
                # with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                #     yaml.dump(config, file, allow_unicode=True)
                # w_cfg_to_file(content=config, path=r'./config/config.yml')
                write_file(content=setu_config, path=r'./config/Setu/config.yml')
                await messagechain_sender(event=event, msg=await messagechain_builder(text="色图已关闭"))
            else:
                await messagechain_sender(event=event, msg=await messagechain_builder(text="本群色图已关闭"))


@bot.on(GroupMessage)
async def randomsetu(event: GroupMessage):
    """发一个随机涩图网站"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(
        fr"^随机[涩色]图(网[址站]?)?", msg.strip())
    if m:
        await messagechain_sender(event=event, msg=await messagechain_builder(text='https://iw233.cn/API/Random.php'))
    return


@bot.on(GroupMessage)
async def getsomesetu(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))

    # 匹配指令
    m1 = re.match(
        fr"^{commandpre}{commands_map['setu']['getsetu1']}", msg.strip())
    m2 = re.match(
        fr"^{commandpre}{commands_map['setu']['getsetu2']}", msg.strip())
    senderid = event.sender.id
    if senderid in blackuser:
        return
    if m1:
        # if random.random() * 100 < 10:
        if random.random() * 100 < 0:
            # print(f"发出对{senderid}的少冲提醒")
            # await messagechain_sender(event=event,msg=await messagechain_builder([At(senderid), " 能不能少冲点啊，这次就不给你发了"])
            pass
        else:
            if setu_config.get('enable', False) and event.group.id in setu_config.get('setugroups'):
                if not cmdbuffer.updategroupcache(GroupCommand(event.group.id, senderid, 'setu')):
                    return messagechain_sender(event=event,
                                               msg=await messagechain_builder(text="你冲的频率太频繁了,休息一下吧", at=senderid))
                try:
                    imginfo = await stfinder.getsetu(
                        m1.group(2), groupid=event.group.id)
                    if imginfo['FoundError']:
                        return await messagechain_sender(event=event, msg=await messagechain_builder(at=senderid,
                                                                                                     text=imginfo[
                                                                                                         'ErrorMsg']))
                    # imgb64 = download_setu_base64_from_url(imginfo['url'])
                    res = await messagechain_sender(event=event, msg=await messagechain_builder(imgurl=imginfo['url']))
                    # res = await messagechain_sender(event=)(evenmsg=t,await messagechain_builder(imgbase64=imgb64))
                    if res == -1:
                        await messagechain_sender(event=event, msg=f"色图发送失败!这肯定不是{config['botconfig']['botname']}的问题!")
                    elif stfinder.recalltime != -1:
                        await asyncio.sleep(stfinder.recalltime)
                        await bot.recall(res)
                except Exception as e:
                    print(f"色图请求失败:{e}")
                    if setu_config.get('err_opt', True):
                        await messagechain_sender(event=event, msg=await messagechain_builder(
                            text=f"出错了!这肯定不是{config['botconfig']['botname']}的问题!"))
    elif m2:
        if random.random() * 100 < 0:
            # print(f"发出对{senderid}的少冲提醒")
            # await messagechain_sender(event=event,msg=await messagechain_builder([At(senderid), " 能不能少冲点啊，这次就不给你发了"])
            pass
        else:
            if setu_config.get('enable', False) and event.group.id in setu_config.get('setugroups'):
                if not cmdbuffer.updategroupcache(GroupCommand(event.group.id, senderid, 'setu')):
                    return messagechain_sender(event=event,
                                               msg=await messagechain_builder(at=senderid, text="你冲的频率太频繁了,休息一下吧"))
                setu_num = m2.group(1)
                if not setu_num:
                    setu_num = 1
                else:
                    setu_num = int(setu_num)
                try:
                    imginfo = await stfinder.getsetu(
                        m2.group(2), event.group.id, setu_num)
                    if imginfo['FoundError']:
                        return await messagechain_sender(event=event, msg=await messagechain_builder(at=senderid,
                                                                                                     text=imginfo[
                                                                                                         'ErrorMsg']))
                    res = await messagechain_sender(event=event, msg=await messagechain_builder(imgurl=imginfo['url']))
                    # await messagechain_sender(event=)(evenmsg=t, MessageChain([Image(url=imginfo['url'])]))
                    if res == -1:
                        await messagechain_sender(event=event, msg=f"色图发送失败!这肯定不是{config['botconfig']['botname']}的问题!")
                    elif stfinder.recalltime != -1:
                        await asyncio.sleep(stfinder.recalltime)
                        await bot.recall(res)
                except Exception as e:
                    print(f"色图请求失败:{e}")
                    if setu_config.get('err_opt', True):
                        await messagechain_sender(event=event, msg=await messagechain_builder(
                            text=f"出错了!这肯定不是{config['botconfig']['botname']}的问题!"))
    return
