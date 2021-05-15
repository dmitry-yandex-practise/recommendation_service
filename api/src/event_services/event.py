from event_producer.kafka import get_kafka_event_producer
from event_producer.abstract import EventProducer
from functools import lru_cache

from fastapi import Depends


class EventService:
    def __init__(self, producer: EventProducer):
        self.producer = producer

    async def send_event(self, topic: str, key: str, value: str):
        result = await self.producer.send_and_wait(topic=topic, key=key, value=value)

        if not result:
            return False

        return True


@lru_cache()
def get_event_service(
        producer: EventProducer = Depends(get_kafka_event_producer)
) -> EventService:
    return EventService(producer)
