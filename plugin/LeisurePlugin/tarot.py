import random
import base64
from io import BytesIO

import yaml
from PIL import Image, ImageDraw, ImageFont


def addfont(img: Image, text: str, position: tuple = (0, 0), textcolor=(0, 0, 0), size=20):
    textlist = text.split(';')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(
        font='./data/fonts/MiSans-Light.ttf', size=size)
    linetext = []
    temptext0 = ''
    temptext1 = ''
    for item in textlist:
        temptext0 += item.strip()+';'
        if font.getsize(temptext0)[0] > img.width:
            linetext.append(temptext1.strip())
            temptext0 = item
        temptext1 = temptext0
    if temptext0.strip() != '':
        linetext.append(temptext0.strip())
    for i in range(len(linetext)):
        draw.text((position[0], position[1] + i * (size + 2)), text=linetext[i], font=font, fill=textcolor)


def calculate_allfont_height(text, fontsize, maxwidth=948):
    textlist = text.split(';')
    font = ImageFont.truetype(
        font='./data/fonts/MiSans-Light.ttf', size=fontsize)
    linetext = []
    temptext0 = ''
    temptext1 = ''
    for item in textlist:
        temptext0 += item.strip()+';'
        if font.getsize(temptext0)[0] > maxwidth:
            linetext.append(temptext1.strip())
            temptext0 = item
        temptext1 = temptext0
    if temptext0.strip() != '':
        linetext.append(temptext0.strip())
    return len(linetext) * (fontsize + 2)


class TarotCard:

    def __init__(self, config):
        self.position = config['position']
        self.imageName = config['imageName']
        if self.position == 'positive':
            self.effective = config['positive']
            self.name = '正位 ' + config['name']
        else:
            self.effective = config['negative']
            self.name = '逆位 ' + config['name']
        self.buildcard()

    def buildcard(self, path=None):
        if not path:
            path = f'./images/tarot/{self.imageName}'
        source_card = Image.open(f'./data/Tarot/Images/{self.imageName}').convert("RGBA")
        width, height = source_card.size
        if self.position == 'negative':
            source_card = source_card.rotate(180)
        # width = width // 2
        # height = height // 2
        # source_card = source_card.resize((width, height))
        new_height = calculate_allfont_height(self.effective, 20, width) + calculate_allfont_height(self.name, 20,
                                                                                                    width) + 20
        bgk = Image.new('RGB', (width, height + new_height), (255, 255, 255))
        bgk.paste(source_card, (0, 0, width, height))
        addfont(bgk, text=self.name, position=(0, height))
        addfont(bgk, text=self.effective, position=(0, height + 30))
        img_bytes = BytesIO()

        bgk.save(img_bytes, format='JPEG')
        b_content = img_bytes.getvalue()
        self.imgcontent = base64.b64encode(b_content)


class TarotCards:

    def __init__(self):
        with open('./data/Tarot/data.yml', 'r', encoding='utf-8') as cfg:
            tarotdata = yaml.safe_load(cfg)
        self.imgdata = tarotdata['tarot']

    def drawcards(self, count=1):
        cardslist = []
        for i in range(count):
            cardinfo = random.choice(self.imgdata)
            # percent = random.random()
            # print(percent)
            if random.random() < 0.5:
                position = 'negative'
            else:
                position = 'positive'
            cardinfo['position'] = position
            cardslist.append(TarotCard(cardinfo))
        return cardslist
