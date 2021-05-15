/*
CREATE TABLE default.user_reviews (id UUID,
                                   film_work_id UUID,
                                   user_id UUID,
                                   score Int8,
                                   review_date Date) Engine=MergeTree()
      ORDER BY id;
*/

CREATE TABLE IF NOT EXISTS default.reviews (
    review_id UUID,
    movie_id UUID,
    user_id UUID,
    score Int8,
    review_date Date
) ENGINE = MergeTree
ORDER BY review_date;

CREATE TABLE if not exists default.kafka_queue (
    movie_id UUID,
    user_id UUID,
    score Int8,
    review_date Date
  ) ENGINE = Kafka SETTINGS
    kafka_broker_list = 'broker:29092',
    kafka_topic_list = 'reviews',
    kafka_group_name = 'clickhouse_views',
    kafka_format = 'JSONEachRow',
    kafka_row_delimiter = '\n';

CREATE MATERIALIZED VIEW IF NOT EXISTS reviews_consumer TO default.reviews
AS SELECT _key as review_id,
          movie_id,
          user_id,
          score,
          review_date Date
FROM kafka_queue;
