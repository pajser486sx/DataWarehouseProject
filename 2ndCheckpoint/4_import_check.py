import unittest
import pandas as pd
import sqlalchemy
from sqlalchemy import text
from pandas.testing import assert_frame_equal

"""
4. Skripta za testiranje importa u bazu podataka (opcionalno, možete ručno provjeriti import u bazu podataka)

U ovom koraku testirmo import u bazu podataka. 
Skripta uspoređuje CSV datoteku s tablicama u bazi podataka.
Rade se dva testa:
1. Testiranje stupaca
2. Testiranje podataka
"""

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/spotify_dw')
        self.connection = self.engine.connect()

        self.csv_path = "2_relational_model/processed/UserBehaviour_PROCESSED.csv"
        self.df = pd.read_csv(self.csv_path)
        
        self.df['signup_date'] = pd.to_datetime(self.df['signup_date']).dt.date

        query = """
        SELECT 
            u.user_id,
            c.name AS country,
            u.age,
            u.signup_date,
            s.name AS subscription_type,
            u.subscription_status,
            u.months_inactive,
            u.inactive_3_months_flag,
            u.ad_interaction,
            u.ad_conversion AS ad_conversion_to_subscription,
            u.suggestion_rating AS music_suggestion_rating_1_to_5,
            u.listening_hours AS avg_listening_hours_per_week,
            g.name AS favorite_genre,
            f1.name AS most_liked_feature,
            f2.name AS desired_future_feature,
            d.name AS primary_device,
            u.playlists_created,
            u.skips_per_day AS avg_skips_per_day
        FROM users u
        JOIN countries c ON u.country_id = c.id
        JOIN subscription_types s ON u.sub_type_id = s.id
        JOIN genres g ON u.genre_id = g.id
        JOIN devices d ON u.device_id = d.id
        JOIN features f1 ON u.liked_feature_id = f1.id
        JOIN features f2 ON u.desired_feature_id = f2.id
        ORDER BY u.user_id ASC
        """
        
        result = self.connection.execute(text(query))
        self.db_df = pd.DataFrame(result.fetchall())
        self.db_df.columns = list(result.keys())


        self.db_df['signup_date'] = pd.to_datetime(self.db_df['signup_date']).dt.date
        
        self.db_df = self.db_df[self.df.columns]

    def test_columns(self):
        """Provjera podudaraju li se nazivi svih stupaca"""
        self.assertListEqual(list(self.df.columns), list(self.db_df.columns))

    def test_dataframes(self):
        """Provjera podudaraju li se sami podaci (vrijednosti)"""

        self.df = self.df.sort_values('user_id').reset_index(drop=True)
        self.db_df = self.db_df.sort_values('user_id').reset_index(drop=True)
        
        assert_frame_equal(self.df, self.db_df, check_dtype=False, check_exact=False, atol=0.01)

    def tearDown(self):
        self.connection.close()

if __name__ == '__main__':
    unittest.main()