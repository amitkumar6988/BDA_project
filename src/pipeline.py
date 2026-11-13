import json
from pathlib import Path
from pyspark.sql import Window, functions as F
from .association_rules import product_associations
from .config import DATASET, ModelConfig, PROCESSED_DIR, RECOMMENDATIONS_DIR, OUTPUT_DIR, ensure_directories
from .data_cleaning import clean_transactions
from .data_loader import load_transactions
from .evaluation import ranking_metrics
from .exploratory_analysis import summary
from .feature_engineering import add_stable_ids, build_interactions
from .recommendation_model import popularity, recommendations_for_all, train_als
from .output_writer import write_parquet


def temporal_train_test_split(interactions):
    user_window = Window.partitionBy("user").orderBy(
        F.col("last_purchase").desc(), F.col("item").desc()
    )
    ranked = interactions.withColumn("_user_interactions", F.count("*").over(Window.partitionBy("user"))).withColumn(
        "_latest_rank", F.row_number().over(user_window)
    )
    test = ranked.filter(
        (F.col("_user_interactions") > 1) & (F.col("_latest_rank") == 1)
    ).select("user", "item")
    train = interactions.join(test, ["user", "item"], "left_anti")
    return train, interactions.join(test, ["user", "item"], "left_semi")


def run(spark, dataset: Path = DATASET) -> dict:
    ensure_directories()
    raw = load_transactions(spark, dataset)
    purchases, quality = clean_transactions(raw)
    interactions = add_stable_ids(build_interactions(purchases)).cache()
    metrics = summary(purchases)
    (OUTPUT_DIR / "data_quality.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    write_parquet(purchases, PROCESSED_DIR / "cleaned_purchases")
    write_parquet(interactions, PROCESSED_DIR / "interactions")
    train_users = interactions.select("user").distinct()
    train, test = temporal_train_test_split(interactions)
    config = ModelConfig()
    try:
        model = train_als(train, config)
        recs = recommendations_for_all(model, train_users, train, config.top_k)
        model_metrics = ranking_metrics(recs, test, config.top_k) if test.take(1) else {}
        model_metrics["algorithm"] = "implicit ALS"
    except ValueError as exc:
        recs = popularity(train, config.top_k).withColumn("user", F.lit(None).cast("int"))
        model_metrics = {"algorithm": "popularity fallback", "reason": str(exc)}
    item_metadata = interactions.groupBy("item").agg(
        F.first("stock_code").alias("stock_code"),
        F.first("description", ignorenulls=True).alias("description"),
    )
    write_parquet(
        recs.join(item_metadata, "item", "left"),
        RECOMMENDATIONS_DIR / "all_customers",
    )
    write_parquet(product_associations(purchases), PROCESSED_DIR / "product_associations")
    (OUTPUT_DIR / "evaluation.json").write_text(json.dumps(model_metrics, indent=2), encoding="utf-8")
    return {"quality": quality, "summary": metrics, "evaluation": model_metrics}
