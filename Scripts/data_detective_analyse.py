"""
============================================================
    DATA DETECTIVE: DEUTSCHE BAHN DATENQUALITÄT
    Systematische Analyse von 2 Millionen Zugfahrten
============================================================

Analyst: Sebastian
Datum: 8. Dezember 2025
Datensatz: Deutsche Bahn API - Oktober 2024
Zeilen: ~2 Millionen
"""

import pandas as pd
import duckdb
from datetime import datetime

# DuckDB Connection
con = duckdb.connect(':memory:')

# Dateipfad
DATA_PATH = '../Data/deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet'

print("=" * 80)
print("   DATA DETECTIVE: DEUTSCHE BAHN")
print("   Datenqualitäts-Analyse")
print("=" * 80)
print()

# ============================================================
# TEIL 1: EXPLORATION & ERSTE CHECKS
# ============================================================

print("📊 TEIL 1: DATEN-ÜBERSICHT")
print("-" * 80)

# Laden mit Pandas für erste Exploration
df = pd.read_parquet(DATA_PATH)

print(f"\n✅ Datensatz geladen:")
print(f"   Zeilen: {len(df):,}")
print(f"   Spalten: {len(df.columns)}")
print(f"\n📋 Spalten: {', '.join(df.columns.tolist())}")

# Aufgabe 1.1: Daten-Übersicht mit DuckDB
print("\n" + "=" * 80)
print("📊 DETAILLIERTE ÜBERSICHT")
print("-" * 80)

result = con.execute(f"""
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT station_name) as unique_stations,
    COUNT(DISTINCT train_name) as unique_trains,
    MIN(time) as first_timestamp,
    MAX(time) as last_timestamp,
    COUNT(DISTINCT train_type) as train_types
FROM '{DATA_PATH}'
""").fetchone()

print(f"\n📈 Statistiken:")
print(f"   Zeilen gesamt:      {result[0]:,}")
print(f"   Unique Bahnhöfe:    {result[1]:,}")
print(f"   Unique Züge:        {result[2]:,}")
print(f"   Zeitraum:           {result[3]} bis {result[4]}")
print(f"   Zugtypen:           {result[5]}")

# ============================================================
# TEIL 2: DATENQUALITÄTS-CHECKS (5 DIMENSIONEN)
# ============================================================

print("\n" + "=" * 80)
print("🔍 TEIL 2: DATA QUALITY CHECKS")
print("=" * 80)

# ============================================================
# 2.1 COMPLETENESS (Vollständigkeit)
# ============================================================

print("\n" + "-" * 80)
print("📝 2.1 COMPLETENESS - Missing Values Analysis")
print("-" * 80)

missing_check = con.execute(f"""
SELECT
    COUNT(*) as total,
    COUNT(*) - COUNT(station_name) as missing_station,
    COUNT(*) - COUNT(xml_station_name) as missing_xml_station,
    COUNT(*) - COUNT(arrival_planned_time) as missing_arr_planned,
    COUNT(*) - COUNT(arrival_change_time) as missing_arr_change,
    COUNT(*) - COUNT(departure_planned_time) as missing_dep_planned,
    COUNT(*) - COUNT(departure_change_time) as missing_dep_change,
    COUNT(*) - COUNT(train_line_ride_id) as missing_ride_id,
    COUNT(*) - COUNT(final_destination_station) as missing_destination
FROM '{DATA_PATH}'
""").fetchone()

total = missing_check[0]

print(f"\n🔎 Missing Values pro Spalte:")
print(f"   station_name:                {missing_check[1]:>10,} ({missing_check[1]/total*100:>6.2f}%)")
print(f"   xml_station_name:            {missing_check[2]:>10,} ({missing_check[2]/total*100:>6.2f}%)")
print(f"   arrival_planned_time:        {missing_check[3]:>10,} ({missing_check[3]/total*100:>6.2f}%)")
print(f"   arrival_change_time:         {missing_check[4]:>10,} ({missing_check[4]/total*100:>6.2f}%)")
print(f"   departure_planned_time:      {missing_check[5]:>10,} ({missing_check[5]/total*100:>6.2f}%)")
print(f"   departure_change_time:       {missing_check[6]:>10,} ({missing_check[6]/total*100:>6.2f}%)")
print(f"   train_line_ride_id:          {missing_check[7]:>10,} ({missing_check[7]/total*100:>6.2f}%)")
print(f"   final_destination_station:   {missing_check[8]:>10,} ({missing_check[8]/total*100:>6.2f}%)")

