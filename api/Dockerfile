FROM python:3.8

ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV ELASTIC_HOST=es01
ENV ELASTIC_PORT=9200

COPY /src/requirements.txt /requirements.txt
RUN pip3 install -U pip && pip3 install -r /requirements.txt

COPY utils/ /utils

COPY src/ /src

ENTRYPOINT ["utils/entrypoint_waiter.sh"]

CMD python3 /src/main.py
