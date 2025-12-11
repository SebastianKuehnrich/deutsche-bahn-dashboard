# DEUTSCHE BAHN DATENQUALITÄTS-BERICHT

**Analyst:** Sebastian  
**Datum:** 8. Dezember 2025  
**Datensatz:** Deutsche Bahn API - Oktober 2024  
**Datensätze geprüft:** 1,984,484

---

## EXECUTIVE SUMMARY

Bei der Analyse von fast 2 Millionen Zugfahrten der Deutschen Bahn aus Oktober 2024 wurden **6 kritische Datenqualitätsprobleme** identifiziert, die **alle 5 Dimensionen** von Datenqualität betreffen. Die Probleme reichen von fehlenden Werten über logische Inkonsistenzen bis hin zu unmöglichen Werten.

**Kritischste Befunde:**
- 46,235 negative Verspätungen (physikalisch unmöglich)
- 884,459 fehlende Zeitstempel (44,57% der Daten)
- 25,220 stornierte Züge mit Verspätung (logischer Widerspruch)

---

## PROBLEM 1: Fehlende Bahnhofsnamen

### KATEGORIE
**COMPLETENESS** (Vollständigkeit)

### BESCHREIBUNG
35,757 Datensätze haben keinen Bahnhofsnamen (station_name = NULL). Dies betrifft 1,80% aller Zugfahrten. Die Bahnhofsinformation ist kritisch für jede geografische Analyse und sollte immer vorhanden sein.

### BETROFFENE DATEN
- **Spalte:** `station_name`
- **Anzahl Zeilen betroffen:** 35,757 (1.80% der Daten)
- **Schweregrad:** HOCH

### BEWEIS (SQL)
```sql
SELECT
    COUNT(*) as total,
    COUNT(*) - COUNT(station_name) as missing_station,
    ROUND((COUNT(*) - COUNT(station_name)) * 100.0 / COUNT(*), 2) as prozent
FROM deutsche_bahn_data
```

**Ergebnis:** 35,757 fehlende Werte (1.80%)

### AUSWIRKUNG
- **Geografische Analysen** sind unvollständig
- **Top-Bahnhof-Rankings** sind verzerrt
- **Regional-Reports** haben Datenlücken
- **Pünktlichkeits-Statistiken pro Station** sind ungenau

### FIX-STRATEGIE
1. **Kurzfristig:** Nutze `xml_station_name` als Fallback (0 missing values)
2. **Mittelfristig:** Ergänze fehlende Namen über EVA-Nummer aus Referenztabelle
3. **Langfristig:** Validierung an der API-Schnittstelle implementieren (station_name = NOT NULL)

---

## PROBLEM 2: Negative Verspätungen

### KATEGORIE
**VALIDITY** (Gültigkeit)

### BESCHREIBUNG
46,235 Zugfahrten haben negative Verspätungswerte (delay_in_min < 0). Der extremste Wert liegt bei **-1,432 Minuten** (fast -24 Stunden). Negative Verspätungen bedeuten, dass ein Zug "früher als geplant" ankam, aber Werte von mehreren hundert Minuten sind unrealistisch und deuten auf Datenfehler hin.

### BETROFFENE DATEN
- **Spalte:** `delay_in_min`
- **Anzahl Zeilen betroffen:** 46,235 (2.33% der Daten)
- **Schweregrad:** KRITISCH
- **Wertebereich:** -1,432 min bis 849 min

### BEWEIS (SQL)
```sql
SELECT
    MIN(delay_in_min) as min_delay,
    COUNT(CASE WHEN delay_in_min < 0 THEN 1 END) as negative_delays,
    ROUND(COUNT(CASE WHEN delay_in_min < 0 THEN 1 END) * 100.0 / COUNT(*), 2) as prozent
FROM deutsche_bahn_data
```

**Ergebnis:** 
- Minimum: -1,432 Minuten
- Negative Werte: 46,235 (2.33%)

### AUSWIRKUNG
- **Pünktlichkeits-Statistiken** sind falsch
- **Durchschnittliche Verspätung** ist verzerrt
- **KPI-Berichte** für Management sind fehlerhaft
- **Presse-Mitteilungen** könnten auf falschen Daten basieren
- **Machine Learning Modelle** lernen falsche Muster

