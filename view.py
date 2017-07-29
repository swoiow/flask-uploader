# -*- coding: utf-8 -*-

"""
http://blog.csdn.net/luoyehanfei/article/details/41803259
http://www.oschina.net/code/snippet_1767531_39336
https://github.com/moxiecode/plupload/wiki/File#loaded-property
"""

import os

from datetime import datetime

from flask import (Flask, render_template, request, redirect, url_for, abort, jsonify, _app_ctx_stack)

from config import *
from utils import *

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app = Flask("uploads", static_folder="static", template_folder="templates")
app.config.from_object('config')
app.add_template_filter(datetime_format, name="dateformat")


@app.route("/pages/<int:page>")
@app.route("/index")
@app.route("/")
def index(page=1):
    sql = 'SELECT * FROM "index" ORDER BY creat_date DESC LIMIT ? OFFSET ?;'
    rv = query_db(get_db(), sql, args=(PER_SIZE, PER_SIZE * (page - 1)))
    file_set = [FileCls(dict(row)).metadata for row in rv]

    return render_template("index.html", files=file_set, cp=page)


@app.route("/f/<fid>", methods=["GET", "POST"])
def details(fid=None):
    sql = 'SELECT * FROM "index" WHERE fid = ?;'
    rv = query_db(get_db(), sql, args=(fid,), one=True)

    if rv:
        file_obj = FileCls(dict(rv))

        if request.form.get("button", "") == u"delete":  # (session.get("userPMS") == u"admin") and
            file_obj.delete_file(db_obj=get_db())
            return redirect(url_for("index"))

        return render_template("details.html", file=file_obj.md)

    return abort(404)


@app.route("/uploads", methods=["GET", "POST"])
def uploads():
    if request.method == "POST":
        _file = request.files["file"]
        filename = char_trans(request.form["name"])
        file_hash = request.form["hs"]

        allowed = FileCls.allowed_file(filename, PLUPLOAD_ALLOWED_EXTENSIONS) if FILE_EXT_CHECK else True
        if any([not _file, not allowed, not file_hash]):
            return jsonify(msg="-2, Not allow"), 501
        else:
            chunk = request.form.get("chunk", 0, type=int)  # current chunk block
            chunks = request.form.get("chunks", 0, type=int)  # how many chunks block

            sql_query = 'SELECT fid, filename, hash FROM "index" WHERE hash = ?;'
            get_file = query_db(get_db(), sql_query, args=(file_hash,), one=True)

            if not get_file:
                # 文件不存在
                fid = id_generator(6, check_db=True, db=get_db())

                file_obj = FileCls(fid)
                file_obj.md.filename = filename

                sql = 'INSERT INTO "index" ("fid", "hash", "filename", "creat_date") VALUES (?, ?, ?, ?);'
                write_db(get_db(), sql, (fid, file_hash, filename, datetime.utcnow()))

            else:
                # 文件已存在
                file_obj = FileCls(dict(get_file))

            real_filename = file_obj.get_file_name(FILE_PREFIX)

            __BIN__ = _file.read()
            if chunks == 1:
                # 处理不需要分块的文件
                filepath = os.path.join(UPLOAD_DIR, real_filename)
            else:
                filepath = os.path.join(UPLOAD_DIR, "%s_%02d" % (real_filename, chunk))
            file_obj.write_file(filepath, content=__BIN__, buff_size=PLUPLOAD_CHUNK_SIZE)

            if (chunk == chunks - 1) and (chunks > 1):
                mix_msg = file_obj.mix_file(real_filename, uploadpath=UPLOAD_DIR)
                return jsonify(msg="0, " + mix_msg, file_address=url_for("details", fid=file_obj.md.fid))

            return jsonify(msg="1, Block has been uploaded", uploaded=(chunk + 1) * PLUPLOAD_CHUNK_SIZE)

    return render_template("demo.html", cfg=UPLOAD_CONFIG)


@app.route("/check_uploads", methods=["POST"])
def check_uploads():
    rt = {"has_loaded": 0}
    exit_chunks, chunk_size = 0, PLUPLOAD_CHUNK_SIZE

    file_chunks = request.form.get("mc", "")
    file_hash = request.form.get("hs", "")

    if file_chunks and file_hash:
        sql = 'SELECT fid, filename FROM "index" WHERE hash = ?;'
        rv = query_db(get_db(), sql, (file_hash,), one=True)

        if rv:
            file_obj = FileCls(dict(rv))
            filename = file_obj.get_file_name(FILE_PREFIX)
            exit_chunks = FileCls.check_exit_file(filename=filename, chunks=int(file_chunks), uploadpath=UPLOAD_DIR)

        rt.update(dict(has_loaded=exit_chunks * chunk_size))

    return jsonify(rt)


@app.teardown_request
def after_request(response):
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()

    return response


if __name__ == '__main__':
    ip = get_local_ip_by_prefix("192")
    print(u"\n本机IP：%s" % ip)
    print (u"请使用手机浏览器'Internet Explorer'，访问  http://{}:{}\n".format(ip, PORT))

    kw = dict(debug=DEBUG, port=PORT, host=HOST)
    app.run(**kw)
