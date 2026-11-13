from pyspark.sql import DataFrame, Window, functions as F


def temporal_train_test(interactions: DataFrame) -> tuple[DataFrame, DataFrame]:
    ranked = interactions.withColumn(
        "_holdout_rank",
        F.row_number().over(
            Window.partitionBy("user").orderBy(
                F.col("last_purchase").desc(), F.col("item").desc()
            )
        ),
    )
    train = ranked.filter(F.col("_holdout_rank") > 1).drop("_holdout_rank")
    eligible_users = train.select("user").distinct()
    test = (
        ranked.filter(F.col("_holdout_rank") == 1)
        .join(eligible_users, "user", "left_semi")
        .drop("_holdout_rank")
    )
    return train, test


def ranking_metrics(recommendations: DataFrame, test: DataFrame, k: int = 10) -> dict[str, float]:
    rec = recommendations.filter(F.col("rank") <= k).select("user", "item").distinct()
    truth = test.select("user", "item").distinct()
    per_user = rec.groupBy("user").agg(F.count("*").alias("recommended")).join(
        truth.groupBy("user").agg(F.count("*").alias("actual")), "user", "left"
    )
    hits = rec.join(truth, ["user", "item"]).groupBy("user").agg(F.count("*").alias("hits"))
    values = per_user.join(hits, "user", "left").fillna(0, ["hits"])
    row = values.select(
        F.avg(F.col("hits") / F.lit(k)).alias("precision"),
        F.avg(F.col("hits") / F.col("actual")).alias("recall"),
    ).first()
    evaluated = values.count()
    return {
        "precision_at_k": float(row["precision"] or 0.0),
        "recall_at_k": float(row["recall"] or 0.0),
        "evaluated_users": int(evaluated),
    }
