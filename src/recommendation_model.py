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
    item_count = purchased.select("item").distinct().count()
    max_purchased = purchased.groupBy("user").count().agg(F.max("count")).first()[0] or 0
    candidate_k = min(item_count, k + int(max_purchased))
    candidates = model.recommendForAllUsers(candidate_k).select(
        "user", F.posexplode("recommendations").alias("candidate_rank", "rec")
    ).select(
        "user", F.col("candidate_rank"), F.col("rec.item").alias("item"),
        F.col("rec.rating").alias("score")
    )
    rank_window = Window.partitionBy("user").orderBy(
        F.col("score").desc(), F.col("candidate_rank")
    )
    return candidates.join(
        purchased.select("user", "item").distinct(), ["user", "item"], "left_anti"
    ).withColumn("rank", F.row_number().over(rank_window)).filter(
        F.col("rank") <= k
    ).select("user", "rank", "item", "score")


def customer_recommendations(model, user_id: int, users: DataFrame, purchased: DataFrame, k: int = 10) -> DataFrame:
    internal = users.filter(F.col("customer_id") == user_id).select("user")
    return recommendations_for_all(model, internal, purchased, k)
