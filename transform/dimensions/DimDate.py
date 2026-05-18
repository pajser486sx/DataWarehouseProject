from pyspark.sql.functions import (
    col, trim, initcap, lit, when, row_number, 
    to_date, year, quarter, month, date_format, current_timestamp
)
from pyspark.sql.window import Window
from spark_session import get_spark_session

def transform_date_dim(csv_df):
    spark = get_spark_session()

    # --- Korak 1: Izdvajanje unikatnih datuma ---
    unique_dates_df = (
        csv_df
        .select(to_date(col("signup_date")).alias("full_date"))
        .filter(col("full_date").isNotNull())
        .distinct()
    )

    # --- Korak 2: Ekstrakcija kalendarskih atributa ---
    processed_df = (
        unique_dates_df
        .withColumn("year", year(col("full_date")).cast("integer"))
        .withColumn("quarter", quarter(col("full_date")).cast("integer"))
        .withColumn("month", month(col("full_date")).cast("integer"))
        .withColumn("month_name", date_format(col("full_date"), "MMMM"))
        .withColumn("day_name", date_format(col("full_date"), "EEEE"))
    )

    # --- Korak 3: Dodavanje Surogatnog ključa ---
    window = Window.orderBy("full_date")

    final_df = (
        processed_df
        .withColumn("date_tk", row_number().over(window).cast("integer"))
        .select("date_tk", "full_date", "year", "quarter", "month", "month_name", "day_name")
    )

    return final_df