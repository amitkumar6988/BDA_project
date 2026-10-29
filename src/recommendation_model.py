from pyspark.sql import DataFrame, Window, functions as F
from pyspark.ml.recommendation import ALS
from .config import ModelConfig


def popularity(interactions: DataFrame, k: int = 10) -> DataFrame:
    return interactions.groupBy("item").agg(F.sum("strength").alias("score")).withColumn(
        "rank", F.row_number().over(Window.orderBy(F.desc("score"), "item"))
    ).filter(F.col("rank") <= k)


def train_als(train: DataFrame, config: ModelConfig):
    if train.select("user").distinct().limit(2).count() < 2 or train.select("item").distinct().limit(2).count() < 2:
        raise ValueError("Not enough distinct customers/products for ALS; use popularity fallback.")
    return ALS(
        userCol="user", itemCol="item", ratingCol="strength", rank=config.rank,
        maxIter=config.max_iter, regParam=config.reg_param, alpha=config.alpha,
        implicitPrefs=True, coldStartStrategy="drop", seed=config.seed,
    ).fit(train)


def recommendations_for_all(model, users: DataFrame, purchased: DataFrame, k: int = 10) -> DataFrame:
    return model.recommendForAllUsers(k).select("user", F.posexplode("recommendations").alias("rank_zero", "rec")).select(
        "user", (F.col("rank_zero") + 1).alias("rank"), F.col("rec.item").alias("item"),
        F.col("rec.rating").alias("score")
    ).join(purchased.select("user", "item").distinct(), ["user", "item"], "left_anti")


def customer_recommendations(model, user_id: int, users: DataFrame, purchased: DataFrame, k: int = 10) -> DataFrame:
    internal = users.filter(F.col("customer_id") == user_id).select("user")
    return recommendations_for_all(model, internal, purchased, k)
