from typing import List, Dict, Tuple, Optional
from uuid import UUID

import backoff
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError, ConnectionTimeout

from db import elastic
from storage.abstract import Storage

exceptions_list = (ConnectionError, ConnectionTimeout,)


class ElasticStorage(Storage):

    def __init__(self, es: AsyncElasticsearch):
        self.elastic = es

    @backoff.on_exception(backoff.expo, exceptions_list, max_tries=10)
    async def get_by_ids(self, index: str, ids: List[UUID]) -> List[Dict]:
        """
        Получить объекты по списку ID
        """
        doc_ids = [{'_id': _id} for _id in ids]
        resp = await self.elastic.mget(index=index, body={'docs': doc_ids})
        docs = [doc['_source'] for doc in resp['docs'] if doc['found']]
        return docs

    @backoff.on_exception(backoff.expo, exceptions_list, max_tries=10)
    async def search(
            self,
            index: str,
            body: Optional[Dict] = None,
            params: Optional[Dict] = None,
    ) -> Tuple[int, List[UUID]]:
        """
        Поиск по объектам
        """
        if params is None:
            params = {}
        params.update({"_source": False, })
        docs = await self.elastic.search(index=index, body=body, params=params)
        ids = [UUID(doc['_id']) for doc in docs['hits']['hits']]
        total = docs['hits']['total']['value']
        return (total, ids)

    @backoff.on_exception(backoff.expo, exceptions_list, max_tries=10)
    async def msearch(
            self,
            index: str,
            body: Optional[List[Dict]] = None,
            params: Optional[Dict] = None,
    ) -> List[Optional[List[UUID]]]:
        """
        Несколько поисковых запросов в одном
        """
        response = await self.elastic.msearch(index=index, body=body, params=params)
        result = []
        for docs in response['responses']:
            result.append([UUID(doc['_id']) for doc in docs['hits']['hits']])
        return result


def get_elastic_storage() -> ElasticStorage:
    return ElasticStorage(es=elastic.es)
