# Tag 12: Deutsche Bahn Dashboard - Projekt

**Mittwoch, 10. Dezember 2025**
**Zeit:** 1.5 - 2 Stunden (Selbstständig)
**Ziel:** Ein interaktives Dashboard bauen und live deployen

---

## 🎯 DEIN ZIEL

Du baust ein **Deutsche Bahn Performance Dashboard** das:

1. Daten transformiert (was wir heute gelernt haben)
2. Business KPIs zeigt
3. Interaktive Filter hat
4. LIVE im Internet deployed ist

**Am Ende hast du einen LINK den du teilen kannst.**

Das ist Portfolio-Material. Das zeigst du im Bewerbungsgespräch.

---

## 📋 WAS DU BAUEN WIRST

| Komponente | Beschreibung |
|------------|--------------|
| **KPI Cards** | Total Fahrten, Avg Delay, Pünktlich %, Canceled % |
| **Rush Hour Analyse** | Vergleich Morgen Rush vs Normal vs Abend Rush |
| **Wochentag Analyse** | Welcher Tag ist am schlimmsten? |
| **Zugtyp Vergleich** | ICE vs IC vs RE Performance |
| **Filter** | Nach Zugtyp filtern können |
| **Deployment** | Live auf Railway.app |

---

## 🛠️ VORBEREITUNG

### Was du brauchst:

- [ ] Python installiert
- [ ] DuckDB installiert (`pip install duckdb`)
- [ ] Streamlit installiert (`pip install streamlit`)
- [ ] Railway Account (kostenlos): https://railway.app
- [ ] Deutsche Bahn Daten (hast du schon)

### Ordnerstruktur:

Erstelle einen neuen Ordner: `db_dashboard`

```
db_dashboard/
├── app.py                 # Dein Dashboard Code
├── requirements.txt       # Dependencies
└── deutsche_bahn_data/
    └── monthly_processed_data/
        └── data-2024-10.parquet
```

**WICHTIG:** Kopiere den `deutsche_bahn_data` Ordner in deinen neuen `db_dashboard` Ordner!

---

## SCHRITT 1: Setup (10 Minuten)

### 1.1 requirements.txt erstellen

Erstelle die Datei `requirements.txt`:

```
streamlit==1.29.0
duckdb==0.9.2
pandas==2.1.3
```

### 1.2 Basis app.py erstellen

Erstelle `app.py`:

```python
# ============================================================
#
#   DEUTSCHE BAHN PERFORMANCE DASHBOARD
#   Tag 12 - Data Transformation Projekt
#
# ============================================================

import streamlit as st
import duckdb
import pandas as pd

# ============================================================
# KONFIGURATION
# ============================================================

# Seiten-Konfiguration (MUSS als erstes kommen!)
st.set_page_config(
    page_title="Deutsche Bahn Dashboard",
    page_icon="🚂",
    layout="wide"
)

# Datenpfad
DATA_PATH = './deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet'

# DuckDB Connection
@st.cache_resource
def get_connection():
    return duckdb.connect()

con = get_connection()

# ============================================================
# TITEL
# ============================================================

st.title("🚂 Deutsche Bahn Performance Dashboard")
st.markdown("**Datenquelle:** Oktober 2024 | ~2 Millionen Zugfahrten")
st.markdown("---")

# ============================================================
# TEST: Daten laden
# ============================================================

# Quick Test ob Daten da sind
try:
    test = con.execute(f"SELECT COUNT(*) FROM '{DATA_PATH}'").fetchone()
    st.success(f"✅ Daten geladen: {test[0]:,} Zeilen")
except Exception as e:
    st.error(f"❌ Fehler beim Laden: {e}")
    st.stop()
```

### 1.3 Testen ob es funktioniert

Öffne Terminal im `db_dashboard` Ordner:

```bash
streamlit run app.py
```

**Erwartetes Ergebnis:** Browser öffnet sich, du siehst den Titel und "✅ Daten geladen: 1,984,484 Zeilen"

### Troubleshooting Schritt 1:

