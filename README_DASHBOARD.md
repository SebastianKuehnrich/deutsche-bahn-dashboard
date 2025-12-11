# 🚂 Deutsche Bahn Performance Dashboard

**Version 2.0 - Refactored & Improved**

Ein professionelles, interaktives Dashboard zur Analyse von Zugverspätungen der Deutschen Bahn. Verarbeitet mehrere Millionen Datenpunkte mit modernster Datenbank-Technologie.

## ✨ Features

### Core Features
- **KPI Cards**: Übersicht über Gesamtfahrten, durchschnittliche Verspätung, Pünktlichkeit und Ausfälle
- **Dynamische Zeitraumauswahl**: Dropdown-Menü zur Auswahl verschiedener Monate
- **Rush Hour Analyse**: Vergleich der Verspätungen zwischen Morgen-Rush, Abend-Rush und normalen Zeiten
- **Wochentag Analyse**: Identifikation des besten und schlechtesten Wochentags
- **Zugtyp Vergleich**: Interaktiver Filter zum Vergleich verschiedener Zugtypen (ICE, IC, RE, RB, S, etc.)
- **Erweiterte Analyse**: Verspätungen pro Zugtyp pro Wochentag mit Pivot-Tabelle

### Version 2.0 Improvements
- ✅ **SQL Injection Protection**: Parametrisierte Queries für Sicherheit
- ✅ **Context Manager**: Thread-sichere DuckDB-Verbindungen
- ✅ **Type Hints**: Vollständig typisierter Code (PEP 484)
- ✅ **Konfigurierbare Konstanten**: Zentrale Schwellenwerte und Parameter
- ✅ **Multi-File Support**: Automatische Erkennung aller verfügbaren Daten-Monate
- ✅ **Error Handling**: Robuste Fehlerbehandlung an allen kritischen Stellen
- ✅ **Cache-Optimierung**: TTL-basiertes Caching für bessere Performance
- ✅ **Debug-Modus**: Ausklappbare Debug-Informationen für Entwickler

## 🚀 Installation

### Voraussetzungen
- Python 3.8+
- pip

### Setup

1. Repository klonen oder Dateien herunterladen

2. Virtuelle Umgebung erstellen (optional aber empfohlen):
```bash
python -m venv .venv
```

3. Virtuelle Umgebung aktivieren:
- Windows: `.venv\Scripts\activate`
- Linux/Mac: `source .venv/bin/activate`

4. Dependencies installieren:
```bash
pip install -r requirements.txt
```

## 📊 Dashboard starten

Führe im Projektverzeichnis aus:
```bash
streamlit run Scripts/Dashboard.py
```

Das Dashboard öffnet sich automatisch im Browser unter `http://localhost:8501`

## 📁 Projektstruktur

```
Big_Data_Deutsche_Bahn/
├── Scripts/
│   ├── Dashboard.py          # Hauptdashboard-Datei
│   ├── transformation.py     # Transformations-Scripts
│   ├── Aggregation.py        # Aggregations-Scripts
│   └── ...
├── Data/
│   └── deutsche_bahn_data/
│       └── monthly_processed_data/
│           └── data-2024-10.parquet
├── requirements.txt          # Python Dependencies
└── README_DASHBOARD.md       # Diese Datei
```

## 🎯 Verwendete Technologien

- **Streamlit**: Web-Dashboard Framework mit interaktiven Komponenten
- **DuckDB**: Hochperformante SQL-Datenbank für analytische Abfragen (OLAP)
- **Pandas**: Datenmanipulation und -analyse
- **Python 3.10+**: Moderne Programmiersprache mit Type Hints
- **Context Managers**: Sichere Ressourcenverwaltung
- **Type Hints**: Vollständige Typsicherheit (PEP 484, PEP 585)

## 📈 Datenquelle

