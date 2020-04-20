# -*- coding: utf-8 -*-

FROM python:3.7-alpine

RUN mkdir -p /app/ \
 && mkdir p /var/lib/demo/

COPY ./generate.py /app/generate.py

WORKDIR /app/

CMD ["python", "generate.py"]