# ============================================================
# 2.2 VALIDITY (Gültigkeit)
# ============================================================

print("\n" + "-" * 80)
print("✅ 2.2 VALIDITY - Range & Value Checks")
print("-" * 80)

# Check: Delays
delay_stats = con.execute(f"""
SELECT
    MIN(delay_in_min) as min_delay,
    MAX(delay_in_min) as max_delay,
    AVG(delay_in_min) as avg_delay,
    STDDEV(delay_in_min) as std_delay,
    COUNT(CASE WHEN delay_in_min < 0 THEN 1 END) as negative_delays,
    COUNT(CASE WHEN delay_in_min > 120 THEN 1 END) as extreme_delays,
    COUNT(CASE WHEN delay_in_min > 300 THEN 1 END) as ultra_extreme_delays
FROM '{DATA_PATH}'
""").fetchone()

print(f"\n🚂 Delay Analysis:")
print(f"   Min Delay:              {delay_stats[0]:>10.2f} Minuten")
print(f"   Max Delay:              {delay_stats[1]:>10.2f} Minuten ⚠️")
print(f"   Avg Delay:              {delay_stats[2]:>10.2f} Minuten")
print(f"   Std Dev:                {delay_stats[3]:>10.2f} Minuten")
print(f"   Negative Delays:        {delay_stats[4]:>10,} ({delay_stats[4]/total*100:>6.2f}%) ❌")
print(f"   Extreme (>120 min):     {delay_stats[5]:>10,} ({delay_stats[5]/total*100:>6.2f}%) ⚠️")
print(f"   Ultra Extreme (>300):   {delay_stats[6]:>10,} ({delay_stats[6]/total*100:>6.2f}%) ⚠️")

# Check: Cancellations
cancellation_stats = con.execute(f"""
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) as canceled,
    ROUND(SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as canceled_pct
FROM '{DATA_PATH}'
""").fetchone()

print(f"\n❌ Cancellation Analysis:")
print(f"   Total Rows:             {cancellation_stats[0]:>10,}")
print(f"   Canceled Trains:        {cancellation_stats[1]:>10,} ({cancellation_stats[2]:>6.2f}%)")

# ============================================================
# 2.3 CONSISTENCY (Konsistenz)
# ============================================================

print("\n" + "-" * 80)
print("🔄 2.3 CONSISTENCY - Logic & Format Checks")
print("-" * 80)

# Check: Canceled trains with delays
inconsistent_canceled = con.execute(f"""
SELECT COUNT(*) as inconsistent_count
FROM '{DATA_PATH}'
WHERE is_canceled = True AND delay_in_min > 0
""").fetchone()

print(f"\n🤔 Logic Inconsistency Check:")
print(f"   Canceled trains WITH delays: {inconsistent_canceled[0]:>10,} ❌")
print(f"   (Diese Züge sind storniert aber haben trotzdem Verspätung)")

# Check: Time Paradoxes
time_paradox = con.execute(f"""
SELECT COUNT(*) as paradox_count
FROM '{DATA_PATH}'
WHERE arrival_planned_time IS NOT NULL 
  AND departure_planned_time IS NOT NULL
  AND arrival_planned_time < departure_planned_time
""").fetchone()

print(f"\n⏰ Time Consistency Check:")
print(f"   Arrival before Departure:    {time_paradox[0]:>10,}")
print(f"   (Züge wo Ankunft VOR Abfahrt ist)")