### FIX-STRATEGIE
1. **Sofort:** Alle Werte < -30 Minuten als Invalid markieren und aus Berechnungen ausschließen
2. **Kurzfristig:** Datenbereinigung durchführen:
   - Werte < -30 min → auf -30 min setzen (Winsorizing)
   - Werte < -1000 min → wahrscheinlich Datenfehler → auf 0 setzen
3. **Langfristig:** 
   - API-Validierung: delay_in_min BETWEEN -30 AND 1000
   - Automatische Quality Checks bei Daten-Import
   - Monitoring für Extremwerte

---

## PROBLEM 3: Extreme Verspätungen (>120 min)

### KATEGORIE
**ACCURACY** (Genauigkeit)

### BESCHREIBUNG
1,350 Zugfahrten haben Verspätungen von über 120 Minuten (2 Stunden). Die extremste Verspätung liegt bei **849 Minuten** (14 Stunden). Von diesen haben 32 Züge sogar über 300 Minuten (5+ Stunden) Verspätung. Die Top 10 extremsten Fälle sind fast alle "Bus SEVS4" ohne Stationsnamen.

### BETROFFENE DATEN
- **Spalte:** `delay_in_min`
- **Anzahl Zeilen betroffen:** 1,350 (0.07% der Daten)
- **Schweregrad:** MITTEL
- **Extreme Fälle (>300 min):** 32

### BEWEIS (SQL)
```sql
SELECT
    COUNT(CASE WHEN delay_in_min > 120 THEN 1 END) as extreme_delays,
    COUNT(CASE WHEN delay_in_min > 300 THEN 1 END) as ultra_extreme,
    MAX(delay_in_min) as max_delay
FROM deutsche_bahn_data
```

**Top 3 Extreme:**
1. Bus SEVS4 | N/A | 849 min
2. Bus SEVS4 | N/A | 831 min  
3. Bus SEVS4 | N/A | 763 min

### AUSWIRKUNG
- Frage: Sind Züge mit 14 Stunden Verspätung nicht **storniert**?
- Diese Werte verzerren **Durchschnitts-Berechnungen** massiv
- **Ausreißer-Analyse** zeigt 178,579 statistische Outliers (9% der Daten)
- Vermutung: Viele sollten als `is_canceled = True` markiert sein

### FIX-STRATEGIE
1. **Sofort:** Manuelle Review der 32 Ultra-Extreme (>300 min)
2. **Kurzfristig:** 
   - Business-Rule definieren: Ab wie viel Verspätung gilt ein Zug als storniert?
   - Vorschlag: >180 min = automatisch als canceled markieren
3. **Langfristig:**
   - Bessere Datenerfassung: Stornierungen richtig markieren
   - Separate Kategorie für "verspätet & später storniert"

---

## PROBLEM 4: Stornierte Züge mit Verspätung

### KATEGORIE
**CONSISTENCY** (Konsistenz)

### BESCHREIBUNG
25,220 Zugfahrten sind als storniert markiert (`is_canceled = True`), haben aber gleichzeitig eine Verspätung (`delay_in_min > 0`). Dies ist ein logischer Widerspruch: Ein stornierter Zug kann keine Verspätung haben, da er nie gefahren ist.

### BETROFFENE DATEN
- **Spalten:** `is_canceled`, `delay_in_min`
- **Anzahl Zeilen betroffen:** 25,220 (1.27% der Daten)
- **Schweregrad:** HOCH

### BEWEIS (SQL)
```sql
SELECT
    COUNT(*) as inconsistent_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM deutsche_bahn_data), 2) as prozent
FROM deutsche_bahn_data
WHERE is_canceled = True AND delay_in_min > 0
```

**Ergebnis:** 25,220 inkonsistente Datensätze (1.27%)

### AUSWIRKUNG
- **Logik-Fehler** in allen Analysen die beide Felder nutzen
- **Berichte** sind inkonsistent (storniert ODER verspätet?)
- **Kunden-Information** ist widersprüchlich
- **Regelbasierte Systeme** können fehlerhafte Entscheidungen treffen

### FIX-STRATEGIE
1. **Sofort:** Business-Regel klären:
   - Option A: `is_canceled = True` → `delay_in_min = 0` setzen
   - Option B: Neue Kategorie "verspätet & dann storniert"
2. **Kurzfristig:** Datenbereinigung nach gewählter Regel
3. **Langfristig:**
   - Datenmodell überarbeiten (zusätzliches Feld: cancellation_reason)
   - API-Validierung: IF is_canceled THEN delay_in_min = 0

---

## PROBLEM 5: Doppelte Ride IDs

