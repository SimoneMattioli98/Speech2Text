FROM python:3.6.13-alpine3.12

WORKDIR /webApp
EXPOSE 80

RUN apk add --no-cache cargo rust libressl-dev musl-dev libffi-dev build-base \
 && pip install --upgrade pip setuptools wheel

COPY ./requirements.txt /webApp

RUN pip install --no-cache-dir -r /webApp/requirements.txt \
 && apk del libressl-dev musl-dev libffi-dev build-base

COPY ./ /webApp/

RUN chmod +x /webApp/start.sh

ENTRYPOINT ["/bin/sh", "-c", "/webApp/start.sh"]