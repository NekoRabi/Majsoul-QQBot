from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


def whitebgk_blacktext(path: str,text: Iterable = None, fontsize: int = 20,
                       bold: bool = False):
    textlength = 0
    texts = []
    if bold:
        font = ImageFont.truetype(
            font='./data/fonts/MiSans-Bold.ttf', size=fontsize)
    else:
        font = ImageFont.truetype(
            font='./data/fonts/MiSans-Light.ttf', size=fontsize)
    if type(text) == str:
        texts = text.replace('\t','   ').split('\n')
    elif type(text) == dict:
        for k, v in text.items():
            texts.append(f'{k}:{v}'.replace('\t','   ').strip())
    elif type(text) in [list, set, tuple]:
        for item in text:
            texts.append(f'{item}'.replace('\t','   ').strip())
    for t in texts:
        if len(t.strip()) > textlength:
            textlength = len(t)

    bgimg = Image.new('RGB', ((textlength + 2) * fontsize, (len(texts) + 2) * (fontsize + 5)), (255, 255, 255))
    textdraw = ImageDraw.Draw(bgimg)
    for i in range(len(texts)):
        textdraw.text((fontsize, i * (fontsize + 5) + fontsize), text=f'{texts[i].strip()}',
                      font=font, fill=(0, 0, 0))
    bgimg.save(f'./images/{path}')
    return
