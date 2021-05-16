from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'reviews',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    group_id='echo-messages-to-stdout',
)

for message in consumer:
    print(message.value)
