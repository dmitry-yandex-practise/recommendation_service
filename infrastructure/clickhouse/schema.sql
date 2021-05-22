CREATE DATABASE IF NOT EXISTS ugc_data;

CREATE TABLE IF NOT EXISTS ugc_data.review_film_work (
    review_id UUID,
    film_work_id UUID,
    user_id UUID,
    score Int8,
    review_date Date
) ENGINE = MergeTree
ORDER BY review_date;

CREATE TABLE if not exists ugc_data.kafka_queue (
    film_work_id UUID,
    user_id UUID,
    score Int8,
    review_date Date
  ) ENGINE = Kafka SETTINGS
    kafka_broker_list = 'broker:29092',
    kafka_topic_list = 'reviews',
    kafka_group_name = 'clickhouse_views',
    kafka_format = 'JSONEachRow',
    kafka_row_delimiter = '\n';

CREATE MATERIALIZED VIEW IF NOT EXISTS ugc_data.reviews_consumer TO ugc_data.review_film_work
AS SELECT _key as review_id,
          film_work_id,
          user_id,
          score,
          review_date Date
FROM ugc_data.kafka_queue;
