from json import dumps
from sys import version as sys_version

from lightfm import __version__ as lightfm_version
from lightfm.cross_validation import random_train_test_split
from luigi import Task, run, Target
from luigi import __version__ as luigi_version
from numpy.random import RandomState
from pandas import DataFrame
from tqdm import tqdm

from connections.postgres import PostgresConnCtxManager
from core.config import Config
from lightfm_engine import create_dataset, create_model, run_metrics, recommend_movies
from movies_data.pg_movies import retrieve_movies_data
from recommendations.redis_db import RedisService
from ugc.pg_ugc import retrieve_ratings
from user_data.pg_user_data import retrieve_users_data


class MemoryTarget(Target):
    _data = {}

    def __init__(self, path):
        self.path = path

    def exists(self):
        return self.path in self._data

    def put(self, value):
        self._data[self.path] = value

    def get(self):
        return self._data[self.path]


class CollectData(Task):
    def run(self):
        conn = PostgresConnCtxManager(Config.PG_HOST, Config.PG_DATABASE, Config.PG_USER, Config.PG_PASSWORD)
        movies = retrieve_movies_data(conn_ctx_manager=conn)  # List of RealDict Objects
        users = retrieve_users_data(conn_ctx_manager=conn)  # List of RealDict Objects
        ratings = retrieve_ratings(conn_ctx_manager=conn)  # List of RealDict Objects
        f = self.output()
        f.put((movies, users, ratings))

    def output(self):
        return MemoryTarget(self.__class__.__name__)


class PrepareData(Task):
    def requires(self):
        return CollectData()

    def run(self):
        input = yield CollectData()
        (movies, users, ratings) = input.get()

        dataset = create_dataset(users, movies)

        # (item id, [list of feature names])
        item_features = dataset.build_item_features(
            data=[(m["id"], [m["title"], "rating:" + str(m["rating"]), "type:" + str(m["type"]), ]) for m in movies]
        )

        # Creating interactions dataframe
        # data: iterable of (user_id, item_id, weight)
        ratings_df = DataFrame(ratings, columns=['user_id', 'film_work_id', 'score'])
        ratings_df.drop_duplicates(subset=['user_id', 'film_work_id'])
        interactions, weights = dataset.build_interactions(data=ratings_df.values)

        # split into train and test sets
        train_interactions, test_interactions = random_train_test_split(
            interactions, test_percentage=Config.TEST_PERCENTAGE, random_state=RandomState(Config.SEEDNO))
        self.output().put((dataset, item_features, train_interactions, test_interactions))

    def output(self):
        return MemoryTarget(self.__class__.__name__)


class CreateModel(Task):
    def requires(self):
        return PrepareData()

    def run(self):
        input = yield PrepareData()
        (dataset, item_features, train_interactions, test_interactions) = input.get()
        model = create_model()

        model.fit(interactions=train_interactions,
                  item_features=item_features,
                  epochs=Config.NO_EPOCHS,
                  num_threads=Config.NO_THREADS,
                  verbose=True)

        run_metrics(model=model,
                    train=train_interactions,
                    test=test_interactions,
                    item_features=item_features)

        self.output().put((dataset, train_interactions, model))

    def output(self):
        return MemoryTarget(self.__class__.__name__)


class CreateRecommendations(Task):
    def requires(self):
        return CreateModel()

    def run(self):
        input = yield CreateModel()
        (dataset, train_interactions, model) = input.get()
        recommendations = recommend_movies(dataset, train_interactions, model)
        self.output().put(recommendations)

    def output(self):
        return MemoryTarget(self.__class__.__name__)


class WriteRecommendations(Task):
    def requires(self):
        return CreateRecommendations()

    def run(self):
        input = yield CreateRecommendations()
        recommendations = input.get()
        redis_conn = RedisService(host=Config.REDIS_HOST)
        for user in tqdm(recommendations):
            redis_conn.set(key=user, value=dumps(recommendations[user]))


if __name__ == '__main__':
    print("System version: {}".format(sys_version))
    print("LightFM version: {}".format(lightfm_version))
    print("Luigi version: {}".format(luigi_version))
    run(local_scheduler=True, main_task_cls=WriteRecommendations)
