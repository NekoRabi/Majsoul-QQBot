import random
import yaml
from tqdm import trange
from PIL import Image as IMG


def drawcards():
    with open(r'./drawcards.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        lottery = config['lottery']
        up_person = config['up']['person']
        up_decoration = config['up']['decoration']
        decoration = lottery['decoration']
        gift = lottery['gift']
        person = lottery['person']
    baodi = False
    results = []
    resultsmsg = "\n您的抽卡结果依次为:\n"
    drawcounts = {'0gift': 0, '1gift': 0,
                  '2gift': 0, 'person': 0, 'decoration': 0}
    for count in range(10):
        luck = random.random() * 100
        if count == 9 and drawcounts['2gift'] == 0:
            gift_index = random.randint(0, 5) * 3 + 2
            gf = gift['item'][gift_index]['name']
            gfrare = gift['item'][gift_index]['rare']
            drawcounts[str(gfrare) + 'gift'] += 1
            results.append(gift['item'][gift_index]['url'])
            resultsmsg += gf
            resultsmsg += '\n\n已触发保底。'

            break
        if luck < 5:
            person_index = random.randint(0, person['length'] - 1)
            ps = person['item'][person_index]['name']
            drawcounts['person'] += 1
            psrare = person['item'][person_index]['rare']
            results.append(person['item'][person_index]['url'])
            resultsmsg += ps
        elif luck < 15:
            dec_index = random.randint(0, decoration['length'] - 1)
            dec = decoration['item'][dec_index]['name']
            drawcounts['decoration'] += 1
            results.append(decoration['item'][dec_index]['url'])
            resultsmsg += dec
        else:
            gift_index = random.randint(0, 7) * 3
            gifttype = random.randint(0, 10)
            if gifttype < 3:
                gift_index += 2
            # elif gifttype < 9:
            else:
                gift_index += 1
            if count == 9 and drawcounts['2gift'] == 0:
                if gift['item'][gift_index]['rare'] == 2:
                    break
                else:
                    gift_index = random.randint(0, 5) * 3 + 2
                    resultsmsg += '\n\n已触发保底。'
            gf = gift['item'][gift_index]['name']
            gfrare = gift['item'][gift_index]['rare']
            drawcounts[str(gfrare) + 'gift'] += 1
            results.append(gift['item'][gift_index]['url'])
            resultsmsg += gf
        if not count == 9:
            resultsmsg += '\n'
    return dict(drawcounts=drawcounts, results=results, resultsmsg=resultsmsg, baodi=baodi, error=False)


def mergeimgs(urls: list, uuid: int) -> IMG:
    imgback = IMG.new("RGB", (1020, 420), (255, 255, 255))
    for i in range(10):
        img = IMG.open(f'./{urls[i]}').convert("RGBA")
        img = img.resize((180, 180), IMG.ANTIALIAS)
        r, g, b, a = img.split()
        posx = 20 + (i % 5) * 200
        posy = 20 + (i // 5) * 200
        imgback.paste(img, (posx, posy, posx + img.size[0], posy + img.size[1]), mask=a)
    imgback.save(fp=f"./Images/temp/{uuid}.png")
    return imgback


for i in trange(100):
    result = drawcards()
    mergeimgs(result.get('results'), i)
