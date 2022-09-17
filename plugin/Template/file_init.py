"""
:Author:  NekoRabi
:Create:  2022/9/18 2:30
:Update: /
:Describe: 文件读写模板
:Version: 0.0.1
"""

from utils.cfg_loader import *
import os

# 为减少资源文件,可以将配置文件写在代码里，自动生成到

# 如果文件夹不存在,先创建对应插件的文件夹
if not os.path.exists("./config/test"):
    os.mkdir("./config/test")

# 再如果文件不存在，则生成文件
if not os.path.exists(r'./config/test/test.yml'):

    # 先把内容存储在变量中
    _data = dict(Describe='这是一个自动创建的文件,生成这个说明创建成功了' )

    # 可以调用 utils.cfg_loader.write_file() 方法，快速生成一个文件
    write_file(content=_data, path=r'./config/test/test.yml')


# 同样可以使用 utils.cfg_loader.read_file() 来读取文件
# 文件不存在会报错,所以要先检验文件是否存在
if os.path.exists(r'./config/test/test.yml'):
    _file = read_file(r'./config/test/test.yml')
    print(_file)