| Problem | Lösung |
|---------|--------|
| `ModuleNotFoundError: streamlit` | `pip install streamlit` |
| `ModuleNotFoundError: duckdb` | `pip install duckdb` |
| `Fehler beim Laden` | Prüfe ob DATA_PATH korrekt ist |
| Browser öffnet nicht | Gehe manuell zu `http://localhost:8501` |

---

## SCHRITT 2: KPI Cards (20 Minuten)

### 2.1 KPIs berechnen

Füge nach dem Test-Block hinzu:

```python
# ============================================================
# KPI BERECHNUNG
# ============================================================

@st.cache_data
def get_kpis():
    """Berechnet die Haupt-KPIs"""
    result = con.execute(f"""
    SELECT
        COUNT(*) as total_fahrten,
        ROUND(AVG(delay_in_min), 2) as avg_delay,
        ROUND(SUM(CASE WHEN delay_in_min <= 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as puenktlich_pct,
        ROUND(SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as canceled_pct,
        MIN(time) as start_datum,
        MAX(time) as end_datum
    FROM '{DATA_PATH}'
    WHERE delay_in_min IS NOT NULL
    """).fetchone()

    return {
        'total_fahrten': result[0],
        'avg_delay': result[1],
        'puenktlich_pct': result[2],
        'canceled_pct': result[3],
        'start_datum': result[4],
        'end_datum': result[5]
    }

kpis = get_kpis()
```

### 2.2 KPI Cards anzeigen

Füge hinzu:

```python
# ============================================================
# KPI CARDS ANZEIGEN
# ============================================================

st.subheader("📊 Key Performance Indicators")

# 4 Spalten für KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Fahrten",
        value=f"{kpis['total_fahrten']:,}"
    )

with col2:
    st.metric(
        label="Ø Verspätung",
        value=f"{kpis['avg_delay']} min"
    )

with col3:
    st.metric(
        label="Pünktlich (≤5 min)",
        value=f"{kpis['puenktlich_pct']}%"
    )

with col4:
    st.metric(
        label="Ausgefallen",
        value=f"{kpis['canceled_pct']}%"
    )

st.markdown("---")
```

### Was passiert hier?

| Code | Erklärung |
|------|-----------|
| `@st.cache_data` | Speichert Ergebnis im Cache - lädt nicht jedes Mal neu |
| `st.columns(4)` | Erstellt 4 Spalten nebeneinander |
| `st.metric()` | Zeigt eine KPI-Card mit Label und Wert |
| `f"{kpis['total_fahrten']:,}"` | Formatiert Zahl mit Tausender-Trennzeichen |

### Erwartetes Ergebnis:

Du siehst 4 Karten nebeneinander:
- Total Fahrten: 1,984,484
- Ø Verspätung: ~3.7 min
- Pünktlich: ~75%
- Ausgefallen: ~5.4%

---

## SCHRITT 3: Rush Hour Analyse (20 Minuten)

### 3.1 Rush Hour Daten holen

Füge hinzu:

```python
# ============================================================
# RUSH HOUR ANALYSE
# ============================================================

@st.cache_data
def get_rush_hour_stats():
    """Vergleicht Rush Hour mit normalen Zeiten"""
    result = con.execute(f"""
    SELECT
        CASE
            WHEN HOUR(time) BETWEEN 7 AND 9 THEN 'Morgen Rush (7-9)'
            WHEN HOUR(time) BETWEEN 16 AND 19 THEN 'Abend Rush (16-19)'
            ELSE 'Normal'
        END as zeitfenster,
        COUNT(*) as fahrten,
        ROUND(AVG(delay_in_min), 2) as avg_delay,
        ROUND(SUM(CASE WHEN delay_in_min > 15 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as verspaetet_pct,
        ROUND(SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as canceled_pct
    FROM '{DATA_PATH}'
    WHERE delay_in_min IS NOT NULL
    GROUP BY 1
    ORDER BY avg_delay DESC
    """).fetchdf()

    return result

rush_hour_df = get_rush_hour_stats()
```

### 3.2 Rush Hour Chart anzeigen

Füge hinzu:

