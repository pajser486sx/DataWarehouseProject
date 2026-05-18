from pyspark.sql.functions import col, when, to_date, row_number, initcap, trim
from pyspark.sql.window import Window

def transform_user_activity_fact( # provjeriti dal su imena točna
    raw_data,
    dim_country_df,
    dim_date_df,
    dim_subscription_df,
    dim_engagement_df
):
    """
    Transformira sirove podatke i povezuje ih s dimenzijama kako bi se stvorila tablica činjenica.
    
    raw_data: rječnik koji sadrži Spark DataFrame učitan iz procesiranog CSV-a (npr. raw_data["csv_user_behaviour"])
    """
    # 1. Dohvaćanje sirovog DataFrame-a iz rječnika podataka
    csv_df = raw_data["csv_user_behaviour"]

    # 2. Priprema i čišćenje sirovih stupaca (uključujući konverziju ad_conversion u 1/0)
    cleaned_df = (
        csv_df
        .withColumn("signup_date_clean", to_date(col("signup_date")))
        .withColumn("ad_conversion_numeric", 
                    when(col("ad_conversion_to_subscription") == "Yes", 1).otherwise(0).cast("integer"))
        .withColumn("age", col("age").cast("integer"))
        .withColumn("avg_listening_hours_per_week", col("avg_listening_hours_per_week").cast("float"))
        .withColumn("playlists_created", col("playlists_created").cast("integer"))
        .withColumn("avg_skips_per_day", col("avg_skips_per_day").cast("integer"))
        .withColumn("music_suggestion_rating_1_to_5", col("music_suggestion_rating_1_to_5").cast("integer"))
        .withColumn("months_inactive", col("months_inactive").cast("integer"))
    )

    # 3. Spajanje (JOIN) sa svim dimenzijama preko tekstualnih/prirodnih ključeva
    # Koristi se "left" join kako ne bismo izgubili podatke ako neka dimenzija nema mapiranje
    fact_joined = (
        cleaned_df.alias("src")
        # Spajanje s DimCountry preko naziva države
        .join(dim_country_df.alias("c"), initcap(trim(col("src.country"))) == initcap(trim(col("c.name"))), "left")
        
        # Spajanje s DimDate preko čistog datuma registracije
        .join(dim_date_df.alias("d"), col("src.signup_date_clean") == col("d.full_date"), "left")
        
        # Spajanje s DimSubscription preko tipa i statusa
        .join(dim_subscription_df.alias("s"), 
              (col("src.subscription_type") == col("s.type_name")) & 
              (col("src.subscription_status") == col("s.status")), "left")
              
        # Spajanje s DimEngagement preko uređaja, oglasa i omiljene značajke
        .join(dim_engagement_df.alias("e"), 
              (col("src.primary_device") == col("e.device_name")) & 
              (col("src.ad_interaction") == col("e.ad_interaction")) & 
              (col("src.most_liked_feature") == col("e.most_liked_feature")), "left")
    )

    # 4. Selekcija surogatnih ključeva i numeričkih mjera (Facts)
    fact_selected = fact_joined.select(
        col("c.country_tk"),
        col("d.date_tk"),
        col("s.subscription_tk"),
        col("e.engagement_tk"),
        col("src.age"),
        col("src.avg_listening_hours_per_week").alias("listening_hours"),
        col("src.playlists_created"),
        col("src.avg_skips_per_day").alias("skips_per_day"),
        col("src.music_suggestion_rating_1_to_5").alias("suggestion_rating"),
        col("src.months_inactive"),
        col("src.ad_conversion_numeric").alias("ad_conversion")
    )

    # 5. Generiranje surogatnog ključa za samu fact tablicu (fact_tk)
    # Sortiranje radimo po ključevima dimenzija radi determinističkog ponašanja
    window_spec = Window.orderBy("country_tk", "date_tk", "subscription_tk", "engagement_tk")
    
    final_fact_df = (
        fact_selected
        .withColumn("fact_tk", row_number().over(window_spec).cast("long"))
        # Preslagivanje stupaca kako bi točno odgovarali poretku u MySQL tablici
        .select(
            "fact_tk", "country_tk", "date_tk", "subscription_tk", "engagement_tk",
            "age", "listening_hours", "playlists_created", "skips_per_day", 
            "suggestion_rating", "months_inactive", "ad_conversion"
        )
    )

    # assert final_fact_df.count() == 8000, "Greška: Broj redaka u Fact tablici ne odgovara izvornom datasetu od 8000 zapisa!"
    print(f"📊 Fact tablica uspješno kreirana s {final_fact_df.count()} redaka!")
    
    return final_fact_df