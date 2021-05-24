from db import clickhouse
from analytic.abstract import AnalyticStorage


POPULAR_NOW_MOVIE_QUERY = 'SELECT film_work_id, view_date FROM ugc_data.movie_view;'
POPULAR_NOW_PERSON_QUERY = 'SELECT person_id, view_date FROM ugc_data.person_view;'

class ClickHouseStorage(AnalyticStorage):

    def __init__(self, clickhouse):
        self.clickhouse = clickhouse

    def select_data(self, query):
        with self.clickhouse.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()


def get_clickhouse_storage() -> ClickHouseStorage:
    return ClickHouseStorage(clickhouse=clickhouse.ch)
