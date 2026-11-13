import os
import sys
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from src.evaluation import temporal_train_test
from src.feature_engineering import add_stable_ids, build_interactions
from src.recommendation_model import rerank_unseen


def test_interactions_and_stable_ids():
    spark = SparkSession.builder.master("local[1]").appName("test").getOrCreate()
    try:
        df = spark.createDataFrame([
            ("1", "A", "A product", 2.0),
            ("1", "A", "A product", 3.0),
            ("2", "B", "B product", 1.0),
        ], ["customer_id", "stock_code", "description", "quantity"])
        df = df.withColumn("invoice_no", df.customer_id).withColumn("invoice_date", __import__("pyspark").sql.functions.current_timestamp())
        result = add_stable_ids(build_interactions(df))
        assert result.count() == 2
        assert result.select("user").distinct().count() == 2
        assert result.filter("stock_code = 'A'").first()["strength"] > 0
    finally:
        spark.stop()


def test_temporal_split_holds_out_latest_item_per_eligible_user():
    spark = SparkSession.builder.master("local[1]").appName("test-split").getOrCreate()
    try:
        df = spark.createDataFrame([
            (1, 10, "2024-01-01"),
            (1, 11, "2024-02-01"),
            (2, 20, "2024-03-01"),
        ], ["user", "item", "last_purchase"]).withColumn(
            "last_purchase", __import__("pyspark").sql.functions.to_timestamp("last_purchase")
        )
        train, test = temporal_train_test(df)
        assert {(row["user"], row["item"]) for row in train.collect()} == {(1, 10)}
        assert {(row["user"], row["item"]) for row in test.collect()} == {(1, 11)}
    finally:
        spark.stop()


def test_rerank_unseen_removes_gaps():
    spark = SparkSession.builder.master("local[1]").appName("test-rank").getOrCreate()
    try:
        recommendations = spark.createDataFrame([
            (1, 1, 100, 0.9),
            (1, 2, 101, 0.8),
            (1, 3, 102, 0.7),
        ], ["user", "rank", "item", "score"])
        purchased = spark.createDataFrame([(1, 100)], ["user", "item"])
        result = rerank_unseen(recommendations, purchased).orderBy("rank").collect()
        assert [(row["rank"], row["item"]) for row in result] == [(1, 101), (2, 102)]
    finally:
        spark.stop()
