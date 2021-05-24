import logging

from typing import List, Dict

import backoff
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError, ConnectionTimeout

from db import elastic

exceptions_list = (ConnectionError, ConnectionTimeout,)

logger = logging.getLogger(__name__)


class ElasticStorage:

    def __init__(self, es: AsyncElasticsearch):
        self.elastic = es

    @backoff.on_exception(backoff.expo, exceptions_list, logger=logger)
    async def get_ordered_list(self, index_, size=10, field='imdb_rating', order='desc') -> List[Dict]:
        """
        Получить список, упорядоченный по полю field
        """
        resp = await self.elastic.search(index=index_, body={'sort': {field: {'order': order}}})
        docs = [doc['_source']['id'] for doc in resp['hits']['hits']][:size]
        logger.info(f'RECEIVED DATA FROM ELASTICSEARCH: {docs}')
        return docs


def get_elastic_storage() -> ElasticStorage:
    return ElasticStorage(es=elastic.es)
