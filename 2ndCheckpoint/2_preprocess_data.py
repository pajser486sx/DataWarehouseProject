import pandas as pd
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(current_dir) 
CSV_FILE_PATH = os.path.join(base_dir, "data", "UserBehaviour.csv")
output_dir = os.path.join(base_dir, "2_relational_model", "processed")


if not os.path.exists(output_dir):
    os.makedirs(output_dir)

df = pd.read_csv(CSV_FILE_PATH)
print("CSV size before: ", df.shape)

# pretvaramo signup date u YYYY-MM-DD format
df['signup_date'] = pd.to_datetime(df['signup_date']).dt.strftime('%Y-%m-%d')

df = df.dropna()

# stavljamo lowercase i zamjenjujemo razmake s underscoreom
df.columns = df.columns.str.lower()
df.columns = df.columns.str.replace(' ', '_')

print("CSV size after cleaning: ", df.shape)
print(df.head())

duplicates = df.duplicated().sum()
print(f"Number of duplicates found: {duplicates}")
if duplicates > 0:
    df = df.drop_duplicates()
    print(f"Duplicates removed. New size: {df.shape}")

# djeljenje 80-20
df20 = df.sample(frac=0.2, random_state=1)
df80 = df.drop(df20.index)

print("Main dataset (80%): ", df80.shape)
print("Sample dataset (20%): ", df20.shape)

df80.to_csv(f"{output_dir}UserBehaviour_PROCESSED.csv", index=False)
df20.to_csv(f"{output_dir}UserBehaviour_PROCESSED_20.csv", index=False)

print(f"Files saved successfully in {output_dir}")