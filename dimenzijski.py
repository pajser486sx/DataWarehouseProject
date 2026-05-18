from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from sqlalchemy import text

CSV_FILE_PATH = "2_relational_model/processed/UserBehaviour_PROCESSED.csv"
df = pd.read_csv(CSV_FILE_PATH)
print(f"Učitana datoteka: {CSV_FILE_PATH} (Veličina: {df.shape})")
DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/spotify_dw"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


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
class DimCountry(Base):
    __tablename__ = 'dim_country'
    __table_args__ = {'schema': 'spotify_dw'}
    country_tk = Column(BigInteger, primary_key=True, autoincrement=True)
    version = Column(Integer)  
    date_from = Column(DateTime)
    date_to = Column(DateTime)
    country_id = Column(Integer, index=True)
    name = Column(String(100))
    continent = Column(String(50))
    # sporo mjenjajuća dimenzija tip 2: stavili smo da se može pratiti datum
    # pratimo promjene, povijest korisnika
    # OD KAD DO KAD NEKI PODATAK VRIJEDI

class DimSubscription(Base):
    __tablename__ = 'dim_subscription'
    __table_args__ = {'schema': 'spotify_dw'}
    subscription_tk = Column(BigInteger, primary_key=True, autoincrement=True)
    subscription_id = Column(Integer, index=True)
    type_name = Column(String(50))
    status = Column(String(20))
    version = Column(Integer)
    date_from = Column(DateTime)
    date_to = Column(DateTime)

class DimEngagement(Base):
    __tablename__ = 'dim_engagement'
    __table_args__ = {'schema': 'spotify_dw'}
    engagement_tk = Column(BigInteger, primary_key=True, autoincrement=True)
    device_name = Column(String(50))
    ad_interaction = Column(String(20))
    most_liked_feature = Column(String(100))
    version = Column(Integer)
    date_from = Column(DateTime)
    date_to = Column(DateTime)

class DimDate(Base):
    __tablename__ = 'dim_date'
    __table_args__ = {'schema': 'spotify_dw'}
    date_tk = Column(Integer, primary_key=True, autoincrement=True)
    full_date = Column(DateTime, unique=True)
    year = Column(Integer)
    quarter = Column(Integer)
    month = Column(Integer)
    month_name = Column(String(20))
    day_name = Column(String(20))

class FactUserActivity(Base):
    __tablename__ = 'fact_user_activity'
    __table_args__ = {'schema': 'spotify_dw'}
    fact_tk = Column(BigInteger, primary_key=True, autoincrement=True)
    country_tk = Column(BigInteger, ForeignKey('spotify_dw.dim_country.country_tk'))
    date_tk = Column(Integer, ForeignKey('spotify_dw.dim_date.date_tk'))
    subscription_tk = Column(BigInteger, ForeignKey('spotify_dw.dim_subscription.subscription_tk'))
    engagement_tk = Column(BigInteger, ForeignKey('spotify_dw.dim_engagement.engagement_tk'))

    age = Column(Integer)
    listening_hours = Column(Float)
    playlists_created = Column(Integer)
    skips_per_day = Column(Integer)
    suggestion_rating = Column(Integer)
    months_inactive = Column(Integer)
    ad_conversion = Column(Integer)


print("Brišem postojeće tablice...")
FactUserActivity.__table__.drop(engine, checkfirst=True)
DimDate.__table__.drop(engine, checkfirst=True)
DimEngagement.__table__.drop(engine, checkfirst=True)
DimSubscription.__table__.drop(engine, checkfirst=True)
DimCountry.__table__.drop(engine, checkfirst=True)

print("Kreiram nove tablice...")
Base.metadata.create_all(engine)

#COUNTRY
print("Popunjavam dim_country...")
countries_query = "SELECT id AS country_id, name FROM countries"
df_countries = pd.read_sql(countries_query, engine)
df_countries['continent'] = df_countries['name'].map(continent_map)
df_countries['version'] = 1
df_countries['date_from'] = '2024-01-01'
df_countries['date_to'] = '9999-12-31'
df_countries.to_sql('dim_country', engine, schema='spotify_dw', if_exists='append', index=False)

