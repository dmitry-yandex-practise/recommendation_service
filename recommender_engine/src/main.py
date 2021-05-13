import numpy as np
from lightfm import LightFM
from lightfm.cross_validation import random_train_test_split
from lightfm.data import Dataset
from lightfm.evaluation import auc_score, precision_at_k

from core.config import Config
from postgres import ratings, movies, users


# Ratings :

# r = [(x["film_work_id"], x["user_id"], x["score"]) for x in ratings]
# m = [(x["id"], x["title"], x["rating"], x["type"],) for x in movies]
# u = [(x["id"], x["name"],) for x in users]


def create_movie_features_set(movies):
    s = set()
    for movie in movies:
        s.add(str(movie["title"]))
        s.add("rating:" + str(movie["rating"]))
        s.add("type:" + str(movie["type"]))
    return s


data = Dataset()

data.fit(
    users=[x["id"] for x in users],
    items=[x["id"] for x in movies],
    item_features=create_movie_features_set(movies),
)
# (item id, [list of feature names])
item_features = data.build_item_features(
    data=[(m["id"], [m["title"], "rating:" + str(m["rating"]), "type:" + str(m["type"]), ]) for m in movies]
)

# data: iterable of (user_id, item_id, weight)
interactions, weights = data.build_interactions(
    data=[(x["user_id"], x["film_work_id"], x["score"]) for x in ratings]
)

interactions = weights

model = LightFM(
    no_components=100,
    k=5,
    n=10,
    learning_schedule="adagrad",
    loss="warp",
    learning_rate=0.05,
    item_alpha=0.0,
    user_alpha=0.0,
    max_sampled=50,
    random_state=None,
)

# split into train and test sets
train, test = random_train_test_split(interactions)

model.fit(
    interactions=train,
    item_features=item_features,
    sample_weight=None,
    epochs=50,
    num_threads=Config.num_threads,
    verbose=True
)


def run_metrics():
    train_precision = precision_at_k(
        model,
        train,
        k=10,
        item_features=item_features,
        num_threads=Config.num_threads,
    ).mean()

    test_precision = precision_at_k(
        model,
        test,
        k=10,
        item_features=item_features,
        num_threads=Config.num_threads,
    ).mean()

    print("Precision")
    print(train_precision)
    print(test_precision)

    train_auc = auc_score(
        model, train, item_features=item_features, num_threads=Config.num_threads
    ).mean()
    test_auc = auc_score(
        model, test, item_features=item_features, num_threads=Config.num_threads
    ).mean()

    print("Auc")
    print(train_auc)
    print(test_auc)


# Example from LightFM docs
def sample_recommendation(model, data, user_ids):
    n_users, n_items = data['train'].shape

    for user_id in user_ids:
        known_positives = data['item_labels'][data['train'].tocsr()[user_id].indices]

        scores = model.predict(user_id, np.arange(n_items))
        top_items = data['item_labels'][np.argsort(-scores)]

        print("User %s" % user_id)
        print("     Known positives:")

        for x in known_positives[:3]:
            print("        %s" % x)

        print("     Recommended:")

        for x in top_items[:3]:
            print("        %s" % x)


# sample_recommendation(model, {"train": train}, ['00043238-3a89-4c64-ab29-313f298ba18b', ])


def find_movie(id, movies_list):
    for movie in movies_list:
        if movie["id"] == id:
            return movie


user_id_map, user_feature_map, item_id_map, item_feature_map = data.mapping()  # returns a tuple of dicts
item_id_map_inv = {v: k for k, v in item_id_map.items()}  # inverting dict
n_users, n_items = train.shape
scores = model.predict(user_id_map['00043238-3a89-4c64-ab29-313f298ba18b'], np.arange(n_items))
top_items = np.argsort(-scores)
for x in top_items[:3]:
    m = find_movie(id=item_id_map_inv[x], movies_list=movies)
    print(m["id"], m["title"])

run_metrics()