- **Quelle**: Deutsche Bahn API via HuggingFace
- **Zeitraum**: Oktober 2024
- **Datenpunkte**: ~2 Millionen Zugfahrten
- **Format**: Parquet

## 🔍 Analysen im Dashboard

### 1. Key Performance Indicators (KPIs)
- Total Fahrten
- Durchschnittliche Verspätung
- Pünktlichkeitsrate (≤5 Minuten)
- Ausfallrate

### 2. Rush Hour Analyse
Vergleicht drei Zeitfenster:
- Morgen Rush (7-9 Uhr)
- Abend Rush (16-19 Uhr)
- Normal (andere Zeiten)

### 3. Wochentag Analyse
- Verspätungen pro Wochentag
- Ausfälle pro Wochentag
- Identifikation des besten und schlechtesten Tags

### 4. Zugtyp Vergleich
Interaktiver Filter zum Vergleich von:
- ICE (Intercity Express)
- IC (Intercity)
- RE (Regional Express)
- RB (Regionalbahn)
- S (S-Bahn)
- Und weitere Zugtypen

### 5. Erweiterte Analyse
- Durchschnittliche Verspätung pro Zugtyp pro Wochentag
- Pivot-Tabelle für flexible Zugtyp-Auswahl
- Heatmap-Ansicht zur Visualisierung von Mustern

### 6. Admin-Features (Version 2.0)
- **Debug-Informationen**: Ausklappbare Konfigurationsdetails
- **Rohdaten-Ansicht**: Erste 100 Zeilen zur Inspektion
- **Zeitraum-Wechsel**: Dropdown zur Auswahl verschiedener Monate
- **Performance-Metriken**: Cache TTL und Query-Optimierungen

## 🚢 Deployment

Das Dashboard kann auf verschiedenen Plattformen deployed werden:

### Railway.app
1. Repository auf GitHub pushen
2. Bei Railway.app anmelden
3. "Deploy from GitHub" wählen
4. Repository auswählen
5. Railway erkennt automatisch Streamlit

### Streamlit Cloud
1. Repository auf GitHub pushen
2. Bei share.streamlit.io anmelden
3. App deployen

## 👨‍💻 Autor

Erstellt im Rahmen des Big Data Moduls bei Morphos GmbH

**Datum**: Dezember 2025

## 📝 Lizenz

Dieses Projekt wurde zu Bildungszwecken erstellt.

## 🐛 Troubleshooting

### Dashboard lädt nicht
- Prüfe ob alle Dependencies installiert sind: `pip install -r requirements.txt`
- Prüfe ob der Datenpfad korrekt ist

### Fehlende Daten
- Stelle sicher, dass die Parquet-Datei im richtigen Ordner liegt
- Pfad: `Data/deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet`

### Import Fehler
- Aktiviere die virtuelle Umgebung
- Installiere alle Requirements neu

## 💡 Tipps

- Das Dashboard nutzt Caching (`@st.cache_data`) für bessere Performance
- Queries werden nur einmal ausgeführt und dann gecached
- Bei Datenänderungen: Cache leeren mit "C" im Browser oder "Clear cache" im Streamlit-Menü

## 🎓 Lernziele

Dieses Projekt demonstriert:

### Data Engineering
- Data Engineering mit Python
- SQL-Abfragen mit DuckDB (OLAP-Datenbank)
- Parametrisierte Queries (SQL Injection Prevention)
- Multi-Source Datenverarbeitung

### Software Engineering
- Type Hints und moderne Python-Features
- Context Manager für Ressourcenverwaltung
- Error Handling und Validierung
- Cache-Strategien mit TTL
- Konfigurierbare Konstanten

### Data Visualization & BI
- Dashboard-Erstellung mit Streamlit
- Interaktive Datenvisualisierung
- Business Intelligence und KPIs
- User Experience Design

### Best Practices
- Clean Code und Refactoring
- Dokumentation und Kommentare
- Deployment-Ready Code
- Production-Grade Error Handling

