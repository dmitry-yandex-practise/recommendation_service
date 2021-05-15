from kafka import KafkaProducer
from time import sleep
import json

# e6bbeea3-5095-48b7-80cf-e17fcb729d1b | 0b9e2951-1dcc-418e-aaf5-d18dae19935e | 322013c1-a9dc-4b74-83f0-bce25548e3aa |    70 | 2010-02-09

data = {"movie_id": "e6bbeea3-5095-48b7-80cf-e17fcb729d1b",
        "user_id": "0b9e2951-1dcc-418e-aaf5-d18dae19935e",
        "score": "30",
        "review_date": "2010-02-09"}

json_data = json.dumps(data)
print(bytes(json_data, 'utf-8'))

producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

producer.send(
    topic='reviews',
    value=bytes(json_data, 'utf-8'),
    key=b'322013c1-a9dc-4b74-83f0-bce25548e3aa',
)

sleep(1)
