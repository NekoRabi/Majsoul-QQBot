import os

from pyecharts import options as opts
from pyecharts.charts import Bar, Line
from pyecharts.faker import Faker
from pyecharts.globals import ThemeType
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot


def create_bar_chart(filename: str, x_data, y_data):
    b = Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT)) \
        .add_xaxis(Faker.days_attrs) \
        .add_yaxis("商家1", Faker.days_values, color=Faker.rand_color()) \
        .set_global_opts(
        title_opts=opts.TitleOpts(title="对局图表"),
        datazoom_opts=opts.DataZoomOpts(orient="vertical"),
    )
    l1 = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期七', '星期日']
    l2 = [100, 200, 300, 400, 500, 400, 300]
    bar = (
        Bar()
            .add_xaxis(l1)
            .add_yaxis("l2", l2, category_gap=0, color='#FFFF00')
            .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"))
    )

    # sankey = Sankey(
    #     init_opts=opts.InitOpts(
    #         width='1000px',
    #         height='600px',
    #         bg_color='#fff'
    #     )
    # )
    # sankey.add('',nodes,links,
    #     node_gap=0,
    #     node_width=80,
    #     pos_right='5%',
    #     node_align='justify',
    #     focus_node_adjacency=True,
    #     linestyle_opt=opts.LineStyleOpts(curve=0.5, opacity=0.2, color="source"),
    #     label_opts=opts.LabelOpts(position='inside', color='white'),
    #     itemstyle_opts=opts.ItemStyleOpts(border_color="#fff"),
    # )
    # .render("Hourly data volumn.html")
    # print("：".join(["CSDN叶庭云", "https://yetingyun.blog.csdn.net/"]))
    # sankey.render("./results/009.html")
    make_snapshot(snapshot, b.render(), "Pyecharts生成条形图.png")
    return


def create_charts_from_option(option: dict, filename: str) -> dict:
    result = {'success': True}
    title = option.get("title")

    return result


def majsoul_bar(filename: str, x_data: list, y1_data: list, timecross="2022-2"):
    y1_data.reverse()
    y2_data = []
    newy1 = []
    for value in y1_data:
        if value < 0:
            y2_data.append(f'{value}')
            newy1.append(None)
        else:
            y2_data.append(None)
            newy1.append(value)
    y1_data = newy1
    bar = (
        Bar(init_opts=opts.InitOpts(bg_color='rgba(255,255,255,1)'))
            .add_xaxis(x_data)
            # .add_yaxis("PT得失", y1_data, category_gap=0, color='#FF0000')
            .add_yaxis("PT增加", y1_data, stack='1', color='#28a745')
            .add_yaxis("PT减少", y2_data, stack='1', color='#dc3545')
            .set_global_opts(title_opts=opts.TitleOpts(title=filename, subtitle=timecross))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=True if len(x_data) < 40 else False),
                             markpoint_opts=opts.MarkPointOpts(
                                 data=[
                                     opts.MarkPointItem(type_="min", name="最小值"),
                                     opts.MarkPointItem(type_="max", name="最大值")])
                             )

    )
    make_snapshot(snapshot, bar.render(f"{filename}.html"), f"images/MajSoulInfo/{filename}.png")
    # make_snapshot(snapshot, bar.render(f"{filename}.html"), f"{filename}.png")
    os.remove(f'{filename}.html')
    return


def majsoul_line(filename: str, x_data: list, y1_data: list, y2_data: list = None, timecross="2022-2"):
    # x = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期七', '星期日']
    # print(x_data)
    # print(y1_data)
    # y1 = [100, 200, 300, 400, 100, 400, 300]
    # y2 = [200, 300, 200, 100, -200, 300, 400]
    # y1_data.reverse()
    newy1 = []
    sum_score = 0
    for value in y1_data:
        sum_score += value
        newy1.append(sum_score)
    y1_data = newy1
    line = (
        # Line(init_opts=opts.InitOpts(bg_color='rgba(255,250,205,0.2)'))
        Line(init_opts=opts.InitOpts(bg_color='rgba(255,255,255,1)'))
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis(series_name="PT变化", y_axis=y1_data, areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
            .set_global_opts(
            title_opts=opts.TitleOpts(title=filename, subtitle=timecross),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")
            # ,visualmap_opts=opts.VisualMapOpts(
            #     is_piecewise=True,
            #     dimension=0,
            #     pieces=[
            #         {"lte": 6, "color": "green"},
            #         {"gt": 6, "lte": 8, "color": "red"},
            #         {"gt": 8, "lte": 14, "color": "yellow"},
            #         {"gt": 14, "lte": 17, "color": "red"},
            #         {"gt": 17, "color": "green"},
            #     ],
            #     pos_right=0,
            #     pos_bottom=100
            # )
        )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=True if len(x_data) < 40 else False),
                             markpoint_opts=opts.MarkPointOpts(
                                 data=[
                                     opts.MarkPointItem(type_="min", name="最小值"),
                                     opts.MarkPointItem(type_="max", name="最大值")])
                             )
        #     .set_series_opts(
        #     markarea_opts=opts.MarkAreaOpts(
        #         data=[
        #             opts.MarkAreaItem(name="4", x=("1", "5")),
        #             opts.MarkAreaItem(name="1", x=("4", "5")),
        #         ]
        #     )
        # )
    )
    make_snapshot(snapshot, line.render(f"{filename}.html"), f"images/MajSoulInfo/{filename}.png")
    # make_snapshot(snapshot, line.render(f"{filename}.html"), f"{filename}.png")
    os.remove(f'{filename}.html')
    return


