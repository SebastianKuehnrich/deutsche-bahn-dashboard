# Tag 10: Data Detective - Deutsche Bahn Datenqualität

**Montag, 8. Dezember 2025**
**Zeit:** 60 Minuten (Selbststudium)
**Ziel:** Du verstehst was Datenqualität ist, warum es kritisch ist, und bist bereit für deine erste Data Quality Analyse

---

## Die Situation

Du kommst heute ins Büro. Neue Email vom Head of Data:

```
Von: head.of.data@deutschebahn.de
Betreff: KRITISCH - Datenqualitäts-Analyse SOFORT

Guten Morgen,

Unser Dashboard zeigt komische Werte. Züge mit 800 Minuten Verspätung.
Negative Delays. Fehlende Daten überall.

Die IT hat uns einen Datensatz mit 2 Millionen Zugfahrten gegeben.
NIEMAND hat die Qualität geprüft.

Dein Job heute: Finde ALLE Probleme. Dokumentiere sie. Schlag Lösungen vor.

Das ist kritisch. Die Presse fragt nach Pünktlichkeits-Statistiken.
Wenn wir mit schlechten Daten antworten, ist das peinlich.

- Head of Data
```

**Das ist deine Mission für heute.**

---

## 1. Was ist Datenqualität? Warum ist es wichtig?

### Definition

**Datenqualität** = Wie gut sind deine Daten geeignet für den beabsichtigten Zweck?

Schlechte Datenqualität = Schlechte Analysen = Schlechte Entscheidungen = Verlorenes Geld

### Real-World Impact

**Beispiel 1: Amazon (2014)**
- Bug in Preis-Daten: Produkte mit 0,01€ gelistet
- Kosten: **$1.7 Millionen Verlust**
- Problem: Fehlende Validierung bei Preis-Updates

**Beispiel 2: NASA Mars Climate Orbiter (1999)**
- Daten-Inkonsistenz: Team A nutzte Meter, Team B nutzte Feet
- Kosten: **$327 Millionen** (Satellit zerstört)
- Problem: Fehlende Format-Standardisierung

**Beispiel 3: Target (2013)**
- Fehlerhafte Kundendaten führten zu falschen Marketing-Kampagnen
- Kosten: **$61 Millionen Datenschutz-Strafe** + Reputationsschaden
- Problem: Duplikate und veraltete Informationen

### Warum ist das wichtig für deine Karriere?

| **Statistik** | **Bedeutung für dich** |
|---------------|------------------------|
| **80%** der Data Science Arbeit ist Data Cleaning & Quality | Du wirst mehr Zeit mit Datenqualität verbringen als mit ML |
| **90%** der Data Analyst Jobs verlangen "Data Quality" Skills | Steht in fast jeder Stellenanzeige |
| Companies verlieren durchschnittlich **$15 Millionen** pro Jahr durch schlechte Datenqualität | Wenn du das verhinderst, bist du wertvoll |
| **60%** aller Analytics-Projekte scheitern wegen Datenqualitäts-Problemen | Gute Data Quality = Projekterfolg |

**Bottom Line:** Wenn du Data Quality beherrschst, bist du unersetzlich.

---

## 2. Die 5 Dimensionen von Datenqualität

Es gibt 5 Kategorien von Problemen. Du musst ALLE checken.

### 2.1 COMPLETENESS (Vollständigkeit)

**Frage:** Haben wir alle Daten die wir brauchen?

**Typische Probleme:**
- **Missing Values (NULL, NaN)** - Fehlende Werte in Spalten
- **Fehlende Zeilen** - Erwartete Daten fehlen komplett
- **Unvollständige Attribute** - Wichtige Spalten fehlen

**Real-World Beispiel:**
```
Kunde-Tabelle:
ID | Name     | Email          | Telefon
1  | Anna     | anna@mail.de   | NULL
2  | Bob      | NULL           | 0123456
3  | Charlie  | charlie@m.de   | 0765432

Problem: Email oder Telefon fehlt oft.
Impact: Marketing kann Kunden nicht erreichen.
```

**SQL Check:**
```sql
-- Wie viele NULLs pro Spalte?
SELECT
    COUNT(*) as total,
    COUNT(*) - COUNT(email) as missing_email,
    COUNT(*) - COUNT(phone) as missing_phone
FROM customers;
```

