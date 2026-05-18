from spark_session import get_spark_session

def extract_table(table_name):
    spark = get_spark_session("ETL_App")

    jdbc_url = "jdbc:mysql://127.0.0.1:3306/spotify_dw?useSSL=false"
    connection_properties = {
        "user": "root",
        "password": "root",
        "driver": "com.mysql.cj.jdbc.Driver"
    }

    df = spark.read.jdbc(url=jdbc_url, table=table_name, properties=connection_properties)
    return df

def extract_all_tables():
    """
    Izvlači sirove relacijske podatke potrebne za transformaciju.
    Iz baze povlačimo samo tablicu 'countries' jer se svi ostali 
    sirovi podaci nalaze unutar CSV datoteke.
    """
    return {
        "countries": extract_table("countries")
    }