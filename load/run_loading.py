from pyspark.sql import DataFrame

def write_spark_df_to_mysql(spark_df: DataFrame, table_name: str, mode: str = "overwrite"):
    jdbc_url = "jdbc:mysql://127.0.0.1:3306/spotify_dw?useSSL=false"
    
    connection_properties = {
        "user": "root",
        "password": "root",
        "driver": "com.mysql.cj.jdbc.Driver",
        "sessionInitStatement": "SET FOREIGN_KEY_CHECKS=0"
        
    }

    print(f"🚀 Writing to table `{table_name}` with mode `{mode}`...")
    
    try:
        spark_df.write.jdbc(
            url=jdbc_url,
            table=table_name,
            mode=mode,
            properties=connection_properties
        )
        print(f"✅ Successfully written to `{table_name}`.")
    except Exception as e:
        print(f"❌ Error writing to `{table_name}`: {e}")