def tenhou_bar(filename: str, x_data: list, y1_data: list, timecross="2022-2"):
    y2_data = []
    newy1 = []
    for value in y1_data:
        if value < 0:
            y2_data.append(f'{value}')
            newy1.append(None)
        else:
            y2_data.append(None)
            newy1.append(value)
    y1_data = newy1
    bar = (
        Bar(init_opts=opts.InitOpts(bg_color='rgba(255,255,255,1)'))
            .add_xaxis(x_data)
            # .add_yaxis("PT得失", y1_data, category_gap=0, color='#FF0000')
            .add_yaxis("PT增加", y1_data, stack='1', color='#28a745')
            .add_yaxis("PT减少", y2_data, stack='1', color='#dc3545')
            .set_global_opts(title_opts=opts.TitleOpts(title=filename, subtitle=timecross))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=True if len(x_data) < 40 else False),
                             markpoint_opts=opts.MarkPointOpts(
                                 data=[
                                     opts.MarkPointItem(type_="min", name="最小值"),
                                     opts.MarkPointItem(type_="max", name="最大值")])
                             )

    )
    make_snapshot(snapshot, bar.render(f"{filename}.html"), f"images/MajSoulInfo/{filename}.png")
    # make_snapshot(snapshot, bar.render(f"{filename}.html"), f"{filename}.png")
    os.remove(f'{filename}.html')
    return


def tenhou_line(filename: str, x_data: list, y1_data: list, y2_data: list = None, timecross="2022-2"):
    # x = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期七', '星期日']
    # print(x_data)
    # print(y1_data)
    # y1 = [100, 200, 300, 400, 100, 400, 300]
    # y2 = [200, 300, 200, 100, -200, 300, 400]
    # y1_data.reverse()
    newy1 = []
    sum_score = 0
    for value in y1_data:
        sum_score += value
        newy1.append(sum_score)
    y1_data = newy1
    line = (
        # Line(init_opts=opts.InitOpts(bg_color='rgba(255,250,205,0.2)'))
        Line(init_opts=opts.InitOpts(bg_color='rgba(255,255,255,1)'))
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis(series_name="PT变化", y_axis=y1_data, areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
            .set_global_opts(
            title_opts=opts.TitleOpts(title=filename, subtitle=timecross),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")
            # ,visualmap_opts=opts.VisualMapOpts(
            #     is_piecewise=True,
            #     dimension=0,
            #     pieces=[
            #         {"lte": 6, "color": "green"},
            #         {"gt": 6, "lte": 8, "color": "red"},
            #         {"gt": 8, "lte": 14, "color": "yellow"},
            #         {"gt": 14, "lte": 17, "color": "red"},
            #         {"gt": 17, "color": "green"},
            #     ],
            #     pos_right=0,
            #     pos_bottom=100
            # )
        )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=True if len(x_data) < 40 else False),
                             markpoint_opts=opts.MarkPointOpts(
                                 data=[
                                     opts.MarkPointItem(type_="min", name="最小值"),
                                     opts.MarkPointItem(type_="max", name="最大值")])
                             )
        #     .set_series_opts(
        #     markarea_opts=opts.MarkAreaOpts(
        #         data=[
        #             opts.MarkAreaItem(name="4", x=("1", "5")),
        #             opts.MarkAreaItem(name="1", x=("4", "5")),
        #         ]
        #     )
        # )
    )
    make_snapshot(snapshot, line.render(f"{filename}.html"), f"images/MajSoulInfo/{filename}.png")
    # make_snapshot(snapshot, line.render(f"{filename}.html"), f"{filename}.png")
    os.remove(f'{filename}.html')
    return



