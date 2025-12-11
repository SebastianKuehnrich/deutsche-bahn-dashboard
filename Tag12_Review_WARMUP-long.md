# Tag 12: Data Quality Mastery - Review & Vorbereitung

**Mittwoch, 10. Dezember 2025**
**Zeit:** 60 Minuten (Selbststudium)
**Ziel:** Festige dein Data Quality Wissen und bereite dich auf die nächste Phase vor

---

## Die Situation

Neue Email in deinem Postfach:

```
Von: head.of.data@deutschebahn.de
Betreff: Status Update & Next Steps

Guten Morgen,

ich habe gehört ihr habt am Montag einige kritische Datenprobleme gefunden.
Gut gemacht.

ABER: Bevor wir weitermachen, brauche ich von dir:

1. Eine Zusammenfassung deiner Findings (mit Zahlen!)
2. Beweis dass du die SQL-Skills hast die Probleme zu analysieren
3. Deine Empfehlungen für Fix-Strategien
4. Vorbereitung auf die nächste Phase: Daten transformieren und analysieren

Du hast 60 Minuten. Dann erwarte ich dich in der Live Session.

- Head of Data
```

**Das ist dein Briefing für heute Morgen.**

---

## ZEITPLAN

| Zeit | Aufgabe |
|------|---------|
| 0-10 min | Teil 1: Theorie Recall |
| 10-25 min | Teil 2: SQL Mastery Check |
| 25-40 min | Teil 3: Hands-On Analysis |
| 40-50 min | Teil 4: Fix-Strategien entwickeln |
| 50-60 min | Teil 5: Vorbereitung Live Session |

---

## Teil 1: Theorie Recall (10 Minuten)

### 1.1 Die 5 Dimensionen - Aus dem Kopf

Schreib OHNE nachzuschauen. Das muss sitzen.

```
DIE 5 DIMENSIONEN VON DATENQUALITÄT:

1. C_____________ (Vollständigkeit)
   Definition:

   SQL Check dafür:

   Beispiel aus DB-Daten:

2. V_____________ (Gültigkeit)
   Definition:

   SQL Check dafür:

   Beispiel aus DB-Daten:

3. C_____________ (Konsistenz)
   Definition:

   SQL Check dafür:

   Beispiel aus DB-Daten:

4. A_____________ (Genauigkeit)
   Definition:

   SQL Check dafür:

   Beispiel aus DB-Daten:

5. U_____________ (Eindeutigkeit)
   Definition:

   SQL Check dafür:

   Beispiel aus DB-Daten:
```

**Erst NACHDEM du fertig bist - check deine Antworten:**

<details>
<summary>Lösungen aufklappen</summary>

1. **COMPLETENESS** (Vollständigkeit)
   - Definition: Haben wir alle Daten die wir brauchen? Fehlen Werte?
   - SQL: `COUNT(*) - COUNT(spalte)` oder `WHERE spalte IS NULL`
   - DB-Beispiel: 22% missing arrival_change_time (441,914 Zeilen)

2. **VALIDITY** (Gültigkeit)
   - Definition: Sind die Werte im korrekten Format und gültigen Bereich?
   - SQL: `WHERE spalte < 0` oder `WHERE spalte > maximum`
   - DB-Beispiel: Negative delays (-1432 min), extreme delays (849 min)

3. **CONSISTENCY** (Konsistenz)
   - Definition: Sind Daten widerspruchsfrei? Gleiche Formate?
   - SQL: `WHERE bedingung1 AND bedingung2` (Logik-Checks)
   - DB-Beispiel: Canceled trains mit delay > 0 (Widerspruch?)

4. **ACCURACY** (Genauigkeit)
   - Definition: Repräsentieren die Daten die Realität korrekt?
   - SQL: `AVG()`, `STDDEV()`, Outlier Detection
   - DB-Beispiel: Verspätung von 14 Stunden - realistisch?

