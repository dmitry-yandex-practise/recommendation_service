from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

DEFAULT_TTL = 60


class AnalyticStorage(ABC):
    """
    Абстрактный класс, аналитическое хранилище
    """

    @abstractmethod
    async def select_data(self):
        """
        Получить данные из аналитического хранилища
        """
        pass