# 下 inforesponse
# """{'count': 104, '和牌率': 0.3173076923076923, '自摸率': 0.45454545454545453, '默听率': 0.030303030303030304, '放铳率': 0.18269230769230768, '副露率': 0.34615384615384615, '立直率': 0.3173076923076923, '平均打点': 9348, '最大连庄': 2, '和了巡数': 11.151515151515152, '平均铳点': 8663, '流局率': 0.14423076923076922, '流听率': 0.6666666666666666, '一发率': 0.058823529411764705, '里宝率': 0.5294117647058824, '被炸率': 0.16666666666666666, '平均被炸点数': 9150, '放铳时立直率': 0.2631578947368421, '放铳时副露率': 0.3684210526315789, '立直后放铳率': 0.15151515151515152, '立直后非瞬间放铳率': 0.09090909090909091, '副露后放铳率': 0.19444444444444445, '立直后和牌率': 0.5151515151515151, '副露后和牌率': 0.4166666666666667, '立直后流局率': 0.18181818181818182, '副露后流局率': 0.1111111111111111, '放铳至立直': 7, '放铳至副露': 9, '放铳至默听': 3, '立直和了': 17, '副露和了': 15, '默听和了': 1, '立直巡目': 8.91919191919192, '立直收支': 4109, '立直收入': 10335, ' 立直支出': 8420, '先制率': 0.7575757575757576, '追立率': 0.24242424242424243, '被追率': 0.15151515151515152, '振听立直率': 0, '立直好型': 0.8181818181818182, '立直多面': 0.8181818181818182, '立直好型2': 0.48484848484848486, '最大累计番数': 10, '打点效率': 2966, '铳点损失': 1583, '净打点效率': 1384, '平均起手向听': 3.298076923076923, '平均起手向听亲': 3.0588235294117645, '平均起手向听子': 3.414285714285714, '最近大铳': {'id': '220905-2f058eef-7e52-425a-9bdf-30b279bc7c38', 'start_time': 1662348873, 'fans': [{'id': 29, 'label': '清一色', 'count': 6, '役满': 0}, {'id': 31, 'label': '宝牌', 'count': 2, '役满': 0}, {'id': 32, 'label': '红宝牌', 'count': 1, '役满': 0}]}, 'id': 1056373, 'played_modes': [23]}"""
# data = '''[{'_id': '8cjC7rEJRHY', 'modeId': 11, 'uuid': '230530-a01bcd14-24f1-4723-837a-f313168f85ba', 'startTime': 1685384713, 'endTime': 1685386444, 'players': [{'accountId': 1096838, 'nickname': '二次元給爺爬', 'level': 10401, 'score': 3600, 'gradingScore': -116}, {'accountId': 12768618, 'nickname': 'Ming789', 'level': 10502, 'score': 21900, 'gradingScore': -8}, {'accountId': 228839, 'nickname': '小真帆', 'level': 10501, 'score': 30300, 'gradingScore': 41}, {'accountId': 69615865, 'nickname': 'Elsodia', 'level': 10503, 'score': 44200, 'gradingScore': 90}]}, {'_id': '8ciGKHhiqTg', 'modeId': 11, 'uuid': '230529-765f5030-5543-48e6-aa84-f5cd16740724', 'startTime': 1685337321, 'endTime': 1685338244, 'players': [{'accountId': 67345411, 'nickname': '_みみお', 'level': 10401, 'score': 18200, 'gradingScore': -101}, {'accountId': 107400096, 'nickname': '奇襲に強い陰獣', 'level': 10502, 'score': 19700, 'gradingScore': -10}, {'accountId': 1096838, 'nickname': '二次元給爺爬', 'level': 10401, 'score': 29000, 'gradingScore': 39}, {'accountId': 72475395, 'nickname': 'がるむちゃん', 'level': 10401, 'score': 33100, 'gradingScore': 79}]}, {'_id': '8cgVrn9TfEV', 'modeId': 11, 'uuid': '230528-26f4036f-72b3-4cb5-876f-28a01716f883', 'startTime': 1685248391, 'endTime': 1685249816, 'players': [{'accountId': 67113774, 'nickname': 'lロックl', 'level': 10402, 'score': 18800, 'gradingScore': -111}, {'accountId': 74285568, 'nickname': 'いくもん', 'level': 10401, 'score': 19500, 'gradingScore': -10}, {'accountId': 68576962, 'nickname': '農家の次男', 'level': 10401, 'score': 27400, 'gradingScore': 38}, {'accountId': 1096838, 'nickname': '二次元給爺爬', 'level': 10401, 'score': 34300, 'gradingScore': 80}]}, {'_id': '8cezLzkUyPO', 'modeId': 11, 'uuid': '230527-4dbd1626-1d74-461e-98d3-51497cb56ec5', 'startTime': 1685170896, 'endTime': 1685172516, 'players': [{'accountId': 1096838, 'nickname': '二次元給爺爬', 'level': 10401, 'score': 11000, 'gradingScore': -109}, {'accountId': 8926230, 'nickname': '皮龘龘', 'level': 10501, 'score': 24800, 'gradingScore': -5}, {'accountId': 59422, 'nickname': '鬼畜天丶使', 'level': 10403, 'score': 29000, 'gradingScore': 39}, {'accountId': 11111922, 'nickname': '一直输怎么办', 'level': 10401, 'score': 35200, 'gradingScore': 81}]}, {'_id': '8cdyARRGru7', 'modeId': 11, 'uuid': '230527-4e0cdabb-9723-45ba-a3ea-419c3366a285', 'startTime': 1685119087, 'endTime': 1685119953, 'players': [{'accountId': 72602862, 'nickname': 'のどぼと毛', 'level': 10502, 'score': 16300, 'gradingScore': -143}, {'accountId': 13916168, 'nickname': '凜喵嗚', 'level': 10401, 'score': 24600, 'gradingScore': -5}, {'accountId': 107350459, 'nickname': 'ねんねこねご', 'level': 10401, 'score': 24900, 'gradingScore': 35}, {'accountId': 1096838, 'nickname': '二次元給爺爬', 'level': 10401, 'score': 34200, 'gradingScore': 80}]}, {'_id': '8cc8ypwPAuV', 'modeId': 11, 'uuid': '230525-a2e97c4f-52c8-4b47-98aa-57b84d0a86b6', 'startTime': 1685026280, 'endTime': 1685027429, 'players': [{'accountId': 74608749, 'nickname': 'Hawkiwi', 'level': 10401, 'score': 18400, 'gradingScore': -101}, {'accountId': 74784302, 'nickname': ' チキモフ', 'level': 10403, 'score': 21000, 'gradingScore': -9}, {'accountId': 1096838, 'nickname': '二次元給爺爬', 'level': 10401, 'score': 26900, 'gradingScore': 37}, {'accountId': 67664246, 'nickname': 'bishabisha', 'level': 10401, 'score': 33700, 'gradingScore': 79}]}, {'_id': '8caYv2wQnQV', 'modeId': 11, 'uuid': '230525-68fd73ff-9922-4f85-9848-1ae0b74bb84c', 'startTime': 1684945876, 'endTime': 1684947252, 'players': [{'accountId': 1096838, 'nickname': '二次元給爺爬', 'level': 10401, 'score': 6300, 'gradingScore': -113}, {'accountId': 74466352, 'nickname': 'myz2', 'level': 10403, 'score': 24800, 'gradingScore': -5}, {'accountId': 71054923, 'nickname': 'パール真珠', 'level': 10401, 'score': 27500, 'gradingScore': 38}, {'accountId': 73285256, 'nickname': 'ミルモでチー', 'level': 10401, 'score': 41400, 'gradingScore': 87}]}, {'_id': '8ca9fR6KWvQ', 'modeId': 11, 'uuid': '230524-78a15088-a700-41d7-9c81-a526469f1bb8', 'startTime': 1684925171, 'endTime': 1684926066, 'players': [{'accountId': 15651430, 'nickname': '在、也不见', 'level': 10501, 'score': 21100, 'gradingScore': -8}, {'accountId': 74041972, 'nickname': 'pazikami', 'level': 10402, 'score': 21100, 'gradingScore': -108}, {'accountId': 73956952, 'nickname': 'ぐで。', 'level': 10401, 'score': 25800, 'gradingScore': 36}, {'accountId': 1096838, 'nickname': '二次元給爺爬', 'level': 10401, 'score': 32000, 'gradingScore': 77}]}, {'_id': '8cYvV3FVWuO', 'modeId': 11, 'uuid': '230524-b5ef7000-766d-4607-a9f9-7cc1d3e34092', 'startTime': 1684862718, 'endTime': 1684863423, 'players': [{'accountId': 105946548, 'nickname': 'Aoxys', 'level': 10401, 'score': 6000, 'gradingScore': -114}, {'accountId': 100914807, 'nickname': 'Decelerator', 'level': 10401, 'score': 26700, 'gradingScore': -3}, {'accountId': 107011269, 'nickname': 'ひよQ', 'level': 10402, 'score': 31300, 'gradingScore': 42}, {'accountId': 1096838, 'nickname': '二次元給爺爬', 'level': 10401, 'score': 36000, 'gradingScore': 81}]}, {'_id': '8cYG0uUXHlP', 'modeId': 11, 'uuid': '230523-90e3e597-e041-45d4-86e4-a2bb046c8b74', 'startTime': 1684828702, 'endTime': 1684830206, 'players': [{'accountId': 68608894, 'nickname': 'Torank', 'level': 10401, 'score': 18500, 'gradingScore': -101}, {'accountId': 75316973, 'nickname': 'まいのりてぃー', 'level': 10501, 'score': 21800, 'gradingScore': -8}, {'accountId': 12947397, 'nickname': '憨憨空板鸭', 'level': 10502, 'score': 25700, 'gradingScore': 36}, {'accountId': 1096838, 'nickname': '二次元給爺爬', 'level': 10401, 'score': 34000, 'gradingScore': 79}]}, {'_id': '8cWHvMqCzFB', 'modeId': 11, 'uuid': '230522-9be68d81-bbda-4d6e-8e53-439c14ce1641', 'startTime': 1684728596, 'endTime': 1684729295, 'players': [{'accountId': 68091759, 'nickname': 'shabomb', 'level': 10403, 'score': 14400, 'gradingScore': -125}, {'accountId': 70346241, 'nickname': 'マーミット', 'level': 10402, 'score': 23000, 'gradingScore': -7}, {'accountId': 74780152, 'nickname': 'りつたろう', 'level': 10401, 'score': 29000, 'gradingScore': 39}, {'accountId': 1096838, 'nickname': '二次元給爺爬', 'level': 10401, 'score': 33600, 'gradingScore': 79}]}, {'_id': '8cWGrEXse0u', 'modeId': 11, 'uuid': '230522-0017d2b8-de01-424c-98cf-164ae9b59f61', 'startTime': 1684727722, 'endTime': 1684728371, 'players': [{'accountId': 67412541, 'nickname': 'たったです', 'level': 10403, 'score': 12400, 'gradingScore': -127}, {'accountId': 72013153, 'nickname': 'えんぱす', 'level': 10402, 'score': 18700, 'gradingScore': -11}, {'accountId': 11783486, 'nickname': '終世のリコリス', 'level': 10401, 'score': 23000, 'gradingScore': 33}, {'accountId': 1096838, 'nickname': ' 二次元給爺爬', 'level': 10401, 'score': 45900, 'gradingScore': 91}]}, {'_id': '8cUzzpydZHJ', 'modeId': 11, 'uuid': '230521-8a1ca1a5-4849-4906-809c-facc7ddb4d59', 'startTime': 1684663060, 'endTime': 1684663727, 'players': [{'accountId': 16655447, 'nickname': '朔罗雨夜', 'level': 10402, 'score': 12600, 'gradingScore': -117}, {'accountId': 1096838, 'nickname': '二次元給爺爬', 'level': 10401, 'score': 25500, 'gradingScore': -4}, {'accountId': 16698359, 'nickname': '若不辞', 'level': 10401, 'score': 27000, 'gradingScore': 37}, {'accountId': 12242166, 'nickname': '寶馒头', 'level': 10401, 'score': 34900, 'gradingScore': 80}]}]'''
# data = eval(data)
# # print(data)
# length = len(data)
# xdata = [f'{i + 1}' for i in range(length)]
# ydata = []
# for d in data:
#     player = d.get("players")
#     # print(player)
#     for p in player:
#         if p.get("accountId") == 1096838:
#             ydata.append(p.get("gradingScore"))
#             # print(p.get("gradingScore"))
#             # break
# #
# majsoul_line(filename='二次元給爺爬最近一个月的折线图表', x_data=xdata, y1_data=ydata, timecross="最近一个月")
# majsoul_bar(filename='二次元給爺爬最近一个月的柱状图表', x_data=xdata, y1_data=ydata, timecross="最近一个月")
# # # print(player)
# # # print(data)
# # # majsoul_lines()
# #
# # # await getmonthreport()