5. **UNIQUENESS** (Eindeutigkeit)
   - Definition: Gibt es Duplikate wo keine sein sollten?
   - SQL: `GROUP BY id HAVING COUNT(*) > 1`
   - DB-Beispiel: Doppelte IDs oder train_line_ride_id

</details>

---

### 1.2 Real-World Impact

Warum ist Data Quality wichtig? Schreib 3 Beispiele aus dem echten Leben:

```
REAL-WORLD DATA QUALITY DISASTERS:

1. Unternehmen: _______________
   Problem: _______________
   Kosten/Impact: _______________

2. Unternehmen: _______________
   Problem: _______________
   Kosten/Impact: _______________

3. Unternehmen: _______________
   Problem: _______________
   Kosten/Impact: _______________
```

<details>
<summary>Beispiele falls du keine hast</summary>

1. **Uber (2019)**
   - Problem: Pricing-Algorithmus mit schlechten Daten, negative Preise
   - Impact: $58 Millionen Verlust in Q2

2. **Amazon (2014)**
   - Problem: NULL-Preise wurden als €0.01 angezeigt
   - Impact: $1.7 Millionen Verlust (Laptops für 1 Cent verkauft)

3. **NASA Mars Climate Orbiter (1999)**
   - Problem: Team A nutzte Meter, Team B nutzte Feet
   - Impact: $327 Millionen (Satellit zerstört)

</details>

---

## Teil 2: SQL Mastery Check (15 Minuten)

Öffne DuckDB CLI oder Python. Wir testen ob du die Queries noch drauf hast.

### Setup (falls nötig)

```bash
# DuckDB CLI starten
C:/Users/oasrvadmin/Documents/duckdb.exe
```

Oder Python:

```python
import duckdb
con = duckdb.connect()
DATA_PATH = './deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet'
```

---

### 2.1 Query Challenge: Missing Values Report

**Aufgabe:** Schreib eine Query die für ALLE wichtigen Spalten zeigt wie viele NULLs es gibt.

Versuch es ERST selbst, dann check die Lösung:

```sql
-- Deine Query hier:




```

<details>
<summary>Lösung</summary>

```sql
SELECT
    COUNT(*) as total_rows,
    COUNT(*) - COUNT(station_name) as missing_station,
    COUNT(*) - COUNT(train_name) as missing_train,
    COUNT(*) - COUNT(delay_in_min) as missing_delay,
    COUNT(*) - COUNT(arrival_planned_time) as missing_arr_planned,
    COUNT(*) - COUNT(arrival_change_time) as missing_arr_change,
    COUNT(*) - COUNT(departure_planned_time) as missing_dep_planned,
    COUNT(*) - COUNT(departure_change_time) as missing_dep_change,
    COUNT(*) - COUNT(train_line_ride_id) as missing_ride_id
FROM './deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet';
```

**Erwartetes Ergebnis:**
- missing_arr_change: ~441,914 (22%)
- missing_dep_change: ~442,377 (22%)
- Die meisten anderen Spalten: 0 oder sehr wenig

</details>

**RUN IT.** Stimmen deine Zahlen mit Montag überein?

---

### 2.2 Query Challenge: Delay Distribution

**Aufgabe:** Zeig die Verteilung der Verspätungen in Kategorien:
- Zu früh (< 0 min)
- Pünktlich (0-5 min)
- Leicht verspätet (6-15 min)
- Verspätet (16-60 min)
- Stark verspätet (61-120 min)
- Extrem verspätet (> 120 min)

```sql
-- Deine Query hier:




```

<details>
<summary>Lösung</summary>

```sql
SELECT
    CASE
        WHEN delay_in_min < 0 THEN '1. Zu früh (< 0)'
        WHEN delay_in_min <= 5 THEN '2. Pünktlich (0-5)'
        WHEN delay_in_min <= 15 THEN '3. Leicht verspätet (6-15)'
        WHEN delay_in_min <= 60 THEN '4. Verspätet (16-60)'
        WHEN delay_in_min <= 120 THEN '5. Stark verspätet (61-120)'
        ELSE '6. Extrem verspätet (> 120)'
    END as kategorie,
    COUNT(*) as anzahl,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as prozent
FROM './deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet'
WHERE delay_in_min IS NOT NULL
GROUP BY 1
ORDER BY 1;
```

