FROM python:3.9

COPY /src/requirements.txt /requirements.txt
RUN pip3 install -U pip && pip3 install -r /requirements.txt

COPY src/ /src

CMD python3 /src/main.py