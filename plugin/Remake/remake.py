from PIL import ImageDraw, ImageFont, Image as IMG
import numpy

score = 0


def getattribute() -> list:
    global score
    attributelist = []
    for i in range(6):
        attributelist.append(numpy.random.randint(4, dtype=int))
        if i == 0:
            score += 10
        else:
            score = score + 25 - i * 25
    print(attributelist)
    return attributelist


def create_remakeimg(senderid):
    bgk = IMG.new('RGB', (1000, 500), (230, 220, 210))
    img = IMG.open('./plugin/Remake/remake.jpg').convert("RGBA")
    count = 0
    attrtext = img.crop((285, 1840, 525, 1910))
    bgk.paste(attrtext, (380, 10, 380 + attrtext.width, 10+attrtext.height))
    for i in getattribute():
        temp = img.crop((150 + 145 * i, 1915 + 245 * count,
                         295 + 145 * i, 2160 + 245 * count))

        temp.save(fp=f'./images/Remake/{count}.png')
        bgk.paste(temp, (145 * count, 100, 145 *
                         count + temp.width, 100 + temp.height))
        count += 1
    bgk.save(fp=f'./images/Remake/{senderid}.png')
    print("图片创建完成")
