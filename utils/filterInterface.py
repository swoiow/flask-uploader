# -*- coding: utf-8 -*-

from datetime import (datetime, timedelta)


def datetime_format(date, format_='%Y.%m.%d'):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S") + timedelta(hours=10)
    return date_obj.strftime(format_)
