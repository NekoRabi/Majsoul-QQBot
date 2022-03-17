from PIL import ImageDraw, ImageFont, Image as IMG
import numpy

score = 0


def getattribute() -> list:
    global score
    attributelist = []
    for i in range(6):
        choice = numpy.random.randint(4, dtype=int)
        attributelist.append(choice)
        if choice == 0:
            score += 10
        else:
            score = score + 25 - i * 25
    return attributelist


def getstart() -> list:
    global score
    startlist = []
    for i in range(5):
        choice = numpy.random.randint(5, dtype=int)
        startlist.append(choice)
        if i == 1:
            if choice == 0:
                score += 10
            elif choice == 2:
                score = score - 5
            elif score == 3:
                score = score - 15
            elif score == 4:
                score == score - 30
        elif i > 2:
            score += 10 - 5 * choice
        else:
            if choice < 2:
                score += 20 - 10 * choice
            else:
                score += choice * 25 - 50
    return startlist


def create_remakeimg(senderid):
    bgk = IMG.new('RGB', (1200, 800), (230, 220, 210))
    img = IMG.open('./plugin/Remake/remake.jpg').convert("RGBA")
    count = 0
    attrtext = img.crop((285, 1840, 525, 1910))
    bgk.paste(attrtext, (380, 10, 380 + attrtext.width, 10 + attrtext.height))
    for i in getattribute():
        temp = img.crop((150 + 145 * i, 1915 + 245 * count,
                         295 + 145 * i, 2160 + 245 * count))
        bgk.paste(temp, (145 * count, 100, 145 *
                         count + temp.width, 100 + temp.height))
        count += 1
    count = 0
    for i in getstart():
        if count == 2:
            temp = img.crop((35 + 146 * i, 120 + 364 * count,
                             190 + 146 * i, 390 + 364*count))
        elif count == 3:
            temp = img.crop((35 + 144 * i, 90 + 364 * count,
                            190 + 144 * i, 380 + 364*count))
        else:
            temp = img.crop((35 + 146 * i, 90 + 364 * count,
                            190 + 146 * i, 360 + 364*count))
        temp.save(fp=f'./images/Remake/{count}.png')
        bgk.paste(temp, (180 * count, 400, 180 *
                         count + temp.width, 400 + temp.height))
        count += 1
    bgk.save(fp=f'./images/Remake/{senderid}.png')
    print("图片创建完成")
