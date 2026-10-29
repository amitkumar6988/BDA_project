from pyspark.sql import DataFrame, functions as F


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
