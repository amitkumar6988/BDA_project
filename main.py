from src.config import DATASET
from src.pipeline import run
from src.spark_session import create_spark


if __name__ == "__main__":
    spark = create_spark()
    try:
        result = run(spark, DATASET)
        print("SmartReco completed:")
        print(result)
    finally:
        spark.stop()
