# 🔍 Data Detective: Deutsche Bahn Datenqualitäts-Analyse

**Modul 3: Big-Data Analyst Experte**
**Morphos GmbH - Weiterbildung KI und Data-Analyst**

---

## 🎯 Deine Mission

Du bist Data Quality Analyst bei der Deutschen Bahn AG.

Die IT-Abteilung hat dir einen Datensatz mit fast 2 Millionen Zugfahrten aus Oktober 2024 gegeben. Dieser Datensatz wird benutzt für:
- Pünktlichkeits-Reports an die Presse
- Interne Performance-Analysen
- Vorhersage-Modelle für Verspätungen

**ABER:** Niemand hat die Datenqualität geprüft.

**Deine Aufgabe:** Finde ALLE Datenqualitäts-Probleme, dokumentiere sie mit Zahlen, und schlage Lösungen vor.

**Am Ende hast du:**
- Mindestens 5 Datenqualitäts-Probleme identifiziert
- Jedes Problem mit konkreten Zahlen belegt
- Für jedes Problem eine Fix-Strategie vorgeschlagen
- Eine professionelle Dokumentation erstellt

**Warum ist das wichtig?**
- 80% der Data Science Arbeit ist Data Quality und Cleaning
- Schlechte Daten = schlechte Analysen = schlechte Business-Entscheidungen
- Deutsche Bahn verliert Millionen durch fehlerhafte Daten-Analysen

**Das ist genau das, was du im echten Job machst!**

---

## 📊 Der Datensatz

**Quelle:** Deutsche Bahn API (via HuggingFace)
**Zeitraum:** Oktober 2024
**Zeilen:** 1,984,484 (~2 Millionen)
**Format:** Parquet (optimiert für große Datenmengen)
**Größe:** 72 MB

### Spalten im Datensatz

| Spalte | Typ | Bedeutung |
|--------|-----|-----------|
| `station_name` | string | Name des Bahnhofs |
| `xml_station_name` | string | XML-Version des Namens |
| `eva` | string | EVA-Nummer (Bahnhofs-ID) |
| `train_name` | string | Zugbezeichnung (z.B. "ICE 123") |
| `final_destination_station` | string | Endziel des Zuges |
| `delay_in_min` | int | Verspätung in Minuten |
| `time` | datetime | Zeitstempel |
| `is_canceled` | boolean | Wurde Zug abgesagt? |
| `train_type` | string | Zugtyp (ICE, IC, RE, etc.) |
| `train_line_ride_id` | string | Eindeutige Fahrt-ID |
| `train_line_station_num` | int | Station Nummer auf Route |
| `arrival_planned_time` | datetime | Geplante Ankunft |
| `arrival_change_time` | datetime | Tatsächliche Ankunft |
| `departure_planned_time` | datetime | Geplante Abfahrt |
| `departure_change_time` | datetime | Tatsächliche Abfahrt |
| `id` | string | Eindeutige Datensatz-ID |

---

## 🛠️ Vorbereitung

### Schritt 1: Daten herunterladen

Falls noch nicht geschehen, erstelle: `download_data.py`

```python
# download_data.py
from huggingface_hub import hf_hub_download

print("Lade Deutsche Bahn Daten...")

file = hf_hub_download(
    repo_id='piebro/deutsche-bahn-data',
    filename='monthly_processed_data/data-2024-10.parquet',
    repo_type='dataset',
    local_dir='./deutsche_bahn_data'
)

print(f"✓ Download erfolgreich: {file}")
```

**Ausführen:**
```bash
python download_data.py
```

### Schritt 2: Neue Projekt-Datei erstellen

Erstelle: `data_detective_analyse.py`

### Schritt 3: Basis-Setup kopieren

