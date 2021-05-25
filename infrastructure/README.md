## Запуск баз

1. Создаем сеть

```
docker network create recommendations-backend
```

2. Скачать файл сданными для postgres: https://disk.yandex.ru/d/Hmvueqd-2d6yRQ
   У файла с данными должно быть имя movies-database.sql.
   Директория ./pg_and_redis/

3. Запуск pg и redis
    Выполняем команду внутри pg_and_redis
    ```
    docker-compose up --build -d
    ```

4. Скачать файл с историей посещения фильма: https://disk.yandex.ru/d/DcCMz8cYNUn6rw
   У файла с данными должно быть имя film_work_views.csv

5. Скачать файл с историей посещения фильма: https://disk.yandex.ru/d/8eBy4iQhFPIlQw
   У файла с данными должно быть имя person_views.csv

6. Скачать файл сданными для clickhouse: https://disk.yandex.ru/d/eonTFeMJl7Xi5w
   У файла с данными должно быть имя pg_review_data_all.csv
   Директория ./clickhouse/
   ```
   docker-compose up --build -d
   ```
7. Запуск kafka
   Директория ./kafka/
   ```
   docker-compose up --build -d
   ```