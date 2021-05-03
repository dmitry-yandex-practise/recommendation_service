# Рекомендательная система

## Запуск базы

1. Скачать файл сданными: https://disk.yandex.ru/d/gXsN_7fToWAJKQ
   У файла с данными должно быть имя movies-database.sql

2. Создать образ
```bash
docker build -f Dockerfile-with-data . -t movies-db
```

3. Запуск базы
```bash
docker run --rm -d -v movies-db-vol:/var/lib/postgresql/data -p 6432:5432 --name=movies-db movies-db
```
