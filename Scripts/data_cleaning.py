"""
============================================================
    BONUS 3: DATEN-BEREINIGUNG
    Deutsche Bahn Datenqualitäts-Probleme beheben
============================================================

Dieser Script behebt alle 6 identifizierten Datenqualitätsprobleme:
1. Fehlende Bahnhofsnamen
2. Negative Verspätungen
3. Extreme Verspätungen
4. Stornierte Züge mit Verspätung
5. Doppelte Ride IDs
6. Fehlende Zeitstempel

Ergebnis: Sauberer Datensatz ohne Qualitätsprobleme
"""

import pandas as pd
from datetime import datetime
import os

# ============================================================
# KONFIGURATION
# ============================================================

# Pfade
INPUT_PATH = '../Data/deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet'
OUTPUT_PATH = '../Data/deutsche_bahn_data/monthly_processed_data/data-2024-10-CLEANED.parquet'
LOG_PATH = '../Data/deutsche_bahn_data/monthly_processed_data/cleaning_log.txt'

# Bereinigungsregeln
RULES = {
    'max_negative_delay': -30,      # Akzeptiere max -30 min Frühankünfte
    'extreme_delay_threshold': 180, # > 180 min = wahrscheinlich storniert
    'min_realistic_delay': -1000,   # Unter -1000 min = definitiv Fehler
}

# ============================================================
# LOGGING
# ============================================================

