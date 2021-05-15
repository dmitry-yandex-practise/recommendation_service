import json
import os.path
from typing import List, Dict, Optional, Tuple
from uuid import UUID

from services.film import FILMS_INDEX
from services.genre import GENRES_INDEX
from services.person import PERSONS_INDEX
from storage.abstract import Storage

TESTDATA_PATH = os.path.join(os.path.dirname(__file__), '../testdata/storage')


class MockStorage(Storage):

    def __init__(self, films_path, genres_path, persons_path: str):
        self.data = {}
        with open(films_path) as f:
            self.data[FILMS_INDEX] = json.load(f)
        with open(genres_path) as f:
            self.data[GENRES_INDEX] = json.load(f)
        with open(persons_path) as f:
            self.data[PERSONS_INDEX] = json.load(f)

    async def get_by_ids(self, index: str, ids: List[UUID]) -> List[Dict]:
        """
        Получить объекты по списку ID
        """
        result = list(filter(lambda x: UUID(x['id']) in ids, self.data[index]))
        return result

    async def search(
            self,
            index: str,
            body: Optional[Dict] = None,
            params: Optional[Dict] = None) -> Tuple[int, List[UUID]]:
        """
        Поиск по объектам
        """
        result = []
        for o in self.data[index]:
            result.append(UUID(o['id']))
        return (len(result), result)

    async def msearch(
            self,
            index: str,
            body: Optional[List[Dict]] = None,
            params: Optional[Dict] = None) -> List[List[UUID]]:
        """
        Несколько поисковых запросов в одном
        """
        if body is None or not isinstance(body, List):
            return []

        result = []
        results_num = int(len(body) / 2)
        for i in range(results_num):
            result.append([UUID(self.data[index][0]['id'])])
        return result


def get_mock_storage():
    films_path = os.path.join(TESTDATA_PATH, 'films.json')
    genres_path = os.path.join(TESTDATA_PATH, 'genres.json')
    persons_path = os.path.join(TESTDATA_PATH, 'persons.json')

    return MockStorage(films_path, genres_path, persons_path)
