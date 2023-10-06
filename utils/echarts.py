import os
import asyncio
import time

from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Grid, Page
from pyecharts.charts.chart import RectChart, Chart
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
    make_snapshot(snapshot, b.render(), "Pyecharts生成条形图.png")
    return


def create_charts_from_option(option: dict, filename: str) -> dict:
    result = {'success': True}
    title = option.get("title")

    return result


def create_chart(chart: RectChart, html_name, png_name, del_html=True):
    make_snapshot(snapshot, chart.render(
        f"images/MajSoulInfo/{html_name}.html"), f"images/MajSoulInfo/{png_name}.png")
    # make_snapshot(snapshot, bar.render(f"{filename}.html"), f"{filename}.png")
    if del_html:
        os.remove(f'images/MajSoulInfo/{html_name}.html')
    # return 0


async def majsoul_echarts(filename, x_data, y_data, timecross="2022-3"):
    newy1 = []
    sum_score = 0
    y_data.reverse()
    for value in y_data:
        sum_score += value
        newy1.append(sum_score)
    y1_data = newy1
    # line = (
    #     Line(init_opts=opts.InitOpts(bg_color='rgba(255,255,255,1)'))
    #     .add_xaxis(xaxis_data=x_data)
    #     .add_yaxis(series_name="PT变化", y_axis=y1_data, areastyle_opts=opts.AreaStyleOpts(opacity=0.5), yaxis_index=1)
    #     .extend_axis(yaxis=opts.AxisOpts(type_="value", position="right"))
    #     .set_global_opts(
    #         yaxis_opts=opts.AxisOpts(position="right"),
    #         title_opts=opts.TitleOpts(title=filename, subtitle=timecross),
    #         tooltip_opts=opts.TooltipOpts(
    #             trigger="axis", axis_pointer_type="cross"),
    #         xaxis_opts=opts.AxisOpts(offset=2)
    #     )
    #     .set_series_opts(label_opts=opts.LabelOpts(is_show=True if len(x_data) < 40 else False),
    #                      markpoint_opts=opts.MarkPointOpts(
    #         data=[
    #             opts.MarkPointItem(
    #                 type_="min", name="最小值"),
    #             opts.MarkPointItem(type_="max", name="最大值")])
    #     )
    # )

    line = (
        Line(init_opts=opts.InitOpts(bg_color='rgba(255,255,255,1)'))
        .add_xaxis(x_data)
        .add_yaxis(series_name="PT变化", y_axis=y1_data, areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="PT变化", pos_top="48%"),
            legend_opts=opts.LegendOpts(pos_top="48%"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False),
                         markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(
                    type_="min", name="最小值"),
                opts.MarkPointItem(type_="max", name="最大值")])
        )
    )

    y1_data = []
    y2_data = []
    for value in y_data:
        if value < 0:
            y2_data.append(f'{value}')
            y1_data.append(None)
        else:
            y2_data.append(None)
            y1_data.append(value)
    # bar = (
    #     Bar(init_opts=opts.InitOpts(bg_color='rgba(255,255,255,1)'))
    #     .add_xaxis(x_data)
    #     .extend_axis(yaxis=opts.AxisOpts(type_="value", position="right"))
    #     .add_yaxis("PT增加", y1_data, stack='1', color='rgba(40,167,69,0.6)')
    #     .add_yaxis("PT减少", y2_data, stack='1', color='rgba(220,53,69,0.6)')
    #     .set_global_opts(title_opts=opts.TitleOpts(title=filename, subtitle=timecross))
    #     .set_series_opts(label_opts=opts.LabelOpts(is_show=False),
    #                      markpoint_opts=opts.MarkPointOpts(
    #         data=[
    #             opts.MarkPointItem(
    #                 type_="min", name="最小值"),
    #             opts.MarkPointItem(type_="max", name="最大值")])
    #     )
    # )

    bar = (
        Bar()
        .add_xaxis(x_data)
        .add_yaxis("PT增加", y1_data, stack='1', color='rgba(40,167,69,0.8)')
        .add_yaxis("PT减少", y2_data, stack='1', color='rgba(220,53,69,0.8)')
        .set_global_opts(title_opts=opts.TitleOpts(title="PT得失"))
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False),
                         markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(
                    type_="min", name="最小值"),
                opts.MarkPointItem(type_="max", name="最大值")])
        )
    )
    # overlap = bar.overlap(line)

    grid = (
        Grid(init_opts=opts.InitOpts(bg_color='rgba(255,255,255,1)'))
        .add(bar, grid_opts=opts.GridOpts(pos_bottom="60%"))
        .add(line, grid_opts=opts.GridOpts(pos_top="60%"))
    )
    await asyncio.to_thread(create_chart, grid, filename, filename)


async def majsoul_bar(filename: str, x_data: list, y1_data: list, timecross="2022-2") -> Bar:
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
                opts.MarkPointItem(
                    type_="min", name="最小值"),
                opts.MarkPointItem(type_="max", name="最大值")])
        )

    )

    # def blocking_io():
    #     print(f"start blocking_io at {time.strftime('%X')}")
    #     time.sleep(1)
    #     print(f"blocking_io complete at {time.strftime('%X')}")
    #
    # def aadds():
    #     print()

    # await asyncio.gather(
    #     asyncio.to_thread(blocking_io),
    #     asyncio.sleep(1))
    await asyncio.to_thread(create_chart, bar, filename, filename)
    # coro = asyncio.to_thread(create_chart(bar,filename,filename))
    # task = asyncio.create_task(coro)
    # await task

    # make_snapshot(snapshot, bar.render(f"{filename}.html"), f"{filename}.png")
    # os.remove(f'{filename}.html')

    return bar


async def majsoul_line(filename: str, x_data: list, y1_data: list, y2_data: list = None, timecross="2022-2") -> Line:
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
            tooltip_opts=opts.TooltipOpts(
                trigger="axis", axis_pointer_type="cross")
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True if len(x_data) < 40 else False),
                         markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(
                    type_="min", name="最小值"),
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
    # make_snapshot(snapshot, line.render(f"{filename}.html"), f"images/MajSoulInfo/{filename}.png")
    # # make_snapshot(snapshot, line.render(f"{filename}.html"), f"{filename}.png")
    # os.remove(f'{filename}.html')

    await asyncio.to_thread(create_chart, line, filename, filename)
    return line


# async def create_majsoul_charts(filename: str, x_data: list, y1_data: list, timecross="2022-2"):
#     await asyncio.to_thread(create_chart, line, filename, filename)


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
                opts.MarkPointItem(
                    type_="min", name="最小值"),
                opts.MarkPointItem(type_="max", name="最大值")])
        )

    )
    make_snapshot(snapshot, bar.render(
        f"{filename}.html"), f"images/MajSoulInfo/{filename}.png")
    # make_snapshot(snapshot, bar.render(f"{filename}.html"), f"{filename}.png")
    os.remove(f'{filename}.html')
    return


def tenhou_line(filename: str, x_data: list, y1_data: list, y2_data: list = None, timecross="2022-2"):
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
            tooltip_opts=opts.TooltipOpts(
                trigger="axis", axis_pointer_type="cross")
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True if len(x_data) < 40 else False),
                         markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(
                    type_="min", name="最小值"),
                opts.MarkPointItem(type_="max", name="最大值")])
        )
    )
    make_snapshot(snapshot, line.render(
        f"{filename}.html"), f"images/MajSoulInfo/{filename}.png")
    # make_snapshot(snapshot, line.render(f"{filename}.html"), f"{filename}.png")
    os.remove(f'{filename}.html')
    return
