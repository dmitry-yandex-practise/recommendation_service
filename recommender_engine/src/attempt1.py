import pandas as pd
from lightfm.data import Dataset


# create dummy dataset
interactions_data = {
    'user': ['u1', 'u1', 'u2', 'u2', 'u3', 'u3', 'u3'],
    'item': ['i1', 'i3', 'i2', 'i3', 'i1', 'i4', 'i2'],
    'r': [1, 2, 1, 3, 4, 5, 2]
}
df = pd.DataFrame(interactions_data, columns=['user', 'item', 'r'])

# dummy user features
user_features_data = {
    'user': ['u1', 'u2', 'u3', 'loc'],
    'f1': [1, 0, 1, 'del'],
    'f2': [1, 1, 1, 'mum'],
    'f3': [0, 0, 1, 'del']
}
features = pd.DataFrame(user_features_data, columns=['user', 'f1', 'f2', 'f3', 'loc'])

# we call fit to supply userid, item id and user/item features
dataset1 = Dataset()
dataset1.fit(
    df['user'].unique(),  # all the users
    df['item'].unique(),  # all the items
    user_features=['f1:1', 'f1:0', 'f2:1', 'f2:0', 'f3:1', 'f3:0', 'loc:mum', 'loc:del'])
dataset1.build_item_features()
dataset1.build_interactions()
