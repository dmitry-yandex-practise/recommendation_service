from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import Row
from postgres import ratings, movies
from pyspark.sql import SparkSession
import pandas as pd
from pyspark.sql.functions import col, explode
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator

spark = SparkSession.builder.appName("Recommendations").getOrCreate()

uuid_int_map = {}


def change_uuid_to_int():
    counter = 1
    for line in ratings:
        if line["user_id"] not in uuid_int_map:
            uuid_int_map[line["user_id"]] = counter
            line["user_id"] = counter
            counter += 1
        if line["user_id"] in uuid_int_map:
            line["user_id"] = uuid_int_map[line["user_id"]]
        if line["film_work_id"] not in uuid_int_map:
            uuid_int_map[line["film_work_id"]] = counter
            line["film_work_id"] = counter
            counter += 1
        if line["film_work_id"] in uuid_int_map:
            line["film_work_id"] = uuid_int_map[line["film_work_id"]]


change_uuid_to_int()
uuid_int_map_inv = {v: k for k, v in uuid_int_map.items()}
z = []
for i, movie in enumerate(movies):
    if movie["id"] in uuid_int_map:
        movie["id"] = uuid_int_map[movie["id"]]
    else:
        z.append(i)

for i in reversed(z):
    movies.pop(i)

ratings = spark.createDataFrame(ratings)
movies = spark.createDataFrame(movies)
(training, test) = ratings.randomSplit([0.8, 0.2])

# Build the recommendation model using ALS on the training data
# Note we set cold start strategy to 'drop' to ensure we don't get NaN evaluation metrics
als = ALS(userCol="user_id", itemCol="film_work_id", ratingCol="score",
          coldStartStrategy="drop", nonnegative=True, implicitPrefs=False)

# Add hyperparameters and their respective values to param_grid
param_grid = ParamGridBuilder() \
    .addGrid(als.rank, [10, 50, 100, 150]) \
    .addGrid(als.regParam, [.01, .05, .1, .15]) \
    .addGrid(als.maxIter, [5, 10]) \
    .build()

# Define evaluator as RMSE and print length of evaluator
evaluator = RegressionEvaluator(
    metricName="rmse",
    labelCol="score",
    predictionCol="prediction")
print("Num models to be tested: ", len(param_grid))
# Build cross validation using CrossValidator
cv = CrossValidator(estimator=als, estimatorParamMaps=param_grid, evaluator=evaluator, numFolds=5)

# Fit cross validator to the 'train' dataset
model = cv.fit(training)

# Extract best model from the cv model above
best_model = model.bestModel
print("**Best Model**")
# Print "Rank"
print("  Rank:", best_model._java_obj.parent().getRank())
# Print "MaxIter"
print("  MaxIter:", best_model._java_obj.parent().getMaxIter())
# Print "RegParam"
print("  RegParam:", best_model._java_obj.parent().getRegParam())

# model = als.fit(training)

# Evaluate the model by computing the RMSE on the test data
predictions = best_model.transform(test)
evaluator = RegressionEvaluator(metricName="rmse", labelCol="score",
                                predictionCol="prediction")
rmse = evaluator.evaluate(predictions)
print("Root-mean-square error = " + str(rmse))

# Generate top 10 movie recommendations for each user
userRecs = best_model.recommendForAllUsers(10)
# Generate top 10 user recommendations for each movie
movieRecs = best_model.recommendForAllItems(10)

# print(userRecs)
recommendations = userRecs \
    .withColumn("rec_exp", explode("recommendations")) \
    .select('user_id', col("rec_exp.film_work_id"), col("rec_exp.rating"))
recommendations.limit(10).show()

recommendations.join(
    movies,
    recommendations.film_work_id == movies.id
).filter('user_id = 31').sort('rating', ascending=False).show(truncate=50)

spark.stop()
