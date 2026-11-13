import os
import sys
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from src.feature_engineering import add_stable_ids, build_interactions
from src.pipeline import temporal_train_test_split


def test_interactions_and_stable_ids():
    spark = SparkSession.builder.master("local[1]").appName("test").getOrCreate()
    try:
        df = spark.createDataFrame([
            ("1", "A", "A product", 2.0),
            ("1", "A", "A product", 3.0),
            ("2", "B", "B product", 1.0),
        ], ["customer_id", "stock_code", "description", "quantity"])
        df = df.withColumn("invoice_no", df.customer_id).withColumn("invoice_date", F.current_timestamp())
        result = add_stable_ids(build_interactions(df))
        assert result.count() == 2
        assert result.select("user").distinct().count() == 2
        assert result.filter("stock_code = 'A'").first()["strength"] > 0
    finally:
        spark.stop()


def test_temporal_split_holds_out_latest_item_per_repeat_customer():
    spark = SparkSession.builder.master("local[1]").appName("test-split").getOrCreate()
    try:
        df = spark.createDataFrame([
            (1, 10, "2024-01-01 10:00:00"),
            (1, 11, "2024-01-02 10:00:00"),
            (2, 20, "2024-01-01 10:00:00"),
        ], ["user", "item", "last_purchase"]).withColumn(
            "last_purchase", F.to_timestamp("last_purchase")
        )
        train, test = temporal_train_test_split(df)
        assert {(row["user"], row["item"]) for row in test.collect()} == {(1, 11)}
        assert {(row["user"], row["item"]) for row in train.collect()} == {(1, 10), (2, 20)}
    finally:
        spark.stop()
