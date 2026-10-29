from pathlib import Path
from datetime import datetime
from openpyxl import load_workbook
from pyspark.sql import DataFrame, SparkSession, types as T

REQUIRED = {"InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID"}


def load_transactions(spark: SparkSession, path: Path) -> DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    if path.suffix.lower() not in {".xlsx", ".xls"}:
        raise ValueError("This loader expects the Online Retail Excel workbook.")
    workbook = load_workbook(path, read_only=True, data_only=True)
    sheet = workbook.active
    rows = sheet.iter_rows(values_only=True)
    headers = [str(value).strip() if value is not None else "" for value in next(rows)]
    missing = REQUIRED - set(headers)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
    schema = T.StructType([
        T.StructField("InvoiceNo", T.StringType(), True),
        T.StructField("StockCode", T.StringType(), True),
        T.StructField("Description", T.StringType(), True),
        T.StructField("Quantity", T.DoubleType(), True),
        T.StructField("InvoiceDate", T.TimestampType(), True),
        T.StructField("UnitPrice", T.DoubleType(), True),
        T.StructField("CustomerID", T.LongType(), True),
        T.StructField("Country", T.StringType(), True),
    ])
    positions = {name: headers.index(name) for name in headers}

    def normalized(row):
        def value(name):
            item = row[positions[name]] if positions[name] < len(row) else None
            if name in {"Quantity", "UnitPrice"} and item is not None:
                return float(item)
            if name == "CustomerID" and item is not None:
                return int(float(item))
            if name == "InvoiceDate" and isinstance(item, datetime):
                return item
            return item
        return tuple(value(field.name) for field in schema.fields)

    data = (normalized(row) for row in rows)
    return spark.createDataFrame(spark.sparkContext.parallelize(list(data), 8), schema=schema)
