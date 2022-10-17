"""
:Author:  NekoRabi
:Create:  2022/10/16 14:06
:Update: /
:Describe: 时间校验工具
:Version: 0.0.1
"""
import re

__all__ = ['date_check', 'time_check']


def date_check(datestr: str):
    """
    日期校验

    Args:
        datestr: yy-M-d等正常的日期格式，必须以 - 链接

    Returns: 是否合法

    """
    m = re.match(r"(\d{2,4})-(\d{1,2})-(\d{1,2})", datestr)
    if m:
        year = m.group(1)
        month = int(m.group(2))
        day = int(m.group(3))
        if len(year) == 2:
            year = f'20{year}'
        year = int(year)
        if month < 1 or month > 12:
            return dict(effective=False, error="月份错误")
        if day < 1:
            return dict(effective=False, error="日期错误")
        if month in {1, 3, 5, 7, 8, 10, 12}:
            if day > 31:
                return dict(effective=False, error="日期错误")
        elif month == 2:
            if year % 400 == 0:
                if day > 29:
                    return dict(effective=False, error="日期错误")
            elif year % 4 == 0 and year % 100 != 0:
                if day > 29:
                    return dict(effective=False, error="日期错误")
            else:
                if day > 28:
                    return dict(effective=False, error="日期错误")
        else:
            if day > 30:
                return dict(effective=False, error="日期错误")
        return dict(effective=True, error=None)
    else:
        return dict(effective=False, error="无效日期")


def time_check(timestr: str):
    """
    时间校验

    Args:
        timestr: hh:mm:ss的时间格式

    Returns:

    """
    m = re.match(r"(\d{1,2}):(\d{1,2}):(\d{1,2})", timestr)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2))
        second = int(m.group(3))
        if second >= 60 or second < 0:
            return dict(effective=False, error="invalid seconds")
        if minute >= 60 or minute < 0:
            return dict(effective=False, error="invalid minutes")
        if hour < 0 or hour > 23:
            return dict(effective=False, error="invalid hours")
        return dict(effective=True, error=None)
