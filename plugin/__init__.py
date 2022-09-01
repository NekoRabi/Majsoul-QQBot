"""
:Author:  NekoRabi
:Create:  2022/8/27 1:57
:Update: /
:Describe: 插件依赖，打包成exe时需要使用下面的方法进行打包
:Version: 0.0.1
"""

# 如果不是exe,就使用这种方法自动导入包
import os

_plugins = os.listdir(r'./plugin')
# print(plugins)
for name in _plugins:
    if os.path.isdir(f'./plugin/{name}'):
        if os.path.exists(f'./plugin/{name}/__init__.py'):
            print(f'加载插件 {name}')
            exec(f"from plugin.{name} import *")

print('\n所有插件加载完毕')

# 'Else'

# from plugin.AlarmClock import *
# from plugin.AutoReply import *
# from plugin.BilibiliPlugin import
# from plugin.draw_wife import *
# from plugin.ImgOperation import *
# from plugin.jupai import *
# from plugin.KissKiss import *
# from plugin.LeisurePlugin import *
# from plugin.MajSoulInfo import *
# from plugin.paili_analysis import *
# from plugin.Petpet import *
# from plugin.prank_on_groupmember import *
# from plugin.Remake import *
# from plugin.Setu import *
# from plugin.Tarot import *
# from plugin.TencentCloudService import *
# from plugin.TenHouPlugin import *
# from plugin.kabishoubei import *
