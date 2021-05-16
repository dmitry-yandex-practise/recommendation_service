import csv
import json
import psycopg2
import sqlite3
import sys
import uuid
from datetime import datetime
from pprint import pprint
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor, execute_batch
from sqlite3 import Row

from parse_score import parse_alphabet, parse_only_score, parse_slash, ALPHABET_SCORES_LETTERS
from util import name_filelds, movie_field_names, review_field_names


class PostgresSaver:

    def __init__(self, pg_conn):
        self.connection = pg_conn
        self.film_work_sql = '''INSERT INTO content.film_work(id, title, description, rating, type, updated_at)
                                       VALUES(%(id)s, %(title)s, %(description)s, %(rating)s, %(type)s, %(updated_at)s);'''

        self.person_sql = '''INSERT INTO content.person(id, full_name, updated_at)
                                       VALUES(%(id)s, %(name)s, %(updated_at)s);'''

        self.genre_sql = '''INSERT INTO content.genre(id, name, updated_at)
                                       VALUES(%(id)s, %(name)s, %(updated_at)s);'''

        self.user_sql = '''INSERT INTO content.users(id, name, updated_at)
                                       VALUES(%(id)s, %(name)s, %(updated_at)s);'''

        self.person_film_work = '''INSERT INTO content.person_film_work(id, film_work_id , person_id, role)
                                       VALUES(%(id)s, %(film_work_id)s, %(person_id)s, %(role)s);'''

        self.genre_film_work = '''INSERT INTO content.genre_film_work(id, film_work_id, genre_id)
                                        VALUES(%(id)s, %(film_work_id)s, %(genre_id)s);'''

        self.review_film_work_sql = '''INSERT INTO content.review_film_work(id, film_work_id, user_id, score, review, review_date)
                                       VALUES(%(id)s, %(film_work_id)s, %(user_id)s, %(score)s, %(review)s, %(review_date)s);'''

    def insert_film_work(self, data):
        with self.connection.cursor() as cursor:
            execute_batch(cursor, self.film_work_sql, data, 1000)

    def insert_person(self, data):
        with self.connection.cursor() as cursor:
            execute_batch(cursor, self.person_sql, data, 1000)

    def insert_genre(self, data):
        with self.connection.cursor() as cursor:
            execute_batch(cursor, self.genre_sql, data, 1000)

    def insert_users(self, data):
        with self.connection.cursor() as cursor:
            execute_batch(cursor, self.user_sql, data, 1000)

    def insert_person_film_work(self, data):
        with self.connection.cursor() as cursor:
            execute_batch(cursor, self.person_film_work, data, 1000)

    def insert_genre_film_work(self, data):
        with self.connection.cursor() as cursor:
            execute_batch(cursor, self.genre_film_work, data, 1000)

    def insert_review_film_work(self, data):
        with self.connection.cursor() as cursor:
            execute_batch(cursor, self.review_film_work_sql, data, 1000)

    def save_all_data(self, data):
        self.insert_film_work(data['data']['film_work'])
        self.insert_person(data['data']['person'])
        self.insert_genre(data['data']['genre'])
        self.insert_person_film_work(data['data']['person_film_work'])
        self.insert_genre_film_work(data['data']['genre_film_work'])
        self.insert_users(data['data']['users'])
        self.insert_review_film_work(data['data']['reviews'])


