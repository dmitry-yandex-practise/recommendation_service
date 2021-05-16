import datetime

from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode

from connections.postgres import PostgresConnCtxManager
from core.config import Config
from movies_data.pg_movies import retrieve_movies_data
from ugc.pg_ugc import retrieve_ratings
from user_data.pg_user_data import retrieve_users_data


def change_uuid_to_int(ratings, movies):
    uuid_int_map = {}
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

    z = []
    for i, movie in enumerate(movies):
        if movie["id"] in uuid_int_map:
            movie["id"] = uuid_int_map[movie["id"]]
        else:
            z.append(i)

    for i in reversed(z):
        movies.pop(i)

    uuid_int_map_inv = {v: k for k, v in uuid_int_map.items()}

    return ratings, movies, uuid_int_map, uuid_int_map_inv


def hyperparameters_tuning(training, rank_grid, reg_param_grid, max_iter_grid):
    # Build the recommendation model using ALS on the training data
    # Note we set cold start strategy to 'drop' to ensure we don't get NaN evaluation metrics
    als = ALS(userCol="user_id", itemCol="film_work_id", ratingCol="score",
              coldStartStrategy="drop", nonnegative=True, implicitPrefs=False, checkpointInterval=2)

    # Add hyperparameters and their respective values to param_grid
    param_grid = ParamGridBuilder() \
        .addGrid(als.rank, rank_grid) \
        .addGrid(als.regParam, reg_param_grid) \
        .addGrid(als.maxIter, max_iter_grid) \
        .build()

    # Define evaluator as RMSE and print length of evaluator
    evaluator = RegressionEvaluator(
        metricName="rmse",
        labelCol="score",
        predictionCol="prediction")
    print("Num models to be tested: ", len(param_grid))
    # Build cross validation using CrossValidator
    cv = CrossValidator(estimator=als, estimatorParamMaps=param_grid, evaluator=evaluator, numFolds=10, parallelism=4, )

    start = datetime.datetime.now()
    print("Starting time: ", start)

    # Fit cross validator to the 'train' dataset
    model = cv.fit(training)

    # Extract best model from the cv model above
    best_model = model.bestModel
    rank = best_model._java_obj.parent().getRank()
    max_iter = best_model._java_obj.parent().getMaxIter()
    reg_param = best_model._java_obj.parent().getRegParam()

    print("**Best Model**")
    # Print "Rank"
    print("  Rank:", rank)
    # Print "MaxIter"
    print("  MaxIter:", max_iter)
    # Print "RegParam"
    print("  RegParam:", reg_param)

    finish = datetime.datetime.now()
    print("Calculation time: ", finish - start)

    return rank, max_iter, reg_param


def generate_recommendations(training, test, rank, max_iter, reg_param):
    als = ALS(
        userCol="user_id",
        itemCol="film_work_id",
        ratingCol="score",
        coldStartStrategy="drop",
        nonnegative=True,
        implicitPrefs=False,
        checkpointInterval=2,
        rank=rank,
        maxIter=max_iter,
        regParam=reg_param, )
    model = als.fit(training)
    # Evaluate the model by computing the RMSE on the test data
    predictions = model.transform(test)
    evaluator = RegressionEvaluator(metricName="rmse", labelCol="score",
                                    predictionCol="prediction")
    rmse = evaluator.evaluate(predictions)
    print("Root-mean-square error = " + str(rmse))

    # Generate top 10 movie recommendations for each user
    userRecs = model.recommendForAllUsers(10)
    # Generate top 10 user recommendations for each movie
    movieRecs = model.recommendForAllItems(10)

    recommendations = userRecs \
        .withColumn("rec_exp", explode("recommendations")) \
        .select('user_id', col("rec_exp.film_work_id"), col("rec_exp.rating"))
    recommendations.limit(10).show()

    recommendations.join(
        movies,
        recommendations.film_work_id == movies.id
    ).filter('user_id = 31').sort('rating', ascending=False).show(truncate=50)


if __name__ == '__main__':
    spark = SparkSession.builder.appName("Recommendations").config('spark.ui.showConsoleProgress', 'true').getOrCreate()
    sparkContext = spark.sparkContext

    conn = PostgresConnCtxManager(Config.pg_host, Config.pg_database, Config.pg_user, Config.pg_password)
    movies = retrieve_movies_data(conn_ctx_manager=conn)  # List of RealDict Objects
    users = retrieve_users_data(conn_ctx_manager=conn)  # List of RealDict Objects
    ratings = retrieve_ratings(conn_ctx_manager=conn)  # List of RealDict Objects

    sparkContext.setCheckpointDir('checkpoint/')
    # sparkContext.setLogLevel('DEBUG')
    change_uuid_to_int(ratings, movies)
    ratings_rdd = spark.createDataFrame(ratings)
    movies = spark.createDataFrame(movies)
    (training, test) = ratings_rdd.randomSplit([0.8, 0.2])

    rank, max_iter, reg_param = hyperparameters_tuning(training, rank_grid=[100, 150], max_iter_grid=[100, 150, 200],
                                                       reg_param_grid=[.01, .05, .1, .15])
    #rank, max_iter, reg_param = 150, 10, 0.1
    generate_recommendations(training, test, rank, max_iter, reg_param)

    spark.stop()
