import duckdb
import pandas as pd


con = duckdb.connect()
# Dateipfad
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, '..', 'Data', 'deutsche_bahn_data', 'monthly_processed_data', 'data-2024-10.parquet')

result = con.execute(f"SELECT COUNT(*) FROM '{DATA_PATH}'").fetchone()
print(f"Dataset Preview {result[0]:,} rows.")

#Erste Transformation:
result = con.execute(f"""
    SELECT
        time,
        HOUR(time) as Stunde,
        Station_name,
        delay_in_min
    FROM '{DATA_PATH}'
    LIMIT 10
 """).fetchdf()
print(result)

result =   con.execute(f"""
    SELECT
        time,
        DAYofWEEK(time) as Wochentag_nummer,
        CASE DAYofWEEK(time)
            WHEN 0 THEN 'Sonntag'
            WHEN 1 THEN 'Montag'
            WHEN 2 THEN 'Dienstag'
            WHEN 3 THEN 'Mittwoch'
            WHEN 4 THEN 'Donnerstag'
            WHEN 5 THEN 'Freitag'
            WHEN 6 THEN 'Samstag'
            ELSE 'Unbekannt'
        END as Wochentag_Name,
        delay_in_min
    FROM '{DATA_PATH}'
    LIMIT 10
 """).fetchdf()
print(result)

result =   con.execute(f"""
    SELECT
        delay_in_min,
        CASE
            WHEN delay_in_min < 0 THEN 'Frühzeitig'
            WHEN delay_in_min = 0 THEN 'Pünktlich'
            WHEN delay_in_min BETWEEN 1 AND 5 THEN 'Leichte Verspätung'
            WHEN delay_in_min BETWEEN 6 AND 15 THEN 'Mäßige Verspätung'
            WHEN delay_in_min BETWEEN 16 AND 30 THEN 'Erhebliche Verspätung'
            WHEN delay_in_min > 30 THEN 'Starke Verspätung'
            ELSE 'Extreme Verspätung'
        END as Verspätungskategorie
    FROM '{DATA_PATH}'
    WHERE delay_in_min IS NOT NULL
    LIMIT 20
""").fetchdf()
print(result)

# Query mit Flags für Rush Hour, Weekend und Problematic Delay
query = f"""
    SELECT
        time,
        train_name,
        delay_in_min,
        is_canceled,
        CASE DAYofWEEK(time)
            WHEN 0 THEN 'Sonntag'
            WHEN 1 THEN 'Montag'
            WHEN 2 THEN 'Dienstag'
            WHEN 3 THEN 'Mittwoch'
            WHEN 4 THEN 'Donnerstag'
            WHEN 5 THEN 'Freitag'
            WHEN 6 THEN 'Samstag'
            ELSE 'Unbekannt'
        END as Wochentag,
        -- FLAG 1: Is Rush Hour (7-9 AM or 4-6 PM)
        CASE
            WHEN (HOUR(time) BETWEEN 7 AND 9) THEN TRUE
            WHEN (HOUR(time) BETWEEN 16 AND 18) THEN TRUE
            ELSE FALSE
        END as is_rush_hour,
        
        -- FLAG 2: Is Weekend?
        CASE
            WHEN DAYofWEEK(time) IN (0, 6) THEN TRUE
            ELSE FALSE
        END as is_weekend,
        
        -- FLAG 3: Problematic Delay (> 30 min)?
        CASE
            WHEN is_canceled = TRUE THEN TRUE
            WHEN delay_in_min > 15 THEN TRUE
            ELSE FALSE
        END as is_problematic_delay
    FROM '{DATA_PATH}'
    LIMIT 20
"""
result = con.execute(query).fetchdf()
print(result)

result =   con.execute(f"""
    SELECT
        station_name,
        arrival_planned_time,
        arrival_change_time,
        -- Difference in minutes
        DATEDIFF('minute', arrival_planned_time, arrival_change_time) as berechnete_Differenz_in_min,
        -- Vergleich mit delay_in_min
        delay_in_min as gespeicherte_Verspätung_in_min
    FROM '{DATA_PATH}'
    WHERE arrival_planned_time IS NOT NULL
      AND arrival_change_time IS NOT NULL
    LIMIT 10
""").fetchdf()
print(result)


result = con.execute(f"""
    SELECT
        train_type,
        CASE
            WHEN train_type IN ('ICE') THEN TRUE ELSE FALSE END as is_ice,
            FROM '{DATA_PATH}'
        END as verkehrskategorie,




# Query mit is_ice Flag
result = con.execute(f"""
    SELECT
        station_name,
        train_type,
        train_name,
        (train_type = 'ICE') as is_ice,
        delay_in_min
    FROM '{DATA_PATH}'
    LIMIT 50
""").fetchdf()
print(result)

# Styled Output mit blauer Markierung für ICE-Züge
print("\n=== ICE-Züge mit blauer Markierung ===")

# ANSI-Farbcodes für blauen Hintergrund
BLUE_BG = '\033[44m'
RESET = '\033[0m'

# Durchlaufe das DataFrame und markiere ICE-Züge
for index, row in result.iterrows():
    station = str(row['station_name']) if row['station_name'] is not None else 'Unbekannt'
    if row['is_ice']:
        print(f"{BLUE_BG}{index:2d} | {station:30s} | {row['train_type']:5s} | {row['train_name']:10s} | ICE: {row['is_ice']} | Delay: {row['delay_in_min']:3.0f} min{RESET}")
    else:
        print(f"{index:2d} | {station:30s} | {row['train_type']:5s} | {row['train_name']:10s} | ICE: {row['is_ice']} | Delay: {row['delay_in_min']:3.0f} min")

















