class CSVLoader:

    def __init__(self, file_path, review_file_path):
        self.review_file_path = review_file_path
        self.file_path = file_path
        self.review_raw = []
        self.review = []
        self.review_film_work = []
        self.film_work_raw = []
        self.film_work = []
        self.genre = []
        self.genre_film_work = []
        self.directors = []
        self.actors = []
        self.authors = []
        self.person = []
        self.person_film_work = []
        self.users = []

    def check_if_exist(self, key: str, value: str, target_rows: list):
        return next((row for row in target_rows if row.get(key) == value), None)

    def enrich_uuid(self, rows: list):
        [row.update({"uuid_id": str(uuid.uuid4())}) for row in rows]

    def add_person_film_work(self, film_work_row: list, film_work_id: uuid.UUID, role_name: str, target_rows: list):
        film_work_uniq = list({person['id']: person for person in film_work_row}.values())
        for role in film_work_uniq:
            person_film_work_id = str(uuid.uuid4())
            person_row = self.check_if_exist(key='id', value=role['id'], target_rows=target_rows)
            self.person_film_work.append({'id': person_film_work_id,
                                          'film_work_id': film_work_id,
                                          'person_id': person_row['uuid_id'] if person_row.get('uuid_id')
                                          else person_row['id'],
                                          'role': role_name})

    def add_genre_film_work(self, genre_ids: list, film_work_id: uuid.UUID):
        for genre in genre_ids:
            genre_film_work_id = str(uuid.uuid4())
            self.genre_film_work.append({"id": genre_film_work_id,
                                         "film_work_id": film_work_id,
                                         "genre_id": genre['id']})

    def add_review_film_work(self, review_ids: list, film_work_id: uuid.UUID, score: int, review_content: str,
                             review_date: str):
        for review in review_ids:
            review_film_work_id = str(uuid.uuid4())
            self.review_film_work.append({"id": review_film_work_id,
                                          "film_work_id": film_work_id,
                                          "user_id": review['id'],
                                          "score": score,
                                          "review": review_content,
                                          "review_date": review_date if review_date else ''})

    def _prepare_movie(self, movie_field: str, film_work_raw_row: dict, target_rows: list):
        movie_field_data = film_work_raw_row[movie_field].replace(', ', ',').split(',')
        ids_data = []
        for data in movie_field_data:
            target_row = self.check_if_exist(key='name', value=data, target_rows=target_rows)

            if target_row:
                ids_data.append({'id': target_row['id']})
            else:
                target_row_id = str(uuid.uuid4())
                target_rows.append({'id': target_row_id, 'name': data, 'updated_at': datetime.now()})
                ids_data.append({'id': target_row_id})

        film_work_raw_row.update({movie_field + '_ids': ids_data})

    def get_movies(self):
        with open(self.file_path, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                self.film_work_raw.append(name_filelds(movie_field_names, row))

    def get_reviews(self):
        with open(self.review_file_path, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                self.review_raw.append(name_filelds(review_field_names, row))

    def load_reviews(self, old_film_id, new_film_id):
        # for idx, review in enumerate(self.review_raw):
        for review in self.review_raw:
            if review['rotten_tomatoes_link'] == old_film_id:
                self._prepare_movie('critic_name', review, self.users)
                # print(review)
                film_reviews = review['critic_name_ids']
                try:
                    if review['review_score'].find('/') != -1:
                        score, like = parse_slash(review['review_score'])

                    elif review['review_score'][0] in ALPHABET_SCORES_LETTERS:
                        score, like = parse_alphabet(review['review_score'])

                    self.add_review_film_work(
                        film_reviews,
                        new_film_id,
                        score,
                        review['review_content'],
                        review['review_date'])
                except Exception:
                    pass

    def load_movies(self):
        self.get_movies()
        self.get_reviews()
        film_work_raw_len = str(len(self.film_work_raw))
        current_film = 0
        for film in self.film_work_raw:
            print(current_film)
            current_film += 1
            film_id = str(uuid.uuid4())
            reviews_data = self.load_reviews(film.get('rotten_tomatoes_link'), film_id)
            # film_id = film.get('rotten_tomatoes_link')
            try:
                rating = float(film['audience_rating'])
            except ValueError:
                rating = 0
            self.film_work.append({'id': str(film_id),
                                   'title': film['movie_title'],
                                   'description': film['movie_info'] if film['movie_info'] != 'N/A' else '',
                                   'rating': rating,
                                   'type': 'film',
                                   'updated_at': datetime.now()})
            self._prepare_movie('directors', film, self.directors)
            self._prepare_movie('actors', film, self.actors)
            self._prepare_movie('authors', film, self.authors)
            self._prepare_movie('genres', film, self.genre)

            film_genres = film['genres_ids']
            self.add_genre_film_work(film_genres, film_id)

            film_directors = film['directors_ids']
            film_actors = film['actors_ids']
            film_authors = film['authors_ids']
            self.add_person_film_work(film_directors, film_id, 'director', self.directors)
            self.add_person_film_work(film_actors, film_id, 'actor', self.actors)
            self.add_person_film_work(film_authors, film_id, 'author', self.authors)

        self.person.extend(self.directors)
        self.person.extend(self.actors)
        self.person.extend(self.authors)
        return {'data': {'person_film_work': self.person_film_work,
                         'person': self.person,
                         'genre': self.genre,
                         'genre_film_work': self.genre_film_work,
                         'film_work': self.film_work,
                         'users': self.users,
                         'reviews': self.review_film_work}}


def load_from_csv(file_path, review_file_path, pg_conn):
    # def load_from_csv(file_path):
    """Основной метод загрузки данных из SQLite в Postgres"""
    postgres_saver = PostgresSaver(pg_conn)
    csv_loader = CSVLoader(file_path, review_file_path)
    data = csv_loader.load_movies()
    postgres_saver.save_all_data(data)
    return data
    # postgres_saver.save_all_data(data)


if __name__ == '__main__':
    import time

    start_time = time.time()
    dsl = {'dbname': 'movies_database', 'user': 'postgres', 'password': 'pass', 'host': 'localhost', 'port': 6432}
    # result = load_from_csv('100_rotten_tomatoes_movies.csv', dsl)
    with psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        result = load_from_csv('rotten_tomatoes_movies.csv', 'clean_critic_review.csv', pg_conn)
    print("--- %s seconds ---" % (time.time() - start_time))
