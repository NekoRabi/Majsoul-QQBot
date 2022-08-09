import math

# 检查牌是否同一区间
def check_same_area(a, b):
    if a < 9 and b < 9:
        return True
    elif 9 <= a < 18 and 9 <= b < 18:
        return True
    elif 18 <= a < 27 and 18 <= b < 27:
        return True
    elif a >= 27 and b >= 27:
        return True


# 获取面子的组合形式
def get_mianzi(single_color_cards):
    single_color_cards = single_color_cards  # [1,0,1,1,0,0,2,1,0]
    depth = math.floor(sum(single_color_cards) / 3)
    available = [[0, 0] for x in range(len(single_color_cards))]
    myava_list = []

    # 顺子
    for x in range(len(single_color_cards) - 2):
        # 字牌无顺子
        if x < 27:
            if all([single_color_cards[x], single_color_cards[x + 1], single_color_cards[x + 2]]) and math.floor(x / 9) == math.floor((x + 1) / 9) == math.floor((x + 2) / 9):
                available[x][0] = 1
    # 刻子
    for x in range(len(single_color_cards)):
        if single_color_cards[x] >= 3:
            available[x][1] = 1

    myava_list = [(x, available[x][0], 0) for x in range(len(single_color_cards)) if available[x][0] > 0]
    myava_list += [(x, 0, available[x][1]) for x in range(len(single_color_cards)) if available[x][1] > 0]

    # myava_list =  [(2, 1, 0), (3, 1, 0), (4, 1, 0), (4, 0, 1), (5, 0, 1)]
    m = []
    mlist = []
    stack = []
    stack.append(single_color_cards)

    def dfs(mlist, d):  # d:深度
        # depth 深度
        if len(mlist) < depth:
            continue_count = 0
            for x in myava_list:
                stack_diff = len(stack) - d - 1
                for y in range(stack_diff):
                    stack.pop()
                hc = stack[d].copy()
                diff = len(mlist) - d
                for y in range(diff):
                    mlist.pop()
                origin_index = x[0]
                if x[1] > 0:
                    # 变位
                    hc[origin_index] -= 1
                    hc[origin_index + 1] -= 1
                    hc[origin_index + 2] -= 1
                    if hc[origin_index] >= 0 and hc[origin_index + 1] >= 0 and hc[origin_index + 2] >= 0:
                        mlist.append(x)
                    else:
                        # 复位
                        hc[origin_index] += 1
                        hc[origin_index + 1] += 1
                        hc[origin_index + 2] += 1
                        continue_count += 1
                        # 连续len(myava_list)次continue 为终点
                        if continue_count >= len(myava_list):
                            mlist_copy = mlist.copy()
                            mlist_copy.sort()
                            if mlist_copy not in m:
                                m.append(mlist_copy)
                        continue
                elif x[2] > 0:
                    # 变位
                    hc[origin_index] -= 3
                    if hc[origin_index] >= 0:
                        mlist.append(x)
                    else:
                        # 复位
                        hc[origin_index] += 3

                        continue_count += 1
                        # 连续len(myava_list)次continue 为终点
                        if continue_count >= len(myava_list):
                            mlist_copy = mlist.copy()
                            mlist_copy.sort()
                            if mlist_copy not in m:
                                m.append(mlist_copy)
                        continue
                stack.append(hc)
                dfs(mlist, d + 1)
        else:
            mlist_copy = mlist.copy()
            mlist_copy.sort()
            if mlist_copy not in m:
                m.append(mlist_copy)

    dfs(mlist, 0)
    # 面子回退 应对 1345型拆解 -> 13 45 or 1 345
    mianzi_count_max = 0
    for x in m:
        mianzi_count = len(x)
        if mianzi_count > mianzi_count_max:
            mianzi_count_max = mianzi_count
    for x in m:
        if len(x) == mianzi_count_max:
            for y in range(len(x)):
                z = x[0:y] + x[y + 1 :]
                z.sort()
                if z not in m:
                    m.append(z)
    return m


