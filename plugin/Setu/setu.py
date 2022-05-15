import random
import yaml
import aiohttp
import json

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


async def getsetuinfo(description: str, num: int) -> dict:
    tag = description
    r18 = False
    if tag:
        tag = tag.replace('的', '')
        if 'r18' in tag:
            tag = tag.replace('r18', '').strip()
            r18 = True
        elif 'R18' in tag:
            tag = tag.replace('R18', '').strip()
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
    print(text)
    text = json.loads(text)
    return text


class SetuFinder:

    def __init__(self, botname):
        with open(r'./config/Setu/config.yml') as f:
            config = yaml.safe_load(f)
            self.r18setting = config['r18setting']
            self.r18groups = config['r18groups']
            self.allowsearchself = config['allowsearchself']
            self.botname = botname

    def keyword_transform(self, keywords: str, value):
        if keywords in ["r18", "num", "uid", "keyword", "size"]:
            return f"{keywords}={value}"
        elif keywords == "tag":
            tag = ""
            for v in value:
                tag += f"{v}"
            return tag

    def getsetu(self, description, groupid, num=1) -> dict:
        if not num:
            num = 1
        if description:
            if 'r18' in description or 'R18' in description:
                if groupid not in self.r18groups:
                    imginfo = dict(FoundError=True, ErrorMsg="本群未开启R18")
                    return imginfo
            if self.botname in description and not self.allowsearchself:
                return dict(FoundError=True, ErrorMsg="不许搜咱的图")

        content = finish_all_asytasks([getsetuinfo(description, num)])
        response = content[0]
        if len(response['data']) == 0:
            imginfo = dict(FoundError=True, ErrorMsg="没找到这样的图片呢")
        else:
            imginfo: dict = response['data'][0]
            imginfo['FoundError'] = False
            imginfo['url'] = imginfo['urls']['original'].replace("cat", "re")
        return imginfo
