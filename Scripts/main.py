"""
Data Detective - Deutsche Bahn Datenqualität Analyse
Punkt 4: Setup & erste Analyse
"""

import duckdb
import os

# Pfad zur Parquet-Datei
data_path = '../Data/deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet'

# Prüfe ob Datei existiert
if not os.path.exists(data_path):
    print("❌ Datei nicht gefunden!")
    print(f"Erwarteter Pfad: {data_path}")
    exit(1)

print("🚂 Deutsche Bahn - Data Quality Analyse")
print("=" * 60)
print()

# DuckDB Verbindung erstellen
con = duckdb.connect(':memory:')

print("📊 1. ALLGEMEINE INFORMATIONEN")
print("-" * 60)

# Zeilen zählen
result = con.execute(f"""
    SELECT COUNT(*) as total_rows
    FROM '{data_path}'
""").fetchone()
print(f"Anzahl Zeilen: {result[0]:,}")

# Spalten anzeigen
print("\n📋 Spalten-Übersicht:")
schema = con.execute(f"""
    DESCRIBE SELECT * FROM '{data_path}'
""").fetchall()

for col in schema:
    print(f"  - {col[0]:25s} | {col[1]}")

print("\n" + "=" * 60)
print("📊 2. SAMPLE DATA (erste 5 Zeilen)")
print("-" * 60)

sample = con.execute(f"""
    SELECT * FROM '{data_path}'
    LIMIT 5
""").fetchdf()

print(sample.to_string())

print("\n" + "=" * 60)
print("📊 3. QUICK STATS - DELAY")
print("-" * 60)

stats = con.execute(f"""
    SELECT
        MIN(delay_in_min) as min_delay,
        MAX(delay_in_min) as max_delay,
        AVG(delay_in_min) as avg_delay,
        STDDEV(delay_in_min) as std_delay,
        COUNT(*) as total_count,
        COUNT(delay_in_min) as non_null_count,
        COUNT(*) - COUNT(delay_in_min) as null_count
    FROM '{data_path}'
""").fetchone()

print(f"Min Delay:       {stats[0]:,.2f} Minuten")
print(f"Max Delay:       {stats[1]:,.2f} Minuten")
print(f"Avg Delay:       {stats[2]:,.2f} Minuten")
print(f"Std Dev Delay:   {stats[3]:,.2f} Minuten")
print(f"Total Count:     {stats[4]:,}")
print(f"Non-NULL Count:  {stats[5]:,}")
print(f"NULL Count:      {stats[6]:,}")

print("\n" + "=" * 60)
print("🔍 4. DATA QUALITY CHECKS")
print("-" * 60)

# Check 1: Missing Values
print("\n🔎 Check 1: COMPLETENESS - Missing Values")
missing_check = con.execute(f"""
    SELECT
        COUNT(*) - COUNT(station_name) as missing_station,
        COUNT(*) - COUNT(delay_in_min) as missing_delay,
        COUNT(*) - COUNT(time) as missing_time,
        COUNT(*) - COUNT(train_type) as missing_train_type
    FROM '{data_path}'
""").fetchone()

print(f"  Missing station_name: {missing_check[0]:,}")
print(f"  Missing delay_in_min: {missing_check[1]:,}")
print(f"  Missing time:         {missing_check[2]:,}")
print(f"  Missing train_type:   {missing_check[3]:,}")

# Check 2: Validity - Negative Delays
print("\n🔎 Check 2: VALIDITY - Negative Delays")
negative_delays = con.execute(f"""
    SELECT COUNT(*) as count
    FROM '{data_path}'
    WHERE delay_in_min < 0
""").fetchone()

print(f"  Negative Delays gefunden: {negative_delays[0]:,}")

# Check 3: Validity - Extreme Delays (> 120 min)
print("\n🔎 Check 3: ACCURACY - Extreme Delays (> 120 min)")
extreme_delays = con.execute(f"""
    SELECT 
        COUNT(*) as count,
        MAX(delay_in_min) as max_delay
    FROM '{data_path}'
    WHERE delay_in_min > 120
""").fetchone()

print(f"  Delays > 120 Minuten: {extreme_delays[0]:,}")
print(f"  Maximum Delay:        {extreme_delays[1]:,.2f} Minuten")

# Check 4: Uniqueness - Duplicate Check
print("\n🔎 Check 4: UNIQUENESS - Duplicate Check")
duplicates = con.execute(f"""
    SELECT COUNT(*) as duplicate_groups
    FROM (
        SELECT station_name, time, train_type, delay_in_min, COUNT(*) as cnt
        FROM '{data_path}'
        GROUP BY station_name, time, train_type, delay_in_min
        HAVING COUNT(*) > 1
    )
""").fetchone()

print(f"  Duplicate Gruppen gefunden: {duplicates[0]:,}")

# Check 5: Consistency - Datetime Range
print("\n🔎 Check 5: CONSISTENCY - Datetime Range")
date_range = con.execute(f"""
    SELECT 
        MIN(time) as min_date,
        MAX(time) as max_date
    FROM '{data_path}'
""").fetchone()

print(f"  Frühestes Datum: {date_range[0]}")
print(f"  Spätestes Datum: {date_range[1]}")

print("\n" + "=" * 60)
print("✅ Analyse abgeschlossen!")
print("=" * 60)

# Verbindung schließen
con.close()

