# -*- coding: utf-8 -*-

import os

db_name = "data.db"
basedir = "" or os.path.abspath(os.path.dirname(__file__))

PER_SIZE = 30

DEBUG = False
PORT = 801
HOST = "0.0.0.0"

LOG_DIR = os.path.join(basedir, "data", "log")
DB_DIR = os.path.join(basedir, "data", db_name)
UPLOAD_DIR = os.path.join(basedir, "data", "uploads")
SCHEMA_SQL_FILE = os.path.join(basedir, "utils", "schema.sql")

CSRF_ENABLED = True
SESSION_COOKIE_HTTPONLY = True
SECRET_KEY = r"<\xc8\xea}\xcf&\xf6*b^\xe8}\xb8$\xda\xc1\x15\xe6v<[j\xf9\xeco\x88\xf0\xaa\x7f\xf9\xfd\xef"

FILE_PREFIX = False
FILE_EXT_CHECK = False

PLUPLOAD_HASH_BUFF_SIZE = 128
PLUPLOAD_CHUNK_SIZE = 5 * 1024 * 1024  # equal to 5MB
PLUPLOAD_SEND_FILE_MAX_AGE_DEFAULT = 30 * 60
PLUPLOAD_MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 文件大小的上限

PLUPLOAD_ALLOWED_EXTENSIONS = {"mp3", "mp4", "avi", "jpg", "gif", "png", "pdf", "bmp", "jpeg", "zip", "rar", "7z", "bz2", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "md"}

UPLOAD_CONFIG = {k: v for k, v in globals().items() if k.startswith("PLUPLOAD_")}

__all__ = [var for var in dir() if var.isupper()]
