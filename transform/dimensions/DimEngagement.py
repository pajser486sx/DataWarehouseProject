from pyspark.sql.functions import (
    col, trim, initcap, lit, when, row_number, 
    to_date, year, quarter, month, date_format, current_timestamp
)
from pyspark.sql.window import Window
from spark_session import get_spark_session

def transform_engagement_dim(csv_df):
    spark = get_spark_session()

    # --- Korak 1: Izdvajanje unikatnih profila angažmana ---
    distinct_eng_df = (
        csv_df
        .select(
            col("primary_device").alias("device_name"),
            col("ad_interaction"),
            col("most_liked_feature")
        )
        .dropDuplicates()
    )

    # --- Korak 2: Generiranje surogatnog ključa ---
    window = Window.orderBy("device_name", "ad_interaction", "most_liked_feature")

    final_df = (
        distinct_eng_df
        .withColumn("engagement_tk", row_number().over(window).cast("long"))
        .withColumn("version", lit(1).cast("integer"))
        .withColumn("date_from", current_timestamp())
        .withColumn("date_to", lit(None).cast("timestamp"))
        .select("engagement_tk", "device_name", "ad_interaction", "most_liked_feature", "version", "date_from", "date_to")
    )

    return final_df