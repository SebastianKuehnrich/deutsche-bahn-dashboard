# ============================================================
#
#   DEUTSCHE BAHN PERFORMANCE DASHBOARD
#   Tag 12 - Data Transformation Projekt
#   Version 2.0 - Refactored & Improved
#
# ============================================================

from __future__ import annotations

import streamlit as st
import duckdb
from duckdb import DuckDBPyConnection
import pandas as pd
import os
from glob import glob
from contextlib import contextmanager
from typing import Any

# ============================================================
# KONSTANTEN & KONFIGURATION
# ============================================================

# Schwellenwerte (zentral definiert)
PUENKTLICH_THRESHOLD_MIN: int = 5
VERSPAETET_THRESHOLD_MIN: int = 15

# Wochentag-Mapping (DuckDB DAYOFWEEK: 0=Sonntag)
WOCHENTAGE: dict[int, str] = {
    0: "Sonntag",
    1: "Montag",
    2: "Dienstag",
    3: "Mittwoch",
    4: "Donnerstag",
    5: "Freitag",
    6: "Samstag",
}

WOCHENTAGE_KURZ: dict[int, str] = {
    0: "So",
    1: "Mo",
    2: "Di",
    3: "Mi",
    4: "Do",
    5: "Fr",
    6: "Sa",
}

# Zeitfenster für Rush Hour Analyse
RUSH_HOUR_MORGEN: tuple[int, int] = (7, 9)
RUSH_HOUR_ABEND: tuple[int, int] = (16, 19)

# Standard-Zugtypen für Filter
DEFAULT_TRAIN_TYPES: list[str] = ["ICE", "IC", "RE", "RB", "S"]

# Cache TTL (Time To Live) in Sekunden
CACHE_TTL_SECONDS: int = 3600  # 1 Stunde

# ============================================================
# SEITEN-KONFIGURATION (MUSS als erstes kommen!)
# ============================================================

st.set_page_config(
    page_title="Deutsche Bahn Dashboard",
    page_icon="🚂",
    layout="wide"
)

# ============================================================
# DATENPFAD-MANAGEMENT
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "Data", "deutsche_bahn_data", "monthly_processed_data")


def get_available_data_files() -> list[str]:
    """Findet alle verfügbaren Parquet-Dateien und gibt sie sortiert zurück."""
    pattern = os.path.join(DATA_DIR, "data-*.parquet")
    files = glob(pattern)

    # Sortiere nach Dateiname (chronologisch: data-2024-01, data-2024-02, ...)
    files.sort(reverse=True)  # Neueste zuerst

    return files


def extract_month_label(filepath: str) -> str:
    """Extrahiert ein lesbares Label aus dem Dateipfad (z.B. 'Oktober 2024')."""
    filename = os.path.basename(filepath)
    # Format: data-2024-10.parquet
    try:
        parts = filename.replace("data-", "").replace(".parquet", "").split("-")
        year, month = parts[0], int(parts[1])
        month_names = {
            1: "Januar", 2: "Februar", 3: "März", 4: "April",
            5: "Mai", 6: "Juni", 7: "Juli", 8: "August",
            9: "September", 10: "Oktober", 11: "November", 12: "Dezember"
        }
        return f"{month_names.get(month, 'Unbekannt')} {year}"
    except (IndexError, ValueError):
        return filename


# ============================================================
# DATENBANK-CONNECTION (Thread-Safe)
# ============================================================

@contextmanager
def get_db_connection():
    """Context Manager für sichere DuckDB-Verbindung."""
    conn = duckdb.connect()
    try:
        yield conn
    finally:
        conn.close()


def execute_query(query: str, params: list[Any] | None = None) -> pd.DataFrame:
    """
    Führt eine Query sicher aus mit optionalen Parametern.
    Verhindert SQL Injection durch parametrisierte Queries.
    """
    with get_db_connection() as conn:
        if params:
            return conn.execute(query, params).fetchdf()
        return conn.execute(query).fetchdf()


def execute_query_single(query: str, params: list[Any] | None = None) -> tuple | None:
    """Führt eine Query aus und gibt eine einzelne Zeile zurück."""
    with get_db_connection() as conn:
        if params:
            return conn.execute(query, params).fetchone()
        return conn.execute(query).fetchone()


