import json
import os

shupai_dic = {}
zipai_dic = {}
log_tmp = []
tsumo_flag = False
cnt_ten = 0
cnt_ron = 0
cnt_tsumo = 0
cnt_kyoku = 0


class pattern:
    mentsu = 0
    tatsu = 0
    head = 0
    mentsu_h = 0
    tatsu_h = 0

    def __str__(self):
        return f'mentsu={self.mentsu},tatse={self.tatsu},head={self.head},mentsu_h={self.mentsu_h},tatsu_h={self.tatsu_h}'


def import_data():
    with open("shupai.txt") as shupai:
        info = shupai.readline()
        for i in range(0, 405350):
            key = int(info[i * 13:i * 13 + 8])
            pat = pattern()
            pat.mentsu = int(info[i * 13 + 8:i * 13 + 9])
            pat.tatsu = int(info[i * 13 + 9:i * 13 + 10])
            pat.head = int(info[i * 13 + 10:i * 13 + 11])
            pat.mentsu_h = int(info[i * 13 + 11:i * 13 + 12])
            pat.tatsu_h = int(info[i * 13 + 12:i * 13 + 13])
            shupai_dic[key] = pat
    with open("zipai.txt") as zipai:
        info = zipai.readline()
        for i in range(0, 43130):
            key = int(info[i * 12:i * 12 + 7])
            pat = pattern()
            pat.mentsu = int(info[i * 12 + 7:i * 12 + 8])
            pat.tatsu = int(info[i * 12 + 8:i * 12 + 9])
            pat.head = int(info[i * 12 + 9:i * 12 + 10])
            pat.mentsu_h = int(info[i * 12 + 10:i * 12 + 11])
            pat.tatsu_h = int(info[i * 12 + 11:i * 12 + 12])
            zipai_dic[key] = pat


def printf(hands):
    for pai in hands:
        if pai <= 19:
            print(str(pai - 10) + "m", end="")
        if 29 >= pai >= 21:
            print(str(pai - 20) + "p", end="")
        if 39 >= pai >= 31:
            print(str(pai - 30) + "s", end="")
        if pai >= 41:
            print(str(pai - 40) + "z", end="")
    print()


def get_hands(pos):
    hands = log_tmp[pos * 3 + 4]
    for i in range(0, len(log_tmp[pos * 3 + 5])):
        if i >= len(log_tmp[pos * 3 + 6]):
            global tsumo_flag
            tsumo_flag = True
            break
        riichi_flag = False
        if isinstance(log_tmp[pos * 3 + 6][i], str):
            log_tmp[pos * 3 + 6][i] = int(log_tmp[pos * 3 + 6][i][1:2])
            riichi_flag = True
        if isinstance(log_tmp[pos * 3 + 5][i], int):
            for j in range(0, len(hands)):
                if hands[j] == log_tmp[pos * 3 + 6][i]:
                    hands[j] = log_tmp[pos * 3 + 5][i]
                    break
        else:
            if log_tmp[pos * 3 + 5][i].find('p') != -1:
                for j in range(0, len(hands)):
                    if hands[j] == log_tmp[pos * 3 + 6][i]:
                        hands[j] = int(log_tmp[pos * 3 + 5][i][
                                       log_tmp[pos * 3 + 5][i].find('p') + 1:log_tmp[pos * 3 + 5][i].find('p') + 3])
                        break
            else:
                if log_tmp[pos * 3 + 5][i].find('c') != -1:
                    for j in range(0, len(hands)):
                        if hands[j] == log_tmp[pos * 3 + 6][i]:
                            hands[j] = int(log_tmp[pos * 3 + 5][i][
                                           log_tmp[pos * 3 + 5][i].find('c') + 1:log_tmp[pos * 3 + 5][i].find('c') + 3])
                            break
    hands.sort()
    return hands