### KATEGORIE
**UNIQUENESS** (Eindeutigkeit)

### BESCHREIBUNG
30,522 `train_line_ride_id` Werte kommen mehrfach vor. Eine Ride ID sollte eine eindeutige Zugfahrt identifizieren. Duplikate deuten darauf hin, dass entweder die ID-Vergabe fehlerhaft ist oder dass eine Fahrt mehrmals erfasst wurde.

### BETROFFENE DATEN
- **Spalte:** `train_line_ride_id`
- **Anzahl Duplikat-Gruppen:** 30,522
- **Schweregrad:** MITTEL

### BEWEIS (SQL)
```sql
SELECT
    train_line_ride_id,
    COUNT(*) as anzahl
FROM deutsche_bahn_data
WHERE train_line_ride_id IS NOT NULL
GROUP BY train_line_ride_id
HAVING COUNT(*) > 1
LIMIT 10
```

**Zusätzlicher Befund:** 36,989 exakte Duplikate (gleiche Station, Zeit, Zug, Verspätung)

### AUSWIRKUNG
- **Fahrt-basierte Analysen** sind fehlerhaft
- **Doppelzählungen** bei Aggregationen
- **Joining** mit anderen Tabellen über ride_id liefert falsche Ergebnisse
- **Tracking** von einzelnen Zügen unmöglich

### FIX-STRATEGIE
1. **Sofort:** Analyse warum Duplikate entstehen:
   - Mehrfache API-Calls für gleiche Fahrt?
   - Updates die als neue Zeilen gespeichert werden?
2. **Kurzfristig:** 
   - Deduplication: Nur neueste Version pro ride_id behalten
   - Oder: GROUP BY ride_id mit Aggregation
3. **Langfristig:**
   - Primärschlüssel auf ride_id + timestamp
   - Upsert-Logik statt Insert-Only

---

## PROBLEM 6: Fehlende Zeitstempel

### KATEGORIE
**COMPLETENESS** (Vollständigkeit)

### BESCHREIBUNG
Über 44% der Datensätze haben fehlende Zeitstempel für Ankunft oder Abfahrt. Dies ist das größte Datenqualitätsproblem nach Anzahl betroffener Zeilen.

**Fehlende Werte:**
- `arrival_planned_time`: 441,997 (22.27%)
- `arrival_change_time`: 441,914 (22.27%)
- `departure_planned_time`: 442,462 (22.30%)
- `departure_change_time`: 442,377 (22.29%)

### BETROFFENE DATEN
- **Spalten:** Alle Zeit-Spalten
- **Anzahl Zeilen betroffen:** ~442,000 pro Spalte (Gesamt: 884,459 unique Zeilen)
- **Schweregrad:** HOCH
- **Prozent:** 44.57% der Daten

### BEWEIS (SQL)
```sql
SELECT
    COUNT(*) - COUNT(arrival_planned_time) as missing_arr_planned,
    COUNT(*) - COUNT(departure_planned_time) as missing_dep_planned,
    ROUND((COUNT(*) - COUNT(arrival_planned_time)) * 100.0 / COUNT(*), 2) as prozent
FROM deutsche_bahn_data
```

### AUSWIRKUNG
- **Zeit-basierte Analysen** funktionieren nur für 55% der Daten
- **Pünktlichkeits-Berechnungen** sind eingeschränkt
- **Delay-Berechnungen** können nicht validiert werden
- **Durchschnittliche Verspätung** kann nicht nachgerechnet werden

### FIX-STRATEGIE
1. **Sofort:** Verstehen warum Zeitstempel fehlen:
   - Sind das Durchfahrten (keine Ankunft/Abfahrt)?
   - Sind das Endhaltestellen (keine Abfahrt) oder Starthaltestellen (keine Ankunft)?
2. **Kurzfristig:**
   - Dokumentieren welche Datensätze erwartbare NULLs haben
   - Separate Analyse für "vollständige" Datensätze
3. **Langfristig:**
   - Datenmodell klarer definieren
   - Flag-Feld: `is_intermediate_stop`, `is_final_station`, etc.

---

## WEITERE BEFUNDE

### Zeitliche Paradoxe
**928,020 Datensätze** (46.76%) haben `arrival_planned_time < departure_planned_time`. Dies ist bei Durchfahrten normal (Ankunft, dann Abfahrt), aber die hohe Zahl sollte validiert werden.

