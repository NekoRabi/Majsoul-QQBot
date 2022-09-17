"""
:Author:  NekoRabi
:Create:  2022/9/18 3:00
:Update: /
:Describe: 简单的文本转图片工具
:Version: 0.0.1
"""
import base64
import random
from io import BytesIO
from typing import Union
from PIL import Image, ImageDraw, ImageFont

__all__ = ['text_to_image']


def get_random_color(alpha=False):
    """
    获取随机颜色

    Args:
        alpha: 是否要Alpha值

    Returns:形如 #ABC123 格式的颜色

    """
    color = '#'
    colorchoice = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'D', 'E', 'F']
    for i in range(6):
        color += f'{random.choice(colorchoice)}'
    if alpha:
        for i in range(2):
            color += f'{random.choice(colorchoice)}'
    return color


def text_to_image(text: Union[str, dict, set, list, tuple], path: str = None, fontsize: int = 30, bold: bool = False,
                  fontcolor: tuple = (0, 0, 0), bgkcolor=(255, 255, 255), backimgpath: str = None, imgbytes=None,
                  needtobase64=False):
    """
    将文本转换为图片

    Args:
        text: 要转换的内容
        path: 如果文件需要保存到本地,则填写保存路径
        fontsize: 字体大小
        bold: 是否加粗
        fontcolor: 字体颜色
        bgkcolor: 背景颜色，使用纯色填充
        backimgpath: 可以用背景图片来替换纯色，填入路径自动获取图片
        imgbytes: 图片字节流，可以用字节流来传递图片
        needtobase64: 是否需要返回base64化后的图片

    Returns: base64化的图片

    """
    textlength = 0
    texts = []
    if type(text) == str:
        texts = text.replace('\t', '   ').split('\n')
    elif type(text) == dict:
        for k, v in text.items():
            texts.append(f'{k}:{v}'.replace('\t', '   ').strip())
    elif type(text) in [list, set, tuple]:
        for item in text:
            texts.append(f'{item}'.replace('\t', '   ').strip())
    else:
        print("文字转图片输入了不支持的类型!")
        return
    for t in texts:
        if len(t.strip()) > textlength:
            textlength = len(t)
    if bold:
        font = ImageFont.truetype(
            font='./data/fonts/MiSans-Bold.ttf', size=fontsize)
    else:
        font = ImageFont.truetype(
            font='./data/fonts/MiSans-Light.ttf', size=fontsize)
    maxwidth = fontsize
    for item in texts:
        wd = font.getsize(item)[0]
        if wd > maxwidth:
            maxwidth = wd
    if backimgpath:
        bgimg = Image.open(f'{backimgpath}').convert("RGB")
    elif imgbytes:
        bgimg = Image.open(BytesIO(imgbytes)).convert("RGB")
    else:
        bgimg = Image.new('RGB', (maxwidth + 2 * (fontsize + 5), (len(texts) + 2) * (fontsize + 5)), bgkcolor)
    bx, by = bgimg.size
    textdraw = ImageDraw.Draw(bgimg)
    textdraw.line((1, 1, 1, 1), get_random_color(), 1)
    textdraw.line((bx - 2, by - 2, bx - 2, by - 2), get_random_color(), 1)
    textdraw.line((1, by - 2, 1, by - 2), get_random_color(), 1)
    textdraw.line((bx - 2, 1, bx - 2, 1), get_random_color(), 1)
    for i in range(len(texts)):
        textdraw.text((fontsize, i * (fontsize + 5) + fontsize), text=f'{texts[i].strip()}',
                      font=font, fill=fontcolor)
    if path:
        bgimg.save(f'./images/{path}')
    if needtobase64:
        img_bytes = BytesIO()
        bgimg.save(img_bytes, format='PNG')

        b_content = img_bytes.getvalue()
        imgcontent = base64.b64encode(b_content)
        return imgcontent
    return


def img_to_base64(path: str = None, PILimg: Image = None):
    """
    图片转换为base64的格式

    Args:
        path: 图片路径
        PILimg: PIL的图片

    Returns:base64的图片

    """
    img_bytes = BytesIO()

    if path:
        img = Image.open(path).convert("RGB")
        img.save(img_bytes, format='PNG')
    elif PILimg:
        PILimg.save(img_bytes, format='PNG')
    else:
        print('没有指定图片路径或给定图片')
        return None
    b_content = img_bytes.getvalue()
    imgcontent = base64.b64encode(b_content)
    return imgcontent
