# -*- coding: utf-8 -*-

import fnmatch
import hashlib
import os
from collections import defaultdict

from config import configProd
from .dbItf import write_db
from .helper import (catch_err_msg, char_convert, id_generator2)

HASH_BUFF_SIZE = configProd.PLUPLOAD_HASH_BUFF_SIZE


class Meta(object):
    __metadata___ = defaultdict(None)

    def __init__(self, data):
        self.__metadata__(metadata=data)
        self.__dict__.update(self.__metadata___)

    def __metadata__(self, key=None, value=None, metadata=None):
        if isinstance(metadata, dict):
            for k, v in list(metadata.items()):
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
            self.md = Meta(fid)
        else:
            self.md = Meta({"fid": fid})

        self.md = self.metadata

    @property
    def metadata(self):
        return self.md

    @staticmethod
    def encode(x):
        return hashlib.sha224(x.encode()).hexdigest()

    def _fn(self, path, name):
        # NOTE: This method should not change as some may depend on it.
        #       See: https://github.com/ionrock/cachecontrol/issues/63
        hashed = self.encode(name)
        parts = list(hashed[:5]) + [hashed]
        return os.path.join(path, *parts)


class FileInterface(FileBase):
    @staticmethod
    def allowed_file(filename, whitelist=list()):
        return ('.' in filename) and filename.rsplit('.', 1)[1] in whitelist

    @staticmethod
    def hash_file(buff):
        rh = hashlib.md5(buff).hexdigest()
        return rh

    @staticmethod
    def write_file(path, content, buff_size, mode="wb", **kwargs):
        """
        :param path: include path and filename
        :param content: the write content
        :param mode: default: wb
        :param buff_size: buffering
        """
        with open(path, mode, buffering=buff_size) as wf:
            wf.write(content)

    def mix_file(self, filename, uploadpath=None):
        if not uploadpath:
            uploadpath = os.path.abspath(os.path.dirname(__file__))

        # find file blocks
        file_block_list = []

        for file_ in os.listdir(uploadpath):
            file_ = char_convert(file_)

            if fnmatch.fnmatch(file_, "{}_*".format(filename)):
                file_block_list.append(file_)

        if file_block_list:
            file_block_list.sort(key=lambda i: int(i.rsplit("_", 1)[1]))

        # check MD5
        _MD5 = hashlib.md5()

        for file_item in file_block_list:
            with open(os.path.join(uploadpath, file_item), "rb", buffering=HASH_BUFF_SIZE) as rf:
                _MD5.update(rf.read(HASH_BUFF_SIZE))

        if _MD5.hexdigest() == getattr(self.md, "hash", ""):
            filename, filepath, is_exist = "", "", False
            for file_item in file_block_list:
                if any([not filename, not filepath]):
                    filename, _chunk_block = file_item.rsplit("_", 1)
                    filepath = os.path.join(uploadpath, filename)

                    if os.path.exists(filepath):
                        is_exist = True

                _filepath = os.path.join(uploadpath, file_item)
                if not is_exist:
                    with open(_filepath, "rb") as rf:
                        self.write_file(path=filepath,
                                        content=rf.read(),
                                        mode="ab",
                                        buff_size=os.path.getsize(_filepath))
                else:
                    return dict(msg="Exist")

                os.remove(_filepath)

            return dict(msg="Completed")
        else:
            return dict(msg="Hash Not Match")

    @staticmethod
    def check_exit_file(filename, chunks, uploadpath=None):
        """
        :param filename: saved file name
        :param chunks: how many file chunks
        :param uploadpath: the saving upload files dir
        :return: how many chunks has been saved. int type.
        """
        count = 0

        if os.path.exists(os.path.join(uploadpath, filename)):
            return chunks

        for chunk in range(chunks):
            filepath = os.path.join(uploadpath, "%s_%02d" % (filename, chunk))
            if os.path.exists(filepath):
                count += 1
            else:
                break

        return count

    def verify(self, input_pwd=""):
        assert hasattr(self.md, "password")
        return (not self.md.password) and True or ((input_pwd == self.md.password) and True or False)

    def get_file_name(self, is_file_prefix):
        if is_file_prefix:
            real_filename = "_".join([self.md.fid, self.md.filename])
        else:
            real_filename = self.md.filename

        return real_filename

    def get_file_path(self, full=True):
        if full:
            return os.path.join(configProd.UPLOAD_DIR, self.md.filename)
        else:
            return self.md.filename

    @catch_err_msg
    def delete_file(self, db_obj):
        sql = 'DELETE FROM "main"."index" WHERE ("id" = ?);'
        err_msg = write_db(db_obj, sql, args=(self.md.id,))

        if configProd.DELETE_IN_LOCAL:
            fp = self.get_file_path()
            if os.path.isfile(fp):
                os.remove(fp)

                err_msg = "succeed"

            else:
                err_msg = "Error: %s file not found" % self.get_file_path(full=False)

        return err_msg

    @staticmethod
    @catch_err_msg
    def share_file(db_obj, fid, share_type, pwd=None):
        msg = ""
        sql = 'UPDATE "main"."index" SET "password" = ? WHERE ("fid" = ?);'
        if share_type == "share":  # share
            pwd = id_generator2(4)
            msg = write_db(db_obj, sql, args=(pwd, fid))

        elif share_type == "unshare":  # stop share
            msg = write_db(db_obj, sql, args=(pwd, fid))

        return msg

    def __repr__(self):
        return "<{} @name={}>".format(self.__class__.__name__, self.metadata.filename)
