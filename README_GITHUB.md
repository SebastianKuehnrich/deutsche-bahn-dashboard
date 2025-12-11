# 🚂 Deutsche Bahn Performance Dashboard

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)](https://duckdb.org/)

**Version 2.0 - Production Ready**

Ein professionelles, interaktives Dashboard zur Analyse von Millionen Zugverspätungen der Deutschen Bahn. Entwickelt mit modernen Data Engineering Praktiken und Production-Ready Code.

![Dashboard Status](https://img.shields.io/badge/Status-Production-success?style=flat-square)
![Python Version](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![License](https://img.shields.io/badge/License-Educational-green?style=flat-square)

---

## 📊 Live Demo

🔗 **Dashboard:** [Auf Railway deployen](https://railway.app) *(siehe Deployment-Anleitung unten)*

---

## ✨ Key Features

### 📈 Business Intelligence
- **Dynamic KPI Cards**: Real-time Metriken für ~2M+ Zugfahrten
- **Rush Hour Analysis**: Identifikation von Stoßzeiten (Morgen 7-9, Abend 16-19)
- **Weekday Patterns**: Beste und schlechteste Wochentage
- **Train Type Comparison**: ICE vs IC vs RE vs RB Performance
- **Advanced Analytics**: Zugtyp × Wochentag Matrix mit Pivot-Tabellen

### 🔧 Technical Excellence (Version 2.0)
- ✅ **SQL Injection Protected**: Parametrisierte Queries für Sicherheit
- ✅ **Type-Safe Code**: Vollständige Type Hints (PEP 484/585)
- ✅ **Context Managers**: Thread-sichere DuckDB-Verbindungen
- ✅ **Smart Caching**: TTL-basierte Query-Optimierung (1h Cache)
- ✅ **Multi-File Support**: Automatische Erkennung aller verfügbaren Monate
- ✅ **Production-Ready**: Umfassendes Error Handling und Validierung
- ✅ **Configurable**: Zentrale Konstanten für Schwellenwerte

### 🎨 User Experience
- 🔄 **Interaktive Filter**: Multi-Select für Zugtypen
- 📅 **Zeitraumauswahl**: Dropdown für verschiedene Monate
- 📊 **Visualisierungen**: Balkendiagramme, Tabellen, Heatmaps
- 🔍 **Debug-Modus**: Ausklappbare Entwickler-Informationen
- 📁 **Rohdaten-Zugriff**: Erste 100 Zeilen zur Inspektion

---

## 🚀 Quick Start

### Option 1: Lokal ausführen

```bash
# 1. Repository klonen
git clone https://github.com/SebastianKuehnrich/deutsche-bahn-dashboard.git
cd deutsche-bahn-dashboard

# 2. Virtual Environment erstellen (empfohlen)
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# 3. Dependencies installieren
pip install -r requirements.txt

# 4. Dashboard starten
streamlit run Scripts/Dashboard.py
```

Das Dashboard öffnet sich automatisch unter **`http://localhost:8501`**

### Option 2: Mit Docker (Optional)

```bash
# Docker Image bauen
docker build -t db-dashboard .

# Container starten
docker run -p 8501:8501 db-dashboard
```

---

## 📁 Projektstruktur

```
deutsche-bahn-dashboard/
├── Scripts/
│   ├── Dashboard.py              # 🎯 Haupt-Dashboard (Version 2.0)
│   ├── transformation.py         # Daten-Transformationen
│   ├── Aggregation.py           # SQL-Aggregationen
│   ├── data_cleaning.py         # Datenbereinigung
│   └── download_data.py         # Daten-Download
├── Data/
│   └── deutsche_bahn_data/
│       └── monthly_processed_data/
│           ├── data-2024-10.parquet
│           └── data-2024-*.parquet  # Weitere Monate
├── .streamlit/
│   └── config.toml              # Dashboard-Theme
├── requirements.txt             # Python Dependencies
├── Procfile                     # Railway Deployment
├── railway.toml                 # Railway Konfiguration
└── README.md                    # Diese Datei
```

---

## 🎯 Dashboard-Bereiche

### 1. **KPI Cards** 📊
Übersicht über die wichtigsten Metriken:
- Total Fahrten
- Durchschnittliche Verspätung
- Pünktlichkeitsrate (≤5 Min)
- Ausfallrate

### 2. **Rush Hour Analyse** 🕐
Vergleich drei Zeitfenster:
- Morgen Rush (7-9 Uhr)
- Abend Rush (16-19 Uhr)
- Normal (restliche Zeiten)

Mit Business Insights und Handlungsempfehlungen.

### 3. **Wochentag Analyse** 📅
- Verspätungs-Muster pro Wochentag
- Ausfallraten pro Wochentag
- Identifikation: Bester vs. Schlechtester Tag

### 4. **Zugtyp Vergleich** 🚄
- **Interaktiver Multi-Select Filter**
- Vergleich beliebiger Zugtypen
- Verspätungs- und Pünktlichkeits-Charts
- Detaillierte Statistik-Tabellen

### 5. **Erweiterte Analyse** 📈
- Zugtyp × Wochentag Matrix
- Pivot-Tabelle für Heatmap-Ansicht
- Flexible Zugtyp-Auswahl

### 6. **Admin-Features** 🔧
- Debug-Informationen (Konfiguration, Pfade)
- Rohdaten-Ansicht (erste 100 Zeilen)
- Performance-Metriken

---

## 🛠️ Technologie-Stack

| Technologie | Verwendung | Warum? |
|-------------|------------|--------|
| **Streamlit** | Web-Framework | Schnelles Prototyping, interaktive Komponenten |
| **DuckDB** | OLAP-Datenbank | Extrem schnell für Analytics auf Parquet-Dateien |
| **Pandas** | Datenverarbeitung | De-facto Standard für Data Science |
| **Python 3.10+** | Programmiersprache | Type Hints, moderne Syntax |
| **Type Hints** | Code-Qualität | Typsicherheit, bessere IDE-Unterstützung |
| **Context Managers** | Ressourcen-Management | Sichere DB-Verbindungen |
| **Parquet** | Datenformat | Spaltenorientiert, komprimiert, schnell |

---

## 📊 Datenquelle

- **Herkunft**: Deutsche Bahn API via HuggingFace
- **Zeitraum**: Oktober 2024 (und weitere Monate)
- **Umfang**: ~2 Millionen Zugfahrten pro Monat
- **Format**: Parquet (spaltenorientiert, komprimiert)
- **Größe**: ~50-100 MB pro Monat (unkomprimiert mehrere GB)

### Daten-Schema
```python
- time: Timestamp
- train_type: String (ICE, IC, RE, RB, S, ...)
- train_name: String
- station_name: String
- delay_in_min: Integer
- is_canceled: Boolean
- arrival_planned_time: Timestamp
- arrival_change_time: Timestamp (optional)
```

---

## 🚢 Deployment

### Railway.app (Empfohlen)

1. **Fork dieses Repository** auf GitHub

2. **Bei Railway anmelden**: [railway.app](https://railway.app)

3. **Neues Projekt erstellen**:
   - "Deploy from GitHub repo"
   - Repository auswählen
   - Railway erkennt automatisch Python/Streamlit

4. **Domain generieren**:
   - Settings → Networking → "Generate Domain"

5. **Fertig!** Dashboard ist live unter `https://dein-projekt.up.railway.app`

### Streamlit Cloud (Alternative)

1. **Bei Streamlit Cloud anmelden**: [share.streamlit.io](https://share.streamlit.io)

2. **App deployen**:
   - Repository auswählen
   - Branch: `main`
   - Main file: `Scripts/Dashboard.py`

3. **Deploy klicken** - Fertig!

### Heroku (Alternative)

```bash
# Heroku CLI installieren und einloggen
heroku login

# App erstellen
heroku create deine-app-name

# Deployen
git push heroku main

# App öffnen
heroku open
```

---

## ⚙️ Konfiguration

### Schwellenwerte anpassen

Datei: `Scripts/Dashboard.py` (Zeilen 24-26)

```python
PUENKTLICH_THRESHOLD_MIN: int = 5   # Pünktlichkeit ≤ X Minuten
VERSPAETET_THRESHOLD_MIN: int = 15  # Verspätet > X Minuten
```

### Rush Hour Zeiten ändern

Datei: `Scripts/Dashboard.py` (Zeilen 51-52)

```python
RUSH_HOUR_MORGEN: tuple[int, int] = (7, 9)   # 7-9 Uhr
RUSH_HOUR_ABEND: tuple[int, int] = (16, 19)  # 16-19 Uhr
```

### Cache TTL anpassen

Datei: `Scripts/Dashboard.py` (Zeile 57)

```python
CACHE_TTL_SECONDS: int = 3600  # 1 Stunde (in Sekunden)
```

### Theme anpassen

Datei: `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#FF6B6B"  # Hauptfarbe
backgroundColor = "#FFFFFF"
```

---

## 🐛 Troubleshooting

### Problem: Daten nicht gefunden
**Lösung**: Prüfe ob Parquet-Dateien vorhanden sind:
```bash
ls Data/deutsche_bahn_data/monthly_processed_data/
```

### Problem: streamlit nicht gefunden
**Lösung**: Installiere Dependencies:
```bash
pip install -r requirements.txt
```

### Problem: Port bereits belegt
**Lösung**: Anderen Port verwenden:
```bash
streamlit run Scripts/Dashboard.py --server.port 8502
```

### Problem: Cache-Probleme
**Lösung**: Cache leeren im Browser mit Taste `C`

### Problem: SQL-Fehler
**Lösung**: Prüfe DuckDB-Version:
```bash
pip install --upgrade duckdb
```

---

## 📚 Dokumentation

- **[Dashboard Start Guide](DASHBOARD_START_GUIDE.md)**: Schnellstart-Anleitung
- **[Detaillierte Docs](README_DASHBOARD.md)**: Vollständige Feature-Dokumentation
- **[Streamlit Docs](https://docs.streamlit.io)**: Streamlit-Framework
- **[DuckDB Docs](https://duckdb.org/docs)**: DuckDB-Datenbank

---

## 🎓 Lernziele & Portfolio

Dieses Projekt demonstriert:

### Data Engineering
- ✅ Verarbeitung großer Datenmengen (2M+ Zeilen)
- ✅ SQL-Abfragen mit DuckDB (OLAP)
- ✅ Parquet-Dateiformat (spaltenorientiert)
- ✅ Parametrisierte Queries (SQL Injection Prevention)

### Software Engineering
- ✅ Type Hints (PEP 484/585)
- ✅ Context Managers
- ✅ Error Handling
- ✅ Caching-Strategien
- ✅ Clean Code & Refactoring

### Data Visualization
- ✅ Interaktive Dashboards
- ✅ Business Intelligence
- ✅ KPI-Design
- ✅ User Experience

### DevOps
- ✅ Git & GitHub
- ✅ Cloud Deployment (Railway/Streamlit Cloud)
- ✅ Environment Management
- ✅ Production-Ready Code

**💼 Portfolio-würdig**: Zeige dieses Projekt in Bewerbungen!

---

## 👨‍💻 Autor

**Sebastian Kühnrich**

Erstellt im Rahmen des Big Data Moduls bei **Morphos GmbH**

- 📧 [Kontakt](mailto:sebastian@example.com)
- 💼 [LinkedIn](https://linkedin.com/in/sebastian-kuehnrich)
- 🐙 [GitHub](https://github.com/SebastianKuehnrich)

---

## 📝 Lizenz

Dieses Projekt wurde zu Bildungszwecken erstellt.

**Datenquelle**: Deutsche Bahn API via HuggingFace  
**Framework**: Open Source (Streamlit, DuckDB, Pandas)

---

## 🙏 Acknowledgments

- **Deutsche Bahn** für die API
- **HuggingFace** für das Hosting der Daten
- **Streamlit** für das großartige Framework
- **DuckDB** für die blitzschnelle Analytics-Engine
- **Morphos GmbH** für das Big Data Modul

---

## 🚀 Nächste Schritte

- [ ] Mehr Monate hinzufügen
- [ ] Stationen-Karte mit Geo-Daten
- [ ] Echtzeit-Updates via API
- [ ] Machine Learning für Verspätungs-Prognosen
- [ ] Export-Funktionalität (CSV, Excel)
- [ ] Email-Alerts für kritische Verspätungen

---

**⭐ Star dieses Repo, wenn es dir gefällt!**

**🐛 Issues oder Verbesserungsvorschläge? [Issue erstellen](https://github.com/SebastianKuehnrich/deutsche-bahn-dashboard/issues)**

---

*Letzte Aktualisierung: Dezember 2025 | Version 2.0*

