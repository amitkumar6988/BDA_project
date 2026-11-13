import json
from pathlib import Path
from pyspark.sql import functions as F
from .association_rules import product_associations
from .config import DATASET, ModelConfig, PROCESSED_DIR, RECOMMENDATIONS_DIR, OUTPUT_DIR, ensure_directories
from .data_cleaning import clean_transactions
from .data_loader import load_transactions
from .evaluation import ranking_metrics, temporal_train_test
from .exploratory_analysis import summary
from .feature_engineering import add_stable_ids, build_interactions
from .recommendation_model import popularity, recommendations_for_all, train_als
from .output_writer import write_parquet


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
    train, test = temporal_train_test(interactions)
    train_users = train.select("user").distinct()
    config = ModelConfig()
    try:
        model = train_als(train, config)
        recs = recommendations_for_all(model, train_users, train, config.top_k)
        model_metrics = ranking_metrics(recs, test, config.top_k) if test.take(1) else {}
        model_metrics["algorithm"] = "implicit ALS"
    except ValueError as exc:
        recs = popularity(train, config.top_k).withColumn("user", F.lit(None).cast("int"))
        model_metrics = {"algorithm": "popularity fallback", "reason": str(exc)}
    write_parquet(
        recs.join(interactions.select("item", "stock_code", "description").distinct(), "item", "left"),
        RECOMMENDATIONS_DIR / "all_customers",
    )
    write_parquet(product_associations(purchases), PROCESSED_DIR / "product_associations")
    (OUTPUT_DIR / "evaluation.json").write_text(json.dumps(model_metrics, indent=2), encoding="utf-8")
    return {"quality": quality, "summary": metrics, "evaluation": model_metrics}