**Fix-Strategien:**
- **Drop** - Zeile löschen (wenn < 5% betroffen)
- **Fill** - Mit Default-Wert füllen (z.B. "Unbekannt")
- **Impute** - Mit Durchschnitt/Median füllen (bei Zahlen)
- **Flag** - Als "fehlend" markieren und separat behandeln

### 2.2 VALIDITY (Gültigkeit)

**Frage:** Sind die Werte gültig und im korrekten Format?

**Typische Probleme:**
- **Falsche Datentypen** - String statt Zahl, Zahl statt Datum
- **Werte außerhalb gültigem Range** - Alter = -5, Preis = -100€
- **Ungültige Formate** - Email ohne @, Telefon mit Buchstaben

**Real-World Beispiel:**
```
Produkt-Tabelle:
ID | Produkt  | Preis    | Lagerbestand
1  | Laptop   | 899.99   | 50
2  | Maus     | -5.00    | -10
3  | Tastatur | 0        | 999999

Probleme:
- Zeile 2: Negativer Preis und negativer Lagerbestand (unmöglich!)
- Zeile 3: Preis = 0 (Bug oder kostenlos?)
- Zeile 3: 999999 Lagerbestand (realistisch oder Placeholder?)
```

**SQL Check:**
```sql
-- Finde invalide Werte
SELECT * FROM products
WHERE price < 0 OR stock < 0 OR stock > 10000;
```

**Fix-Strategien:**
- **Reject** - Zeile ablehnen wenn kritisch
- **Correct** - Wert korrigieren wenn offensichtlich (z.B. -100 → 100)
- **Flag** - Für manuelle Review markieren

### 2.3 CONSISTENCY (Konsistenz)

**Frage:** Sind die Daten widerspruchsfrei?

**Typische Probleme:**
- **Format-Inkonsistenzen** - "2024-01-01" vs "01/01/2024" vs "1. Januar 2024"
- **Encoding-Probleme** - "München" vs "M�nchen"
- **Logik-Widersprüche** - Bestellung vor Registrierung, Ankunft vor Abfahrt

**Real-World Beispiel:**
```
Bestellungen:
ID | Bestelldatum | Versanddatum | Status
1  | 2024-01-15   | 2024-01-10   | Versendet
2  | 2024-01-20   | NULL         | Zugestellt

Probleme:
- Zeile 1: Versand VOR Bestellung (Zeitreise?)
- Zeile 2: Zugestellt aber kein Versanddatum (inkonsistent)
```

**SQL Check:**
```sql
-- Finde Logik-Widersprüche
SELECT * FROM orders
WHERE ship_date < order_date;
```

**Fix-Strategien:**
- **Standardize** - Formate vereinheitlichen
- **Correct Encoding** - UTF-8 erzwingen
- **Logic Rules** - Validierungs-Regeln anwenden

### 2.4 ACCURACY (Genauigkeit)

**Frage:** Repräsentieren die Daten die Realität korrekt?

**Typische Probleme:**
- **Outliers** - Extremwerte die unrealistisch sind
- **Falsche Werte** - Eingabefehler, Copy-Paste-Fehler
- **Veraltete Daten** - Alte Werte die nicht mehr stimmen

**Real-World Beispiel:**
```
Mitarbeiter:
ID | Name   | Gehalt  | Abteilung
1  | Anna   | 45000   | IT
2  | Bob    | 4500000 | Sales
3  | Chris  | 52000   | IT

Problem:
- Zeile 2: Bob verdient 4.5 Millionen? (Wahrscheinlich Tippfehler: 45000)
```

**SQL Check:**
```sql
-- Finde Outliers mit Statistik
SELECT
    MIN(salary) as min_sal,
    MAX(salary) as max_sal,
    AVG(salary) as avg_sal
FROM employees;

-- Alles über 3x Durchschnitt = verdächtig
SELECT * FROM employees
WHERE salary > (SELECT AVG(salary) * 3 FROM employees);
```

**Fix-Strategien:**
- **Winsorize** - Extreme Werte auf Maximum/Minimum setzen
- **Remove** - Outliers löschen wenn klar fehlerhaft
- **Investigate** - Bei wichtigen Daten manuell prüfen

### 2.5 UNIQUENESS (Eindeutigkeit)

**Frage:** Gibt es Duplikate wo keine sein sollten?

**Typische Probleme:**
- **Exakte Duplikate** - Komplette Zeile doppelt
- **ID-Kollisionen** - Gleiche ID für verschiedene Einträge
- **Ähnliche Duplikate** - Leicht unterschiedliche Schreibweise