# ============================================================
# TITEL & DATENAUSWAHL
# ============================================================

st.title("🚂 Deutsche Bahn Performance Dashboard")

# Dynamische Dateiauswahl
available_files = get_available_data_files()

if not available_files:
    st.error("❌ Keine Datendateien gefunden! Bitte prüfe den Pfad: " + DATA_DIR)
    st.stop()

# Dropdown für Monatsauswahl
file_options = {extract_month_label(f): f for f in available_files}
selected_month = st.selectbox(
    "📅 Zeitraum auswählen:",
    options=list(file_options.keys()),
    index=0  # Neuester Monat als Default
)

DATA_PATH = file_options[selected_month]

st.markdown(f"**Datenquelle:** {selected_month}")
st.markdown("---")

# ============================================================
# DATEN-VALIDIERUNG
# ============================================================

try:
    result = execute_query_single(f"SELECT COUNT(*) FROM '{DATA_PATH}'")
    if result:
        row_count = result[0]
        st.success(f"✅ Daten geladen: {row_count:,} Zeilen")
    else:
        st.error("❌ Keine Daten gefunden.")
        st.stop()
except Exception as e:
    st.error(f"❌ Fehler beim Laden der Daten: {e}")
    st.info("💡 Prüfe ob die Datei existiert: " + DATA_PATH)
    st.stop()


# ============================================================
# KPI BERECHNUNG
# ============================================================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_kpis(data_path: str) -> dict[str, int | float | str]:
    """
    Berechnet die Haupt-KPIs für das Dashboard.

    Returns:
        Dictionary mit total_fahrten, avg_delay, puenktlich_pct,
        canceled_pct, start_datum, end_datum
    """
    query = f"""
    SELECT
        COUNT(*) as total_fahrten,
        ROUND(AVG(delay_in_min), 2) as avg_delay,
        ROUND(
            SUM(CASE WHEN delay_in_min <= {PUENKTLICH_THRESHOLD_MIN} THEN 1 ELSE 0 END) 
            * 100.0 / COUNT(*), 1
        ) as puenktlich_pct,
        ROUND(
            SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) 
            * 100.0 / COUNT(*), 2
        ) as canceled_pct,
        MIN(time) as start_datum,
        MAX(time) as end_datum
    FROM '{data_path}'
    WHERE delay_in_min IS NOT NULL
    """

    result = execute_query_single(query)

    if not result:
        return {
            "total_fahrten": 0,
            "avg_delay": 0.0,
            "puenktlich_pct": 0.0,
            "canceled_pct": 0.0,
            "start_datum": "N/A",
            "end_datum": "N/A",
        }

    return {
        "total_fahrten": result[0],
        "avg_delay": result[1] or 0.0,
        "puenktlich_pct": result[2] or 0.0,
        "canceled_pct": result[3] or 0.0,
        "start_datum": result[4],
        "end_datum": result[5],
    }


# KPIs laden mit Error Handling
try:
    kpis = get_kpis(DATA_PATH)
except Exception as e:
    st.error(f"❌ Fehler bei KPI-Berechnung: {e}")
    st.stop()

# ============================================================
# KPI CARDS ANZEIGEN
# ============================================================

st.subheader("📊 Key Performance Indicators")

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
        label=f"Pünktlich (≤{PUENKTLICH_THRESHOLD_MIN} min)",
        value=f"{kpis['puenktlich_pct']}%"
    )

with col4:
    st.metric(
        label="Ausgefallen",
        value=f"{kpis['canceled_pct']}%"
    )

st.markdown("---")


