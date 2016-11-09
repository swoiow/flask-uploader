from gevent import monkey
from gevent.pool import Pool
from gevent.pywsgi import WSGIServer

from view import upload_app
__import__("includes.filterInterface")

monkey.patch_all()

host = ""
port = 5000

http_server = WSGIServer((host, port), upload_app, spawn=Pool(4))
print "\nlisten on {}:{}".format(host, port)
http_server.serve_forever()