def get_normal_syaten(mask_code):
    wan = mask_code & ((1 << 27) - 1)
    pin = (mask_code >> 27) & ((1 << 27) - 1)
    suo = (mask_code >> 54) & ((1 << 27) - 1)
    zi = (mask_code >> 81) & ((1 << 21) - 1)

    base_mentsu = shupai_dic.get(wan).mentsu + shupai_dic.get(pin).mentsu + shupai_dic.get(suo).mentsu + zipai_dic.get(
        zi).mentsu
    base_tatsu = shupai_dic.get(wan).tatsu + shupai_dic.get(pin).tatsu + shupai_dic.get(suo).tatsu + zipai_dic.get(
        zi).tatsu
    syaten = min(4 - base_mentsu, base_tatsu) + base_mentsu * 2

    if shupai_dic.get(wan).head != 0:
        now_mentsu = base_mentsu - shupai_dic.get(wan).mentsu + shupai_dic.get(wan).mentsu_h
        now_tatsu = base_tatsu - shupai_dic.get(wan).tatsu + shupai_dic.get(wan).tatsu_h
        now_syaten = min(4 - now_mentsu, now_tatsu) + now_mentsu * 2 + 1
        syaten = max(syaten, now_syaten)

    if shupai_dic.get(pin).head != 0:
        now_mentsu = base_mentsu - shupai_dic.get(pin).mentsu + shupai_dic.get(pin).mentsu_h
        now_tatsu = base_tatsu - shupai_dic.get(pin).tatsu + shupai_dic.get(pin).tatsu_h
        now_syaten = min(4 - now_mentsu, now_tatsu) + now_mentsu * 2 + 1
        syaten = max(syaten, now_syaten)

    if shupai_dic.get(suo).head != 0:
        now_mentsu = base_mentsu - shupai_dic.get(suo).mentsu + shupai_dic.get(suo).mentsu_h
        now_tatsu = base_tatsu - shupai_dic.get(suo).tatsu + shupai_dic.get(suo).tatsu_h
        now_syaten = min(4 - now_mentsu, now_tatsu) + now_mentsu * 2 + 1
        syaten = max(syaten, now_syaten)

    if zipai_dic.get(zi).head != 0:
        now_mentsu = base_mentsu - zipai_dic.get(zi).mentsu + zipai_dic.get(zi).mentsu_h
        now_tatsu = base_tatsu - zipai_dic.get(zi).tatsu + zipai_dic.get(zi).tatsu_h
        now_syaten = min(4 - now_mentsu, now_tatsu) + now_mentsu * 2 + 1
        syaten = max(syaten, now_syaten)

    return 8 - syaten


def check_hu(mask_code):
    wan = mask_code & ((1 << 27) - 1)
    pin = (mask_code >> 27) & ((1 << 27) - 1)
    suo = (mask_code >> 54) & ((1 << 27) - 1)
    zi = (mask_code >> 81) & ((1 << 21) - 1)

    if shupai_dic.get(wan).head != 0:
        if shupai_dic.get(wan).mentsu_h + shupai_dic.get(pin).mentsu + shupai_dic.get(suo).mentsu + zipai_dic.get(
                zi).mentsu == 4:
            return 1
    if shupai_dic.get(pin).head != 0:
        if shupai_dic.get(wan).mentsu + shupai_dic.get(pin).mentsu_h + shupai_dic.get(suo).mentsu + zipai_dic.get(
                zi).mentsu == 4:
            return 1
    if shupai_dic.get(suo).head != 0:
        if shupai_dic.get(wan).mentsu + shupai_dic.get(pin).mentsu + shupai_dic.get(suo).mentsu_h + zipai_dic.get(
                zi).mentsu == 4:
            return 1
    if zipai_dic.get(zi).head != 0:
        if shupai_dic.get(wan).mentsu + shupai_dic.get(pin).mentsu + shupai_dic.get(suo).mentsu + zipai_dic.get(
                zi).mentsu_h == 4:
            return 1
    return 0


