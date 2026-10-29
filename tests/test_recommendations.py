import os
import sys
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from src.feature_engineering import add_stable_ids, build_interactions


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
