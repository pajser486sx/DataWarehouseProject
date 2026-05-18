import os
from extract.extract_mysql import extract_all_tables
from extract.extract_csv import extract_from_csv
from transform.pipeline import run_transformations
from spark_session import get_spark_session
from load.run_loading import write_spark_df_to_mysql

# Hadoop konfiguracija za Windows okruženje (sprječava česte Spark greške)
os.environ["HADOOP_HOME"] = "C:\\hadoop"
os.environ["hadoop.home.dir"] = "C:\\hadoop"
os.environ["PATH"] += os.pathsep + "C:\\hadoop\\bin"

# Uklanjanje SPARK_HOME varijable ako postoji kako bi se spriječili konflikti verzija
os.environ.pop("SPARK_HOME", None) 

os.environ["PYSPARK_PYTHON"] = "python"
os.environ["PYSPARK_DRIVER_PYTHON"] = "python"

def main():
    # Inicijalizacija Apache Spark sesije preko tvoje pomoćne skripte
    spark = get_spark_session() 
    spark.sparkContext.setLogLevel("ERROR") # Prikazuj samo kritične greške u terminalu
    spark.catalog.clearCache()              # Čišćenje predmemorije (cache-a) prije početka

    # =========================================================================
    # 1. KORAK: EXTRACTION (Izvlačenje podataka)
    # =========================================================================
    print("🚀 Starting data extraction...")
    
    # Izvlačenje tablice 'countries' iz MySQL relacijske baze
    mysql_df = extract_all_tables()
    
    # Definiranje točne putanje do tvog procesiranog Spotify CSV-a
    PUTANJA_DO_CSV = "2_relational_model/processed/UserBehaviour_PROCESSED_20.csv"
    
    # Pozivanje funkcije iz extract_csv.py i predavanje putanje
    # Spremamo pod ključem 'csv_user_behaviour' koji tvoja Fact tablica očekuje
    csv_df = {"csv_user_behaviour": extract_from_csv(PUTANJA_DO_CSV)}
    
    # Spajanje MySQL rječnika i CSV rječnika u jedan zajednički skup sirovih podataka
    merged_df = {**mysql_df, **csv_df}
    print("✅ Data extraction completed successfully.")

    # =========================================================================
    # 2. KORAK: TRANSFORMATION (Transformacija podataka)
    # =========================================================================
    print("🚀 Starting data transformation...")
    
    # run_transformations unutar transform/pipeline.py će primiti sve sirove podatke,
    # pokrenuti transformacije za 4 dimenzije, a zatim sklopiti Fact tablicu.
    # Vraća rječnik s gotovim Spark DataFrame-ovima spremnim za bazu.
    load_ready_dict = run_transformations(merged_df)
    print("✅ Data transformation completed successfully.")

    # =========================================================================
    # 3. KORAK: LOADING (Učitavanje u Skladište Podataka)
    # =========================================================================
    print("🚀 Starting data loading into spotify_dw...")
    
    # Prolazimo kroz sve transformirane tablice (dimenzije i fact) i upisujemo ih u MySQL
    for table_name, df in load_ready_dict.items():
        print(f"📦 Loading table: {table_name}...")
        write_spark_df_to_mysql(df, table_name)
        
    print("👏 Data loading completed. Your Spotify Data Warehouse is ready!")

if __name__ == "__main__":
    main()