def get_num(mask_code, i):
    return (mask_code >> (i * 3)) & 7


def add_mask(mask_code, i):
    return mask_code + (1 << (i * 3))


def del_mask(mask_code, i):
    return mask_code - (1 << (i * 3))


def printf_pai(mask_code):
    pai = ""
    kind_list = ['m', 'p', 's', 'z']
    for i in range(0, 37):
        if get_num(mask_code, i) > 0:
            for j in range(0, get_num(mask_code, i)):
                pai += str((i % 9) + 1)
        if i % 9 == 8:
            pai += kind_list[i // 9]
    print(pai)


def base_machi_kind(mask_code, i):  # 1 ryoumenn machi; 2 kancyan machi; 3 pencyan machi; 4 syanpon machi;5 danki machi
    if i <= 6:
        if get_num(mask_code, i + 1) >= 1 and get_num(mask_code, i + 2) >= 1:
            tmp_mask_code = del_mask(mask_code, i + 1)
            tmp_mask_code = del_mask(tmp_mask_code, i + 2)
            if shupai_dic[mask_code].mentsu == shupai_dic[tmp_mask_code].mentsu \
                    and shupai_dic[mask_code].tatsu == shupai_dic[tmp_mask_code].tatsu + 1:
                if i == 6:
                    return 3
                else:
                    return 1

    if i >= 2:
        if get_num(mask_code, i - 1) >= 1 and get_num(mask_code, i - 2) >= 1:
            tmp_mask_code = del_mask(mask_code, i - 1)
            tmp_mask_code = del_mask(tmp_mask_code, i - 2)
            if shupai_dic[mask_code].mentsu == shupai_dic[tmp_mask_code].mentsu \
                    and shupai_dic[mask_code].tatsu == shupai_dic[tmp_mask_code].tatsu + 1:
                if i == 2:
                    return 3
                else:
                    return 1

    if 0 < i < 8:
        if get_num(mask_code, i + 1) >= 1 and get_num(mask_code, i - 1) >= 1:
            tmp_mask_code = del_mask(mask_code, i + 1)
            tmp_mask_code = del_mask(tmp_mask_code, i - 1)
            if shupai_dic[mask_code].mentsu == shupai_dic[tmp_mask_code].mentsu \
                    and shupai_dic[mask_code].tatsu == shupai_dic[tmp_mask_code].tatsu + 1:
                return 2

    if get_num(mask_code, i) >= 2:
        tmp_mask_code = del_mask(mask_code, i)
        tmp_mask_code = del_mask(tmp_mask_code, i)
        if shupai_dic[mask_code].mentsu == shupai_dic[tmp_mask_code].mentsu \
                and shupai_dic[mask_code].tatsu == shupai_dic[tmp_mask_code].tatsu + 1:
            return 4

    return 5


def get_machi_kind(mask_code, i):
    if i < 9:
        return base_machi_kind(mask_code & ((1 << 27) - 1), i)
    if i < 18:
        return base_machi_kind((mask_code >> 27) & ((1 << 27) - 1), i - 9)
    if i < 27:
        return base_machi_kind((mask_code >> 54) & ((1 << 27) - 1), i - 18)
    if i < 34:
        zi = (mask_code >> 81) & ((1 << 21) - 1)
        if get_num(zi, i - 27) == 2:
            return 4
        else:
            return 5


def get_machi_set(mask_code):
    machi_set_now = {}
    for i in range(0, 34):
        if get_num(mask_code, i) < 4:
            tmp_mask_code = add_mask(mask_code, i)
            if check_hu(tmp_mask_code) == 1:
                machi_set_now[i] = get_machi_kind(mask_code, i)
    return machi_set_now


def analysis(machi_kind, hupai, kind):  # kind: 0 tsumo;1 ryoumenn;2 kancyan;3 pencyan;4 syanpon;5 danki
    pai = -1
    pai2 = -1
    global cnt_ron
    global cnt_tsumo
    global cnt_ten
    if isinstance(hupai, str):
        map_dic = {'m': 1, 'p': 2, 's': 3, 'z': 4}
        if hupai[0] == '0':
            pai = 50 + map_dic[hupai[1]]
        else:
            pai = int(hupai[0]) + map_dic[hupai[1]] * 10
            pai2 = int(hupai[0]) - 1 + (map_dic[hupai[1]] - 1) * 9
    else:
        pai = hupai
        pai2 = (hupai // 10 - 1) * 9 + (hupai % 10 - 1)

    if tsumo_flag:  # check some information for tsumo
        if kind == 0:
            pass
        else:
            return
    else:  # check some information for ron
        if kind == 0:
            return
        winpos = []
        losepos = -1
        for i in range(0, 4):
            if log_tmp[16][1][i] > 0:
                winpos.append(i)
            if log_tmp[16][1][i] < 0:
                losepos = i
        chongpai = log_tmp[losepos * 3 + 6][-1]
        cnt_tmp = 0
        for i in range(0, 4):
            if machi_kind[i].get(pai2) is not None:
                if machi_kind[i].get(pai2) == kind:
                    cnt_tmp += 1
        cnt_ten += cnt_tmp
        if chongpai == pai:
            cnt_ron += cnt_tmp


def main():
    import_data()
    global cnt_kyoku

    file = "E:\\mahjong data\\data\\2017\\tmpall\\"
    for root, dirs, files in os.walk(file):
        for file_name in files:
            with open(file + file_name, "r", encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    cnt_kyoku += 1
                    global tsumo_flag
                    tsumo_flag = False
                    json_tmp = json.loads(line)
                    global log_tmp
                    log_tmp = json_tmp["log"][0]
                    if log_tmp[16][0] != '和了':
                        continue

                    # for i in range(0, len(log_tmp)):
                    #     print(i, log_tmp[i])
                    all_last_hand = []
                    for i in range(0, 4):
                        all_last_hand.append(get_hands(i))

                    code = [0, 0, 0, 0]
                    for i in range(0, 4):
                        cnt = [0] * 40
                        for j in range(0, len(all_last_hand[i])):  # man 0~8 pin 9~17 suo 18~26 zi 27~33
                            if all_last_hand[i][j] <= 19:
                                cnt[all_last_hand[i][j] - 11] += 1
                                continue
                            if all_last_hand[i][j] <= 29:
                                cnt[all_last_hand[i][j] - 12] += 1
                                continue
                            if all_last_hand[i][j] <= 39:
                                cnt[all_last_hand[i][j] - 13] += 1
                                continue
                            if all_last_hand[i][j] <= 47:
                                cnt[all_last_hand[i][j] - 14] += 1
                                continue
                            if all_last_hand[i][j] <= 53:
                                cnt[(all_last_hand[i][j] - 51) * 9 + 4] += 1
                                continue
                        for j in range(0, 40):
                            code[i] |= cnt[j] << (j * 3)

                    syaten = [0, 0, 0, 0]
                    for i in range(0, 4):
                        syaten[i] = get_normal_syaten(code[i])

                    machi_kind = [{}, {}, {}, {}]
                    for i in range(0, 4):
                        if syaten[i] == 0:
                            machi_kind[i] = get_machi_set(code[i])
                    # analysis(machi_kind, "1s", 4)
                    # analysis(machi_kind, "1p", 4)
                    # analysis(machi_kind, "1m", 4)
    print("sum:", cnt_kyoku, "局")
    if cnt_ten != 0:
        print(cnt_ten, cnt_ron, cnt_ron / cnt_ten)
    else:
        print("no enough data")


if __name__ == '__main__':
    # main()
    # import_data()       0b11001001001001001001001100
    # # get_normal_syaten(0b1000010010010010010010010110000000000000000000000000000000000000000000000000000000000000000000000000)
    # print(get_normal_syaten(52728396))
    print(bin(52728396))

