from lightfm import LightFM
from lightfm.data import Dataset
from lightfm.evaluation import auc_score, precision_at_k
from numpy import arange, argsort
from numpy.random import RandomState
from tqdm import tqdm

from core.config import Config


def create_movie_features_set(movies):
    s = set()
    for movie in movies:
        s.add(str(movie["title"]))
        s.add("rating:" + str(movie["rating"]))
        s.add("type:" + str(movie["type"]))
    return s


def create_dataset(users, movies):
    dataset = Dataset()

    dataset.fit(
        users=[x["id"] for x in users],
        items=[x["id"] for x in movies],
        item_features=create_movie_features_set(movies),
    )

    return dataset


def create_model():
    model = LightFM(
        no_components=Config.NO_COMPONENTS,
        learning_schedule="adagrad",
        loss="warp",
        max_sampled=50,
        learning_rate=Config.LEARNING_RATE,
        item_alpha=Config.ITEM_ALPHA,
        random_state=RandomState(Config.SEEDNO)
    )
    return model


def run_metrics(model, train, test, item_features):
    precision = precision_at_k(
        model,
        test_interactions=test,

        k=Config.K,
        item_features=item_features,
        num_threads=Config.NO_THREADS,
        check_intersections=False
    ).mean()

    auc = auc_score(
        model,
        test_interactions=test,

        item_features=item_features,
        num_threads=Config.NO_THREADS,
        check_intersections=False
    ).mean()

    return {"precision": precision, "auc": auc}


def recommend_movies(data, train, model):
    user_id_map, user_feature_map, item_id_map, item_feature_map = data.mapping()  # returns a tuple of dicts
    item_id_map_inv = {
        v: k for k, v in item_id_map.items()
    }  # inverting dict so we can turn internal integer ids back to uuids
    n_users, n_items = train.shape
    recommendations = {}
    for user in tqdm(user_id_map, desc='Generating Recommendations', colour='green'):
        scores = model.predict(user_id_map[user], arange(n_items), num_threads=Config.NO_THREADS)

        top_items = {count: item_id_map_inv[value] for count, value in enumerate(argsort(-scores)[0:Config.K])}
        recommendations[user] = {"must_watch": list(top_items.values())}
    return recommendations
