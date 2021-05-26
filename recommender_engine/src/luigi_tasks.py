import datetime
import os
from json import dumps
from logging import getLogger
from sys import version as sys_version
from luigi.contrib.postgres import PostgresTarget
from luigi.contrib.redis_store import RedisTarget
import luigi
import json
from notifications.telegram import LuigiTelegramNotification
from luigi import Parameter
from luigi.notifications import TestNotificationsTask
from lightfm import __version__ as lightfm_version
from lightfm.cross_validation import random_train_test_split
from luigi import Task, run, Target, build
from luigi import __version__ as luigi_version
from numpy.random import RandomState
from pandas import DataFrame
from tqdm import tqdm
from luigi.local_target import LocalTarget
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
        logger = getLogger("luigi-interface")
        logger.info("Creating connection object")
        conn = PostgresConnCtxManager(Config.PG_HOST, Config.PG_DATABASE, Config.PG_USER, Config.PG_PASSWORD)
        logger.info("Starting data retrieval")
        movies = retrieve_movies_data(conn_ctx_manager=conn)  # List of RealDict Objects
        users = retrieve_users_data(conn_ctx_manager=conn)  # List of RealDict Objects
        ratings = retrieve_ratings(conn_ctx_manager=conn)  # List of RealDict Objects
        logger.info(f"Collected data of {len(movies)} movies, {len(users)} users, {len(ratings)} ratings")
        f = self.output()
        f.put((movies, users, ratings))

    def output(self):
        return MemoryTarget(self.__class__.__name__)


class PrepareData(Task):

    def requires(self):
        return CollectData()

    def run(self):
        logger = getLogger("luigi-interface")
        input = yield CollectData()
        (movies, users, ratings) = input.get()

        logger.info("Creating dataset")
        dataset = create_dataset(users, movies)

        logger.info("Creating Item features")
        # (item id, [list of feature names])
        item_features = dataset.build_item_features(
            data=[(m["id"], [m["title"], "rating:" + str(m["rating"]), "type:" + str(m["type"]), ]) for m in movies]
        )

        logger.info("Creating interactions dataframe")
        # data: iterable of (user_id, item_id, weight)
        ratings_df = DataFrame(ratings, columns=['user_id', 'film_work_id', 'score'])
        ratings_df.drop_duplicates(subset=['user_id', 'film_work_id'])
        interactions, weights = dataset.build_interactions(data=ratings_df.values)

        logger.info("split into train and test sets")
        train_interactions, test_interactions = random_train_test_split(
            interactions, test_percentage=Config.TEST_PERCENTAGE, random_state=RandomState(Config.SEEDNO))
        self.output().put((dataset, item_features, train_interactions, test_interactions))

    def output(self):
        return MemoryTarget(self.__class__.__name__)


class CreateModel(Task):

    def requires(self):
        return PrepareData()

    def run(self):
        logger = getLogger("luigi-interface")
        input = yield PrepareData()
        (dataset, item_features, train_interactions, test_interactions) = input.get()
        logger.info("Creating model")
        model = create_model()
        logger.info("Training model")
        model.fit(interactions=train_interactions,
                  item_features=item_features,
                  epochs=Config.NO_EPOCHS,
                  num_threads=Config.NO_THREADS,
                  verbose=True)
        logger.info("Running precision@k and AUC metrics")
        metrics = run_metrics(
            model=model,
            train=train_interactions,
            test=test_interactions,
            item_features=item_features,
        )
        logger.info(f"Precision at K={Config.K}: {metrics['precision']}\nAUC: {metrics['auc']}")

        self.output().put((dataset, train_interactions, model))

    def output(self):
        return MemoryTarget(self.__class__.__name__)


class CreateRecommendations(Task):
    date = luigi.DateParameter(default=datetime.date.today())

    def requires(self):
        return CreateModel()

    def run(self):
        logger = getLogger("luigi-interface")
        input = yield CreateModel()
        (dataset, train_interactions, model) = input.get()
        logger.info("Generating recommendations")
        recommendations = recommend_movies(dataset, train_interactions, model)
        logger.info("Backing up recommendations on disk")
        directory = './generated/recommendations/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        with self.output().open('w') as f:
            json.dump(recommendations, f)

    def output(self):
        return LocalTarget(path='./generated/recommendations/{}.json'.format(self.date))


class WriteRecommendations(Task):
    redis_db = luigi.Parameter(
        default="default",
        description="Database name in Redis which data should be written to. Not implemented for now")

    def requires(self):
        return CreateRecommendations()

    def run(self):
        logger = getLogger("luigi-interface")
        with self.input().open('r') as in_file:
            recommendations = json.load(in_file)
        logger.info("Connecting to Recommendations Storage")
        redis_conn = RedisService(host=Config.REDIS_HOST)
        logger.info("Writing new recommendations")
        for user in tqdm(recommendations):
            redis_conn.set(key=user, value=dumps({"must_watch": recommendations[user]}))

    def complete(self):
        try:
            with self.input().open('r') as in_file:
                recommendations = json.load(in_file)
        except IOError:
            return False
        redis_conn = RedisService(host=Config.REDIS_HOST)
        for count, user_id in enumerate(recommendations):
            if count >= 10:
                break
            recommendation = recommendations[user_id]
            redis_rec = json.loads(redis_conn.get(user_id))
            if recommendation != redis_rec:
                return False
        return True


def trigger_luigi_tasks():
    print("System version: {}".format(sys_version))
    print("LightFM version: {}".format(lightfm_version))
    print("Luigi version: {}".format(luigi_version))

    with LuigiTelegramNotification(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT, failed_only=True):
        run(main_task_cls=WriteRecommendations,
            worker_scheduler_factory=None,
            local_scheduler=False,
            detailed_summary=False
            )


# TODO Notify if build fails
# TODO Create Commentaries

if __name__ == '__main__':
    trigger_luigi_tasks()
