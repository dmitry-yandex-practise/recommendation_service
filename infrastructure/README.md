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

4. Скачать файл сданными для clickhouse: https://disk.yandex.ru/d/eonTFeMJl7Xi5w
   У файла с данными должно быть имя pg_review_data_all.csv
   Директория ./clickhouse/
   ```
   docker-compose up --build -d
   ```

5. Запуск kafka
   Директория ./kafka/
   ```
   docker-compose up --build -d
   ```