</details>

**RUN IT.** Was ist die größte Kategorie?

---

### 2.3 Query Challenge: Cancellation Analysis

**Aufgabe:** Zeig die Ausfallrate pro Zugtyp (ICE, IC, RE, etc.)

```sql
-- Deine Query hier:




```

<details>
<summary>Lösung</summary>

```sql
SELECT
    train_type,
    COUNT(*) as total_fahrten,
    SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) as canceled,
    ROUND(SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as cancel_rate_pct
FROM './deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet'
WHERE train_type IS NOT NULL
GROUP BY train_type
ORDER BY cancel_rate_pct DESC;
```

</details>

**RUN IT.** Welcher Zugtyp hat die höchste Ausfallrate?

---

### 2.4 Query Challenge: Logik-Check (Konsistenz)

**Aufgabe:** Finde Züge die `is_canceled = True` haben ABER trotzdem eine Verspätung > 0. Das ist ein potenzieller Logik-Widerspruch.

```sql
-- Deine Query hier:




```

<details>
<summary>Lösung</summary>

```sql
SELECT
    station_name,
    train_name,
    train_type,
    is_canceled,
    delay_in_min,
    time
FROM './deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet'
WHERE is_canceled = True AND delay_in_min > 0
ORDER BY delay_in_min DESC
LIMIT 20;
```

**Frage zum Nachdenken:** Ist das ein Bug oder macht das Sinn? (Hint: Vielleicht wurde der Zug gecancelt NACHDEM er schon verspätet gemeldet wurde?)

</details>

**RUN IT.** Wie viele solcher Fälle gibt es?

---

### 2.5 Query Challenge: Station Ranking

**Aufgabe:** Top 10 Bahnhöfe mit der höchsten durchschnittlichen Verspätung (nur Bahnhöfe mit mehr als 1000 Einträgen).

```sql
-- Deine Query hier:




```

<details>
<summary>Lösung</summary>

```sql
SELECT
    station_name,
    COUNT(*) as anzahl_zuege,
    ROUND(AVG(delay_in_min), 2) as avg_delay,
    ROUND(MAX(delay_in_min), 2) as max_delay,
    SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) as canceled_count
FROM './deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet'
WHERE delay_in_min IS NOT NULL
GROUP BY station_name
HAVING COUNT(*) > 1000
ORDER BY avg_delay DESC
LIMIT 10;
```

</details>

**RUN IT.** Erkennst du Muster? Sind das große Bahnhöfe? Knotenpunkte?

---

## Teil 3: Hands-On Analysis (15 Minuten)

Jetzt machst du NEUE Analysen die du am Montag vielleicht nicht gemacht hast.

### 3.1 Zeitliche Analyse

**Aufgabe:** Analysiere Verspätungen nach Wochentag.

Erstelle eine neue Python-Datei: `zeit_analyse.py`

