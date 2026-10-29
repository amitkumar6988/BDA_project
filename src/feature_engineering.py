from pyspark.sql import DataFrame, functions as F, Window


def build_interactions(purchases: DataFrame) -> DataFrame:
    return (
        purchases.groupBy("customer_id", "stock_code")
        .agg(
            F.sum("quantity").alias("total_quantity"),
            F.countDistinct("invoice_no").alias("purchase_frequency"),
            F.max("invoice_date").alias("last_purchase"),
            F.first("description", ignorenulls=True).alias("description"),
        )
        .withColumn("strength", F.log1p("total_quantity"))
    )


def add_stable_ids(interactions: DataFrame) -> DataFrame:
    users = interactions.select("customer_id").distinct().withColumn(
        "user", F.row_number().over(Window.orderBy("customer_id")).cast("int")
    )
    items = interactions.select("stock_code").distinct().withColumn(
        "item", F.row_number().over(Window.orderBy("stock_code")).cast("int")
    )
    return interactions.join(users, "customer_id").join(items, "stock_code")
