FROM python:3.8

COPY ./requirements.txt /requirements.txt
RUN pip3 install -U pip && pip3 install -r /requirements.txt

COPY . .
