FROM python:alpine

WORKDIR /app

RUN addgroup -S app && adduser -S -g app app \
    && apk update && apk upgrade \
    && apk add --no-cache dumb-init \
    && wget -O- https://github.com/swoiow/flask-uploader/archive/dev.tar.gz | tar zx \
    && mv flask-uploader-dev/* ./ \
    && pip install https://github.com/swoiow/libs/raw/master/gevent/greenlet-0.4.14-cp37-cp37m-linux_x86_64.whl --no-cache-dir \
    && pip install https://github.com/swoiow/libs/raw/master/gevent/gevent-1.3.5-cp37-cp37m-linux_x86_64.whl --no-cache-dir \
    && pip install -r requirements.txt --no-cache-dir \
    && mkdir -p ./data/uploads \
    && chown -R app:app /app \
    && python testcase.py

USER app

ENTRYPOINT ["dumb-init", "--"]

EXPOSE 30080

CMD ["/usr/local/bin/python", "wsgi.py"]
