# transform/pipeline.py

# Uvozimo tvoje PySpark funkcije za dimenzije i facts
from transform.dimensions.DimCountry import transform_country_dim
from transform.dimensions.DimDate import transform_date_dim
from transform.dimensions.DimSubscription import transform_subscription_dim
from transform.dimensions.DimEngagement import transform_engagement_dim
from transform.facts.FactUserActivity import transform_user_activity_fact


def run_transformations(raw_data):
    """
    Glavni pipeline koji prima sirove podatke, pokreće transformacije
    za 4 Spotify dimenzije i na kraju sklapa Fact tablicu.
    """
    
    # 1️⃣ Transformacija: DimCountry
    # Iz MySQL-a prosljeđujemo tablicu "countries" (izvučenu u tvojem extract_mysql.py)
    dim_country_df = transform_country_dim(
        raw_data["countries"]
    )
    print("1️⃣ Country dimension complete")
    
    # 2️⃣ Transformacija: DimDate
    # Budući da su svi datumi u CSV-u, prosljeđujemo tvoj "csv_user_behaviour"
    dim_date_df = transform_date_dim(
        raw_data["csv_user_behaviour"]
    )
    print("2️⃣ Date dimension complete")
    
    # 3️⃣ Transformacija: DimSubscription
    # Podaci za pretplate se također nalaze isključivo u CSV-u
    dim_subscription_df = transform_subscription_dim(
        raw_data["csv_user_behaviour"]
    )
    print("3️⃣ Subscription dimension complete")
    
    # 4️⃣ Transformacija: DimEngagement
    # Podaci za angažman (uređaji, oglasi) se izvlače iz CSV-a
    dim_engagement_df = transform_engagement_dim(
        raw_data["csv_user_behaviour"]
    )
    print("4️⃣ Engagement dimension complete")
    
    # 5️⃣ Transformacija: FactUserActivity
    # Tablici činjenica prosljeđujemo cijeli raw_data rječnik (isto kao profesor) 
    # i sve četiri tek stvorene dimenzije kako bi ih mogla spojiti (JOIN)
    fact_user_activity_df = transform_user_activity_fact(
        raw_data,
        dim_country_df,
        dim_date_df,
        dim_subscription_df,
        dim_engagement_df
    )
    print("5️⃣ User Activity fact table complete")

    # Vraćamo rječnik s točnim nazivima tablica.
    # PAŽNJA: Provjeri kako ti se točno zovu tablice u bazi, pod tim ključevima ih vrati ovdje!
    return {
        "dim_country": dim_country_df,
        "dim_date": dim_date_df,
        "dim_subscription": dim_subscription_df,
        "dim_engagement": dim_engagement_df,
        "fact_user_activity": fact_user_activity_df
    }