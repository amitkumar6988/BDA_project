from pyspark.sql import DataFrame, functions as F


def summary(purchases: DataFrame) -> dict[str, float | int]:
    row = purchases.agg(
        F.countDistinct("invoice_no").alias("transactions"),
        F.countDistinct("customer_id").alias("customers"),
        F.countDistinct("stock_code").alias("products"),
        F.sum("quantity").alias("quantity"),
        F.sum("amount").alias("revenue"),
        F.avg("amount").alias("average_line_value"),
    ).first()
    return {key: (float(row[key]) if key in {"quantity", "revenue", "average_line_value"} else int(row[key] or 0))
            for key in row.asDict()}