```python
st.subheader("🕐 Rush Hour Analyse")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Durchschnittliche Verspätung nach Tageszeit**")
    st.bar_chart(
        rush_hour_df.set_index('zeitfenster')['avg_delay'],
        color='#FF6B6B'
    )

with col2:
    st.markdown("**Detaillierte Statistiken**")
    st.dataframe(
        rush_hour_df,
        hide_index=True,
        use_container_width=True
    )

# Business Insight Box
worst_time = rush_hour_df.iloc[0]['zeitfenster']
worst_delay = rush_hour_df.iloc[0]['avg_delay']

st.info(f"""
**💡 Business Insight:**
{worst_time} hat die höchste durchschnittliche Verspätung ({worst_delay} min).
Empfehlung: Zusätzliche Kapazitäten in diesem Zeitfenster einplanen.
""")

st.markdown("---")
```

### Was ist neu hier?

| Code | Erklärung |
|------|-----------|
| `st.bar_chart()` | Erstellt automatisch ein Balkendiagramm |
| `.set_index('zeitfenster')` | Setzt die Spalte als X-Achse |
| `st.dataframe()` | Zeigt DataFrame als interaktive Tabelle |
| `st.info()` | Blaue Info-Box für Insights |
| `rush_hour_df.iloc[0]` | Erste Zeile (höchster Wert wegen ORDER BY DESC) |

---

## SCHRITT 4: Wochentag Analyse (15 Minuten)

### 4.1 Wochentag Daten holen

Füge hinzu:

```python
# ============================================================
# WOCHENTAG ANALYSE
# ============================================================

@st.cache_data
def get_weekday_stats():
    """Analysiert Verspätungen nach Wochentag"""
    result = con.execute(f"""
    SELECT
        CASE DAYOFWEEK(time)
            WHEN 0 THEN 'Sonntag'
            WHEN 1 THEN 'Montag'
            WHEN 2 THEN 'Dienstag'
            WHEN 3 THEN 'Mittwoch'
            WHEN 4 THEN 'Donnerstag'
            WHEN 5 THEN 'Freitag'
            WHEN 6 THEN 'Samstag'
            ELSE 'Unbekannt'
        END as wochentag,
        DAYOFWEEK(time) as tag_nummer,
        COUNT(*) as fahrten,
        ROUND(AVG(delay_in_min), 2) as avg_delay,
        ROUND(SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as canceled_pct
    FROM '{DATA_PATH}'
    WHERE delay_in_min IS NOT NULL
    GROUP BY DAYOFWEEK(time)
    ORDER BY DAYOFWEEK(time)
    """).fetchdf()

    return result

weekday_df = get_weekday_stats()
```

### 4.2 Wochentag Chart anzeigen

Füge hinzu:

```python
st.subheader("📅 Wochentag Analyse")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Verspätung pro Wochentag**")
    st.bar_chart(
        weekday_df.set_index('wochentag')['avg_delay'],
        color='#4ECDC4'
    )

with col2:
    st.markdown("**Ausfälle pro Wochentag**")
    st.bar_chart(
        weekday_df.set_index('wochentag')['canceled_pct'],
        color='#FFE66D'
    )

# Bester und schlechtester Tag
best_day = weekday_df.loc[weekday_df['avg_delay'].idxmin()]
worst_day = weekday_df.loc[weekday_df['avg_delay'].idxmax()]

col1, col2 = st.columns(2)
with col1:
    st.success(f"✅ **Bester Tag:** {best_day['wochentag']} ({best_day['avg_delay']} min)")
with col2:
    st.error(f"❌ **Schlechtester Tag:** {worst_day['wochentag']} ({worst_day['avg_delay']} min)")

st.markdown("---")
```

---

## SCHRITT 5: Zugtyp Vergleich mit Filter (20 Minuten)

### 5.1 Zugtyp Daten holen

Füge hinzu:

