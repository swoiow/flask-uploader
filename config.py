#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

db_name = "data.db"
basedir = "" or os.path.abspath(os.path.dirname(__file__))

PER_SIZE = 30

DEBUG = True
PORT = 801
HOST = "0.0.0.0"

LOG_DIR = os.path.join(basedir, "includes", "log")
DB_DIR = os.path.join(basedir, "includes", db_name)
UPLOAD_DIR = os.path.join(basedir, "uploads")
SCHEMA_SQL_FILE = os.path.join(basedir, "includes", "schema.sql")

FILE_PREFIX = False
FILE_EXT_CHENK = False
CHUNK_SIZE = 5 * 1024 * 1024  # equal to 1MB
SEND_FILE_MAX_AGE_DEFAULT = 30 * 60
MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 文件大小的上限

ALLOWED_EXTENSIONS = {"mp3", "mp4", "avi", "jpg", "gif", "png", "pdf", "bmp", "jpeg", "zip", "rar", "7z", "bz2", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "md"}

CSRF_ENABLED = True
SESSION_COOKIE_HTTPONLY = True
SECRET_KEY = r"<\xc8\xea}\xcf&\xf6*b^\xe8}\xb8$\xda\xc1\x15\xe6v<[j\xf9\xeco\x88\xf0\xaa\x7f\xf9\xfd\xef"

UP_CFG = {
    "chunk_size": os.environ.get("UPLOAD_CHUNK_SIZE", CHUNK_SIZE),
    "max_content_length": os.environ.get("UPLOAD_MAX_LENGTH", MAX_CONTENT_LENGTH)
}

__all__ = [var for var in dir() if var.isupper()]
