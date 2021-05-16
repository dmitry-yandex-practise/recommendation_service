from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

DEFAULT_TTL = 60


class Cache(ABC):
    """
    Абстрактный класс, реализующий кеш
    """

    @abstractmethod
    async def get(self, obj_id: UUID) -> Optional[str]:
        """
        Получить данные из кеша
        """
        pass

    async def put(self, obj_id: UUID, data: str):
        """
        Записать данные объекта с ID obj_id в кеш
        """
        pass
