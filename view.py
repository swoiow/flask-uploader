#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
http://blog.csdn.net/luoyehanfei/article/details/41803259
http://www.oschina.net/code/snippet_1767531_39336
https://github.com/moxiecode/plupload/wiki/File#loaded-property
"""
from collections import defaultdict
from datetime import datetime

from flask import (render_template, request, redirect, session, url_for, abort, jsonify, send_from_directory,
                   _app_ctx_stack)
from werkzeug.security import check_password_hash

from app import *
from includes.dbInterface import (query_db, get_db, write_db)
from includes.fileInterface import FileInterface as FileINT
from includes.units import (char_trans, id_generator)


@upload_app.route("/pages/<int:page>")
@upload_app.route("/")
def index(page=1):
    sql = 'SELECT * FROM "index" ORDER BY creat_date DESC LIMIT ? OFFSET ?;'
    rv = query_db(get_db(), sql, args=(PER_SIZE, PER_SIZE * (page - 1)))
    fileObjs = [FileINT(dict(row)).metadata for row in rv]

    return render_template("index.html", files=fileObjs, cp=page)


@upload_app.route("/f/<fid>", methods=["GET", "POST"])
def details(fid=None):
    sql = 'SELECT * FROM "index" WHERE fid = ?;'
    rv = query_db(get_db(), sql, args=(fid,), one=True)

    if rv:
        fileObj = FileINT(dict(rv))
        is_allowed = security(fileObj)

        if session.get("userPMS") == u"admin":
            is_allowed = True

        if request.method == "POST":

            if request.form.get("button") == u"security":
                _pwd = request.form.get("pwd", "").strip()
                is_allowed = security(fileObj, pwd_verify=_pwd)

            if is_allowed and (request.form.get("button") == u"download"):
                return redirect(url_for("download", token=fileObj.md.fid))

            if (session.get("userPMS") == u"admin") and (request.form.get("button") == u"delete"):
                rv = fileObj.delete_file(db_obj=get_db())
                # return jsonify(rv)
                return redirect(url_for("index"))

        return render_template("details.html", allowed=is_allowed, file=(is_allowed and fileObj.md))

    return abort(404)


@upload_app.route("/uploads", methods=["GET", "POST"])
def uploads():
    if request.method == "POST":
        _file = request.files["file"]
        filename = char_trans(request.form["name"])
        file_hash = request.form["hs"]

        allowed = FileINT.allowed_file(filename, whitelist=ALLOWED_EXTENSIONS)
        if any([not _file, not allowed, not file_hash]):
            return jsonify(msg="-2, Not allow"), 501
        else:
            chunk = request.form.get("chunk", 0, type=int)  # current chunk block
            chunks = request.form.get("chunks", 0, type=int)  # how many chunks block

            sql_query = 'SELECT fid, filename, hash FROM "index" WHERE hash = ?;'
            rv = query_db(get_db(), sql_query, args=(file_hash,), one=True)

            if not rv:
                # 文件不存在
                fid = id_generator(6, check_db=True, db=get_db())

                fileObj = FileINT(fid)
                fileObj.md.filename = filename

                sql = 'INSERT INTO "index" ("fid", "hash", "filename", "creat_date") VALUES (?, ?, ?, ?);'
                write_db(get_db(), sql, (fid, file_hash, filename, datetime.utcnow()))

            else:
                # 文件已存在
                fileObj = FileINT(dict(rv))

            w_filename = "_".join([fileObj.md.fid, fileObj.md.filename])

            __BIN__ = _file.read()
            if chunks == 1:
                # 处理不需要分块的文件
                filepath = os_path.join(UPLOAD_PATH, w_filename)
            else:
                filepath = os_path.join(UPLOAD_PATH, "%s_%02d" % (w_filename, chunk))
            fileObj.write_file(filepath, content=__BIN__, buff_size=CHUNK_SIZE)

            if (chunk == chunks - 1) and (chunks > 1):
                mix_msg = fileObj.mix_file(w_filename, uploadpath=UPLOAD_PATH)
                return jsonify(msg="0, " + mix_msg, file_address=url_for("details", fid=fileObj.md.fid))

            return jsonify(msg="1, Block has been uploaded", uploaded=(chunk + 1) * CHUNK_SIZE)

    return render_template("demo.html", cfg=app.config["UP_CFG"])


@upload_app.route("/check_uploads", methods=["POST"])
def check_uploads():
    rt = {"has_loaded": 0}
    exit_chunks, chunk_size = 0, CHUNK_SIZE

    file_chunks = request.form.get("mc", "")
    file_hash = request.form.get("hs", "")

    if file_chunks and file_hash:
        sql = 'SELECT fid, filename FROM "index" WHERE hash = ?;'
        rv = query_db(get_db(), sql, (file_hash,), one=True)

        if rv:
            fileObj = FileINT(dict(rv))
            filename = char_trans("_".join([fileObj.md.fid, fileObj.md.filename]))
            exit_chunks = FileINT.check_exit_file(filename=filename, chunks=int(file_chunks), uploadpath=UPLOAD_PATH)

        rt.update(has_loaded=exit_chunks * chunk_size)

    return jsonify(rt)


@upload_app.route("/d/<token>", methods=["GET"])
def download(token):
    sql = 'SELECT fid FROM "index" WHERE fid = ?;'
    rv = query_db(get_db(), sql, args=(token,), one=True)

    fileObj = FileINT(dict(rv))
    try:
        _FILE_NAME = "_".join([fileObj.md.fid, fileObj.md.filename])
        kw = dict(attachment_filename=char_trans(fileObj.md.filename, str_=True), as_attachment=True, cache_timeout=0)
        return send_from_directory(UPLOAD_PATH, _FILE_NAME, **kw)
    except KeyError:
        return abort(404)


@upload_app.route("/share_friends/<share_type>", methods=["POST"])
def share_friends(share_type=None):
    fid = request.form.get("id", type=str)

    is_allowed = security(FileINT(fid))
    if is_allowed:
        FileINT.share_file(db_obj=get_db(), fid=fid, share_type=share_type)
    else:
        return abort(400)

    return redirect(request.referrer, 302)


@upload_app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        sql = 'SELECT * FROM users WHERE username = ?;'
        user = query_db(get_db(), sql, (request.form['username'],), one=True)

        if user is None:
            error = "Invalid username"
        elif not check_password_hash(user['pw_hash'], request.form['password']):
            error = "Invalid password"
        else:
            # write session
            session.update(logged_in=True, user=user['username'], userPMS=user["pms"])
            return redirect(url_for("index"))

    return render_template("login.html", error=error)


@upload_app.route("/logout")
def logout():
    rm = ["logged_in", "user", "access", "userPMS"]
    for item in rm:
        session.pop(item, None)
    return redirect(url_for("index"))


@upload_app.before_request
def before_request():
    if upload_app.config["DEBUG"] and session.get("times", 0) < 1:
        if not session.get("logged_in", False) and request.remote_addr in ["127.0.0.1", "localhost"]:
            session.update(logged_in=True, user="demo", times=1, userPMS="admin")

    if not session.get("logged_in", False) and request.endpoint not in ("login", "logout", "static", "details"):
        return redirect("login")

    if not session.get("access"):
        session["access"] = defaultdict(lambda: False)


@upload_app.teardown_request
def after_request(response):
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()

    return response


def security(fileObj, pwd_verify=""):
    _fid = fileObj.md.fid

    if fileObj.verify(pwd_verify):
        session["access"][_fid] = True

    return session["access"].get(_fid)


if __name__ == '__main__':
    __import__("includes.filterInterface")

    kw = dict(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])
    upload_app.run(**kw)
