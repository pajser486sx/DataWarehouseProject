from pyspark.sql import SparkSession

def get_spark_session(app_name="ETL_App"):
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars", "Connectors/mysql-connector-j-9.2.0.jar") \
        .getOrCreate()