# ============================================================
# RUSH HOUR ANALYSE
# ============================================================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_rush_hour_stats(data_path: str) -> pd.DataFrame:
    """
    Vergleicht Rush Hour Zeiten mit normalen Zeiten.
    Nutzt konfigurierbare Zeitfenster aus Konstanten.
    """
    morgen_start, morgen_end = RUSH_HOUR_MORGEN
    abend_start, abend_end = RUSH_HOUR_ABEND

    query = f"""
    SELECT
        CASE
            WHEN HOUR(time) BETWEEN {morgen_start} AND {morgen_end} 
                THEN 'Morgen Rush ({morgen_start}-{morgen_end})'
            WHEN HOUR(time) BETWEEN {abend_start} AND {abend_end} 
                THEN 'Abend Rush ({abend_start}-{abend_end})'
            ELSE 'Normal'
        END as zeitfenster,
        COUNT(*) as fahrten,
        ROUND(AVG(delay_in_min), 2) as avg_delay,
        ROUND(
            SUM(CASE WHEN delay_in_min > {VERSPAETET_THRESHOLD_MIN} THEN 1 ELSE 0 END) 
            * 100.0 / COUNT(*), 2
        ) as verspaetet_pct,
        ROUND(
            SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) 
            * 100.0 / COUNT(*), 2
        ) as canceled_pct
    FROM '{data_path}'
    WHERE delay_in_min IS NOT NULL
    GROUP BY 1
    ORDER BY avg_delay DESC
    """

    return execute_query(query)


rush_hour_df = get_rush_hour_stats(DATA_PATH)

st.subheader("🕐 Rush Hour Analyse")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Durchschnittliche Verspätung nach Tageszeit**")
    st.bar_chart(
        rush_hour_df.set_index("zeitfenster")["avg_delay"],
        color="#FF6B6B"
    )

with col2:
    st.markdown("**Detaillierte Statistiken**")
    st.dataframe(
        rush_hour_df,
        hide_index=True,
        use_container_width=True
    )

# Business Insight Box
if not rush_hour_df.empty:
    worst_time = rush_hour_df.iloc[0]["zeitfenster"]
    worst_delay = rush_hour_df.iloc[0]["avg_delay"]

    st.info(f"""
    **💡 Business Insight:**
    {worst_time} hat die höchste durchschnittliche Verspätung ({worst_delay} min).
    Empfehlung: Zusätzliche Kapazitäten in diesem Zeitfenster einplanen.
    """)

st.markdown("---")


# ============================================================
# WOCHENTAG ANALYSE
# ============================================================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_weekday_stats(data_path: str) -> pd.DataFrame:
    """
    Analysiert Verspätungen nach Wochentag.
    Nutzt zentrales Wochentag-Mapping.
    """
    # Erstelle CASE-Statement aus dem Dictionary
    case_parts = [f"WHEN {num} THEN '{name}'" for num, name in WOCHENTAGE.items()]
    case_statement = "CASE DAYOFWEEK(time) " + " ".join(case_parts) + " END"

    query = f"""
    SELECT
        {case_statement} as wochentag,
        DAYOFWEEK(time) as tag_nummer,
        COUNT(*) as fahrten,
        ROUND(AVG(delay_in_min), 2) as avg_delay,
        ROUND(
            SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) 
            * 100.0 / COUNT(*), 2
        ) as canceled_pct
    FROM '{data_path}'
    WHERE delay_in_min IS NOT NULL
    GROUP BY DAYOFWEEK(time)
    ORDER BY DAYOFWEEK(time)
    """

    return execute_query(query)


weekday_df = get_weekday_stats(DATA_PATH)

st.subheader("📅 Wochentag Analyse")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Verspätung pro Wochentag**")
    st.bar_chart(
        weekday_df.set_index("wochentag")["avg_delay"],
        color="#4ECDC4"
    )

with col2:
    st.markdown("**Ausfälle pro Wochentag**")
    st.bar_chart(
        weekday_df.set_index("wochentag")["canceled_pct"],
        color="#FFE66D"
    )

# Bester und schlechtester Tag (mit Fehlerbehandlung)
if not weekday_df.empty:
    best_day = weekday_df.loc[weekday_df["avg_delay"].idxmin()]
    worst_day = weekday_df.loc[weekday_df["avg_delay"].idxmax()]

    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ **Bester Tag:** {best_day['wochentag']} ({best_day['avg_delay']} min)")
    with col2:
        st.error(f"❌ **Schlechtester Tag:** {worst_day['wochentag']} ({worst_day['avg_delay']} min)")

st.markdown("---")


