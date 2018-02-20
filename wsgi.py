# -*- coding: utf-8 -*-

from gevent import monkey
from gevent.pool import Pool
from gevent.pywsgi import WSGIServer

from view import app
from utils.helper import get_local_ip_by_prefix
import config

monkey.patch_all()

host = config.HOST
port = config.PORT

ip = get_local_ip_by_prefix("192")
print(u"\n本机IP：%s" % ip)
print (u"请使用手机浏览器'Internet Explorer'，访问  http://{}:{}\n".format(ip, config.PORT))

http_server = WSGIServer((host, port), app, spawn=Pool(4))
http_server.serve_forever()
