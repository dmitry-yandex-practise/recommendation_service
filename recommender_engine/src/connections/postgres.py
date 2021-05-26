import psycopg2
from psycopg2.extras import RealDictCursor


class PostgresConnCtxManager:
    """
    Simple Context Manager for PostgreSQL connection. Accepts dsn as separate string keywords, returns cursor object.
    """

    def __init__(self, host: str, database: str, user: str, password: str, cursor_factory=RealDictCursor):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.cursor_factory = cursor_factory

    def __enter__(self):
        self.conn = psycopg2.connect(database = self.database, user = self.user, password = self.password,host= self.host,port=5432)
        self.cur = self.conn.cursor(cursor_factory=self.cursor_factory)
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.conn.close()


def retrieve_movies_data(conn_ctx_manager):
    with conn_ctx_manager as cur:
        query = cur.mogrify("""
            select fw.id, fw.title, fw.type
            --ARRAY_AGG(DISTINCT G.NAME) AS GENRES,
            --ARRAY_AGG(DISTINCT P.FULL_NAME) AS PERSONS
            from content.film_work as fw
            --join content.genre_film_work as gfw on fw.id = gfw.film_work_id
            --join content.genre as g on gfw.genre_id = g.id
            --join content.person_film_work as pfw on fw.id = pfw.film_work_id
            --join content.person as p on pfw.person_id = p.id
            group BY fw.id;
            """)
        cur.execute(query)
        movies = cur.fetchall()
        print(movies[0])
        return movies


def retrieve_users_data(conn_ctx_manager):
    with conn_ctx_manager as cur:
        query = cur.mogrify("""
        select id, name from content.users;
        """)
        cur.execute(query)
        users = cur.fetchall()
        print(users[0])
        return users


def retrieve_ratings(conn_ctx_manager):
    with conn_ctx_manager as cur:
        query = cur.mogrify("""
            select film_work_id, user_id, score from content.review_film_work;
            """)
        cur.execute(query)
        ratings = cur.fetchall()
        print(ratings[0])
        return ratings
