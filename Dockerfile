FROM nischalstha/python_postgres_master:0.1

RUN apk update \
    && apk add curl bash

RUN mkdir /code
WORKDIR /code

COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN chmod 755 /code/docker-entrypoint.sh
RUN chmod 755 /code/celery.sh
# RUN sh ./docker-entrypoint.sh