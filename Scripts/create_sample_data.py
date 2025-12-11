import duckdb
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FULL_PATH = os.path.join(BASE_DIR, 'Data', 'deutsche_bahn_data', 'monthly_processed_data', 'data-2024-10.parquet')
OUT_PATH = os.path.join(BASE_DIR, 'Data', 'deutsche_bahn_data', 'monthly_processed_data', 'data-2024-10-SAMPLE.parquet')

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

print('Lese Original-Datei:', FULL_PATH)
con = duckdb.connect()

# Nimm z.B. 2000 Zeilen als Sample
df = con.execute(f"SELECT * FROM '{FULL_PATH}' LIMIT 2000").fetchdf()
print('Sample Zeilen:', len(df))

print('Schreibe Sample-Datei:', OUT_PATH)
df.to_parquet(OUT_PATH)
print('Fertig.')

