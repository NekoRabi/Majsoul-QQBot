from PIL import Image as IMG
from PIL import ImageDraw
from moviepy.editor import ImageSequenceClip as imageclip
import numpy
import aiohttp
from io import BytesIO
import os

# 插件信息
__name__ = "KissKiss"
__description__ = "生成亲吻gif"
__author__ = "Super_Water_God"
__usage__ = "在群内发送 亲@目标 即可"

async def save_gif(gif_frames, dest, fps=10):
    clip = imageclip(gif_frames, fps=fps)
    clip.write_gif(dest)
    clip.close()


async def kiss_make_frame(operator, target, i):
    operator_x = [92, 135, 84, 80, 155, 60, 50, 98, 35, 38, 70, 84, 75]
    operator_y = [64, 40, 105, 110, 82, 96, 80, 55, 65, 100, 80, 65, 65]
    target_x = [58, 62, 42, 50, 56, 18, 28, 54, 46, 60, 35, 20, 40]
    target_y = [90, 95, 100, 100, 100, 120, 110, 100, 100, 100, 115, 120, 96]
    bg = IMG.open(f"./plugin/KissKiss/KissFrames/{i}.png")
    gif_frame = IMG.new('RGB', (200, 200), (255, 255, 255))
    gif_frame.paste(bg, (0, 0))
    gif_frame.paste(target, (target_x[i - 1], target_y[i - 1]), target)
    gif_frame.paste(operator, (operator_x[i - 1], operator_y[i - 1]), operator)
    return numpy.array(gif_frame)


async def kiss(operator_id, target_id) -> None:


    if not os.path.exists("./images/KissKiss"):
        os.mkdir("./images/KissKiss")
    if not os.path.exists("./images/KissKiss/temp"):
        os.mkdir("./images/KissKiss/temp")
    operator_url = f'http://q1.qlogo.cn/g?b=qq&nk={str(operator_id)}&s=640'
    target_url = f'http://q1.qlogo.cn/g?b=qq&nk={str(target_id)}&s=640'
    gif_frames = []
    if str(operator_id) != "":  # admin自定义
        async with aiohttp.ClientSession() as session:
            async with session.get(url=operator_url) as resp:
                operator_img = await resp.read()
        operator = IMG.open(BytesIO(operator_img))
    else:
        operator = IMG.open("./plugin/KissKiss/avatar.png").convert("RGBA")

    if str(target_id) != "":  # admin自定义
        async with aiohttp.ClientSession() as session:
            async with session.get(url=target_url) as resp:
                target_img = await resp.read()
        target = IMG.open(BytesIO(target_img)).convert("RGBA")
    else:
        target = IMG.open("./plugin/KissKiss/avatar.png")

    operator = operator.resize((40, 40), IMG.ANTIALIAS)
    size = operator.size
    r2 = min(size[0], size[1])
    circle = IMG.new('L', (r2, r2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, r2, r2), fill=255)
    alpha = IMG.new('L', (r2, r2), 255)
    alpha.paste(circle, (0, 0))
    operator.putalpha(alpha)

    target = target.resize((50, 50), IMG.ANTIALIAS)
    size = target.size
    r2 = min(size[0], size[1])
    circle = IMG.new('L', (r2, r2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, r2, r2), fill=255)
    alpha = IMG.new('L', (r2, r2), 255)
    alpha.paste(circle, (0, 0))
    target.putalpha(alpha)

    for i in range(1, 14):
        gif_frames.append(await kiss_make_frame(operator, target, i))
    await save_gif(gif_frames, f'./images/KissKiss/temp/tempKiss-{operator_id}-{target_id}.gif', fps=25)
