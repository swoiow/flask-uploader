# -*- coding: utf-8 -*-

import sqlite3

from flask import _app_ctx_stack

import config as Cfg

SCHEMA_SQL = Cfg.SCHEMA_SQL_FILE
DB_PATH = Cfg.DB_DIR


def connect_db():
    _db = sqlite3.connect(DB_PATH)
    _db.row_factory = sqlite3.Row
    return _db


def get_db():
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(DB_PATH)
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db


def init_db():
    db = connect_db()

    with open(SCHEMA_SQL, mode="r") as rf:
        db.cursor().executescript(rf.read())
    db.commit()

    if not query_db(db, 'SELECT * FROM "users" WHERE "username" = "demo"', one=True):
        sql = 'INSERT INTO "users" ("username", "pw_hash", "pms") VALUES ("demo", "pbkdf2:sha1:1000$JRgRzRjc$6f868a04660633294eea9cf737a032a1e7eecb7d", "admin");'
        write_db(db, sql)


def query_db(db_obj, query, args=(), one=False):
    cur = db_obj.execute(query, args)
    # rv = [{cur.description[idx][0]: value for idx, value in enumerate(row)} for row in cur.fetchall()]
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def write_db(db_obj, query, args=()):
    rtn_msg = ""
    try:
        cur = db_obj.execute(query, args)
        db_obj.commit()
        rtn_msg = "succeed"
    except Exception as e:
        rtn_msg = e
    finally:
        return rtn_msg


if __name__ == '__main__':
    print(dir())
