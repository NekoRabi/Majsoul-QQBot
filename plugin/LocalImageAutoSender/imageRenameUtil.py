"""
:Author:  NekoRabi
:Create:  2023/6/16 1:59
:Update: /
:Describe: 一个不成熟的文件自动命名工具
:Version: 0.0.1
:HowToUse: 例:命令行中进入Cheshire文件夹,运行cmd，输入 'python xxxx/imageRenameUtil.py',再输入Cheshire，所有文件自动重命名
"""
import os

# files = os.listdir("")

i = 0
foldername = input("请输入父文件夹名字")
# for file in os.listdir():

downline = False
for parent, dirnames, filenames in os.walk("."):
    if os.path.exists(f'{foldername}{0}.{filenames[0].split(".")[-1]}'):
        downline = True
    for filename in filenames:
        # print("parent is: " + parent)
        # print("filename is: " + filename)
        # print(os.path.join(parent, filename))  # 输出rootdir路径下所有文件（包含子文件）信息
        if downline:
            newName = f'{foldername}-{i}.{filename.split(".")[-1]}'
        else:
            newName = f'{foldername}{i}.{filename.split(".")[-1]}'
        os.rename(os.path.join(parent, filename), os.path.join(parent, newName))
        i = i + 1