```python
# ============================================================
#
#   DATA DETECTIVE: DEUTSCHE BAHN DATENQUALITÄT
#   Deine Aufgabe: Finde ALLE Probleme in den Daten
#
# ============================================================

import pandas as pd
import duckdb

# DuckDB Connection
con = duckdb.connect()

# Dateipfad
DATA_PATH = './deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet'

print("=" * 60)
print("   DATA DETECTIVE: DEUTSCHE BAHN")
print("   Datenqualitäts-Analyse")
print("=" * 60)

# Quick Check: Daten laden mit Pandas (für erste Exploration)
df = pd.read_parquet(DATA_PATH)

print(f"\nDatensatz geladen:")
print(f"  Zeilen: {len(df):,}")
print(f"  Spalten: {len(df.columns)}")
print(f"\nSpalten: {df.columns.tolist()}")
```

**Teste dass es funktioniert!**

---

## 📋 Deine Deliverables

Erstelle ein Dokument (Text-Datei, Markdown, oder Notebook) mit folgendem Format:

```
DEUTSCHE BAHN DATENQUALITÄTS-BERICHT
Analyst: [Dein Name]
Datum: 8. Dezember 2025

===================================================================
PROBLEM 1: [Name des Problems]
===================================================================

KATEGORIE: [Completeness/Validity/Consistency/Accuracy/Uniqueness]

BESCHREIBUNG:
[Was ist das Problem? Erkläre es in 2-3 Sätzen]

BETROFFENE DATEN:
- Spalte: [Spaltenname]
- Anzahl Zeilen betroffen: [Zahl] ([Prozent]% der Daten)
- Schweregrad: [Kritisch/Hoch/Mittel/Niedrig]

BEWEIS (SQL/Code):
[Die Query die das Problem zeigt]

AUSWIRKUNG:
[Was passiert wenn wir das nicht fixen?]

FIX-STRATEGIE:
[Wie würdest du das Problem lösen?]

===================================================================
PROBLEM 2: ...
===================================================================
```

**Mindestens 5 Probleme dokumentieren!**

---

## 🔍 Teil 1: Exploration & Erste Checks

### Aufgabe 1.1: Daten-Übersicht

Erstelle Queries die zeigen:

1. Wie viele Zeilen insgesamt?
2. Wie viele einzigartige Bahnhöfe?
3. Wie viele einzigartige Züge?
4. Zeitraum der Daten (erstes und letztes Datum)?
5. Wie viele verschiedene Zugtypen?

**Beispiel-Code:**

```python
# Übersicht mit DuckDB
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

print("\n📊 DATEN-ÜBERSICHT:")
print(f"  Zeilen gesamt: {result[0]:,}")
print(f"  Unique Bahnhöfe: {result[1]:,}")
print(f"  Unique Züge: {result[2]:,}")
print(f"  Zeitraum: {result[3]} bis {result[4]}")
print(f"  Zugtypen: {result[5]}")
```

---

## 🕵️ Teil 2: Datenqualitäts-Checks

Jetzt wird detektiviert! Gehe durch **alle 5 Kategorien**:

### 2.1 COMPLETENESS (Vollständigkeit)

**Frage dich:**
- Gibt es fehlende Werte (NULL)?
- In welchen Spalten?
- Wie viele?

**Hilfreiches SQL:**

```sql
-- Missing Values pro Spalte
SELECT
    COUNT(*) as total,
    COUNT(*) - COUNT(station_name) as missing_station,
    COUNT(*) - COUNT(arrival_planned_time) as missing_arr_planned,
    COUNT(*) - COUNT(arrival_change_time) as missing_arr_change,
    COUNT(*) - COUNT(departure_planned_time) as missing_dep_planned,
    COUNT(*) - COUNT(departure_change_time) as missing_dep_change,
    COUNT(*) - COUNT(train_line_ride_id) as missing_ride_id
FROM 'dein_pfad.parquet'
```

**Fragen die du beantworten solltest:**
- Welche Spalte hat die meisten NULLs?
- Macht das Sinn? (Manchmal sind NULLs okay!)
- Wie kritisch ist das?

### 2.2 VALIDITY (Gültigkeit)

**Frage dich:**
- Gibt es unmögliche Werte?
- Negative Werte wo sie nicht sein sollten?
- Werte außerhalb des gültigen Bereichs?

**Check: Delays**

