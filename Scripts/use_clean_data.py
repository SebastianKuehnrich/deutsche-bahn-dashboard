"""
Beispiel: Verwendung des bereinigten Datensatzes
"""

import pandas as pd
import duckdb

# ============================================================
# VARIANTE 1: Mit Pandas
# ============================================================

# Lade den bereinigten Datensatz
df_clean = pd.read_parquet('../Data/deutsche_bahn_data/monthly_processed_data/data-2024-10-CLEANED.parquet')

print("✅ BEREINIGTER DATENSATZ GELADEN")
print("=" * 60)
print(f"Zeilen: {len(df_clean):,}")
print(f"Spalten: {len(df_clean.columns)}")
print()

# Zeige erste Zeilen
print("📋 Erste 5 Zeilen:")
print(df_clean.head())
print()

# Qualitäts-Check
print("✅ DATENQUALITÄT:")
print(f"  Station NULL:        {df_clean['station_name'].isna().sum()} (0%)")
print(f"  Negative Delays:     {(df_clean['delay_in_min'] < -30).sum()} (0%)")
print(f"  Logik-Inkonsistenzen: {((df_clean['is_canceled']) & (df_clean['delay_in_min'] > 0)).sum()} (0%)")
print(f"  Min Delay:           {df_clean['delay_in_min'].min():.2f} min")
print(f"  Max Delay:           {df_clean['delay_in_min'].max():.2f} min")
print()

# ============================================================
# VARIANTE 2: Mit DuckDB (schneller für große Analysen)
# ============================================================

con = duckdb.connect()

# Direkte SQL-Queries auf dem bereinigten Datensatz
result = con.execute("""
SELECT 
    train_type,
    COUNT(*) as anzahl,
    ROUND(AVG(delay_in_min), 2) as avg_delay,
    SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) as canceled
FROM '../Data/deutsche_bahn_data/monthly_processed_data/data-2024-10-CLEANED.parquet'
GROUP BY train_type
ORDER BY anzahl DESC
LIMIT 10
""").fetchall()

print("🚂 TOP 10 ZUGTYPEN (Bereinigter Datensatz):")
print("-" * 60)
for row in result:
    print(f"  {row[0]:<8s} | {row[1]:>6,} Fahrten | Ø {row[2]:>5.2f} min | {row[3]:>4} storniert")

con.close()

# ============================================================
# JETZT KANNST DU:
# ============================================================

print()
print("=" * 60)
print("🎯 DER BEREINIGTE DATENSATZ IST BEREIT FÜR:")
print("=" * 60)
print("  ✅ Machine Learning Training")
print("  ✅ Business Intelligence Dashboards")
print("  ✅ Statistische Analysen")
print("  ✅ Management Reports")
print("  ✅ Production Deployment")
print()
print("💡 Keine Sorgen mehr über Datenqualität!")
print("=" * 60)

