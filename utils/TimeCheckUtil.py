import re


def date_check(date):
    """
    日期校验

    Args:
        date: yy-M-d等正常的日期格式

    Returns: 是否合法

    """
    m = re.match(r"(\d{2,4})-(\d{1,2})-(\d{1,2})", date)
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
