from clickhouse_driver import Client

CLICKHOUSE_HOST = 'localhost'
KAFKA_HOST_AND_PORT = 'broker:29092'

client = Client(host=CLICKHOUSE_HOST)

print(client.execute('SHOW DATABASES'))

client.execute(
    'CREATE DATABASE IF NOT EXISTS test_kafka ON CLUSTER company_cluster'
)

client.execute(
    '''CREATE TABLE IF NOT EXISTS default.reviews   
(review_id String, value String
) ENGINE = MergeTree
order by review_id;
'''
)

client.execute(f'''
CREATE TABLE if not exists default.kafka_queue (
    review_id String,
    value String
  ) ENGINE = Kafka SETTINGS
    kafka_broker_list = 'broker:29092',
    kafka_topic_list = 'reviews',
    kafka_group_name = 'clickhouse_views',
    kafka_format = 'JSONEachRow',
    kafka_row_delimiter = '\n';
''')

client.execute('''
CREATE MATERIALIZED VIEW IF NOT EXISTS reviews_consumer TO default.reviews
AS SELECT _key as review_id,
          value
FROM kafka_queue;
''')
