"""
:Author:  NekoRabi
:Create:  2022/9/18 3:56
:Update: /
:Describe: 文件读写工具
:Version: 0.0.1
"""
import os

import yaml
import json



def read_file(path: str, filetype: str = None, encoding='utf-8'):
    """
    读文件

    Args:
        path: 文件路径
        filetype: 文件类型，未给定时会自动识别。目前仅支持JSON和YML
        encoding: 文件编码

    Returns:

    """
    cfg = None
    if filetype is None:
        filetype = os.path.splitext(path)[-1][1:].lower()
    try:
        with open(path, encoding=encoding) as filecfg:
            if filetype in ['yml', 'yaml']:
                cfg = yaml.safe_load(filecfg)
            elif filetype in ['json']:
                cfg = json.load(filecfg)
            else:
                raise Exception("不支持的文件类型! 目前仅支持JSON、 YML")
    except Exception as e:
        print(e)
    return cfg


def write_file(content, path: str, filetype: str = None, encoding='utf-8', allow_unicode=True):
    """

    Args:
        content: 要写的内容
        path: 文件路径
        filetype: 文件类型，未给定时会自动识别。目前仅支持JSON和YML
        encoding: 文件编码
        allow_unicode: 允许Unicode编码存在

    Returns: None

    """
    if filetype is None:
        filetype = os.path.splitext(path)[-1][1:]
    try:
        with open(path, 'w', encoding=encoding) as filecfg:
            if filetype in ['yml', 'yaml']:
                yaml.dump(content, filecfg, allow_unicode=allow_unicode)
            elif filetype in ['json']:
                json.dump(content, filecfg, allow_unicode=allow_unicode)
            else:
                raise Exception("不支持的文件类型! 目前仅支持 JSON、 YML")
        return True
    except Exception as e:
        print(e)
        return False