```python
# zeit_analyse.py
# Zeitliche Analyse der Verspätungen

import duckdb

con = duckdb.connect()
DATA_PATH = './deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet'

print("=" * 60)
print("ZEITLICHE ANALYSE - DEUTSCHE BAHN OKTOBER 2024")
print("=" * 60)

# Verspätungen nach Wochentag
print("\n📅 VERSPÄTUNGEN NACH WOCHENTAG:")
print("-" * 40)

result = con.execute(f"""
SELECT
    CASE strftime(time, '%w')
        WHEN '0' THEN 'Sonntag'
        WHEN '1' THEN 'Montag'
        WHEN '2' THEN 'Dienstag'
        WHEN '3' THEN 'Mittwoch'
        WHEN '4' THEN 'Donnerstag'
        WHEN '5' THEN 'Freitag'
        WHEN '6' THEN 'Samstag'
    END as wochentag,
    COUNT(*) as fahrten,
    ROUND(AVG(delay_in_min), 2) as avg_delay,
    SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) as canceled
FROM '{DATA_PATH}'
WHERE delay_in_min IS NOT NULL
GROUP BY strftime(time, '%w')
ORDER BY strftime(time, '%w')
""").fetchall()

for row in result:
    print(f"{row[0]:12} | {row[1]:>8,} Fahrten | Ø {row[2]:>6.2f} min | {row[3]:>5,} canceled")

# Verspätungen nach Stunde
print("\n\n🕐 VERSPÄTUNGEN NACH STUNDE (Rush Hour Check):")
print("-" * 40)

result = con.execute(f"""
SELECT
    HOUR(time) as stunde,
    COUNT(*) as fahrten,
    ROUND(AVG(delay_in_min), 2) as avg_delay
FROM '{DATA_PATH}'
WHERE delay_in_min IS NOT NULL
GROUP BY HOUR(time)
ORDER BY avg_delay DESC
LIMIT 10
""").fetchall()

print("Top 10 Stunden mit höchster Verspätung:")
for row in result:
    print(f"  {row[0]:02d}:00 Uhr | {row[1]:>7,} Fahrten | Ø {row[2]:>6.2f} min Verspätung")

print("\n" + "=" * 60)
```

**RUN IT.**

**Fragen zum Nachdenken:**
- Welcher Wochentag ist am schlimmsten?
- Gibt es eine Rush Hour mit mehr Verspätungen?
- Macht das Sinn? Warum?

---

### 3.2 Outlier Deep Dive

**Aufgabe:** Analysiere die extremsten Fälle genauer.

Erstelle: `outlier_analyse.py`

```python
# outlier_analyse.py
# Deep Dive in Outliers

import duckdb

con = duckdb.connect()
DATA_PATH = './deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet'

print("=" * 60)
print("OUTLIER ANALYSE - EXTREME FÄLLE")
print("=" * 60)

# Extremste positive Verspätungen
print("\n🔴 TOP 10 EXTREMSTE VERSPÄTUNGEN:")
print("-" * 60)

result = con.execute(f"""
SELECT
    station_name,
    train_name,
    train_type,
    delay_in_min,
    is_canceled,
    time
FROM '{DATA_PATH}'
WHERE delay_in_min IS NOT NULL
ORDER BY delay_in_min DESC
LIMIT 10
""").fetchall()

for i, row in enumerate(result, 1):
    stunden = row[3] // 60
    minuten = row[3] % 60
    canceled = "CANCELED" if row[4] else "nicht canceled"
    print(f"{i:2}. {row[3]:>5} min ({stunden}h {minuten}m) | {row[2]} | {row[1]}")
    print(f"    Station: {row[0]} | {canceled}")
    print()

# Extremste negative Verspätungen (zu früh)
print("\n🟢 TOP 10 'ZU FRÜH' (negative delays):")
print("-" * 60)

result = con.execute(f"""
SELECT
    station_name,
    train_name,
    train_type,
    delay_in_min,
    time
FROM '{DATA_PATH}'
WHERE delay_in_min < 0
ORDER BY delay_in_min ASC
LIMIT 10
""").fetchall()

for i, row in enumerate(result, 1):
    print(f"{i:2}. {row[3]:>6} min | {row[2]} {row[1]} | {row[0]}")

# Statistische Outlier Detection
print("\n\n📊 STATISTISCHE OUTLIER ANALYSE:")
print("-" * 60)

result = con.execute(f"""
SELECT
    ROUND(AVG(delay_in_min), 2) as mean,
    ROUND(STDDEV(delay_in_min), 2) as stddev,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY delay_in_min), 2) as q1,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY delay_in_min), 2) as median,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY delay_in_min), 2) as q3,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY delay_in_min), 2) as p95,
    ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY delay_in_min), 2) as p99
FROM '{DATA_PATH}'
WHERE delay_in_min IS NOT NULL
""").fetchone()

print(f"Mean (Durchschnitt): {result[0]} min")
print(f"Std Dev:             {result[1]} min")
print(f"Q1 (25%):            {result[2]} min")
print(f"Median (50%):        {result[3]} min")
print(f"Q3 (75%):            {result[4]} min")
print(f"95. Perzentil:       {result[5]} min")
print(f"99. Perzentil:       {result[6]} min")

# IQR Outlier Grenzen
iqr = result[4] - result[2]
lower_bound = result[2] - 1.5 * iqr
upper_bound = result[4] + 1.5 * iqr

print(f"\nIQR (Q3-Q1):         {iqr} min")
print(f"Outlier Grenzen (1.5 * IQR):")
print(f"  Untere Grenze:     {lower_bound} min")
print(f"  Obere Grenze:      {upper_bound} min")

# Wie viele Outliers?
result = con.execute(f"""
SELECT COUNT(*)
FROM '{DATA_PATH}'
WHERE delay_in_min < {lower_bound} OR delay_in_min > {upper_bound}
""").fetchone()

print(f"\nAnzahl statistische Outliers: {result[0]:,}")

print("\n" + "=" * 60)
```

