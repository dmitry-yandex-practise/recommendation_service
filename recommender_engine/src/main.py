from lightfm import LightFM
from lightfm.data import Dataset
from core.config import Config
from lightfm.cross_validation import random_train_test_split
from postgres import ratings, movies, users
from lightfm.evaluation import precision_at_k
from lightfm.evaluation import auc_score


# r = [(x["film_work_id"], x["user_id"], x["score"]) for x in ratings]
# m = [(x["id"], x["title"], x["rating"], x["type"],) for x in movies]
# u = [(x["id"], x["name"],) for x in users]


def movie_features_set(movies):
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
    item_features=movie_features_set(movies),
)
# (item id, [list of feature names])
item_features = data.build_item_features(
    data=[(x["id"], [x["title"], "rating:" + str(x["rating"]), "type:" + str(x["type"]), ]) for x in movies]
)

# data: iterable of (user_id, item_id, weight)
interactions, weights = data.build_interactions(
    data=[(x["user_id"], x["film_work_id"], x["score"]) for x in ratings]
)

model = LightFM(
    learning_rate=0.05,
    no_components=10,
    loss="warp",
)

# split into train and test sets
train, test = random_train_test_split(interactions)

model.fit(
    interactions=train,
    item_features=item_features,
    sample_weight=None,
    epochs=80,
    num_threads=3,
)

train_precision = precision_at_k(
    model,
    train,
    k=100,
    item_features=item_features,
    num_threads=3,
).mean()

test_precision = precision_at_k(
    model,
    test,
    k=100,
    item_features=item_features,
    num_threads=3,
).mean()

print("Precision")
print(train_precision)
print(test_precision)

train_auc = auc_score(
    model, train, item_features=item_features, num_threads=3
).mean()
test_auc = auc_score(
    model, test, item_features=item_features, num_threads=3
).mean()

print("Auc")
print(train_auc)
print(test_auc)

# recommendations = model.predict()
