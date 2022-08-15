import base64
import random
from io import BytesIO

import aiohttp
from mirai import GroupMessage, Plain

# from plugin.preinit.create_bot import bot
from core import bot

from utils.MessageChainBuilder import messagechain_builder

from PIL import Image, ImageDraw
import re

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

asytimeout = aiohttp.ClientTimeout(total=60)


async def download_img(url):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=asytimeout,
                                     headers={'User-Agent': random.choice(user_agent_list)}) as session:
        async with session.get(url=url, allow_redirects=True) as response:
            img = await response.read()
            wifeimg = Image.open(BytesIO(img)).convert("RGBA")
            bx, by = wifeimg.size
            textdraw = ImageDraw.Draw(wifeimg)
            textdraw.line((1, 1, 1, 1), (255, 255, 255), 1)
            textdraw.line((bx - 2, by - 2, bx - 2, by - 2), (255, 255, 255), 1)
            textdraw.line((1, by - 2, 1, by - 2), (255, 255, 255), 1)
            textdraw.line((bx - 2, 1, bx - 2, 1), (255, 255, 255), 1)

    img_bytes = BytesIO()
    wifeimg.save(img_bytes, format='PNG')

    b_content = img_bytes.getvalue()
    imgcontent = base64.b64encode(b_content)
    return imgcontent


@bot.on(GroupMessage)
async def drawwife(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(
        fr"^抽老婆$", msg.strip())
    if m:
        index = random.randint(1, 9999)
        img = await download_img(f'https://www.thiswaifudoesnotexist.net/example-{index}.jpg')
        return await bot.send(event, messagechain_builder(at=event.sender.id,
                                                          imgbase64=img))
