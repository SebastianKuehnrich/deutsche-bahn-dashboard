# 🚀 Dashboard Quick Start Guide

## Dashboard starten

### Option 1: Mit Python direkt
```bash
# Im Projektverzeichnis
C:\Users\sebas\PycharmProjects\Big_Data_Deutsche_Bahn\.venv\Scripts\streamlit.exe run Scripts/Dashboard.py
```

### Option 2: Mit aktivierter venv
```bash
# 1. venv aktivieren
C:\Users\sebas\PycharmProjects\Big_Data_Deutsche_Bahn\.venv\Scripts\activate

# 2. Dashboard starten
streamlit run Scripts/Dashboard.py
```

## Was du im Dashboard siehst

### 1️⃣ KPI Cards (oben)
- Total Fahrten: ~1,98 Millionen
- Durchschnittliche Verspätung: ~3.7 Minuten
- Pünktlichkeitsrate: ~75%
- Ausfallrate: ~5.4%

### 2️⃣ Rush Hour Analyse
- Balkendiagramm: Verspätungen nach Tageszeit
- Tabelle: Detaillierte Statistiken
- Insight-Box: Business Empfehlungen

### 3️⃣ Wochentag Analyse
- 2 Balkendiagramme: Verspätungen und Ausfälle
- Grüne Box: Bester Wochentag
- Rote Box: Schlechtester Wochentag

### 4️⃣ Zugtyp Vergleich
- **Interaktiver Filter**: Wähle Zugtypen aus
- Standard: ICE, IC, RE, RB, S
- 2 Diagramme: Verspätung und Pünktlichkeit
- Detaillierte Tabelle

### 5️⃣ Erweiterte Analyse
- Tabelle: ICE, IC, RE pro Wochentag
- Pivot-Tabelle: Heatmap-Ansicht

### 6️⃣ Footer
- Informationen zum Dashboard
- Ausklappbar: Rohdaten (erste 100 Zeilen)

## 🎨 Features die du testen solltest

### Interaktive Filter
1. Scrolle zu "🚄 Zugtyp Vergleich"
2. Klicke auf das Dropdown-Menü
3. Wähle verschiedene Zugtypen aus
4. Diagramme aktualisieren sich automatisch

### Rohdaten anzeigen
1. Scrolle ganz nach unten
2. Klicke auf "🔍 Rohdaten anzeigen"
3. Siehe die ersten 100 Zeilen der Daten

## 🔄 Dashboard aktualisieren

Wenn du Änderungen am Code machst:
1. Speichere die Datei (Strg+S)
2. Im Browser: Klicke "Rerun" oben rechts
3. Oder: Drücke "R" im Browser

## 🛑 Dashboard stoppen

Im Terminal:
- Drücke `Strg + C`

## 📊 Erwartete Ergebnisse

### KPIs
- Total Fahrten: 1,984,484
- Avg Delay: ~3.7 min
- Pünktlich: ~75%
- Ausgefallen: ~5.4%

### Rush Hour
- Abend Rush hat normalerweise höchste Verspätung
- Normal-Zeit ist am besten

### Wochentag
- Sonntag ist oft der beste Tag
- Freitag/Montag oft schlechter

### Zugtyp
- ICE: ~4-5 min Verspätung
- S-Bahn: ~2-3 min Verspätung
- RE/RB: ~3-4 min Verspätung

## ❗ Troubleshooting

### Problem: streamlit nicht gefunden
**Lösung**: Installiere streamlit
```bash
C:\Users\sebas\PycharmProjects\Big_Data_Deutsche_Bahn\.venv\Scripts\pip.exe install streamlit
```

### Problem: Daten nicht gefunden
**Lösung**: Prüfe ob Parquet-Datei existiert:
```
Data/deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet
```

### Problem: Browser öffnet nicht automatisch
**Lösung**: Öffne manuell: `http://localhost:8501`

### Problem: Port bereits belegt
**Lösung**: Verwende anderen Port:
```bash
streamlit run Scripts/Dashboard.py --server.port 8502
```

## 🎯 Nächste Schritte

### 1. Lokales Testen
- [ ] Dashboard starten
- [ ] Alle Bereiche durchklicken
- [ ] Filter ausprobieren
- [ ] Screenshots machen für Portfolio

### 2. Code verstehen
- [ ] Öffne Dashboard.py
- [ ] Lies die Kommentare
- [ ] Verstehe die SQL-Queries
- [ ] Probiere Änderungen aus

### 3. Erweitern (optional)
- [ ] Füge neue Analysen hinzu
- [ ] Ändere Farben im Theme
- [ ] Füge weitere Filter hinzu
- [ ] Exportiere Daten als CSV

### 4. Deployment (optional)
- [ ] Push zu GitHub
- [ ] Deploy auf Railway.app
- [ ] Teile den Link

## 💡 Tipps

1. **Performance**: Dashboard nutzt Caching - Queries laufen nur einmal
2. **Datenänderung**: Drücke "C" im Browser um Cache zu leeren
3. **Debugging**: Füge `st.write()` hinzu um Werte anzuzeigen
4. **Styling**: Ändere Farben in `.streamlit/config.toml`

## 📚 Weitere Ressourcen

- Streamlit Docs: https://docs.streamlit.io
- DuckDB Docs: https://duckdb.org/docs
- Streamlit Gallery: https://streamlit.io/gallery

---

**Viel Erfolg! 🚀**