```python
# ============================================================
# ZUGTYP ANALYSE MIT FILTER
# ============================================================

@st.cache_data
def get_train_types():
    """Holt alle verfügbaren Zugtypen"""
    result = con.execute(f"""
    SELECT DISTINCT train_type
    FROM '{DATA_PATH}'
    WHERE train_type IS NOT NULL
    ORDER BY train_type
    """).fetchdf()
    return result['train_type'].tolist()

@st.cache_data
def get_train_type_stats(selected_types):
    """Analysiert Performance nach Zugtyp"""
    # Konvertiere Liste zu SQL IN clause
    types_str = ", ".join([f"'{t}'" for t in selected_types])

    result = con.execute(f"""
    SELECT
        train_type,
        COUNT(*) as fahrten,
        ROUND(AVG(delay_in_min), 2) as avg_delay,
        ROUND(SUM(CASE WHEN delay_in_min <= 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as puenktlich_pct,
        ROUND(SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as canceled_pct
    FROM '{DATA_PATH}'
    WHERE train_type IN ({types_str})
      AND delay_in_min IS NOT NULL
    GROUP BY train_type
    ORDER BY avg_delay DESC
    """).fetchdf()

    return result
```

### 5.2 Filter und Chart anzeigen

Füge hinzu:

```python
st.subheader("🚄 Zugtyp Vergleich")

# Alle Zugtypen holen
all_train_types = get_train_types()

# Filter erstellen
selected_types = st.multiselect(
    "Wähle Zugtypen zum Vergleichen:",
    options=all_train_types,
    default=['ICE', 'IC', 'RE', 'RB', 'S']  # Standard-Auswahl
)

# Nur anzeigen wenn mindestens ein Typ gewählt
if selected_types:
    train_type_df = get_train_type_stats(selected_types)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Durchschnittliche Verspätung**")
        st.bar_chart(
            train_type_df.set_index('train_type')['avg_delay'],
            color='#9B59B6'
        )

    with col2:
        st.markdown("**Pünktlichkeitsrate**")
        st.bar_chart(
            train_type_df.set_index('train_type')['puenktlich_pct'],
            color='#2ECC71'
        )

    # Detaillierte Tabelle
    st.markdown("**Detaillierte Statistiken:**")
    st.dataframe(
        train_type_df,
        hide_index=True,
        use_container_width=True
    )
else:
    st.warning("⚠️ Bitte wähle mindestens einen Zugtyp aus.")

st.markdown("---")
```

### Was ist neu hier?

| Code | Erklärung |
|------|-----------|
| `st.multiselect()` | Dropdown mit Mehrfachauswahl |
| `default=['ICE', 'IC', 'RE']` | Vorausgewählte Werte |
| `", ".join([f"'{t}'" ...])` | Baut SQL IN clause: `'ICE', 'IC', 'RE'` |
| `if selected_types:` | Prüft ob Liste nicht leer |

---

## SCHRITT 6: Footer und Finale Touches (10 Minuten)

### 6.1 Footer hinzufügen

Füge am Ende hinzu:

```python
# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown("""
### 📝 Über dieses Dashboard

**Datenquelle:** Deutsche Bahn API via HuggingFace
**Zeitraum:** Oktober 2024
**Datenpunkte:** ~2 Millionen Zugfahrten

**Erstellt von:** [DEIN NAME]
**Datum:** Dezember 2025
**Technologien:** Python, DuckDB, Streamlit, Railway

---

*Dieses Dashboard wurde im Rahmen des Big Data Moduls bei Morphos GmbH erstellt.*
""")

# Rohdaten anzeigen (optional, ausklappbar)
with st.expander("🔍 Rohdaten anzeigen"):
    sample = con.execute(f"SELECT * FROM '{DATA_PATH}' LIMIT 100").fetchdf()
    st.dataframe(sample)
```

---

## SCHRITT 7: Lokal Testen (5 Minuten)

### 7.1 Finale Tests

Stoppe den Server (Ctrl+C) und starte neu:

```bash
streamlit run app.py
```

### Checkliste - Was funktionieren MUSS:

- [ ] KPI Cards zeigen Zahlen
- [ ] Rush Hour Chart wird angezeigt
- [ ] Wochentag Chart wird angezeigt
- [ ] Zugtyp Filter funktioniert
- [ ] Keine Fehlermeldungen in rot

### Troubleshooting Schritt 7:

| Problem | Lösung |
|---------|--------|
| Leere Charts | Prüfe ob DATA_PATH korrekt ist |
| `KeyError` | Prüfe Spaltennamen in deinen Queries |
| `BinderException` | SQL Syntax Fehler - prüfe Kommas und Klammern |
| Seite lädt ewig | Entferne `@st.cache_data` zum Debuggen |
| Filter zeigt nichts | Prüfe ob `selected_types` nicht leer ist |

---

## SCHRITT 8: Deployment auf Railway (20 Minuten)

### 8.1 GitHub Repository erstellen

1. Gehe zu https://github.com
2. Klicke "New Repository"
3. Name: `deutsche-bahn-dashboard`
4. Public auswählen
5. Erstellen

### 8.2 Code hochladen

Im Terminal (im `db_dashboard` Ordner):

```bash
git init
git add .
git commit -m "Initial commit - Deutsche Bahn Dashboard"
git branch -M main
git remote add origin https://github.com/DEIN_USERNAME/deutsche-bahn-dashboard.git
git push -u origin main
```

### 8.3 Railway Setup

1. Gehe zu https://railway.app
2. Login mit GitHub
3. Klicke "New Project"
4. Wähle "Deploy from GitHub repo"
5. Wähle dein `deutsche-bahn-dashboard` Repository
6. Railway erkennt automatisch dass es Python ist

### 8.4 Railway Konfiguration

Railway braucht noch ein paar Einstellungen.

**Erstelle Datei: `Procfile`** (ohne Endung!)

```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**Erstelle Datei: `railway.toml`**

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0"
```

### 8.5 Erneut pushen

```bash
git add .
git commit -m "Add Railway config"
git push
```

### 8.6 Railway Deployment

1. Gehe zurück zu Railway
2. Klicke auf dein Projekt
3. Gehe zu "Settings" → "Networking"
4. Klicke "Generate Domain"
5. Warte 2-3 Minuten bis Deployment fertig ist

**FERTIG!** Du hast jetzt eine URL wie: `https://deutsche-bahn-dashboard-production.up.railway.app`

### Troubleshooting Deployment:

| Problem | Lösung |
|---------|--------|
| Build failed | Prüfe `requirements.txt` - alle Packages drin? |
| App crashed | Prüfe Logs in Railway Dashboard |
| Port Error | Prüfe `Procfile` - `$PORT` muss da sein |
| Daten nicht gefunden | Daten müssen im Git Repo sein! |
| 502 Bad Gateway | Warte 2-3 Minuten, Railway startet noch |

---

## 📁 VOLLSTÄNDIGER CODE

Falls etwas nicht funktioniert, hier der komplette `app.py`:

