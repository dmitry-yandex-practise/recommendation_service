from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
from uuid import UUID


class Storage(ABC):
    """
    Абстрактный класс, реализующий хранилище данных
    """

    @abstractmethod
    async def get_by_ids(self, index: str, ids: List[UUID]) -> List[Dict]:
        """
        Получить объекты по списку ID
        """
        pass

    @abstractmethod
    async def search(
            self,
            index: str,
            body: Optional[Dict] = None,
            params: Optional[Dict] = None
            ) -> Tuple[int, List[UUID]]:
        """
        Поиск по объектам
        """
        pass

    @abstractmethod
    async def msearch(
            self,
            index: str,
            body: Optional[List[Dict]] = None,
            params: Optional[Dict] = None) -> List[Optional[List[UUID]]]:
        """
        Несколько поисковых запросов в одном
        """
        pass
