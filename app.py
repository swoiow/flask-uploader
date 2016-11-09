from os import path as os_path, mkdir as os_mkdir

from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

PER_SIZE = app.config['PER_SIZE']
DB_PATH = app.config['DB_DIR']
ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']

CHUNK_SIZE = app.config["CHUNK_SIZE"]
UPLOAD_PATH = app.config['UPLOAD_DIR']

if not os_path.exists(UPLOAD_PATH):
    os_mkdir(UPLOAD_PATH)

upload_app = app