```python
# ============================================================
#
#   DEUTSCHE BAHN PERFORMANCE DASHBOARD
#   Tag 12 - Data Transformation Projekt
#
# ============================================================

import streamlit as st
import duckdb
import pandas as pd

# ============================================================
# KONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Deutsche Bahn Dashboard",
    page_icon="🚂",
    layout="wide"
)

DATA_PATH = './deutsche_bahn_data/monthly_processed_data/data-2024-10.parquet'

@st.cache_resource
def get_connection():
    return duckdb.connect()

con = get_connection()

# ============================================================
# TITEL
# ============================================================

st.title("🚂 Deutsche Bahn Performance Dashboard")
st.markdown("**Datenquelle:** Oktober 2024 | ~2 Millionen Zugfahrten")
st.markdown("---")

# Test
try:
    test = con.execute(f"SELECT COUNT(*) FROM '{DATA_PATH}'").fetchone()
except Exception as e:
    st.error(f"❌ Fehler beim Laden: {e}")
    st.stop()

# ============================================================
# KPI BERECHNUNG
# ============================================================

@st.cache_data
def get_kpis():
    result = con.execute(f"""
    SELECT
        COUNT(*) as total_fahrten,
        ROUND(AVG(delay_in_min), 2) as avg_delay,
        ROUND(SUM(CASE WHEN delay_in_min <= 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as puenktlich_pct,
        ROUND(SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as canceled_pct
    FROM '{DATA_PATH}'
    WHERE delay_in_min IS NOT NULL
    """).fetchone()

    return {
        'total_fahrten': result[0],
        'avg_delay': result[1],
        'puenktlich_pct': result[2],
        'canceled_pct': result[3]
    }

kpis = get_kpis()

# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Fahrten", value=f"{kpis['total_fahrten']:,}")

with col2:
    st.metric(label="Ø Verspätung", value=f"{kpis['avg_delay']} min")

with col3:
    st.metric(label="Pünktlich (≤5 min)", value=f"{kpis['puenktlich_pct']}%")

with col4:
    st.metric(label="Ausgefallen", value=f"{kpis['canceled_pct']}%")

st.markdown("---")

# ============================================================
# RUSH HOUR ANALYSE
# ============================================================

@st.cache_data
def get_rush_hour_stats():
    result = con.execute(f"""
    SELECT
        CASE
            WHEN HOUR(time) BETWEEN 7 AND 9 THEN 'Morgen Rush (7-9)'
            WHEN HOUR(time) BETWEEN 16 AND 19 THEN 'Abend Rush (16-19)'
            ELSE 'Normal'
        END as zeitfenster,
        COUNT(*) as fahrten,
        ROUND(AVG(delay_in_min), 2) as avg_delay,
        ROUND(SUM(CASE WHEN delay_in_min > 15 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as verspaetet_pct,
        ROUND(SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as canceled_pct
    FROM '{DATA_PATH}'
    WHERE delay_in_min IS NOT NULL
    GROUP BY 1
    ORDER BY avg_delay DESC
    """).fetchdf()
    return result

rush_hour_df = get_rush_hour_stats()

st.subheader("🕐 Rush Hour Analyse")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Durchschnittliche Verspätung nach Tageszeit**")
    st.bar_chart(rush_hour_df.set_index('zeitfenster')['avg_delay'], color='#FF6B6B')

with col2:
    st.markdown("**Detaillierte Statistiken**")
    st.dataframe(rush_hour_df, hide_index=True, use_container_width=True)

worst_time = rush_hour_df.iloc[0]['zeitfenster']
worst_delay = rush_hour_df.iloc[0]['avg_delay']

st.info(f"💡 **Business Insight:** {worst_time} hat die höchste durchschnittliche Verspätung ({worst_delay} min).")

st.markdown("---")

# ============================================================
# WOCHENTAG ANALYSE
# ============================================================

@st.cache_data
def get_weekday_stats():
    result = con.execute(f"""
    SELECT
        CASE DAYOFWEEK(time)
            WHEN 0 THEN 'Sonntag'
            WHEN 1 THEN 'Montag'
            WHEN 2 THEN 'Dienstag'
            WHEN 3 THEN 'Mittwoch'
            WHEN 4 THEN 'Donnerstag'
            WHEN 5 THEN 'Freitag'
            WHEN 6 THEN 'Samstag'
            ELSE 'Unbekannt'
        END as wochentag,
        COUNT(*) as fahrten,
        ROUND(AVG(delay_in_min), 2) as avg_delay,
        ROUND(SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as canceled_pct
    FROM '{DATA_PATH}'
    WHERE delay_in_min IS NOT NULL
    GROUP BY DAYOFWEEK(time)
    ORDER BY DAYOFWEEK(time)
    """).fetchdf()
    return result

weekday_df = get_weekday_stats()

st.subheader("📅 Wochentag Analyse")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Verspätung pro Wochentag**")
    st.bar_chart(weekday_df.set_index('wochentag')['avg_delay'], color='#4ECDC4')

with col2:
    st.markdown("**Ausfälle pro Wochentag**")
    st.bar_chart(weekday_df.set_index('wochentag')['canceled_pct'], color='#FFE66D')

best_day = weekday_df.loc[weekday_df['avg_delay'].idxmin()]
worst_day = weekday_df.loc[weekday_df['avg_delay'].idxmax()]

col1, col2 = st.columns(2)
with col1:
    st.success(f"✅ **Bester Tag:** {best_day['wochentag']} ({best_day['avg_delay']} min)")
with col2:
    st.error(f"❌ **Schlechtester Tag:** {worst_day['wochentag']} ({worst_day['avg_delay']} min)")

st.markdown("---")

# ============================================================
# ZUGTYP ANALYSE
# ============================================================

@st.cache_data
def get_train_types():
    result = con.execute(f"""
    SELECT DISTINCT train_type FROM '{DATA_PATH}'
    WHERE train_type IS NOT NULL ORDER BY train_type
    """).fetchdf()
    return result['train_type'].tolist()

@st.cache_data
def get_train_type_stats(selected_types):
    types_str = ", ".join([f"'{t}'" for t in selected_types])
    result = con.execute(f"""
    SELECT
        train_type,
        COUNT(*) as fahrten,
        ROUND(AVG(delay_in_min), 2) as avg_delay,
        ROUND(SUM(CASE WHEN delay_in_min <= 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as puenktlich_pct,
        ROUND(SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as canceled_pct
    FROM '{DATA_PATH}'
    WHERE train_type IN ({types_str}) AND delay_in_min IS NOT NULL
    GROUP BY train_type
    ORDER BY avg_delay DESC
    """).fetchdf()
    return result

st.subheader("🚄 Zugtyp Vergleich")

all_train_types = get_train_types()

selected_types = st.multiselect(
    "Wähle Zugtypen:",
    options=all_train_types,
    default=['ICE', 'IC', 'RE', 'RB', 'S']
)

if selected_types:
    train_type_df = get_train_type_stats(selected_types)

    col1, col2 = st.columns(2)

    with col1:
        st.bar_chart(train_type_df.set_index('train_type')['avg_delay'], color='#9B59B6')

    with col2:
        st.bar_chart(train_type_df.set_index('train_type')['puenktlich_pct'], color='#2ECC71')

    st.dataframe(train_type_df, hide_index=True, use_container_width=True)
else:
    st.warning("⚠️ Bitte wähle mindestens einen Zugtyp.")

st.markdown("---")

# ============================================================
# FOOTER
# ============================================================

st.markdown("""
### 📝 Über dieses Dashboard

**Datenquelle:** Deutsche Bahn API via HuggingFace
**Zeitraum:** Oktober 2024
**Datenpunkte:** ~2 Millionen Zugfahrten

---
*Big Data Modul - Morphos GmbH*
""")

with st.expander("🔍 Rohdaten anzeigen"):
    sample = con.execute(f"SELECT * FROM '{DATA_PATH}' LIMIT 100").fetchdf()
    st.dataframe(sample)
```

