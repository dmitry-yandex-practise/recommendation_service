import sklearn_recommender as skr

tf = skr.transformer.UserItemTransformer(user_col='user_id', item_col='item_id', value_col='ranking', agg_fct='mean')
user_item = tf.transform(df_reviews)