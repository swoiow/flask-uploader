# -*- coding: utf-8 -*-

import functools
import hashlib
import random
import socket
import string

try:
    from .dbItf import query_db
except (ImportError, ModuleNotFoundError) as e:
    import traceback

    traceback.print_exc()
    # print "Track INFO: ", u"Unable to import: {} in {}".format(e.message, __file__)

from datetime import (datetime, timedelta)


def catch_err_msg(func):
    import traceback

    @functools.wraps(func)
    def wrapper(*args, **kw):
        # wrapper.err_msg = "xxx"
        try:
            wrapper.err_msg = func(*args, **kw)
        except Exception as _e:
            wrapper.err_msg = _e
        finally:
            traceback.print_exc()
            return {"msg": wrapper.err_msg}

    # wrapper.err_msg = ""
    return wrapper


def datetime_format(date, format_='%Y.%m.%d'):
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S") + timedelta(hours=10)
        return date_obj.strftime(format_)

    return "0000-00-00"


def char_convert(word, coding="utf-8", str_=False):
    """
    :param word:
    :param coding:
    :param str_: 是否转换成str。默认返回utf8
    """
    if str_:
        if isinstance(word, str):
            return word

        if isinstance(word, str):
            try:
                return word.encode(coding)
            except UnicodeEncodeError:
                return char_convert(word.encode("gbk"), str_=True)

    if isinstance(word, str):
        return word

    if isinstance(word, str):
        try:
            return word.decode(coding)
        except UnicodeDecodeError:
            return char_convert(word.decode("gbk"))


def id_generator2(size=6, db=None, chars=string.ascii_letters + string.digits, check_db=False):
    if check_db:
        assert db is not None

        _MAX_RETRY, _SIZE = 10, 6
        while _MAX_RETRY > 0:
            fid = id_generator2(size=_SIZE)
            sql_query = 'SELECT fid FROM "index" WHERE fid = ?;'
            rv = query_db(db, sql_query, args=(fid,), one=True)

            if rv:
                _MAX_RETRY -= 1
                if _MAX_RETRY == 0:
                    _MAX_RETRY, _SIZE = 10, _SIZE + 1

            else:
                return fid

    else:
        return ''.join(random.choice(chars) for _ in range(size))


def id_generator(s):
    s = s.encode() if isinstance(s, str) else s
    abcdef = string.ascii_lowercase + string.digits + string.ascii_uppercase
    fedcba = abcdef[::-1]
    h1 = hashlib.md5(b'<%s>' % s).hexdigest()
    h2 = hashlib.md5(b'</%s>' % h1.encode()).hexdigest()
    h = h1 + h2
    j = 0
    adict = {}
    for i in h:
        if not i.isalpha():
            continue
        if j >= 26:
            adict[j - 26] = i
        else:
            adict[j] = i
        j += 1
    a = []
    for j in adict:
        pos = abcdef.index(adict[j]) + j
        if pos >= 26:
            pos = pos - 26
        a.append(fedcba[pos])
    s1 = ''.join(a)
    if len(s1) >= 8:
        s2 = s1[:8]
    else:
        s2 = s1.ljust(8, s1[0])
    return s2


def get_local_ip_by_prefix(ip_prefix):
    local_ip = ''
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        if ip.startswith(ip_prefix):
            local_ip = ip

    return local_ip


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]
