import pandas as pd
import numpy as np
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "data", "UserBehaviour.csv")


data = pd.read_csv(csv_path)


print("\n1. Prvih 5 redaka:")
print(data.head())
print("=" * 30)


print("2. Veličina skupa:")
print(f"Redovi: {data.shape[0]}, Stupci: {data.shape[1]}")
print("=" * 30)


print("3. Nazivi stupaca:")
for i, col in enumerate(data.columns, 1):
    print(f"{i}. {col}")
print("=" * 30)


print("4. Nedostajuće vrijednosti po stupcu:")
missing = data.isna().sum()
print(missing[missing > 0] if missing.sum() > 0 else "Nema nedostajućih vrijednosti")
print("=" * 30)


print("5. Jedinstvene vrijednosti:")
tekstualni_stupci = ['country', 'subscription_type', 'subscription_status', 'favorite_genre', 'most_liked_feature  ', 'desired_future_feature', 'primary_device']
for col in tekstualni_stupci:
   if col in data.columns:
        unique_vals = data[col].unique()
        print(f"\n{col}: {len(unique_vals)} jedinstvenih")
        print(unique_vals)
print("=" * 30)


print("6. Ispis tipova vrijednosti .dtypes()")
print(data.dtypes)
print("=" * 30)


print("7. Frekvencije vrijednosti po stupcu") 
for col in tekstualni_stupci:
    if col in data.columns:
        print("\n", data[col].value_counts())
print("=" * 30)

# Je li je skup podataka dovoljno velik? (Optimalno >15 000 redaka i >20 stupaca)
# Je li skup ima dovoljno različite podatke?
# Je li skup ima vremensku dimenziju? 2018 - 2026
# Je li skup ima kvantitativne i kvalitativne podatke?
# Je li skup ima puno nedostajućih vrijednosti?