#DATE
print("Popunjavam dim_date...")
unique_dates = pd.to_datetime(df['signup_date']).unique()
df_dates = pd.DataFrame(unique_dates, columns=['full_date'])
df_dates['year'] = df_dates['full_date'].dt.year
df_dates['quarter'] = df_dates['full_date'].dt.quarter
df_dates['month'] = df_dates['full_date'].dt.month
df_dates['month_name'] = df_dates['full_date'].dt.month_name()
df_dates['day_name'] = df_dates['full_date'].dt.day_name()
df_dates.to_sql('dim_date', engine, schema='spotify_dw', if_exists='append', index=False)

#SUBSCRIPTION
print("Popunjavam dim_subscription...")
df_sub = df[['subscription_type', 'subscription_status']].drop_duplicates().reset_index(drop=True)
df_sub = df_sub.rename(columns={'subscription_type': 'type_name', 'subscription_status': 'status'})
df_sub['subscription_id'] = df_sub.index + 1
df_sub['version'] = 1
df_sub['date_from'] = '2024-01-01'
df_sub['date_to'] = '9999-12-31'
df_sub.to_sql('dim_subscription', engine, schema='spotify_dw', if_exists='append', index=False)

#ENGAGEMENT
print("Popunjavam dim_engagement...")
df_eng = df[['primary_device', 'ad_interaction', 'most_liked_feature']].drop_duplicates().reset_index(drop=True)
df_eng = df_eng.rename(columns={'primary_device': 'device_name'})
df_eng['version'] = 1
df_eng['date_from'] = '2024-01-01'
df_eng['date_to'] = '9999-12-31'
df_eng.to_sql('dim_engagement', engine, schema='spotify_dw', if_exists='append', index=False)

#Tablica činjenica
print("Popunjavam fact_user_activity...")
c_map = {n: tk for n, tk in session.query(DimCountry.name, DimCountry.country_tk).all()}
d_map = {str(d.date()): tk for d, tk in session.query(DimDate.full_date, DimDate.date_tk).all()}
s_map = {(t, s): tk for t, s, tk in session.query(DimSubscription.type_name, DimSubscription.status, DimSubscription.subscription_tk).all()}
e_map = {(d, a, f): tk for d, a, f, tk in session.query(DimEngagement.device_name, DimEngagement.ad_interaction, DimEngagement.most_liked_feature, DimEngagement.engagement_tk).all()}

fact_rows = []
for _, row in df.iterrows():
    fact_rows.append({
        'country_tk': c_map.get(row['country']),
        'date_tk': d_map.get(str(pd.to_datetime(row['signup_date']).date())),
        'subscription_tk': s_map.get((row['subscription_type'], row['subscription_status'])),
        'engagement_tk': e_map.get((row['primary_device'], row['ad_interaction'], row['most_liked_feature'])),
        'age': row['age'],
        'listening_hours': row['avg_listening_hours_per_week'],
        'playlists_created': row['playlists_created'],
        'skips_per_day': row['avg_skips_per_day'],
        'suggestion_rating': row['music_suggestion_rating_1_to_5'],
        'months_inactive': row['months_inactive'],
        'ad_conversion': 1 if row['ad_conversion_to_subscription'] == 'Yes' else 0
    })

pd.DataFrame(fact_rows).to_sql('fact_user_activity', engine, schema='spotify_dw', if_exists='append', index=False)

print("\n" + "="*30 + "\nVERIFIKACIJA\n" + "="*30)
with engine.connect() as conn:
    for tbl in ['dim_country', 'dim_date', 'dim_subscription', 'dim_engagement', 'fact_user_activity']:
        res = conn.execute(text(f"SELECT COUNT(*) FROM spotify_dw.{tbl}"))
        print(f"{tbl}: {res.scalar()} redaka")