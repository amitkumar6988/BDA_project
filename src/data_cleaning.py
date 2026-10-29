from pyspark.sql import DataFrame, functions as F, types as T


def validate_columns(df: DataFrame) -> None:
    required = {"InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")


def clean_transactions(df: DataFrame) -> tuple[DataFrame, dict[str, int]]:
    validate_columns(df)
    typed = (
        df.withColumn("invoice_no", F.trim(F.col("InvoiceNo").cast("string")))
        .withColumn("stock_code", F.trim(F.col("StockCode").cast("string")))
        .withColumn("description", F.trim(F.col("Description").cast("string")))
        .withColumn("quantity", F.col("Quantity").cast("double"))
        .withColumn("unit_price", F.col("UnitPrice").cast("double"))
        .withColumn("customer_id", F.col("CustomerID").cast("long"))
        .withColumn("invoice_date", F.to_timestamp("InvoiceDate"))
        .withColumn("is_cancellation", F.upper(F.col("InvoiceNo").cast("string")).startswith("C"))
        .withColumn("amount", F.col("quantity") * F.col("unit_price"))
    )
    initial = typed.count()
    duplicates = typed.count() - typed.dropDuplicates().count()
    valid = typed.filter(
        F.col("invoice_no").isNotNull()
        & F.col("stock_code").isNotNull()
        & (F.length("stock_code") > 0)
        & F.col("customer_id").isNotNull()
        & F.col("quantity").isNotNull()
        & F.col("unit_price").isNotNull()
        & F.col("invoice_date").isNotNull()
    )
    cancellations = valid.filter(F.col("is_cancellation") | (F.col("quantity") < 0)).count()
    purchases = valid.filter((F.col("quantity") > 0) & (F.col("unit_price") > 0)).dropDuplicates()
    retained = purchases.count()
    report = {
        "input_rows": initial,
        "duplicate_rows": duplicates,
        "cancellations_or_returns": cancellations,
        "retained_positive_purchases": retained,
        "dropped_rows": initial - retained,
    }
    return purchases.select(
        "invoice_no", "stock_code", "description", "quantity", "unit_price",
        "customer_id", "invoice_date", "amount", "is_cancellation"
    ), report
