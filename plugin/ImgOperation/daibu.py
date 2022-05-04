import asyncio

from PIL import Image
from PIL import ImageOps
from moviepy.editor import ImageSequenceClip as imageclip
import numpy
import aiohttp
from io import BytesIO
import os


async def getimg(member_id):

    # if not os.path.exists("./images/daibu"):
    #     os.mkdir("./images/daibu")
    url = f'http://q1.qlogo.cn/g?b=qq&nk={str(member_id)}&s=640'
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            img_content = await resp.read()

    avatar = Image.open(BytesIO(img_content)).convert("RGB")
    size = avatar.size
    # 因为是要圆形，所以需要正方形的图片
    ima = avatar.resize((80, 80), Image.ANTIALIAS)
    # bgk = Image.open('./plugin/image/daibu/daibu.png').convert("RGB")
    bgk = Image.open('./image/daibu.png').convert("RGB")
    bgk.paste(ima,(40,40,ima.width,ima.height))
    # bgk.save(fp=f'./plugin/images/daibu/{member_id}.png')
    bgk.save(fp=f'./daibu_{member_id}.png')


getimg(1215791340)

tasks = [
    asyncio.ensure_future(getimg(1215791340))
]
loop = asyncio.get_event_loop()
tasks = asyncio.gather(*tasks)
loop.run_until_complete(tasks)