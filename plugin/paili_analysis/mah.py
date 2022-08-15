import pickle
from plugin.paili_analysis.utils import *
from plugin.paili_analysis.dfs import *

from mirai import GroupMessage, Plain

# from plugin.preinit.create_bot import bot
from core import bot

from utils.MessageChainBuilder import messagechain_builder

from utils.text_to_img import text_to_image


# 焰胡
def yanhu(hc: str):
    hc = convert_hc_to_list(hc)
    if sum(hc) != 14:
        raise ValueError("请传入14位手牌.")
    with open("ron_set.pickle", "rb") as f:
        ron_set = pickle.load(f)
    ehc = encode_hand_cards(hc)
    if ehc in ron_set:
        print("RON!")
    else:
        print("nothing happens.")


def calc_shanten_13(hc=None, hc_list=None):
    if hc_list:
        hc = hc_list
    else:
        hc = convert_hc_to_list(hc)
    if sum(hc) != 13:
        raise ValueError("请传入13位手牌.")
    m = get_mianzi(hc)
    # 没有面子拆解的情况 传入空数组
    if not m:
        m = [[]]
    # 最大8向听
    xt_list = [
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    ]
    for x in m:
        # 面子数量
        mianzi_count = len(x)
        thc = get_trimed_hc(hc.copy(), x)
        dazi_list = get_dazi(thc)
        da_list_xt_min = 999
        for dazi in dazi_list:
            # 是否有雀头
            if_quetou = 0
            for y in dazi:
                if y[1] > 0:
                    if_quetou = 1
            dazi_count = len(dazi)
            xt = calc_xiangting(mianzi_count, dazi_count, if_quetou)
            if xt <= da_list_xt_min:
                tthc = get_trimed_dazi(thc.copy(), dazi)
                # 孤张
                guzhang_list = get_guzhang(tthc)
                # 进张
                tenpai = get_tenpai_from_dazi(dazi, xt)

                # TODO 或许有更多情况
                # 向听为0
                if xt == 0:
                    # 无搭子 即单吊
                    if not dazi:
                        tenpai += guzhang_list
                # 向听数为1
                if xt == 1:
                    if dazi_count == 1:
                        if if_quetou:
                            ga = get_guzhang_around(guzhang_list)
                            tenpai += ga
                            tenpai += guzhang_list
                        else:
                            tenpai += guzhang_list
                    if dazi_count == 2:
                        # 搭子自身可以减少向听
                        for d in dazi:
                            i = d[0]
                            if d[1] > 0:
                                tenpai.append(i)
                            elif d[2] > 0:
                                tenpai.append(i)
                                tenpai.append(i + 1)
                            elif d[3] > 0:
                                tenpai.append(i)
                                tenpai.append(i + 2)
                # 向听为2以上
                if xt >= 2:
                    if mianzi_count + dazi_count < 5:
                        # 4搭子0雀头, 不需要新的搭子(顺子型)
                        if mianzi_count + dazi_count == 4 and not if_quetou:
                            less_than5 = get_md_less_than5(tthc, 0)
                            tenpai += less_than5
                        else:
                            less_than5 = get_md_less_than5(tthc)
                            tenpai += less_than5
                        # pass
                    elif mianzi_count + dazi_count >= 5:
                        # 超载时 搭子自身可以化为雀头 孤张也可
                        if not if_quetou:
                            for d in dazi:
                                i = d[0]
                                if d[1] > 0:
                                    tenpai.append(i)
                                elif d[2] > 0:
                                    tenpai.append(i)
                                    tenpai.append(i + 1)
                                elif d[3] > 0:
                                    tenpai.append(i)
                                    tenpai.append(i + 2)
                            tenpai += guzhang_list
                tenpai = list(set(tenpai))
                tenpai.sort()
                xt_list[xt] += tenpai
    for y in range(len(xt_list)):
        if xt_list[y]:
            # (向听数, 进张列表)
            return y, list(set(xt_list[y]))


# 一般形牌理分析
def calc_shanten_14(hc: str):
    shoupai = hc
    xiangting = '听牌'
    hc = convert_hc_to_list(hc)
    if sum(hc) != 14:
        raise ValueError("请传入14位手牌.")
    xt_list = []
    for x in range(len(hc)):
        if hc[x] > 0:
            # 变位
            hc[x] -= 1
            xt = calc_shanten_13(hc_list=hc)
            if xt:
                xt_list.append([x, xt])
            # 复位
            hc[x] += 1
    # 最小向听数
    xt_min = min([x[1][0] for x in xt_list])
    if xt_min == 0:
        # print("聴牌")
        pass
    else:
        # print(f"{xt_min}向听\n")
        xiangting = f"{xt_min}向听\n"
    card_advice_list = []
    for xxt in xt_list:
        xt = xxt[1]
        if xt[0] == xt_min:
            xt[1].sort()
            msum = calc_tenpai_sum(hc, xt[1])
            card_advice_list.append([xxt[0], xt[1], msum])
    card_advice_list.sort(key=lambda x: x[2], reverse=1)
    msg = f'手牌:{shoupai}\t{xiangting}\t不含国士无双/七对子分析\n'
    for x in card_advice_list:
        # print(f"打{convert_num_to_card(x[0])}  摸:", [convert_num_to_card(x) for x in x[1]], f"{x[2]}枚\n")
        msg += f"""打{convert_num_to_card(x[0])}  摸: {[convert_num_to_card(x) for x in x[1]]} {x[2]}枚\n"""
    if not xt:
        print("出现错误.")
        return '出错了'
    return text_to_image(text=msg, needtobase64=True)


@bot.on(GroupMessage)
async def paili_calculator(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(
        r"^牌理(分析)?\s*(:：)?\s*(\S+)$", msg.strip())
    if m:
        shoupai = m.group(3)
        try:
            await bot.send(event, messagechain_builder(at=event.sender.id, imgbase64=calc_shanten_14(shoupai)))
        except ValueError:
            await bot.send(event, messagechain_builder(at=event.sender.id, text='请输入14位手牌'))
