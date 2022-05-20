from io import BytesIO
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


def text_to_image(path: str, text: Iterable = None, fontsize: int = 20,
                  bold: bool = False, fontcolor: tuple = (0, 0, 0), bgkcolor=(255, 255, 255),
                  backimgpath: str = None, imgbytes=None):
    textlength = 0
    texts = []
    if bold:
        font = ImageFont.truetype(
            font='./data/fonts/MiSans-Bold.ttf', size=fontsize)
    else:
        font = ImageFont.truetype(
            font='./data/fonts/MiSans-Light.ttf', size=fontsize)
    if type(text) == str:
        texts = text.replace('\t', '   ').split('\n')
    elif type(text) == dict:
        for k, v in text.items():
            texts.append(f'{k}:{v}'.replace('\t', '   ').strip())
    elif type(text) in [list, set, tuple]:
        for item in text:
            texts.append(f'{item}'.replace('\t', '   ').strip())
    for t in texts:
        if len(t.strip()) > textlength:
            textlength = len(t)
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
        bgimg = Image.new('RGB', (maxwidth+ 2 * (fontsize+5), (len(texts) + 2) * (fontsize + 5)), bgkcolor)
    textdraw = ImageDraw.Draw(bgimg)
    for i in range(len(texts)):
        textdraw.text((fontsize, i * (fontsize + 5) + fontsize), text=f'{texts[i].strip()}',
                      font=font, fill=fontcolor)
    bgimg.save(f'./images/{path}')
    return
