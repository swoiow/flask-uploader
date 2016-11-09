#!/usr/bin/env python
# -*- coding: utf-8 -*-
import fnmatch
import functools
import hashlib
from collections import defaultdict
from os import listdir as os_listdir, remove as os_remove, path as os_path

from dbInterface import write_db
from units import (char_trans, id_generator)

__all__ = ["FileInterface"]


def catch_err_msg(func):
    import traceback

    @functools.wraps(func)
    def wrapper(*args, **kw):
        # wrapper.err_msg = "xxx"
        try:
            wrapper.err_msg = func(*args, **kw)
        except Exception, e:
            wrapper.err_msg = e
        finally:
            traceback.print_exc()
            return {"msg": wrapper.err_msg}

    # wrapper.err_msg = ""
    return wrapper


class Meta(object):
    __metadata___ = defaultdict(None)

    def __init__(self, data):
        self.__metadata__(metadata=data)
        self.__dict__.update(self.__metadata___)

    def __metadata__(self, key=None, value=None, metadata=None):
        if isinstance(metadata, dict):
            for k, v in metadata.items():
                self.__metadata___[k] = v

        if key and value:
            self.__setitem__(key=key, value=value)

    def __getitem__(self, item):
        return self.__metadata___.get(item, None)

    def __setitem__(self, key, value):
        self.__metadata___[key] = value
        self.__dict__.update({key: value})


class FileBase(object):
    def __init__(self, fid):
        if isinstance(fid, dict):
            self.metadata = Meta(fid)
        else:
            self.metadata = Meta({"fid": fid})

        self.md = self.metadata


class FileInterface(FileBase):
    @staticmethod
    def allowed_file(filename, whitelist=list()):
        return ('.' in filename) and filename.rsplit('.', 1)[1] in whitelist

    @staticmethod
    def hash_file(buff):
        rh = hashlib.md5(buff).hexdigest()
        return rh

    @staticmethod
    def write_file(path, content, buff_size, **kwargs):
        """
        :param path: include path and filename
        :param content: the write content
        :param buff_size: buffering
        """
        with open(path, "ab", buffering=buff_size) as wf:
            wf.write(content)

    def mix_file(self, filename, uploadpath=None):
        file_block_list = []

        if uploadpath is None:
            uploadpath = os_path.abspath(os_path.dirname(__file__))

        # find file blocks
        for file_ in os_listdir(uploadpath):
            file_ = char_trans(file_)

            if fnmatch.fnmatch(file_, u"{0}*".format(filename)):
                file_block_list.append(file_)
        file_block_list.sort(key=lambda i: int(i.rsplit("_", 1)[1]))

        # check MD5
        _MD5 = hashlib.md5()

        for file_item in file_block_list:
            with open(os_path.join(uploadpath, file_item), "rb", buffering=4) as rf:
                _MD5.update(rf.read(4))

        if _MD5.hexdigest() == getattr(self.md, "hash", ""):
            filename, filepath, is_exist = "", "", False
            for file_item in file_block_list:
                if any([not filename, not filepath]):
                    filename, _chunk_block = file_item.rsplit("_", 1)
                    filepath = os_path.join(uploadpath, filename)

                    if os_path.exists(filepath):
                        is_exist = True

                _filepath = os_path.join(uploadpath, file_item)
                if not is_exist:
                    with open(_filepath, "rb") as rf:
                        self.write_file(path=filepath, content=rf.read(), buff_size=os_path.getsize(_filepath))
                else:
                    return "Exist"

                os_remove(_filepath)

            return "Completed"
        else:
            return "Not Match"

    @staticmethod
    def check_exit_file(filename, chunks, uploadpath=None):
        """
        :param filename: saved file name
        :param chunks: how many file chunks
        :param uploadpath: the saving upload files dir
        :return: how many chunks has been saved. int type.
        """
        count = 0
        if uploadpath is None:  # TODO: 没uploadpath报错
            uploadpath = os_path.abspath(os_path.dirname(__file__))

        if os_path.exists(os_path.join(uploadpath, filename)):
            return chunks

        for chunk in range(chunks):
            filepath = os_path.join(uploadpath, "%s_%02d" % (filename, chunk))
            if os_path.exists(filepath):
                count += 1
            else:
                break

        return count

    def verify(self, input_pwd=""):
        assert hasattr(self.md, "password")
        return (not self.md.password) and True or ((input_pwd == self.md.password) and True or False)

    @catch_err_msg
    def delete_file(self, db_obj):
        sql = 'DELETE FROM "main"."index" WHERE ("id" = ?);'
        err_msg = write_db(db_obj, sql, args=(self.md.id,))

        # TODO:delete file in local

        return err_msg

    @staticmethod
    @catch_err_msg
    def share_file(db_obj, fid, share_type, pwd=None):
        msg = ""
        sql = 'UPDATE "main"."index" SET "password" = ? WHERE ("fid" = ?);'
        if share_type == u"share":  # share
            pwd = id_generator(4)
            msg = write_db(db_obj, sql, args=(pwd, fid))

        elif share_type == u"unshare":  # stop share
            msg = write_db(db_obj, sql, args=(pwd, fid))

        return msg
