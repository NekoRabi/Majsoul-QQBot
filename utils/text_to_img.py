from collections import Iterable

from PIL import Image, ImageDraw, ImageFont


def whitebgk_blacktext(path: str, textline: str = None, textiterable: Iterable = None, fontsize: int = 20, bold: bool = False):
    texts = textline.split('\n')
    textlength = 0
    for text in texts:
        text = text.strip()
        if len(text) > textlength:
            textlength = len(text)
    if bold:
        font = ImageFont.truetype(
            font='./data/fonts/MiSans-Bold.ttf', size=fontsize)
    else:
        font = ImageFont.truetype(
            font='./data/fonts/MiSans-Light.ttf', size=fontsize)
    bgimg = Image.new('RGB', (textlength * fontsize + 40, len(texts) * (fontsize + 5) + 40), (255, 255, 255))
    textdraw = ImageDraw.Draw(bgimg)
    for i in range(len(texts)):
        textdraw.text((20, i * (fontsize + 5) + 20), text=f'{texts[i].strip()}',
                      font=font,
                      fill=(0, 0, 0))
    bgimg.save(f'./images/{path}')
    return