# ============================================================
# ZUGTYP ANALYSE MIT FILTER (SQL Injection sicher)
# ============================================================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_train_types(data_path: str) -> list[str]:
    """Holt alle verfügbaren Zugtypen aus den Daten."""
    query = f"""
    SELECT DISTINCT train_type
    FROM '{data_path}'
    WHERE train_type IS NOT NULL
    ORDER BY train_type
    """
    result = execute_query(query)
    return result["train_type"].tolist()


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_train_type_stats(data_path: str, selected_types: tuple[str, ...]) -> pd.DataFrame:
    """
    Analysiert Performance nach Zugtyp.

    WICHTIG: selected_types wird als Tuple übergeben für Cache-Kompatibilität.
    Die Query ist SQL Injection sicher durch Verwendung von list_value().
    """
    if not selected_types:
        return pd.DataFrame()

    # DuckDB-sichere Methode: Liste als Parameter
    # Wir erstellen eine temporäre Liste in DuckDB
    types_list = list(selected_types)
    placeholders = ", ".join(["?" for _ in types_list])

    query = f"""
    SELECT
        train_type,
        COUNT(*) as fahrten,
        ROUND(AVG(delay_in_min), 2) as avg_delay,
        ROUND(
            SUM(CASE WHEN delay_in_min <= {PUENKTLICH_THRESHOLD_MIN} THEN 1 ELSE 0 END) 
            * 100.0 / COUNT(*), 1
        ) as puenktlich_pct,
        ROUND(
            SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) 
            * 100.0 / COUNT(*), 2
        ) as canceled_pct
    FROM '{data_path}'
    WHERE train_type IN ({placeholders})
      AND delay_in_min IS NOT NULL
    GROUP BY train_type
    ORDER BY avg_delay DESC
    """

    return execute_query(query, types_list)


st.subheader("🚄 Zugtyp Vergleich")

# Alle Zugtypen holen
all_train_types = get_train_types(DATA_PATH)

# Validiere Default-Auswahl gegen tatsächlich vorhandene Zugtypen
valid_defaults = [t for t in DEFAULT_TRAIN_TYPES if t in all_train_types]

# Filter erstellen
selected_types = st.multiselect(
    "Wähle Zugtypen zum Vergleichen:",
    options=all_train_types,
    default=valid_defaults if valid_defaults else all_train_types[:5]
)

