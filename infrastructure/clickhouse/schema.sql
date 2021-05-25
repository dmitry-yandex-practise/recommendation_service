CREATE DATABASE IF NOT EXISTS ugc_data;
--
-- review event
--

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


--
-- person view event 
--

CREATE TABLE IF NOT EXISTS ugc_data.person_view (
    view_id UUID,
    person_id UUID,
    user_id UUID,
    view_date Date
) ENGINE = MergeTree
ORDER BY view_date;

CREATE TABLE if not exists ugc_data.kafka_person_view_queue (
    person_id UUID,
    user_id UUID,
    view_date Date
  ) ENGINE = Kafka SETTINGS
    kafka_broker_list = 'broker:29092',
    kafka_topic_list = 'person_view',
    kafka_group_name = 'clickhouse_views',
    kafka_format = 'JSONEachRow',
    kafka_row_delimiter = '\n';

CREATE MATERIALIZED VIEW IF NOT EXISTS ugc_data.person_view_consumer TO ugc_data.person_view
AS SELECT _key as view_id,
          person_id,
          user_id,
          view_date Date
FROM ugc_data.kafka_person_view_queue;

--
-- movie view event 
--

CREATE TABLE IF NOT EXISTS ugc_data.movie_view (
    view_id UUID,
    film_work_id UUID,
    user_id UUID,
    view_date Date
) ENGINE = MergeTree
ORDER BY view_date;

CREATE TABLE if not exists ugc_data.kafka_movie_view_queue (
    film_work_id UUID,
    user_id UUID,
    view_date Date
  ) ENGINE = Kafka SETTINGS
    kafka_broker_list = 'broker:29092',
    kafka_topic_list = 'movie_view',
    kafka_group_name = 'clickhouse_views',
    kafka_format = 'JSONEachRow',
    kafka_row_delimiter = '\n';

CREATE MATERIALIZED VIEW IF NOT EXISTS ugc_data.movie_view_consumer TO ugc_data.movie_view
AS SELECT _key as view_id,
          film_work_id,
          user_id,
          view_date Date
FROM ugc_data.kafka_movie_view_queue;
