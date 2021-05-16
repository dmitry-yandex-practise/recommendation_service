from abc import ABC, abstractmethod
from typing import Optional


class EventProducer(ABC):
    """
    Абстрактный класс, реализующий
    """

    @abstractmethod
    async def send(self, topic: str, key: str, value: str) -> Optional[str]:
        """
        Send data to event store
        """
        pass

    @abstractmethod
    async def send_and_wait(self, topic: str, key: bytes, value: bytes) -> Optional[str]:
        """
        Send data to event store and wait for result
        """
        pass