**RUN IT.**

**Fragen zum Nachdenken:**
- Ist -1432 Minuten Verspätung ein Datenfehler oder echte Daten?
- Wie würdest du Outliers definieren? > 2 Stunden? > 3 Stunden?
- Sollten wir IQR-Methode oder feste Grenzen benutzen?

---

## Teil 4: Fix-Strategien entwickeln (10 Minuten)

Jetzt das Wichtigste: WIE fixst du die Probleme?

### 4.1 Missing Values Strategie

**441,914 fehlende arrival_change_time (22%)**

```
OPTIONEN:

[ ] A) Zeilen komplett löschen
    Vorteil: Saubere Daten
    Nachteil: Verlierst 22% der Daten!

[ ] B) Mit arrival_planned_time füllen
    Vorteil: Behältst alle Zeilen
    Nachteil: Falsche Annahme (geplant ≠ real)

[ ] C) Mit Durchschnitt füllen
    Vorteil: Statistisch neutral
    Nachteil: Einzelwerte sind falsch

[ ] D) NULL lassen aber Flag-Spalte erstellen
    Vorteil: Transparent, nichts verfälscht
    Nachteil: Manche Analysen funktionieren nicht

[ ] E) Forward Fill (vorherigen Wert nutzen)
    Vorteil: Macht bei Zeitreihen Sinn
    Nachteil: Nicht bei diesem Datensatz sinnvoll

MEINE ENTSCHEIDUNG: ___

BEGRÜNDUNG (2-3 Sätze):


```

---

### 4.2 Negative Delays Strategie

**46,235 Zeilen mit delay < 0 (Minimum: -1432 min)**

```
ANALYSE:

- Züge können FRÜHER ankommen → negative delay ist valide
- ABER: -1432 Minuten = 24 Stunden zu früh??? Das ist unmöglich.

Vermutung: Kleine negative Werte = echt, extreme = Bug

OPTIONEN:

[ ] A) Alle negativen löschen
    Problem: Verlierst valide Daten

[ ] B) Alle auf 0 setzen
    Problem: Verfälscht Statistik

[ ] C) Nur extreme löschen (z.B. < -60 min)
    Vorteil: Behält realistische "zu früh" Werte

[ ] D) Absolute Werte nehmen (aus -5 wird 5)
    Problem: Komplett falsch, macht keinen Sinn

MEINE ENTSCHEIDUNG: ___

GRENZE FÜR "EXTREM": ___ Minuten

BEGRÜNDUNG:


```

---

### 4.3 Extreme Delays Strategie

**Maximum: 849 Minuten (14 Stunden!)**

```
FRAGE: Ab wann ist eine Verspätung "unrealistisch"?

- 60 min? Passiert jeden Tag...
- 120 min? Auch noch realistisch
- 300 min (5h)? Grenzwertig
- 500 min+? Wahrscheinlich sollte das canceled sein

OPTIONEN:

[ ] A) Harte Grenze: Alles > X min löschen
[ ] B) Winsorizing: Extreme auf Maximum cappen (z.B. 180 min)
[ ] C) Als canceled markieren wenn > X min
[ ] D) Behalten aber in separater Spalte flaggen

MEINE ENTSCHEIDUNG: ___

GRENZE: ___ Minuten

BEGRÜNDUNG:


```

