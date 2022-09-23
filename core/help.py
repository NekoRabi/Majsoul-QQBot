"""
:Author:  NekoRabi
:Create:  2022/9/23 13:34
:Update: /
:Describe: "帮助"生成功能
:Version: 0.0.1
"""
from typing import Union

from utils import read_file, text_to_image

__all__ = ['add_help', 'create_helpimg', 'get_help_list']

_help = read_file(r'./data/sys/help.yml')
all_help = dict(friendhelp=_help['friendhelp'], grouphelp=_help['grouphelp'], adminhelp=[], masterhelp=[])


def add_help(event_type: str, data: Union[set, list, str, tuple, dict]):
    """
    向全局帮助添加文本

    Args:
        event_type: 消息事件或身份, friend,gropu,admin,master
        data: 帮助内容, 适配 str,list,set,tuple,dict 类型

    Returns:

    """
    if event_type.lower().startswith('friend'):
        event = 'friendhelp'
    elif event_type.lower().startswith('group'):
        event = 'grouphelp'
    elif event_type.lower().startswith('admin'):
        event = 'adminhelp'
    elif event_type.lower().startswith('master'):
        event = 'masterhelp'
    else:
        raise ValueError("帮助添加失败,无效参数")

    if type(data) == str:
        if not data.endswith('\n'):
            data = f'{data}\n'
        all_help[event].append(data)
    elif type(data) in [set, list, tuple]:
        for _item in data:
            if not f'{_item}'.endswith('\n'):
                all_help[event].append(f'{_item}\n')
            else:
                all_help[event].append(f'{_item}')
    elif type(data) == dict:
        for _k, _v in data.items():
            if not f'{_v}'.endswith('\n'):
                all_help[event].append(f'{_k} : {_v}\n')
            else:
                all_help[event].append(f'{_k} : {_v}')
    else:
        raise TypeError('帮助添加失败,添加的帮助内容的类型不匹配')


def get_help_list():
    return all_help


def create_helpimg():
    """生成帮助"""
    text_to_image(text=all_help['grouphelp'], path='grouphelp.png')
    text_to_image(text=all_help['friendhelp'], path='friendhelp.png')