---

## ✅ CHECKLISTE - BIST DU FERTIG?

- [ ] Dashboard läuft lokal ohne Fehler
- [ ] KPI Cards zeigen korrekte Zahlen
- [ ] Rush Hour Analyse funktioniert
- [ ] Wochentag Analyse funktioniert
- [ ] Zugtyp Filter funktioniert
- [ ] Code ist auf GitHub
- [ ] Dashboard ist auf Railway deployed
- [ ] Du hast einen LIVE LINK

---

## 🎯 WAS DU GELERNT HAST

| Skill | Was du gemacht hast |
|-------|---------------------|
| **Data Transformation** | HOUR(), DAYOFWEEK(), CASE WHEN |
| **Aggregation** | GROUP BY, COUNT, AVG, SUM |
| **Business KPIs** | Pünktlichkeit, Ausfallrate berechnet |
| **Kategorisierung** | Rush Hour Zeitfenster erstellt |
| **Dashboard** | Streamlit App gebaut |
| **Deployment** | Live auf Railway deployed |

---

## 🚀 BONUS: Zeig es im Bewerbungsgespräch

Wenn du gefragt wirst: "Haben Sie Erfahrung mit Datenanalyse?"

> "Ja, ich habe ein Dashboard gebaut das 2 Millionen Deutsche Bahn Fahrten analysiert.
> Ich habe Data Transformation mit SQL gemacht, KPIs berechnet, und das ganze live deployed.
> Hier ist der Link: [DEIN LINK]"

**Das ist beeindruckend. Das zeigt echte Skills.**

---

## 💪 VIEL ERFOLG!

Du hast alles was du brauchst. Nimm dir Zeit. Schritt für Schritt.

Wenn etwas nicht funktioniert: Lies die Fehlermeldung. Google sie. Frag.

**Du schaffst das!** 🚀
