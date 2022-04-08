import os

from PIL import Image, ImageDraw, ImageFont


def makebwimg(imgname, text: str = ""):
    filename = os.path.splitext(imgname)[0]
    suffixname = os.path.splitext(imgname)[-1]
    if suffixname == '.jpg':
        suffixname = '.jpeg'
    img = Image.open(f'./images/tempimg/{filename}{suffixname}').convert('L')
    width = img.width
    height = img.height
    if width > height:
        fontsize = height//10
    else:
        fontsize = width//10
    textlength = len(text)
    if textlength == 0:
        textlength = 1
    if fontsize > width / textlength:
        fontsize = width // textlength
    font = ImageFont.truetype(
        font='./plugin/ImgOperation/MiSans-Bold.ttf', size=fontsize)
    bgimg = Image.new('RGB', (width, height + 20 + fontsize), (0, 0, 0))
    bgimg.paste(img, (0, 0, width, height))
    textdraw = ImageDraw.Draw(bgimg)
    textdraw.text(((width - fontsize * textlength) / 2, height + 10), text=f'{text}', font=font, fill=(255,255,255))
    bgimg.save(f'./images/tempimg/{filename}{os.path.splitext(imgname)[-1]}')


def deletesource(imgname):
    filename = os.path.splitext(imgname)[0]
    suffixname = os.path.splitext(imgname)[-1]
    if suffixname == '.jpg':
        suffixname = '.jpeg'
    if os.path.exists(f'./images/tempimg/{filename}{suffixname}'):
        os.remove(f'./images/tempimg/{filename}{suffixname}')
    if os.path.exists(f'./images/tempimg/{imgname}'):
        os.remove(f'./images/tempimg/{imgname}')