class CleaningLogger:
    def __init__(self, log_path):
        self.log_path = log_path
        self.logs = []
        self.start_time = datetime.now()

    def log(self, category, message, count=None):
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {category}: {message}"
        if count is not None:
            log_entry += f" (Betroffene Zeilen: {count:,})"
        self.logs.append(log_entry)
        print(log_entry)

    def save(self):
        with open(self.log_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("DATENBEREINIGUNG - LOG\n")
            f.write(f"Datum: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            f.write("\n".join(self.logs))
            f.write("\n\n" + "=" * 80 + "\n")
            f.write(f"Abgeschlossen: {datetime.now().strftime('%H:%M:%S')}\n")
            f.write(f"Dauer: {(datetime.now() - self.start_time).total_seconds():.2f} Sekunden\n")

# ============================================================
# HAUPTPROGRAMM
# ============================================================

def main():
    logger = CleaningLogger(LOG_PATH)

    print("=" * 80)
    print("   DATENBEREINIGUNG - Deutsche Bahn")
    print("=" * 80)
    print()

    # Daten laden
    logger.log("INFO", "Lade Originaldaten...")
    df = pd.read_parquet(INPUT_PATH)
    original_count = len(df)
    logger.log("INFO", f"Originaldaten geladen: {original_count:,} Zeilen")

    # ============================================================
    # PROBLEM 1: FEHLENDE BAHNHOFSNAMEN
    # ============================================================

    logger.log("PROBLEM 1", "Behebe fehlende Bahnhofsnamen")

    missing_station = df['station_name'].isna().sum()
    logger.log("FOUND", "Fehlende station_name", missing_station)

    # Fix: Nutze xml_station_name als Fallback
    df['station_name'] = df['station_name'].fillna(df['xml_station_name'])

    # Prüfe Verbesserung
    still_missing = df['station_name'].isna().sum()
    fixed = missing_station - still_missing
    logger.log("FIXED", f"Gefüllt mit xml_station_name", fixed)

    if still_missing > 0:
        # Wenn immer noch NULLs: Markiere als "Unbekannt"
        df['station_name'] = df['station_name'].fillna("Unbekannt")
        logger.log("FIXED", "Rest als 'Unbekannt' markiert", still_missing)

    # ============================================================
    # PROBLEM 2: NEGATIVE VERSPÄTUNGEN (KRITISCH)
    # ============================================================

    logger.log("PROBLEM 2", "Behebe negative Verspätungen")

    # Kategorisiere negative Delays
    extreme_negative = (df['delay_in_min'] < RULES['min_realistic_delay']).sum()
    moderate_negative = ((df['delay_in_min'] < 0) &
                        (df['delay_in_min'] >= RULES['max_negative_delay'])).sum()
    acceptable_negative = ((df['delay_in_min'] < RULES['max_negative_delay']) &
                          (df['delay_in_min'] >= RULES['min_realistic_delay'])).sum()

    logger.log("FOUND", f"Extreme negative (< {RULES['min_realistic_delay']} min)", extreme_negative)
    logger.log("FOUND", f"Inakzeptabel negative (< {RULES['max_negative_delay']} min)", acceptable_negative)
    logger.log("FOUND", f"Akzeptabel negative (>= {RULES['max_negative_delay']} min)", moderate_negative)

    # Fix 1: Extreme Negative = Datenfehler → auf 0 setzen
    df.loc[df['delay_in_min'] < RULES['min_realistic_delay'], 'delay_in_min'] = 0
    logger.log("FIXED", f"Extreme negative auf 0 gesetzt", extreme_negative)

    # Fix 2: Inakzeptabel negative → auf maximal erlaubtes Negative (-30) setzen
    mask = (df['delay_in_min'] < RULES['max_negative_delay']) & (df['delay_in_min'] >= RULES['min_realistic_delay'])
    df.loc[mask, 'delay_in_min'] = RULES['max_negative_delay']
    logger.log("FIXED", f"Auf {RULES['max_negative_delay']} min begrenzt", acceptable_negative)

    # Moderate negative Werte bleiben (sind realistisch)

    # ============================================================
    # PROBLEM 3: EXTREME VERSPÄTUNGEN
    # ============================================================

    logger.log("PROBLEM 3", "Behebe extreme Verspätungen")

    extreme_delays = (df['delay_in_min'] > RULES['extreme_delay_threshold']).sum()
    logger.log("FOUND", f"Extreme Delays (> {RULES['extreme_delay_threshold']} min)", extreme_delays)

    # Fix: Züge mit extremer Verspätung als storniert markieren
    mask = df['delay_in_min'] > RULES['extreme_delay_threshold']
    df.loc[mask, 'is_canceled'] = True
    df.loc[mask, 'delay_in_min'] = 0  # Stornierte Züge haben keine Verspätung
    logger.log("FIXED", f"Als storniert markiert + Delay auf 0", extreme_delays)

    # ============================================================
    # PROBLEM 4: STORNIERTE ZÜGE MIT VERSPÄTUNG (LOGIK-FEHLER)
    # ============================================================

    logger.log("PROBLEM 4", "Behebe Logik-Inkonsistenzen")

    inconsistent = ((df['is_canceled'] == True) & (df['delay_in_min'] > 0)).sum()
    logger.log("FOUND", "Storniert + Verspätung", inconsistent)

    # Fix: Stornierte Züge können keine Verspätung haben → auf 0 setzen
    df.loc[df['is_canceled'] == True, 'delay_in_min'] = 0
    logger.log("FIXED", "Verspätung von stornierten Zügen auf 0 gesetzt", inconsistent)

    # ============================================================
    # PROBLEM 5: DOPPELTE RIDE IDs
    # ============================================================

    logger.log("PROBLEM 5", "Behebe doppelte Ride IDs")

    # Zähle Duplikate
    duplicates_before = df[df['train_line_ride_id'].notna()].duplicated(subset=['train_line_ride_id']).sum()
    logger.log("FOUND", "Duplikate bei train_line_ride_id", duplicates_before)

    # Fix: Behalte nur neueste Version pro ride_id (höchster Zeitstempel)
    # Sortiere nach time (neueste zuerst) und entferne Duplikate
    df_sorted = df.sort_values('time', ascending=False)
    df_dedup = df_sorted.drop_duplicates(subset=['train_line_ride_id'], keep='first')

    removed = len(df) - len(df_dedup)
    df = df_dedup.sort_index()  # Zurück zur ursprünglichen Reihenfolge

    logger.log("FIXED", "Ältere Duplikate entfernt (neueste behalten)", removed)

    # ============================================================
    # PROBLEM 6: FEHLENDE ZEITSTEMPEL
    # ============================================================

    logger.log("PROBLEM 6", "Analysiere fehlende Zeitstempel")

    missing_arr_planned = df['arrival_planned_time'].isna().sum()
    missing_dep_planned = df['departure_planned_time'].isna().sum()

    logger.log("FOUND", "Fehlende arrival_planned_time", missing_arr_planned)
    logger.log("FOUND", "Fehlende departure_planned_time", missing_dep_planned)

    # Analyse: Warum fehlen Zeitstempel?
    # Mögliche Gründe:
    # 1. Endhaltestelle (keine Abfahrt)
    # 2. Starthaltestelle (keine Ankunft)
    # 3. Durchfahrten ohne Halt

    # Erstelle Flags für bessere Datenqualität
    df['is_potential_final_station'] = (df['departure_planned_time'].isna()) & (df['arrival_planned_time'].notna())
    df['is_potential_start_station'] = (df['arrival_planned_time'].isna()) & (df['departure_planned_time'].notna())
    df['is_missing_both_times'] = (df['arrival_planned_time'].isna()) & (df['departure_planned_time'].isna())

    final_stations = df['is_potential_final_station'].sum()
    start_stations = df['is_potential_start_station'].sum()
    missing_both = df['is_missing_both_times'].sum()

    logger.log("INFO", f"Potenzielle Endhaltestellen: {final_stations:,}")
    logger.log("INFO", f"Potenzielle Starthaltestellen: {start_stations:,}")
    logger.log("INFO", f"Beide Zeiten fehlen: {missing_both:,}")
    logger.log("DECISION", "Flags hinzugefügt statt Deletion (Daten bleiben erhalten)")

    # ============================================================
    # ZUSÄTZLICHE BEREINIGUNGEN
    # ============================================================

    logger.log("BONUS", "Zusätzliche Qualitätsverbesserungen")

    # Entferne komplett leere Zeilen (falls vorhanden)
    empty_rows = df.isna().all(axis=1).sum()
    if empty_rows > 0:
        df = df.dropna(how='all')
        logger.log("FIXED", "Komplett leere Zeilen entfernt", empty_rows)

    # Trimme String-Spalten (entferne Leerzeichen)
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.strip() if df[col].notna().any() else df[col]
    logger.log("INFO", f"String-Spalten getrimmt: {len(string_columns)}")

    # ============================================================
    # DATEN-VALIDIERUNG
    # ============================================================

    logger.log("VALIDATION", "Validiere bereinigte Daten")

    # Check 1: Keine negativen Delays unter Schwellwert
    invalid_negative = (df['delay_in_min'] < RULES['max_negative_delay']).sum()
    logger.log("CHECK", f"Negative Delays < {RULES['max_negative_delay']}", invalid_negative)
    assert invalid_negative == 0, "Es gibt noch zu negative Delays!"

    # Check 2: Keine Inkonsistenzen
    inconsistent = ((df['is_canceled'] == True) & (df['delay_in_min'] > 0)).sum()
    logger.log("CHECK", "Storniert + Verspätung", inconsistent)
    assert inconsistent == 0, "Es gibt noch Logik-Inkonsistenzen!"

    # Check 3: Keine extremen Delays ohne Stornierung
    extreme_not_canceled = ((df['delay_in_min'] > RULES['extreme_delay_threshold']) &
                           (df['is_canceled'] == False)).sum()
    logger.log("CHECK", f"Extreme Delays ohne Stornierung", extreme_not_canceled)
    assert extreme_not_canceled == 0, "Es gibt noch extreme Delays ohne Stornierung!"

    # Check 4: Keine NULLs in station_name
    null_stations = df['station_name'].isna().sum()
    logger.log("CHECK", "NULL station_name", null_stations)
    assert null_stations == 0, "Es gibt noch fehlende Bahnhofsnamen!"

    logger.log("SUCCESS", "✅ Alle Validierungen bestanden!")

    # ============================================================
    # STATISTIKEN
    # ============================================================

    print("\n" + "=" * 80)
    print("📊 VORHER/NACHHER STATISTIKEN")
    print("=" * 80)

    final_count = len(df)
    removed_total = original_count - final_count

    print(f"\n📈 Datensatz-Größe:")
    print(f"   Vorher:      {original_count:>10,} Zeilen")
    print(f"   Nachher:     {final_count:>10,} Zeilen")
    print(f"   Entfernt:    {removed_total:>10,} Zeilen ({removed_total/original_count*100:.2f}%)")

    # Delay Statistiken
    print(f"\n⏰ Verspätungs-Statistiken:")
    print(f"   Min Delay:   {df['delay_in_min'].min():>10.2f} min")
    print(f"   Max Delay:   {df['delay_in_min'].max():>10.2f} min")
    print(f"   Avg Delay:   {df['delay_in_min'].mean():>10.2f} min")
    print(f"   Std Dev:     {df['delay_in_min'].std():>10.2f} min")

    # Cancellation Rate
    cancel_rate = (df['is_canceled'].sum() / len(df)) * 100
    print(f"\n❌ Stornierungen:")
    print(f"   Storniert:   {df['is_canceled'].sum():>10,} ({cancel_rate:.2f}%)")

    # Data Quality Score
    print(f"\n✅ Datenqualität:")
    print(f"   Vollständigkeit (station_name):  100.00%")
    print(f"   Logik-Konsistenz:                 100.00%")
    print(f"   Wertebereich (delay):             100.00%")
    print(f"   Duplikate entfernt:               Ja")

    # ============================================================
    # EXPORT
    # ============================================================

    print("\n" + "=" * 80)
    logger.log("EXPORT", "Speichere bereinigte Daten...")

    # Entferne temporäre Flag-Spalten (optional)
    flags_to_remove = ['is_potential_final_station', 'is_potential_start_station', 'is_missing_both_times']
    # Kommentar: Wir behalten die Flags für bessere Transparenz
    # df = df.drop(columns=flags_to_remove)

    # Exportiere als Parquet
    df.to_parquet(OUTPUT_PATH, index=False, compression='snappy')

    file_size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
    logger.log("SUCCESS", f"Datei gespeichert: {OUTPUT_PATH}")
    logger.log("INFO", f"Dateigröße: {file_size_mb:.1f} MB")

    # Speichere Log
    logger.save()
    logger.log("SUCCESS", f"Log gespeichert: {LOG_PATH}")

    print("\n" + "=" * 80)
    print("✅ DATENBEREINIGUNG ERFOLGREICH ABGESCHLOSSEN!")
    print("=" * 80)
    print(f"\n📁 Bereinigte Datei: {OUTPUT_PATH}")
    print(f"📄 Log-Datei:        {LOG_PATH}")
    print()
    print("💡 Die bereinigte Datei kann jetzt für Analysen verwendet werden!")
    print()

    # ============================================================
    # VERGLEICHS-BERICHT
    # ============================================================

    print("=" * 80)
    print("📋 ZUSAMMENFASSUNG DER BEHOBENEN PROBLEME")
    print("=" * 80)
    print()
    print("✅ Problem 1: Fehlende Bahnhofsnamen → Mit xml_station_name gefüllt")
    print("✅ Problem 2: Negative Verspätungen → Auf realistische Werte begrenzt")
    print("✅ Problem 3: Extreme Verspätungen  → Als storniert markiert")
    print("✅ Problem 4: Logik-Inkonsistenzen  → Stornierte haben delay=0")
    print("✅ Problem 5: Doppelte Ride IDs     → Duplikate entfernt (neueste behalten)")
    print("✅ Problem 6: Fehlende Zeitstempel  → Flags hinzugefügt für Analyse")
    print()
    print("🎯 Ergebnis: Sauberer Datensatz bereit für Production!")
    print("=" * 80)

# ============================================================
# AUSFÜHRUNG
# ============================================================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ FEHLER: {e}")
        print("\n💡 Stelle sicher dass:")
        print("   - Die Originaldaten existieren")
        print("   - Du Schreibrechte für das Output-Verzeichnis hast")
        print("   - Pandas, DuckDB installiert sind")
        raise