# Nur anzeigen wenn mindestens ein Typ gewählt
if selected_types:
    # Tuple für Cache-Kompatibilität
    train_type_df = get_train_type_stats(DATA_PATH, tuple(selected_types))

    if not train_type_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Durchschnittliche Verspätung**")
            st.bar_chart(
                train_type_df.set_index("train_type")["avg_delay"],
                color="#9B59B6"
            )

        with col2:
            st.markdown("**Pünktlichkeitsrate**")
            st.bar_chart(
                train_type_df.set_index("train_type")["puenktlich_pct"],
                color="#2ECC71"
            )

        # Detaillierte Tabelle
        st.markdown("**Detaillierte Statistiken:**")
        st.dataframe(
            train_type_df,
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("⚠️ Keine Daten für die ausgewählten Zugtypen gefunden.")
else:
    st.warning("⚠️ Bitte wähle mindestens einen Zugtyp aus.")

st.markdown("---")

# ============================================================
# ERWEITERTE ANALYSE: Zugtyp × Wochentag
# ============================================================

st.subheader("📊 Erweiterte Analyse: Zugtyp × Wochentag")


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_train_weekday_stats(data_path: str, train_types: tuple[str, ...]) -> pd.DataFrame:
    """
    Durchschnittliche Verspätung pro Zugtyp pro Wochentag.
    SQL Injection sicher durch parametrisierte Query.
    """
    if not train_types:
        return pd.DataFrame()

    # Erstelle CASE-Statement für Wochentage
    case_parts = [f"WHEN {num} THEN '{name}'" for num, name in WOCHENTAGE_KURZ.items()]
    case_statement = "CASE DAYOFWEEK(time) " + " ".join(case_parts) + " END"

    types_list = list(train_types)
    placeholders = ", ".join(["?" for _ in types_list])

    query = f"""
    SELECT
        train_type,
        {case_statement} as wochentag,
        DAYOFWEEK(time) as tag_nummer,
        COUNT(*) as fahrten,
        ROUND(AVG(delay_in_min), 2) as avg_delay
    FROM '{data_path}'
    WHERE train_type IN ({placeholders})
        AND delay_in_min IS NOT NULL
    GROUP BY train_type, DAYOFWEEK(time)
    ORDER BY train_type, DAYOFWEEK(time)
    """

    return execute_query(query, types_list)


# Auswahl für erweiterte Analyse
extended_analysis_types = st.multiselect(
    "Zugtypen für erweiterte Analyse:",
    options=all_train_types,
    default=["ICE", "IC", "RE"] if all(t in all_train_types for t in ["ICE", "IC", "RE"]) else all_train_types[:3],
    key="extended_analysis"
)

if extended_analysis_types:
    train_weekday_df = get_train_weekday_stats(DATA_PATH, tuple(extended_analysis_types))

    if not train_weekday_df.empty:
        st.markdown(f"**Verspätungen nach Zugtyp und Wochentag ({', '.join(extended_analysis_types)}):**")
        st.dataframe(
            train_weekday_df.drop(columns=["tag_nummer"]),
            hide_index=True,
            use_container_width=True
        )

        # Pivot-Tabelle für Heatmap-Ansicht
        pivot_df = train_weekday_df.pivot(
            index="train_type",
            columns="wochentag",
            values="avg_delay"
        )

        # Sortiere Spalten nach Wochentag-Reihenfolge
        weekday_order = list(WOCHENTAGE_KURZ.values())
        pivot_df = pivot_df[[col for col in weekday_order if col in pivot_df.columns]]

        st.markdown("**Heatmap-Ansicht (Durchschnittliche Verspätung in Minuten):**")
        st.dataframe(pivot_df, use_container_width=True)
    else:
        st.info("Keine Daten für die ausgewählten Zugtypen verfügbar.")
else:
    st.info("Wähle mindestens einen Zugtyp für die erweiterte Analyse.")

st.markdown("---")

# ============================================================
# FOOTER
# ============================================================

st.markdown(f"""
### 📝 Über dieses Dashboard

**Datenquelle:** Deutsche Bahn API via HuggingFace  
**Aktueller Zeitraum:** {selected_month}  
**Datenpunkte:** {kpis['total_fahrten']:,} Zugfahrten

**Konfiguration:**
- Pünktlichkeitsschwelle: ≤{PUENKTLICH_THRESHOLD_MIN} Minuten
- Verspätungsschwelle: >{VERSPAETET_THRESHOLD_MIN} Minuten
- Cache TTL: {CACHE_TTL_SECONDS // 60} Minuten

**Erstellt von:** Big Data Team  
**Technologien:** Python, DuckDB, Streamlit

---

*Dieses Dashboard wurde im Rahmen des Big Data Moduls bei Morpheus GmbH erstellt.*
""")

# Rohdaten anzeigen (optional, ausklappbar)
with st.expander("🔍 Rohdaten anzeigen (erste 100 Zeilen)"):
    try:
        sample = execute_query(f"SELECT * FROM '{DATA_PATH}' LIMIT 100")
        st.dataframe(sample, use_container_width=True)
    except Exception as e:
        st.error(f"Fehler beim Laden der Rohdaten: {e}")

# Debug-Info (nur für Entwickler)
with st.expander("🔧 Debug-Informationen"):
    st.write("**Datenpfad:**", DATA_PATH)
    st.write("**Verfügbare Dateien:**", len(available_files))
    st.write("**Verfügbare Zugtypen:**", len(all_train_types))
    st.write("**Konfigurierte Konstanten:**")
    st.json({
        "PUENKTLICH_THRESHOLD_MIN": PUENKTLICH_THRESHOLD_MIN,
        "VERSPAETET_THRESHOLD_MIN": VERSPAETET_THRESHOLD_MIN,
        "RUSH_HOUR_MORGEN": RUSH_HOUR_MORGEN,
        "RUSH_HOUR_ABEND": RUSH_HOUR_ABEND,
        "CACHE_TTL_SECONDS": CACHE_TTL_SECONDS,
    })