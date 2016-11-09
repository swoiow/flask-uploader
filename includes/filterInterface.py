#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import (datetime, timedelta)

from app import app


@app.template_filter('dateformat')
def datetime_format(date, format_='%Y.%m.%d'):
    try:
        dateObj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        dateObj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S") + timedelta(hours=10)
    return dateObj.strftime(format_)
