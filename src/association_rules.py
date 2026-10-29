from pyspark.sql import DataFrame, functions as F


def product_associations(purchases: DataFrame, min_product_baskets: int = 2) -> DataFrame:
    frequent = purchases.groupBy("stock_code").agg(F.countDistinct("invoice_no").alias("product_baskets")).filter(
        F.col("product_baskets") >= min_product_baskets
    )
    baskets = purchases.select("invoice_no", "stock_code").distinct().join(frequent, "stock_code")
    pairs = (
        baskets.alias("a").join(
            baskets.alias("b"),
            (F.col("a.invoice_no") == F.col("b.invoice_no"))
            & (F.col("a.stock_code") < F.col("b.stock_code")),
        )
        .groupBy(F.col("a.stock_code").alias("product_a"), F.col("b.stock_code").alias("product_b"))
        .agg(F.countDistinct("a.invoice_no").alias("co_purchase_baskets"))
    )
    total = purchases.select("invoice_no").distinct().count()
    counts = frequent.select(F.col("stock_code").alias("product"), "product_baskets")
    return (
        pairs.join(counts.alias("ca"), F.col("product_a") == F.col("ca.product"))
        .join(counts.alias("cb"), F.col("product_b") == F.col("cb.product"))
        .withColumn("support", F.col("co_purchase_baskets") / F.lit(total))
        .withColumn("confidence_a_to_b", F.col("co_purchase_baskets") / F.col("ca.product_baskets"))
        .withColumn("confidence_b_to_a", F.col("co_purchase_baskets") / F.col("cb.product_baskets"))
        .withColumn(
            "lift",
            F.col("support") / (
                (F.col("ca.product_baskets") / F.lit(total))
                * (F.col("cb.product_baskets") / F.lit(total))
            ),
        )
        .select("product_a", "product_b", "co_purchase_baskets", "support",
                "confidence_a_to_b", "confidence_b_to_a", "lift")
    )
