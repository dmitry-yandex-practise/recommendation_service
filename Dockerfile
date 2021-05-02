FROM postgres:12.5

RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV POSTGRES_PASSWORD pass
ENV POSTGRES_DB movies_database

COPY schema.sql /docker-entrypoint-initdb.d/schema.sql
