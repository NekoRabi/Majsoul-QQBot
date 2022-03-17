import math
import random
import sqlite3
import time

import requests
import yaml
import os


def getrare(elem):
    return elem['rare']


def initYaml():
    dirpath = './Images'
    list_dir = os.listdir(dirpath)
    list1 = {}
    for item in list_dir:
        templist = []
        lenth = 0
        index = 0
        rare = 0
        if item == '宝玉':
            continue
        elif item == 'decoration':
            rare = 3
        elif item == 'person':
            rare = 4
        print(item)
        for name in os.listdir(dirpath + '/' + item):
            if item == 'gift':
                raret = int(name[0:2]) % 3
                namet = name[3:-4]
                indext = int(name[0:2])
                print(f'name={namet},index={indext},rare={raret}')
                templist.append(
                    {'name': namet, 'type': item, 'rare': raret, 'url': (dirpath + '/' + item + '/' + name),
                     'index': indext})
            else:
                templist.append(
                    {'name': name[:-4], 'type': item, 'rare': rare, 'url': (dirpath + '/' + item + '/' + name),
                     'index': index})
                index += 1
            lenth += 1
        for i in range(len(templist)):
            templist[i]['index'] = i
        list1[f'{item}'] = {'item': templist, 'length': lenth}

    f = open(r'./config.yml', 'w')
    yaml.dump({'lottery': list1, 'up': {'person': [''], 'decoration': ['']}}, f, allow_unicode=True,encoding='GBK')
    f.close()
    f = open(r'./config.yml')
    y = yaml.safe_load(f)
    print(y)
    f.close()


def drawcards(up=False):
    baodi = False
    drawcounts = {'0gift': 0, '1gift': 0, '2gift': 0, 'person': 0, 'decoration': 0}
    results = []
    resultsmsg = "您的抽卡结果依次为:\n"
    # with open(r'./plugin/MajSoulInfo/config.yml', 'r') as f:
    with open(r'./config.yml', 'r') as f:

        config = yaml.safe_load(f)
        lottery = config['lottery']
        up_person = config['up']['person']
        up_decoration = config['up']['decoration']
        decoration = lottery['decoration']
        gift = lottery['gift']
        person = lottery['person']
        # print(decoration)
        # print(gift['length'])
        # print(person)
        for count in range(10):
            luck = random.randint(0, 100)
            if count == 9 and drawcounts['2gift'] == 0:
                print("出保底喽")
                gift_index = random.randint(0, 5) * 3 + 2
                gf = gift['item'][gift_index]['name']
                gfrare = gift['item'][gift_index]['rare']
                drawcounts[str(gfrare) + 'gift'] += 1
                results.append(gift['item'][gift_index]['url'])
                resultsmsg += gf
                resultsmsg += '\n\n已触发保底。'
                break
            if luck < 5:
                if up:
                    if random.randint(0, 100) < 59:
                        person_name = random.choice(up_person)
                        ps = person_name + '\n'
                        drawcounts['person'] += 1
                        results.append(f'./Images/person/{person_name}.png')
                        resultsmsg += ps
                        continue

                person_index = random.randint(0, person['length'] - 1)
                ps = person['item'][person_index]['name']
                drawcounts['person'] += 1
                results.append(person['item'][person_index]['url'])
                resultsmsg += ps
            elif luck < 15:
                if up:
                    if random.randint(0, 100) < 49:
                        decoration_name = random.choice(up_decoration)
                        dec = decoration_name + '\n'
                        drawcounts['decoration'] += 1
                        results.append(f'./Images/decoration/{decoration_name}.jpg')
                        resultsmsg += dec
                        continue
                dec_index = random.randint(0, decoration['length'] - 1)
                dec = decoration['item'][dec_index]['name']
                drawcounts['decoration'] += 1
                results.append(decoration['item'][dec_index]['url'])
                resultsmsg += dec
            else:
                gift_index = random.randint(0, 7) * 3
                gifttype = random.randint(0, 8)
                if gifttype < 1:
                    gift_index += 2
                # elif gifttype < 3:
                else:
                    gift_index += 1
                if count == 9 and drawcounts['2gift'] == 0:
                    if gift['item'][gift_index]['rare'] == 2:
                        break
                    else:
                        print("出保底喽")
                        gift_index = random.randint(0, 5) * 3 + 2
                        resultsmsg += '\n\n已触发保底。'
                gf = gift['item'][gift_index]['name']
                gfrare = gift['item'][gift_index]['rare']
                drawcounts[str(gfrare) + 'gift'] += 1
                results.append(gift['item'][gift_index]['url'])
                resultsmsg += gf
            if not count == 9:
                resultsmsg += '\n'
    print(resultsmsg)
    return dict(drawcounts=drawcounts, results=results, resultsmsg=resultsmsg, baodi=baodi)


def getpaipu():
    nowtime = time.time()
    nowtime = math.floor(nowtime / 10) * 10000 + 9999
    print(nowtime)
    playerid = 16721423
    if playerid:
        xhr = requests.get(
            f"https://ak-data-1.sapk.ch/api/v2/pl4/player_records/{playerid}/{nowtime}/1262304000000"
            "?limit=5&mode=12&descending=true&tag=304")
        # xhr = requests.get(
        #     f"https://ak-data-1.sapk.ch/api/v2/pl3/player_records/{playerid}/{nowtime}/1262304000000?limit=10"
        #     f"&mode=21&descending=true&tag=304")
        # print(xhr.text)
        content = eval(xhr.text)
        print(content)


def jiexi(paipuText: list):
    hasNewPaipu = False
    playerid = 16721423
    cx = sqlite3.connect('../../database/majsoul.sqlite')
    cursor = cx.cursor()
    cursor.execute("create table IF NOT EXISTS paipu("
                   "id integer primary key,"
                   "uuid varchar(50) UNIQUE,"
                   "watchid integer,"
                   "startTime varchar(50),"
                   "endTime varchar(50),"
                   "player1 varcher(50),"
                   "player2 varcher(50),"
                   "player3 varcher(50),"
                   "player4 varcher(50)"
                   ")")
    cx.commit()
    for item in paipuText:
        # print(item)
        paipuurl = f'https://game.maj-soul.com/1/?paipu={item["uuid"]}'
        startTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item["startTime"]))
        endTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item["endTime"]))
        print(paipuurl)
        print("开始时间:" + startTime, end="\t")
        print("\t结束时间:" + endTime)
        players = item['players']
        for player in players:
            print(f"{player['nickname']}:{player['score']}")
        try:
            cursor.execute(
                "insert into paipu(uuid,watchid,startTime,endTime,player1,player2,player3,player4) values(?,?,?,?,?,?,?,?)",
                (item['uuid'], playerid, startTime, endTime, f"{players[0]['nickname']}:{players[0]['score']}",
                 f"{players[1]['nickname']}:{players[1]['score']}", f"{players[2]['nickname']}:{players[2]['score']}",
                 f"{players[3]['nickname']}:{players[3]['score']}"))
            cx.commit()
        except:
            print(f"存在uuid={item['uuid']}的记录")
    cursor.close()
    cx.close()


initYaml()
# drawcards(True)

# getpaipu()

# jiexi()
# for i in range(30):
#     xhr = requests.get("https://ak-data-1.sapk.ch/api/v2/pl4/player_records/8560870/1645379039999/1262304000000?limit=171&mode=16,12,9&descending=true")
#     print(xhr)
