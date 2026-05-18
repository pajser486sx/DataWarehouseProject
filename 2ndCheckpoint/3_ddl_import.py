import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, insert, text
from sqlalchemy.orm import sessionmaker, declarative_base

current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(current_dir)
CSV_FILE_PATH = os.path.join(base_dir, "2_relational_model", "processed", "UserBehaviour_PROCESSED.csv")
df = pd.read_csv(CSV_FILE_PATH)
print(f"Učitana datoteka: {CSV_FILE_PATH} (Veličina: {df.shape})")

temp_engine = create_engine('mysql+pymysql://root:root@localhost:3306/')
with temp_engine.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS spotify_dw"))
    conn.execute(text("COMMIT"))# promjena vidljiva odmah
    print("Baza podataka 'spotify_dw' je spremna.")

engine = create_engine('mysql+pymysql://root:root@localhost:3306/spotify_dw', echo=False)
Base = declarative_base()

class Country(Base):
    __tablename__ = 'countries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

class SubscriptionType(Base):
    __tablename__ = 'subscription_types'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

class Genre(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

class Device(Base):
    __tablename__ = 'devices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

class Feature(Base):
    __tablename__ = 'features'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    age = Column(Integer)
    signup_date = Column(Date)
    subscription_status = Column(String(20))
    months_inactive = Column(Integer)
    inactive_3_months_flag = Column(Integer)
    ad_interaction = Column(String(10))
    ad_conversion = Column(String(10))
    suggestion_rating = Column(Integer)
    listening_hours = Column(Float)
    playlists_created = Column(Integer)
    skips_per_day = Column(Integer)
    
    country_id = Column(Integer, ForeignKey('countries.id'))
    sub_type_id = Column(Integer, ForeignKey('subscription_types.id'))
    genre_id = Column(Integer, ForeignKey('genres.id'))
    device_id = Column(Integer, ForeignKey('devices.id'))
    liked_feature_id = Column(Integer, ForeignKey('features.id'))
    desired_feature_id = Column(Integer, ForeignKey('features.id'))

print("Resetiranje tablica (Drop & Create)...")
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

print("Ubacivanje lookup podataka...")

def populate_table(model, series):
    unique_values = sorted(series.unique())
    items = [{"name": val} for val in unique_values]
    session.execute(insert(model), items)
    session.commit()
    return {item.name: item.id for item in session.query(model).all()}

country_map = populate_table(Country, df['country'])
sub_type_map = populate_table(SubscriptionType, df['subscription_type'])
genre_map = populate_table(Genre, df['favorite_genre'])
device_map = populate_table(Device, df['primary_device'])
# posebno za features jer imamo 2 različita stupca koji referenciraju istu tablicu
all_features = pd.concat([df['most_liked_feature'], df['desired_future_feature']]).unique()
session.execute(insert(Feature), [{"name": f} for f in all_features])
session.commit()
feature_map = {f.name: f.id for f in session.query(Feature).all()}

print("Mapiranje i ubacivanje korisnika (Bulk insert)...")

users_list = []
for _, row in df.iterrows():
    users_list.append({
        "user_id": row['user_id'],
        "age": row['age'],
        "signup_date": row['signup_date'],
        "subscription_status": row['subscription_status'],
        "months_inactive": row['months_inactive'],
        "inactive_3_months_flag": row['inactive_3_months_flag'],
        "ad_interaction": row['ad_interaction'],
        "ad_conversion": row['ad_conversion_to_subscription'],
        "suggestion_rating": row['music_suggestion_rating_1_to_5'],
        "listening_hours": row['avg_listening_hours_per_week'],
        "playlists_created": row['playlists_created'],
        "skips_per_day": row['avg_skips_per_day'],
        "country_id": country_map[row['country']],
        "sub_type_id": sub_type_map[row['subscription_type']],
        "genre_id": genre_map[row['favorite_genre']],
        "device_id": device_map[row['primary_device']],
        "liked_feature_id": feature_map[row['most_liked_feature']],
        "desired_feature_id": feature_map[row['desired_future_feature']]
    })

session.execute(insert(User), users_list)
session.commit()

print("Podaci su uspješno uvezeni!")
session.close()