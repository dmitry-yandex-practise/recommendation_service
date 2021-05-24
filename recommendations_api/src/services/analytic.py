from analytic.abstract import AnalyticStorage
from analytic.clickhouse import get_clickhouse_storage
from functools import lru_cache

from fastapi import Depends

POPULAR_NOW_PERSON_QUERY = """
SELECT person_id,
       visits
  FROM 
    (
        SELECT person_id,
               count(*) AS visits
          FROM ugc_data.person_view
          GROUP BY person_id
    )
ORDER BY visits DESC
LIMIT 10;"""

POPULAR_NOW_MOVIE_QUERY = """
SELECT film_work_id,
       visits
  FROM 
    (
        SELECT film_work_id,
               count(*) AS visits
          FROM ugc_data.movie_view
          GROUP BY film_work_id
    )
ORDER BY visits DESC
LIMIT 10;"""




def name_filelds(keys, values):
    result = dict([(key, value,) for key, value in zip(keys, values)])
    return result


class AnalyticService:

    def __init__(self, analytic_storage: AnalyticStorage):
        self.analytic_storage = analytic_storage

    def get_popular_movies(self):
        raw_result = self.analytic_storage.select_data(POPULAR_NOW_MOVIE_QUERY)
        result = [str(row[0]) for row in raw_result]
        return result

    def get_popular_persons(self):
        raw_result = self.analytic_storage.select_data(POPULAR_NOW_PERSON_QUERY)
        result = [str(row[0]) for row in raw_result]
        return result


@lru_cache()
def get_analytic_service(
        analytic_storage: AnalyticStorage = Depends(get_clickhouse_storage)
) -> AnalyticService:
    return AnalyticService(analytic_storage)
