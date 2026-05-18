from pyspark.sql.functions import (
    col, trim, initcap, lit, when, row_number, 
    to_date, year, quarter, month, date_format, current_timestamp
)
from pyspark.sql.window import Window
from spark_session import get_spark_session

def transform_country_dim(mysql_country_df):
    spark = get_spark_session()

    continent_map = {
        'Germany': 'Europe', 'UK': 'Europe', 'France': 'Europe', 'Spain': 'Europe', 
        'Netherlands': 'Europe', 'Sweden': 'Europe', 'Italy': 'Europe', 'Belgium': 'Europe',
        'Norway': 'Europe', 'Finland': 'Europe', 'Denmark': 'Europe', 'Russia': 'Europe',
        'USA': 'North America', 'Canada': 'North America', 'Mexico': 'North America',
        'Brazil': 'South America', 'Argentina': 'South America', 'Colombia': 'South America',
        'India': 'Asia', 'Thailand': 'Asia', 'Vietnam': 'Asia', 'Indonesia': 'Asia', 'China': 'Asia',
        'Philippines': 'Asia', 'Japan': 'Asia', 'South Korea': 'Asia', 'Turkey': 'Asia', 'Saudi Arabia': 'Asia',
        'Nigeria': 'Africa', 'South Africa': 'Africa', 'Egypt': 'Africa', 'Kenya': 'Africa',
        'Australia': 'Oceania', 'New Zealand': 'Oceania'
    }

    # --- Korak 1: Normalizacija i čišćenje naziva ---
    base_df = (
        mysql_country_df
        .select(
            col("id").cast("long").alias("country_id"),
            initcap(trim(col("name"))).alias("name")
        )
        .dropDuplicates(["name"])
    )

    # --- Korak 2: Mapiranje kontinenata u Sparku (umjesto spore .map() metode) ---
    mapping_expr = when(lit(False), None)  # Bazni uvjet
    for country, continent in continent_map.items():
        mapping_expr = mapping_expr.when(col("name") == country, lit(continent))
    mapping_expr = mapping_expr.otherwise(lit("Unknown"))

    combined_df = base_df.withColumn("continent", mapping_expr)

    # --- Korak 3: Dodavanje Surogatnog ključa (SCD Type 2) ---
    window = Window.orderBy("name")

    final_df = (
        combined_df
        .withColumn("country_tk", row_number().over(window).cast("long"))
        .withColumn("version", lit(1).cast("integer"))
        .withColumn("date_from", current_timestamp())
        .withColumn("date_to", lit(None).cast("timestamp"))
        .select("country_tk", "version", "date_from", "date_to", "country_id", "name", "continent")
    )

    return final_df