```sql
-- Verspätungs-Statistiken
SELECT
    MIN(delay_in_min) as min_delay,
    MAX(delay_in_min) as max_delay,
    AVG(delay_in_min) as avg_delay,
    COUNT(CASE WHEN delay_in_min < 0 THEN 1 END) as negative_delays,
    COUNT(CASE WHEN delay_in_min > 120 THEN 1 END) as extreme_delays
FROM 'dein_pfad.parquet'
```

**Fragen:**
- Kann ein Zug negative Verspätung haben?
- Wenn ja, wie viel ist realistisch?
- Ist eine Verspätung von 800+ Minuten möglich?
- Was bedeutet das für die Datenqualität?

**Check: Cancellations**

```sql
-- Wie viele Züge sind ausgefallen?
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) as canceled,
    ROUND(SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as canceled_pct
FROM 'dein_pfad.parquet'
```

**Frage:**
- Ist die Ausfallrate realistisch?
- Gibt es Züge die `is_canceled = True` haben aber trotzdem `delay_in_min` > 0?
- Ist das ein Logik-Fehler?

### 2.3 CONSISTENCY (Konsistenz)

**Frage dich:**
- Sind die Daten konsistent formatiert?
- Gibt es Encoding-Probleme?
- Gibt es Widersprüche in den Daten?

**Check: Encoding**

```sql
-- Suche nach Encoding-Problemen
SELECT DISTINCT station_name
FROM 'dein_pfad.parquet'
WHERE station_name LIKE '%�%'  -- Zeichen die nicht richtig encodiert sind
LIMIT 10
```

**Check: Logik-Konsistenz**

```sql
-- Züge die canceled sind aber trotzdem Verspätung haben
SELECT
    station_name,
    train_name,
    is_canceled,
    delay_in_min
FROM 'dein_pfad.parquet'
WHERE is_canceled = True AND delay_in_min > 0
LIMIT 10
```

**Fragen:**
- Macht es Sinn dass ein ausgefallener Zug Verspätung hat?
- Ist das ein Daten-Fehler oder ein Logik-Problem?

### 2.4 ACCURACY (Genauigkeit)

**Frage dich:**
- Gibt es Outliers?
- Sind die Werte realistisch?
- Gibt es statistische Anomalien?

**Check: Extreme Verspätungen**

```sql
-- Top 10 extremste Verspätungen
SELECT
    station_name,
    train_name,
    delay_in_min,
    is_canceled,
    time
FROM 'dein_pfad.parquet'
WHERE delay_in_min > 300  -- Mehr als 5 Stunden
ORDER BY delay_in_min DESC
LIMIT 10
```

**Fragen:**
- Sind Verspätungen von 800+ Minuten (13+ Stunden) realistisch?
- Sollten diese Züge nicht als `is_canceled` markiert sein?
- Wie viele solcher Extremfälle gibt es?

**Check: Zeitliche Anomalien**

```sql
-- Gibt es Züge wo Ankunft vor Abfahrt ist?
SELECT
    COUNT(*) as time_paradox
FROM 'dein_pfad.parquet'
WHERE arrival_planned_time < departure_planned_time
```

### 2.5 UNIQUENESS (Eindeutigkeit)

**Frage dich:**
- Gibt es Duplikate?
- Sind IDs wirklich einzigartig?

**Check: ID Uniqueness**

```sql
-- Sind IDs einzigartig?
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT id) as unique_ids,
    COUNT(*) - COUNT(DISTINCT id) as duplicates
FROM 'dein_pfad.parquet'
```

**Check: Ride ID Uniqueness**

```sql
-- Sind train_line_ride_id einzigartig pro Fahrt?
SELECT
    train_line_ride_id,
    COUNT(*) as anzahl
FROM 'dein_pfad.parquet'
WHERE train_line_ride_id IS NOT NULL
GROUP BY train_line_ride_id
HAVING COUNT(*) > 1
LIMIT 10
```

---

## 📊 Teil 3: Verteilungs-Analysen

Manchmal sind Probleme in der Verteilung versteckt.

