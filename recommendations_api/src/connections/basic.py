from abc import ABC, abstractmethod
from uuid import UUID
from typing import Dict


class BasicConnection(ABC):
    """
    Базовый класс для работы с рекомендательной системой
    """

    @abstractmethod
    async def get(self, user_id: UUID) -> Dict[str, list]:
        """
        Метод получение рекомендаций пользователя по id
        :param user_id: id пользователя
        :return:
        """
        pass
