# Рекомендательная система

## Запуск базы

Схема базы описана в schema.sql


1. Скачать файл сданными: https://disk.yandex.ru/d/Hmvueqd-2d6yRQ
   У файла с данными должно быть имя movies-database.sql

2. Создать образ
```bash
docker build -f Dockerfile-with-data . -t movies-db-with-data
```

3. Запуск базы
```bash
docker run --rm -d -v movies-db-vol:/var/lib/postgresql/data -p 6432:5432 --name=movies-db movies-db-with-data
```