**Real-World Beispiel:**
```
Kunden:
ID | Name          | Email
1  | Anna Schmidt  | anna@mail.de
1  | Bob Mueller   | bob@mail.de
2  | Anna Schmidt  | anna@mail.de

Probleme:
- ID=1 kommt 2x vor (verschiedene Personen!)
- Anna Schmidt kommt 2x vor (gleiches Email, verschiedene IDs)
```

**SQL Check:**
```sql
-- Finde Duplikate
SELECT id, COUNT(*) as anzahl
FROM customers
GROUP BY id
HAVING COUNT(*) > 1;
```

**Fix-Strategien:**
- **Deduplicate** - Duplikate entfernen
- **Merge** - Duplikate zu einem Record zusammenführen
- **ID Rewrite** - Neue eindeutige IDs vergeben

---

## 3. Dein Werkzeugkasten: SQL für Data Quality

### Wichtigste SQL-Funktionen

| **Funktion** | **Zweck** | **Beispiel** |
|--------------|-----------|--------------|
| `COUNT(*)` vs `COUNT(spalte)` | Finde missing values | `SELECT COUNT(*) - COUNT(email) FROM users` |
| `MIN()`, `MAX()` | Finde Range und Outliers | `SELECT MIN(age), MAX(age) FROM users` |
| `AVG()`, `STDDEV()` | Statistiken für Outlier-Detection | `SELECT AVG(price), STDDEV(price) FROM products` |
| `DISTINCT` | Zähle unique Werte | `SELECT COUNT(DISTINCT user_id) FROM orders` |
| `GROUP BY ... HAVING` | Finde Duplikate | `SELECT id, COUNT(*) FROM t GROUP BY id HAVING COUNT(*) > 1` |
| `WHERE spalte IS NULL` | Finde NULLs | `SELECT * FROM users WHERE email IS NULL` |
| `CASE WHEN` | Kategorisiere Probleme | `SELECT CASE WHEN age < 0 THEN 'invalid' END FROM users` |

### Typische Data Quality Queries

**1. Missing Value Report**
```sql
SELECT
    'column_name' as spalte,
    COUNT(*) as total,
    COUNT(column_name) as not_null,
    COUNT(*) - COUNT(column_name) as nulls,
    ROUND((COUNT(*) - COUNT(column_name)) * 100.0 / COUNT(*), 2) as null_pct
FROM your_table;
```

**2. Outlier Detection (IQR Method)**
```sql
-- Finde Werte ausserhalb von Q1 - 1.5*IQR bis Q3 + 1.5*IQR
WITH stats AS (
    SELECT
        percentile_cont(0.25) WITHIN GROUP (ORDER BY value) as q1,
        percentile_cont(0.75) WITHIN GROUP (ORDER BY value) as q3
    FROM your_table
)
SELECT * FROM your_table
WHERE value < (SELECT q1 - 1.5 * (q3 - q1) FROM stats)
   OR value > (SELECT q3 + 1.5 * (q3 - q1) FROM stats);
```

**3. Duplicate Detection**
```sql
-- Finde exakte Duplikate
SELECT *, COUNT(*) as duplicate_count
FROM your_table
GROUP BY col1, col2, col3
HAVING COUNT(*) > 1;
```

**4. Format Inconsistencies**
```sql
-- Finde verschiedene Datums-Formate
SELECT date_column, COUNT(*) as count
FROM your_table
GROUP BY date_column
ORDER BY count DESC;
```

---

## 4. Setup: Daten laden & DuckDB CLI

### Schritt 1: Daten herunterladen

Erstelle neue Datei: `download_data.py`

```python
from huggingface_hub import hf_hub_download

print("Lade Deutsche Bahn Daten von HuggingFace...")

file = hf_hub_download(
    repo_id='piebro/deutsche-bahn-data',
    filename='monthly_processed_data/data-2024-10.parquet',
    repo_type='dataset',
    local_dir='./deutsche_bahn_data'
)

print(f"✓ Download erfolgreich!")
print(f"Datei: {file}")
print("\nDatei-Infos:")
import os
size_mb = os.path.getsize(file) / (1024 * 1024)
print(f"Größe: {size_mb:.1f} MB")
```

**Ausführen:**
```bash
python download_data.py
```

Dauert ~1 Minute. Du solltest sehen:
```
✓ Download erfolgreich!
Datei: ./deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet
Größe: 72.0 MB
```

### Schritt 2: DuckDB CLI kennenlernen