# 获取搭子的组合形式
def get_dazi(single_color_cards):
    single_color_cards = single_color_cards
    depth = math.floor(sum(single_color_cards) / 2)
    available = [[0, 0, 0] for x in range(len(single_color_cards))]
    myava_list = []

    # [2]
    for x in range(len(single_color_cards)):
        if single_color_cards[x] >= 2:
            available[x][0] = 1

    # [11]
    for x in range(len(single_color_cards) - 1):
        # 字牌无顺子
        if x < 27:
            if all([single_color_cards[x], single_color_cards[x + 1]]) and check_same_area(x, x + 1):
                available[x][1] = 1

    # [101]
    for x in range(len(single_color_cards) - 2):
        # 字牌无顺子
        if x < 27:
            if all([single_color_cards[x], single_color_cards[x + 2]]) and check_same_area(x, x + 2):
                available[x][2] = 1
    myava_list = [(x, available[x][0], 0, 0) for x in range(len(single_color_cards)) if available[x][0] > 0]
    myava_list += [(x, 0, available[x][1], 0) for x in range(len(single_color_cards)) if available[x][1] > 0]
    myava_list += [(x, 0, 0, available[x][2]) for x in range(len(single_color_cards)) if available[x][2] > 0]
    m = []
    d = 0
    stack = []
    stack.append(single_color_cards)
    mlist = []

    def dfs(mlist, d):
        # depth 深度
        if len(mlist) < depth:
            continue_count = 0
            for x in myava_list:
                stack_diff = len(stack) - d - 1
                for y in range(stack_diff):
                    stack.pop()
                hc = stack[d].copy()
                diff = len(mlist) - d
                for y in range(diff):
                    mlist.pop()
                origin_index = x[0]
                # [2]
                if x[1] > 0:
                    # 变位
                    hc[origin_index] -= 2
                    if hc[origin_index] >= 0:
                        mlist.append(x)
                    else:
                        # 复位
                        hc[origin_index] += 2

                        continue_count += 1
                        # 连续len(myava_list)次continue 为终点
                        if continue_count >= len(myava_list):
                            mlist_copy = mlist.copy()
                            mlist_copy.sort()
                            if mlist_copy not in m:
                                m.append(mlist_copy)
                        continue
                # [11]
                elif x[2] > 0:
                    # 变位
                    hc[origin_index] -= 1
                    hc[origin_index + 1] -= 1
                    if hc[origin_index] >= 0 and hc[origin_index + 1] >= 0:
                        mlist.append(x)
                    else:
                        # 复位
                        hc[origin_index] += 1
                        hc[origin_index + 1] += 1

                        continue_count += 1
                        # 连续len(myava_list)次continue 为终点
                        if continue_count >= len(myava_list):
                            mlist_copy = mlist.copy()
                            mlist_copy.sort()
                            if mlist_copy not in m:
                                m.append(mlist_copy)
                        continue
                elif x[3] > 0:
                    # 变位
                    hc[origin_index] -= 1
                    hc[origin_index + 2] -= 1
                    if hc[origin_index] >= 0 and hc[origin_index + 2] >= 0:
                        mlist.append(x)
                    else:
                        # 复位
                        hc[origin_index] += 1
                        hc[origin_index + 2] += 1
                        continue_count += 1
                        # 连续len(myava_list)次continue 为终点
                        if continue_count >= len(myava_list):
                            mlist_copy = mlist.copy()
                            mlist_copy.sort()
                            if mlist_copy not in m:
                                m.append(mlist_copy)
                        continue
                stack.append(hc)
                dfs(mlist, d + 1)
        else:
            mlist_copy = mlist.copy()
            mlist_copy.sort()
            if mlist_copy not in m:
                m.append(mlist_copy)

    dfs(mlist, 0)

    return m