### Aufgabe 3.1: Bahnhofs-Verteilung

```sql
-- Welche Bahnhöfe haben die meisten Einträge?
SELECT
    station_name,
    COUNT(*) as anzahl_eintraege,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM 'dein_pfad.parquet'), 2) as prozent
FROM 'dein_pfad.parquet'
GROUP BY station_name
ORDER BY anzahl_eintraege DESC
LIMIT 20
```

**Frage:** Gibt es Bahnhöfe die auffällig über-/unterrepräsentiert sind?

### Aufgabe 3.2: Zugtyp-Verteilung

```sql
-- Verteilung nach Zugtyp
SELECT
    train_type,
    COUNT(*) as anzahl,
    ROUND(AVG(delay_in_min), 2) as avg_delay,
    SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) as canceled_count
FROM 'dein_pfad.parquet'
WHERE train_type IS NOT NULL
GROUP BY train_type
ORDER BY anzahl DESC
```

**Frage:** Welcher Zugtyp hat die meisten Probleme?

### Aufgabe 3.3: Zeitliche Verteilung

```sql
-- Verspätungen pro Wochentag
SELECT
    strftime(time, '%A') as wochentag,
    COUNT(*) as anzahl_fahrten,
    ROUND(AVG(delay_in_min), 2) as avg_delay
FROM 'dein_pfad.parquet'
GROUP BY strftime(time, '%A')
ORDER BY avg_delay DESC
```

**Frage:** Gibt es Wochentage mit auffällig mehr Problemen?

---

## 💡 Hilfreiche Ressourcen

Falls du nicht weiterkommst:

| Thema | Link |
|-------|------|
| DuckDB SQL Syntax | [DuckDB Docs](https://duckdb.org/docs/sql/introduction) |
| Pandas isnull() | [Pandas Docs](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.isnull.html) |
| Data Quality Best Practices | [Google: "data quality dimensions"](https://www.google.com/search?q=data+quality+dimensions) |
| SQL NULL Handling | [W3Schools NULL](https://www.w3schools.com/sql/sql_null_values.asp) |

---

## ✅ Checkliste: Habe ich alles?

Bevor du fertig bist, check ab:

- [ ] Mindestens 5 Probleme gefunden
- [ ] Jedes Problem hat konkrete Zahlen (Anzahl, Prozent)
- [ ] Jedes Problem hat eine Kategorie (Completeness, Validity, etc.)
- [ ] Jedes Problem hat SQL/Code als Beweis
- [ ] Jedes Problem hat eine Fix-Strategie
- [ ] Dokumentation ist strukturiert und professionell
- [ ] Code ist kommentiert und nachvollziehbar

---

## 🎯 Bonus-Challenges (Optional)

Wenn du früher fertig bist:

### Bonus 1: Zeitreihen-Analyse
- Wie entwickeln sich Verspätungen über den Monat?
- Gibt es Tage mit besonders vielen Problemen?

### Bonus 2: Korrelations-Analyse
- Gibt es einen Zusammenhang zwischen Verspätung und Ausfällen?
- Haben bestimmte Bahnhöfe mehr Probleme?

### Bonus 3: Daten-Bereinigung
- Schreibe Code der die gefundenen Probleme behebt
- Exportiere einen "sauberen" Datensatz

### Bonus 4: Visualisierung
- Erstelle Plots die deine Findings zeigen
- Nutze matplotlib oder plotly

---

## 💼 Das nimmst du mit

Nach diesem Projekt kannst du:

✅ Datenqualitäts-Probleme systematisch identifizieren
✅ SQL für Data Quality Checks schreiben
✅ Statistische Anomalien erkennen
✅ Professionelle Dokumentation erstellen
✅ Business Impact von schlechten Daten einschätzen

**Das sind Skills die jeder Data Analyst braucht!**

Viel Erfolg beim Detektivieren! 🔍

---

## 📝 Notizen

Platz für deine eigenen Notizen während der Arbeit:

```
[Hier kannst du Notizen machen während du arbeitest]
```
