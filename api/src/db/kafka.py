from kafka import KafkaProducer

kafka_producer: KafkaProducer = None

# Функция понадобится при внедрении зависимостей


async def get_kafka_producer() -> KafkaProducer:
    return kafka_producer