# Check: Station Name Encoding Issues
encoding_check = con.execute(f"""
SELECT COUNT(DISTINCT station_name) as names_with_issues
FROM '{DATA_PATH}'
WHERE station_name LIKE '%ü%' 
   OR station_name LIKE '%ö%'
   OR station_name LIKE '%ä%'
   OR station_name LIKE '%ß%'
""").fetchone()

print(f"\n🔤 Encoding Check:")
print(f"   Stations mit Umlauten:       {encoding_check[0]:>10,}")

# ============================================================
# 2.4 ACCURACY (Genauigkeit)
# ============================================================

print("\n" + "-" * 80)
print("🎯 2.4 ACCURACY - Outlier Detection")
print("-" * 80)

# Top 10 extreme delays
print(f"\n🚨 Top 10 Extreme Delays:")
extreme_delays = con.execute(f"""
SELECT
    station_name,
    train_name,
    delay_in_min,
    is_canceled,
    time
FROM '{DATA_PATH}'
WHERE delay_in_min > 300
ORDER BY delay_in_min DESC
LIMIT 10
""").fetchall()

for i, row in enumerate(extreme_delays, 1):
    station = row[0] if row[0] else "N/A"
    train = row[1] if row[1] else "N/A"
    print(f"   {i:2d}. {train:15s} | {station:25s} | {row[2]:>6.0f} min | Canceled: {row[3]}")

# Statistical Outlier Detection (IQR Method)
outlier_stats = con.execute(f"""
WITH stats AS (
    SELECT
        percentile_cont(0.25) WITHIN GROUP (ORDER BY delay_in_min) as q1,
        percentile_cont(0.75) WITHIN GROUP (ORDER BY delay_in_min) as q3
    FROM '{DATA_PATH}'
)
SELECT
    q1,
    q3,
    q3 - q1 as iqr,
    q1 - 1.5 * (q3 - q1) as lower_bound,
    q3 + 1.5 * (q3 - q1) as upper_bound,
    (SELECT COUNT(*) FROM '{DATA_PATH}' 
     WHERE delay_in_min < (SELECT q1 - 1.5 * (q3 - q1) FROM stats)
        OR delay_in_min > (SELECT q3 + 1.5 * (q3 - q1) FROM stats)) as outliers
FROM stats
""").fetchone()

print(f"\n📊 Statistical Outlier Analysis (IQR Method):")
print(f"   Q1 (25%):                    {outlier_stats[0]:>10.2f}")
print(f"   Q3 (75%):                    {outlier_stats[1]:>10.2f}")
print(f"   IQR:                         {outlier_stats[2]:>10.2f}")
print(f"   Lower Bound:                 {outlier_stats[3]:>10.2f}")
print(f"   Upper Bound:                 {outlier_stats[4]:>10.2f}")
print(f"   Outliers detected:           {outlier_stats[5]:>10,} ({outlier_stats[5]/total*100:>6.2f}%)")

# ============================================================
# 2.5 UNIQUENESS (Eindeutigkeit)
# ============================================================

print("\n" + "-" * 80)
print("🔑 2.5 UNIQUENESS - Duplicate Detection")
print("-" * 80)

# Check: ID Uniqueness
id_uniqueness = con.execute(f"""
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT id) as unique_ids,
    COUNT(*) - COUNT(DISTINCT id) as duplicate_ids
FROM '{DATA_PATH}'
""").fetchone()

print(f"\n🆔 ID Uniqueness Check:")
print(f"   Total Rows:                  {id_uniqueness[0]:>10,}")
print(f"   Unique IDs:                  {id_uniqueness[1]:>10,}")
print(f"   Duplicate IDs:               {id_uniqueness[2]:>10,}")

# Check: Ride ID Duplicates
ride_id_dups = con.execute(f"""
SELECT COUNT(*) as duplicate_groups
FROM (
    SELECT train_line_ride_id, COUNT(*) as cnt
    FROM '{DATA_PATH}'
    WHERE train_line_ride_id IS NOT NULL
    GROUP BY train_line_ride_id
    HAVING COUNT(*) > 1
)
""").fetchone()

print(f"\n🚆 Train Line Ride ID Check:")
print(f"   Duplicate ride_id groups:    {ride_id_dups[0]:>10,}")

