FROM python:3.9
ENV LUIGI_CONFIG_PATH=/src/luigi.cfg

COPY /src/requirements.txt /requirements.txt
RUN pip3 install -U pip && pip3 install -r /requirements.txt

COPY src/ /src

CMD bash -c "luigid --background && python3 /src/main.py"