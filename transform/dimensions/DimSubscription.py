from pyspark.sql.functions import (
    col, trim, initcap, lit, when, row_number, 
    to_date, year, quarter, month, date_format, current_timestamp
)
from pyspark.sql.window import Window
from spark_session import get_spark_session

def transform_subscription_dim(csv_df):
    spark = get_spark_session()

    # --- Korak 1: Izdvajanje unikatnih kombinacija pretplata ---
    distinct_sub_df = (
        csv_df
        .select(
            col("subscription_type").alias("type_name"),
            col("subscription_status").alias("status")
        )
        .dropDuplicates()
    )

    # --- Korak 2: Dodavanje ID-eva i SCD2 stupaca ---
    window = Window.orderBy("type_name", "status")

    final_df = (
        distinct_sub_df
        .withColumn("subscription_id", row_number().over(window).cast("integer"))
        .withColumn("subscription_tk", row_number().over(window).cast("long"))
        .withColumn("version", lit(1).cast("integer"))
        .withColumn("date_from", current_timestamp())
        .withColumn("date_to", lit(None).cast("timestamp"))
        .select("subscription_tk", "subscription_id", "type_name", "status", "version", "date_from", "date_to")
    )

    return final_df