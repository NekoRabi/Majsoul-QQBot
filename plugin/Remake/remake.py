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


def getstart(worlddifficulty: str = None) -> list:
    global score
    startlist = []
    for i in range(5):
        choice = numpy.random.randint(5, dtype=int)
        if i == 1:
            if choice == 0:
                score += 10
            elif choice == 2:
                score = score - 5
            elif score == 3:
                score = score - 15
            elif score == 4:
                score = score - 30
        elif i == 2:
            if worlddifficulty in ['peace', 'p', '0', '理想乡', '和平']:
                startlist.append(4)
                continue
            elif worlddifficulty in ['easy', 'e', '1', '桃园', '简单']:
                startlist.append(3)
                continue
            elif worlddifficulty in ['normal', 'common', '2', '普通', '一般']:
                startlist.append(2)
                continue
            elif worlddifficulty in ['hard', 'h', 'difficult', '3', '严酷', '困难']:
                startlist.append(1)
                continue
            elif worlddifficulty in ['Purgatory', 'Infernal', 'hell', 'vh', '4', '炼狱', '地狱', '超难']:
                startlist.append(0)
                continue
            else:
                score += choice * 25 - 50
        elif i > 2:
            score += 10 - 5 * choice
        else:
            if choice < 2:
                score += 20 - 10 * choice
            else:
                score += choice * 25 - 50
        startlist.append(choice)
    return startlist


def addfont(img: IMG, senderid):
    draw = ImageDraw.Draw(img)
    h1font = ImageFont.truetype(
        font='./plugin/Remake/font/MiSans-Bold.ttf', size=40)
    h4font = ImageFont.truetype(
        font='./plugin/Remake/font/MiSans-Light.ttf', size=20)
    titlefont = ImageFont.truetype(
        font='./plugin/Remake/font/MiSans-Bold.ttf', size=60)

    draw.text((10, 10), text=f'No.{senderid}', font=h4font, fill=(0, 0, 0))
    draw.text((370, 10), text='重生档案', font=titlefont, fill=(0, 0, 0))

    draw.text((10, 80), text='基础能力', font=h1font, fill=(0, 0, 0))
    draw.text((190, 100), text='(力量/魔力/智力/体质/魅力/运气)', font=h4font, fill=(0, 0, 0))

    draw.text((10, 400), text='世界设定', font=h1font, fill=(0, 0, 0))
    draw.text((190, 420), text='(种族/性别/局势/开局/审美)', font=h4font, fill=(0, 0, 0))


def create_remakeimg(senderid, basic_score=30, worlddifficulty=None):
    bgk = IMG.new('RGB', (900, 800), (230, 220, 210))
    img = IMG.open('./plugin/Remake/remake.jpg').convert("RGBA")
    count = 0
    for i in getattribute():
        temp = img.crop((150 + 145 * i, 1915 + 245 * count,
                         295 + 145 * i, 2165 + 245 * count))
        bgk.paste(temp, (145 * count, 150, 145 *
                         count + temp.width, 150 + temp.height))
        count += 1
    count = 0
    for i in getstart(worlddifficulty):
        if count == 2:
            temp = img.crop((35 + 146 * i, 120 + 364 * count,
                             190 + 146 * i, 390 + 364 * count))
        elif count == 3:
            temp = img.crop((35 + 144 * i, 90 + 364 * count,
                             190 + 144 * i, 380 + 364 * count))
        else:
            temp = img.crop((35 + 146 * i, 90 + 364 * count,
                             190 + 146 * i, 360 + 364 * count))
        bgk.paste(temp, (145 * count, 460, 145 *
                         count + temp.width, 460 + temp.height))
        count += 1

    addfont(bgk, senderid=senderid)
    bgk.save(fp=f'./images/Remake/{senderid}.png')