# Check: Exact Duplicates
exact_dups = con.execute(f"""
SELECT COUNT(*) as duplicate_groups
FROM (
    SELECT station_name, time, train_name, delay_in_min, COUNT(*) as cnt
    FROM '{DATA_PATH}'
    GROUP BY station_name, time, train_name, delay_in_min
    HAVING COUNT(*) > 1
)
""").fetchone()

print(f"\n📋 Exact Duplicate Records:")
print(f"   Duplicate groups found:      {exact_dups[0]:>10,}")

# ============================================================
# TEIL 3: VERTEILUNGS-ANALYSEN
# ============================================================

print("\n" + "=" * 80)
print("📈 TEIL 3: VERTEILUNGS-ANALYSEN")
print("=" * 80)

# 3.1 Bahnhofs-Verteilung
print("\n" + "-" * 80)
print("🚉 Top 15 Bahnhöfe nach Anzahl Einträge:")
print("-" * 80)

station_dist = con.execute(f"""
SELECT
    station_name,
    COUNT(*) as anzahl_eintraege,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM '{DATA_PATH}'), 2) as prozent,
    ROUND(AVG(delay_in_min), 2) as avg_delay
FROM '{DATA_PATH}'
WHERE station_name IS NOT NULL
GROUP BY station_name
ORDER BY anzahl_eintraege DESC
LIMIT 15
""").fetchall()

print(f"\n{'Bahnhof':<30s} | {'Einträge':>10s} | {'Prozent':>8s} | {'Avg Delay':>10s}")
print("-" * 70)
for row in station_dist:
    print(f"{row[0]:<30s} | {row[1]:>10,} | {row[2]:>7.2f}% | {row[3]:>10.2f}")

# 3.2 Zugtyp-Verteilung
print("\n" + "-" * 80)
print("🚂 Zugtyp-Verteilung:")
print("-" * 80)

train_type_dist = con.execute(f"""
SELECT
    train_type,
    COUNT(*) as anzahl,
    ROUND(AVG(delay_in_min), 2) as avg_delay,
    SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) as canceled_count,
    ROUND(SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as cancel_rate
FROM '{DATA_PATH}'
WHERE train_type IS NOT NULL
GROUP BY train_type
ORDER BY anzahl DESC
LIMIT 15
""").fetchall()

print(f"\n{'Zugtyp':<10s} | {'Anzahl':>10s} | {'Avg Delay':>10s} | {'Canceled':>10s} | {'Cancel %':>8s}")
print("-" * 70)
for row in train_type_dist:
    print(f"{row[0]:<10s} | {row[1]:>10,} | {row[2]:>10.2f} | {row[3]:>10,} | {row[4]:>7.2f}%")

# 3.3 Zeitliche Verteilung (Wochentag)
print("\n" + "-" * 80)
print("📅 Verteilung nach Wochentag:")
print("-" * 80)

weekday_dist = con.execute(f"""
SELECT
    CASE strftime(time, '%w')
        WHEN '0' THEN '7_Sonntag'
        WHEN '1' THEN '1_Montag'
        WHEN '2' THEN '2_Dienstag'
        WHEN '3' THEN '3_Mittwoch'
        WHEN '4' THEN '4_Donnerstag'
        WHEN '5' THEN '5_Freitag'
        WHEN '6' THEN '6_Samstag'
    END as wochentag,
    COUNT(*) as anzahl_fahrten,
    ROUND(AVG(delay_in_min), 2) as avg_delay,
    SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) as canceled
FROM '{DATA_PATH}'
GROUP BY strftime(time, '%w')
ORDER BY wochentag
""").fetchall()

print(f"\n{'Wochentag':<15s} | {'Fahrten':>10s} | {'Avg Delay':>10s} | {'Canceled':>10s}")
print("-" * 60)
for row in weekday_dist:
    day_name = row[0][2:]  # Remove sorting prefix
    print(f"{day_name:<15s} | {row[1]:>10,} | {row[2]:>10.2f} | {row[3]:>10,}")