**Was ist DuckDB CLI?**
- Command-Line Tool für SQL
- Schneller als Python für Quick Checks
- Kann direkt Parquet lesen (ohne Import!)
- Industry-Standard Tool

**Starte DuckDB:**
```bash
C:/Users/oasrvadmin/Documents/duckdb.exe
```

Du siehst:
```
v1.4.2 stable
D
```

Das `D` ist der DuckDB Prompt. Jetzt kannst du SQL schreiben!

**Query 1: Zähle Zeilen**
```sql
SELECT COUNT(*)
FROM './deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet';
```

Ergebnis:
```
┌──────────┐
│ count(*) │
├──────────┤
│  1984484 │
└──────────┘
```

Fast 2 Millionen Zeilen!

**Query 2: Spalten anzeigen**
```sql
DESCRIBE SELECT *
FROM './deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet';
```

Zeigt alle 16 Spalten mit Datentypen.

**Query 3: Sample Data**
```sql
SELECT * FROM './deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet'
LIMIT 5;
```

**Query 4: Quick Stats**
```sql
SELECT
    MIN(delay_in_min) as min_delay,
    MAX(delay_in_min) as max_delay,
    AVG(delay_in_min) as avg_delay
FROM './deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet';
```

**WICHTIG:** Schau dir die Ergebnisse an. Siehst du schon Probleme?

**Beenden:**
```
.quit
```

---

## 5. Deine Mission (nochmal zusammengefasst)

**Ab 10:10 Uhr bekommst du die Projekt-Datei.**

Darin ist deine Aufgabe:

1. **Finde mindestens 5 Datenqualitäts-Probleme** in den Deutsche Bahn Daten
2. **Kategorisiere jedes Problem** (Completeness, Validity, Consistency, Accuracy, Uniqueness)
3. **Dokumentiere mit Zahlen** (Wie viele Zeilen betroffen? Prozent?)
4. **Schreibe die SQL/Code** die das Problem beweist
5. **Schlage eine Fix-Strategie vor** (Wie würdest du es lösen?)

**Deliverable:** Ein professioneller Datenqualitäts-Bericht

---

## 6. Hilfreiche Ressourcen

| **Thema** | **Link** |
|-----------|----------|
| DuckDB SQL Syntax | [DuckDB Docs](https://duckdb.org/docs/sql/introduction) |
| Data Quality Best Practices | [Google: "data quality dimensions"](https://www.google.com/search?q=data+quality+dimensions) |
| SQL Aggregation Functions | [W3Schools SQL](https://www.w3schools.com/sql/sql_count_avg_sum.asp) |
| Outlier Detection Methods | [Wikipedia: Outlier](https://en.wikipedia.org/wiki/Outlier) |
| Missing Data Strategies | [Towards Data Science: Missing Data](https://towardsdatascience.com/handling-missing-values-in-machine-learning-part-1-dda70d4341c8) |

---

## 7. Checkliste: Bist du bereit?

Vor 10:10 Uhr solltest du:

- [ ] Verstehen was Datenqualität ist und warum es wichtig ist
- [ ] Die 5 Dimensionen kennen (Completeness, Validity, Consistency, Accuracy, Uniqueness)
- [ ] Deutsche Bahn Daten heruntergeladen haben
- [ ] DuckDB CLI getestet haben (mindestens 2-3 Queries)
- [ ] Wissen wie man missing values, outliers, und duplicates findet

**Wenn du alle Checkboxen hast → Du bist bereit! 🚀**

---

## 8. Quick Reference Card

**Speicher das ab - du brauchst es heute:**

```sql
-- COMPLETENESS
SELECT COUNT(*) - COUNT(spalte) as missing FROM tabelle;

-- VALIDITY
SELECT * FROM tabelle WHERE spalte < 0 OR spalte > maximum;

-- CONSISTENCY
SELECT * FROM tabelle WHERE date1 > date2;  -- Logik-Check

-- ACCURACY
SELECT AVG(spalte), STDDEV(spalte) FROM tabelle;  -- Outliers

-- UNIQUENESS
SELECT id, COUNT(*) FROM tabelle GROUP BY id HAVING COUNT(*) > 1;
```

---

## Los geht's!

Du hast jetzt alles was du brauchst.

**Um 10:10 Uhr** bekommst du die Projekt-Datei mit allen Details.

Bis dahin: Mach dich mit den Daten vertraut. Probiere DuckDB CLI aus. Schau dir die Spalten an.

**Data Detective Mode: ACTIVATED 🔍**

Viel Erfolg!
