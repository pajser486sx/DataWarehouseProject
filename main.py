import os
from extract.extract_mysql import extract_all_tables
from extract.extract_csv import extract_from_csv
from transform.pipeline import run_transformations
from spark_session import get_spark_session
from load.run_loading import write_spark_df_to_mysql

os.environ["HADOOP_HOME"] = "C:\\hadoop"
os.environ["hadoop.home.dir"] = "C:\\hadoop"
os.environ["PATH"] += os.pathsep + "C:\\hadoop\\bin"

os.environ.pop("SPARK_HOME", None) 

os.environ["PYSPARK_PYTHON"] = "python"
os.environ["PYSPARK_DRIVER_PYTHON"] = "python"

def main():
    spark = get_spark_session() 
    spark.sparkContext.setLogLevel("ERROR")
    spark.catalog.clearCache()

    
    print("🚀 Starting data extraction...")
    
    mysql_df = extract_all_tables()
    
    PUTANJA_DO_CSV = "2_relational_model/processed/UserBehaviour_PROCESSED_20.csv"
    
    csv_df = {"csv_user_behaviour": extract_from_csv(PUTANJA_DO_CSV)}
    
    merged_df = {**mysql_df, **csv_df}
    print("✅ Data extraction completed successfully.")

    print("🚀 Starting data transformation...")
    
    load_ready_dict = run_transformations(merged_df)
    print("✅ Data transformation completed successfully.")

    print("🚀 Starting data loading into spotify_dw...")
    
    for table_name, df in load_ready_dict.items():
        print(f"📦 Loading table: {table_name}...")
        write_spark_df_to_mysql(df, table_name)
        
    print("👏 Data loading completed. Your Spotify Data Warehouse is ready!")

if __name__ == "__main__":
    main()