# ============================================================
# ZUSAMMENFASSUNG & KRITISCHE PROBLEME
# ============================================================

print("\n" + "=" * 80)
print("🚨 ZUSAMMENFASSUNG: KRITISCHE DATENQUALITÄTS-PROBLEME")
print("=" * 80)

problems = []

# Problem 1: Missing Station Names
if missing_check[1] > 0:
    problems.append({
        'id': 1,
        'name': 'Fehlende Bahnhofsnamen',
        'category': 'COMPLETENESS',
        'affected': missing_check[1],
        'percent': missing_check[1]/total*100,
        'severity': 'HOCH'
    })

# Problem 2: Negative Delays
if delay_stats[4] > 0:
    problems.append({
        'id': 2,
        'name': 'Negative Verspätungen',
        'category': 'VALIDITY',
        'affected': delay_stats[4],
        'percent': delay_stats[4]/total*100,
        'severity': 'KRITISCH'
    })

# Problem 3: Extreme Delays
if delay_stats[5] > 0:
    problems.append({
        'id': 3,
        'name': 'Extreme Verspätungen (>120 min)',
        'category': 'ACCURACY',
        'affected': delay_stats[5],
        'percent': delay_stats[5]/total*100,
        'severity': 'MITTEL'
    })

# Problem 4: Canceled with Delay
if inconsistent_canceled[0] > 0:
    problems.append({
        'id': 4,
        'name': 'Stornierte Züge mit Verspätung',
        'category': 'CONSISTENCY',
        'affected': inconsistent_canceled[0],
        'percent': inconsistent_canceled[0]/total*100,
        'severity': 'HOCH'
    })

# Problem 5: Duplicate Ride IDs
if ride_id_dups[0] > 0:
    problems.append({
        'id': 5,
        'name': 'Doppelte Ride IDs',
        'category': 'UNIQUENESS',
        'affected': ride_id_dups[0],
        'percent': 0,  # Groups, not rows
        'severity': 'MITTEL'
    })

# Problem 6: Missing Arrival/Departure Times
missing_times_total = missing_check[3] + missing_check[5]
if missing_times_total > 0:
    problems.append({
        'id': 6,
        'name': 'Fehlende Zeitstempel',
        'category': 'COMPLETENESS',
        'affected': missing_times_total,
        'percent': missing_times_total/total*100,
        'severity': 'HOCH'
    })

# Print all problems
print()
for problem in problems:
    print(f"❌ PROBLEM {problem['id']}: {problem['name']}")
    print(f"   Kategorie:        {problem['category']}")
    print(f"   Betroffene Zeilen: {problem['affected']:,}")
    if problem['percent'] > 0:
        print(f"   Prozent:          {problem['percent']:.2f}%")
    print(f"   Schweregrad:      {problem['severity']}")
    print()

print("=" * 80)
print("📝 EMPFEHLUNGEN:")
print("=" * 80)
print()
print("1. SOFORT:")
print("   - Negative Verspätungen korrigieren (wahrscheinlich Datenfehler)")
print("   - Logik-Inkonsistenzen beheben (storniert + Verspätung)")
print()
print("2. KURZFRISTIG:")
print("   - Fehlende Bahnhofsnamen aus anderen Quellen ergänzen")
print("   - Extreme Verspätungen validieren (>120 min)")
print("   - Duplicate Ride IDs bereinigen")
print()
print("3. LANGFRISTIG:")
print("   - Validierung an der Datenquelle implementieren")
print("   - Monitoring für Datenqualität einrichten")
print("   - Automatische Qualitätschecks bei Daten-Import")
print()
print("=" * 80)
print("✅ ANALYSE ABGESCHLOSSEN")
print("=" * 80)
print(f"\nGeprüfte Datensätze: {total:,}")
print(f"Gefundene Probleme:  {len(problems)}")
print(f"Analysedauer:        {datetime.now().strftime('%H:%M:%S')}")
print()
print("📊 Bericht kann für Stakeholder verwendet werden!")
print("=" * 80)

# Verbindung schließen
con.close()

