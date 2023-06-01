from pyecharts.faker import Faker
from pyecharts.globals import ThemeType
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot
from pyecharts import options as opts
from pyecharts.charts import Sankey, Bar, Line

import os



def create_bar_chart(filename:str,x_data,y_data):
    b = Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT)) \
        .add_xaxis(Faker.days_attrs) \
        .add_yaxis("商家1", Faker.days_values, color=Faker.rand_color()) \
        .set_global_opts(
        title_opts=opts.TitleOpts(title="对局图表"),
        datazoom_opts=opts.DataZoomOpts(orient="vertical"),
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
    make_snapshot(snapshot, b.render(), "Pyecharts生成图片.png")
    return

def create_charts_from_option(option: dict, filename: str) -> dict:
    result = {'success': True}
    title = option.get("title")

    return result


def majsoul_lines(filename="xyshu的2023-9的雀魂图表", x_data="", y_data="",timecross="2022-2"):
    x = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期七', '星期日']
    y1 = [100, 200, 300, 400, 100, 400, 300]
    y2 = [200, 300, 200, 100, -200, 300, 400]
    line = (
        Line()
            .add_xaxis(xaxis_data=x)
            .add_yaxis(series_name="y1线", y_axis=y1, areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
            .add_yaxis(series_name="y2线", y_axis=y2, areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
            .set_global_opts(
        title_opts=opts.TitleOpts(title=filename, subtitle=timecross),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")
        )
    )
    make_snapshot(snapshot, line.render(f"{filename}.html"),f"{filename}.png")
    os.remove(f'{filename}.html')
    return

majsoul_lines()
