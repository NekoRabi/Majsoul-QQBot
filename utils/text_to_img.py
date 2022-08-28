import base64
import random
from io import BytesIO
from typing import Union
from PIL import Image, ImageDraw, ImageFont

__all__ = ['text_to_image']


def _get_random_color():
    color = '#'
    colorchoice = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'D', 'E', 'F']
    for i in range(6):
        color += f'{random.choice(colorchoice)}'
    return color


def text_to_image(text: Union[str, dict, set, list, tuple] = None, path: str = None, fontsize: int = 30,
                  bold: bool = False, fontcolor: tuple = (0, 0, 0), bgkcolor=(255, 255, 255),
                  backimgpath: str = None, imgbytes=None, needtobase64=False):
    """

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
    textdraw.line((1, 1, 1, 1), _get_random_color(), 1)
    textdraw.line((bx - 2, by - 2, bx - 2, by - 2), _get_random_color(), 1)
    textdraw.line((1, by - 2, 1, by - 2), _get_random_color(), 1)
    textdraw.line((bx - 2, 1, bx - 2, 1), _get_random_color(), 1)
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
    img_bytes = BytesIO()

    if path:
        img = Image.open(path).convert("RGB")
        img.save(img_bytes, format='JPEG')
    elif PILimg:
        PILimg.save(img_bytes, format='JPEG')
    else:
        print('没有指定图片路径或给定图片')
        return None
    b_content = img_bytes.getvalue()
    imgcontent = base64.b64encode(b_content)
    return imgcontent