---

### 4.4 Canceled + Delay Widerspruch

**Züge mit is_canceled=True UND delay > 0**

```
INTERPRETATION:

Möglichkeit 1: Bug in den Daten
Möglichkeit 2: Zug wurde gecancelt NACHDEM Verspätung gemeldet wurde

WAS MACHT MEHR SINN? ___

WIE BEHANDELN?

[ ] A) delay auf NULL setzen wenn canceled
[ ] B) is_canceled auf False setzen wenn delay > 0
[ ] C) Beides behalten (kein Widerspruch, verschiedene Zeitpunkte)
[ ] D) Neue Spalte: canceled_after_delay = True

MEINE ENTSCHEIDUNG: ___

BEGRÜNDUNG:


```

---

## Teil 5: Vorbereitung Live Session (10 Minuten)

### 5.1 Deine Summary

Schreib eine kurze Zusammenfassung (so als würdest du es dem Chef präsentieren):

```
DEUTSCHE BAHN DATA QUALITY SUMMARY
Analyst: [Dein Name]
Datum: 10. Dezember 2025

KRITISCHE FINDINGS:

1. ____________________________________________
   Impact: ___________________________________

2. ____________________________________________
   Impact: ___________________________________

3. ____________________________________________
   Impact: ___________________________________

EMPFOHLENE FIX-STRATEGIEN:

1. ____________________________________________

2. ____________________________________________

3. ____________________________________________

NÄCHSTE SCHRITTE:

1. ____________________________________________

2. ____________________________________________
```

---

### 5.2 Ready Check

Bevor die Live Session startet - check ab:

- [ ] Ich kann die 5 Dimensionen erklären (ohne Notizen!)
- [ ] Ich kenne meine Top 3 Findings mit exakten Zahlen
- [ ] Ich kann SQL Queries für alle Checks schreiben
- [ ] Ich habe für jedes Problem eine Fix-Strategie mit Begründung
- [ ] Meine Dokumentation/Code von Montag ist griffbereit
- [ ] Ich habe die neuen Analysen (Zeit, Outlier) durchgeführt

---

### 5.3 Fragen für die Live Session

Schreib auf was du fragen willst:

```
MEINE FRAGEN:

1.

2.

3.
```

---

## Quick Reference

### Zahlen die du kennen MUSST:

| Metrik | Wert | Prozent |
|--------|------|---------|
| Total Zeilen | 1,984,484 | 100% |
| Missing arrival_change | 441,914 | 22% |
| Missing departure_change | 442,377 | 22% |
| Negative delays | 46,235 | 2.3% |
| Min delay | -1,432 min | |
| Max delay | 849 min | |
| Canceled trains | 107,666 | 5.4% |

### SQL Cheat Sheet:

```sql
-- Missing Values
COUNT(*) - COUNT(spalte)

-- Prozent Missing
ROUND((COUNT(*) - COUNT(spalte)) * 100.0 / COUNT(*), 2)

-- Outlier Grenzen (IQR)
PERCENTILE_CONT(0.25) -- Q1
PERCENTILE_CONT(0.75) -- Q3
-- Outlier wenn < Q1 - 1.5*IQR oder > Q3 + 1.5*IQR

-- Kategorisieren
CASE WHEN bedingung THEN 'A' ELSE 'B' END

-- Gruppieren mit Prozent
COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()
```

---

## Fertig!

Du hast 60 Minuten intensiv gearbeitet.

**Du bist jetzt ready für:**
- Deine Findings zu verteidigen
- Fix-Strategien zu diskutieren
- Die nächste Phase: Daten bereinigen und transformieren

**Bring alles mit zur Live Session!**

Bis gleich! 🚀
