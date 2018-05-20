# -*- coding: utf-8 -*-

import os

db_name = "data.db"
basedir = os.path.abspath(os.path.dirname(__file__))


class Default(object):
    SAVE_FILE_MODE = "direct"
    # SAVE_FILE_MODE = "hash"
    DELETE_IN_LOCAL = True

    PER_SIZE = 30

    LOG_DIR = os.path.join(basedir, "data", "log")
    DB_DIR = os.environ.get("DB_DIR", os.path.join(basedir, "data", db_name))
    UPLOAD_DIR = os.path.join(basedir, "data", "uploads")
    SCHEMA_SQL_FILE = os.path.join(basedir, "utils", "schema.sql")


class WebConfig(object):
    DEBUG = True
    PORT = 801
    HOST = "0.0.0.0"

    CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True

    SECRET_KEY = os.urandom(32)

    FILE_PREFIX = False
    FILE_EXT_CHECK = False

    def __init__(self):
        dp = os.path.join(basedir, "data")
        if not os.path.exists(dp):
            os.makedirs(dp)


class PluploadConfig(object):
    PLUPLOAD_HASH_BUFF_SIZE = 1024 * 4  # 数值不能太低, default 4096
    PLUPLOAD_CHUNK_SIZE = 5 * 1024 * 1024  # equal to 5MB
    PLUPLOAD_SEND_FILE_MAX_AGE_DEFAULT = 30 * 60
    PLUPLOAD_MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 文件大小的上限

    PLUPLOAD_ALLOWED_EXTENSIONS = [
        "mp3", "mp4", "avi",
        "jpg", "gif", "png", "pdf", "bmp", "jpeg",
        "zip", "rar", "7z", "bz2", "tar.gz",
        "doc", "docx", "xls", "xlsx", "ppt", "pptx",
        "txt", "md"
    ]


class DefaultConfig(Default, WebConfig, PluploadConfig):

    def to_list(self):
        pr = {}
        for name in dir(self):
            value = getattr(self, name)
            if not name.startswith('_') and not callable(value):
                pr[name] = value

        return pr.items()

    def _save_config(self):
        import json
        json.dumps(self)

    def _load_config(self):
        pass


configProd = DefaultConfig()
