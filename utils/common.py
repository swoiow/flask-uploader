# -*- coding: utf-8 -*-
import random
import string
import socket

try:
    from dbInterface import query_db
except ImportError as e:
    import traceback

    traceback.print_exc()
    # print "Track INFO: ", u"Unable to import: {} in {}".format(e.message, __file__)


def char_trans(word, coding="utf-8", str_=False):
    """
    :param str_: 是否转换成str。默认返回utf8
    """
    if str_:
        if isinstance(word, str):
            return word

        if isinstance(word, unicode):
            try:
                return word.encode(coding)
            except UnicodeEncodeError:
                return char_trans(word.encode("gbk"), str_=True)

    if isinstance(word, unicode):
        return word

    if isinstance(word, str):
        try:
            return word.decode(coding)
        except UnicodeDecodeError:
            return char_trans(word.decode("gbk"))


def id_generator(size=6, db=None, chars=string.ascii_letters + string.digits, check_db=False):
    if check_db:
        assert db is not None

        _MAX_RETRY, _SIZE = 10, 6
        while _MAX_RETRY > 0:
            fid = id_generator(size=_SIZE)
            sql_query = 'SELECT fid FROM "index" WHERE fid = ?;'
            rv = query_db(db, sql_query, args=(fid,), one=True)

            if rv is None:
                break
            else:
                _MAX_RETRY -= 1
                if _MAX_RETRY == 0:
                    _MAX_RETRY, _SIZE = 10, _SIZE + 1
        return fid

    else:
        return ''.join(random.choice(chars) for _ in range(size))


def get_local_ip_by_prefix(prefix):
    local_ip = ''
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        if ip.startswith(prefix):
            local_ip = ip

    return local_ip
