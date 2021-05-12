from lightfm import LightFM
from lightfm.data import Dataset
from core.config import Config
from sklearn.model_selection import train_test_split
from postgres import ratings, movies

r = [(x["film_work_id"], x["user_id"], x["score"]) for x in ratings]
m = [(x["id"], x["title"], x["rating"], x["type"],) for x in movies]

# split into train and test sets
train, test = train_test_split(ratings, test_size=0.2)

data = Dataset(user_identity_features=False)

data.fit(
    users="",
    items="",
    item_features="",
)

item_features = data.build_item_features()

interactions = data.build_interactions()

model = LightFM(
    no_components=10,
    loss="warp",
)

model.fit(
    interactions=interactions,
    item_features=item_features,
    epochs=30,
    num_threads=2,
)

recommendations = model.predict()
