# -*- coding: utf-8 -*-

from gevent import monkey
from gevent.pool import Pool
from gevent.pywsgi import WSGIServer

from config import configProd
from utils.helper import get_local_ip
from view import app

monkey.patch_all()

config = configProd

host = config.HOST
port = config.PORT

ip = get_local_ip()
print("\n本机IP：%s" % ip)
print("请使用手机浏览器'Internet Explorer'，访问  http://{}:{}\n".format(ip, config.PORT))

http_server = WSGIServer((host, port), app, spawn=Pool(4))
http_server.serve_forever()