### Encoding
**25 Bahnhöfe** haben Umlaute in den Namen (ä, ö, ü, ß). Dies ist korrekt für deutsche Städte (München, Düsseldorf, etc.), aber Encoding sollte konsistent UTF-8 sein.

### Statistische Outliers
Nach der **IQR-Methode** sind **178,579 Werte** (9%) statistische Ausreißer bei den Verspätungen. Das ist sehr hoch und deutet auf Datenqualitätsprobleme hin.

---

## VERTEILUNGS-ERKENNTNISSE

### Top-Problematische Bahnhöfe
Nach durchschnittlicher Verspätung:
1. **Köln Hbf:** 6.33 min avg delay (32,098 Fahrten)
2. **München Hbf:** 5.99 min avg delay (64,663 Fahrten)
3. **Düsseldorf Hbf:** 5.86 min avg delay (43,367 Fahrten)

### Top-Problematische Zugtypen
1. **ICE:** 10.29 min avg delay, 6.92% canceled
2. **IC:** 9.33 min avg delay, 9.34% canceled (höchste Ausfallrate!)
3. **ME:** 5.34 min avg delay

### Zeitliche Muster
- **Höchste Verspätungen:** Donnerstag (3.99 min avg)
- **Niedrigste Verspätungen:** Sonntag (3.07 min avg)
- **Meiste Ausfälle:** Freitag (17,962 canceled)

---

## EMPFEHLUNGEN

### 1. SOFORT (Diese Woche)
✅ **Negative Verspätungen korrigieren**
- Alle Werte < -1000 min → Datenfehler → Flag setzen
- Business-Regel definieren für acceptable negative delays

✅ **Storniert + Verspätung Logik klären**
- Meeting mit Daten-Besitzern: Was bedeutet das?
- Entscheidung: Bereinigungsregel festlegen

### 2. KURZFRISTIG (Nächste 2 Wochen)
📊 **Datenbereinigung durchführen**
- Skript schreiben für alle 6 Probleme
- Bereinigte Version als `data-2024-10-cleaned.parquet` exportieren

📋 **Dokumentation erstellen**
- Data Dictionary mit erlaubten Wertebereichen
- Business Rules dokumentieren

### 3. LANGFRISTIG (Nächste 3 Monate)
🔄 **Automatisierung**
- CI/CD Pipeline mit Data Quality Checks
- Automatische Validierung bei jedem Daten-Import
- Alerting wenn Schwellwerte überschritten

🎯 **Datenmodell verbessern**
- Zusätzliche Felder für bessere Semantik
- Klare Definition was NULL bedeutet
- Constraints an der Datenquelle

---

## TECHNISCHE DETAILS

### Verwendete Tools
- **DuckDB** für SQL-Analysen
- **Pandas** für Daten-Exploration
- **Python** für Automatisierung

### Analysierte Zeitraum
Oktober 2024 (01.10.2024 - 31.10.2024)

### Datensatz
- **Quelle:** Deutsche Bahn API (via HuggingFace)
- **Format:** Parquet
- **Größe:** 72 MB
- **Zeilen:** 1,984,484

### Methodik
Alle 5 Dimensionen von Datenqualität wurden systematisch geprüft:
1. ✅ COMPLETENESS (Vollständigkeit)
2. ✅ VALIDITY (Gültigkeit)
3. ✅ CONSISTENCY (Konsistenz)
4. ✅ ACCURACY (Genauigkeit)
5. ✅ UNIQUENESS (Eindeutigkeit)

---

## FAZIT

Die Analyse zeigt **erhebliche Datenqualitätsprobleme** in allen 5 Dimensionen. Mit **6 kritischen Problemen** die über **1 Million Datensätze** betreffen, ist eine **sofortige Bereinigung notwendig** bevor die Daten für Business-Entscheidungen oder Machine Learning verwendet werden.

**Business Impact:** 
- Ohne Bereinigung sind Pünktlichkeits-Reports **unzuverlässig**
- KPIs können **nicht korrekt berechnet** werden
- Presse-Mitteilungen könnten auf **falschen Zahlen** basieren
- ML-Modelle würden **falsche Muster** lernen

**Nächster Schritt:** Meeting mit Data-Besitzern zur Klärung der Business-Regeln und Start der Datenbereinigung.

---

**Ende des Berichts**

*Erstellt am: 8. Dezember 2025*  
*Analysedauer: ~45 Minuten*  
*Analyst: Sebastian*

