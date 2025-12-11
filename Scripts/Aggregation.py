import duckdb
import pandas as pd

con = duckdb.connect()
# Dateipfad
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, '..', 'Data', 'deutsche_bahn_data', 'monthly_processed_data', 'data-2024-10.parquet')
result = con.execute(f"SELECT COUNT(*) FROM '{DATA_PATH}'").fetchone()
print(f"Dataset Preview {result[0]:,} rows.")

#Erste Transformation:
result = con.execute(f"""
    SELECT
        COUNT(*) as total_fahrten,
        COUNT(DISTINCT Station_name) as unique_stations,
        COUNT(DISTINCT train_name) as unique_trains,
        ROUND(AVG(delay_in_min),2) as avg_delay,
        ROUND(MAX(delay_in_min),2) as max_delay,
        ROUND(MIN(delay_in_min),2) as min_delay,
        SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) as total_canceled
    FROM '{DATA_PATH}'
 """).fetchdf()
print(result)

############################################################################

############################################################################
result = con.execute(f"""
    SELECT
        train_type,
        COUNT(*) as total_fahrten,
        ROUND(AVG(delay_in_min),2) as avg_delay,
        ROUND(SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) *100.0 / COUNT(*),2) as canceled_rate
        FROM '{DATA_PATH}'
        WHERE train_type IS NOT NULL AND delay_in_min IS NOT NULL
        GROUP BY train_type
        ORDER BY avg_delay DESC
                     
    """).fetchdf()
print(result)
############################################################################
#Durschnitliche Zugverspätung pro Wochentag und Zugtyp
############################################################################
print("\n=== Durchschnittliche Verspätung pro Zugtyp pro Wochentag ===")
result = con.execute(f"""
    SELECT
        train_type,

        CASE DAYOFWEEK(time)
            WHEN 0 THEN 'So'
            WHEN 1 THEN 'Mo'
            WHEN 2 THEN 'Di'
            WHEN 3 THEN 'Mi'
            WHEN 4 THEN 'Do'
            WHEN 5 THEN 'Fr'
            WHEN 6 THEN 'Sa'


        END as wochentag,
        COUNT(*) as fahrten,
        ROUND(AVG(delay_in_min), 2) as avg_delay

    FROM '{DATA_PATH}'
    WHERE train_type IN ('ICE', 'IC', 'RE')
        AND delay_in_min IS NOT NULL

    GROUP BY train_type, DAYOFWEEK(time)
    ORDER BY train_type, DAYOFWEEK(time)

""").fetchdf()
print(result)


############################################################################

############################################################################
result = con.execute(f"""
    SELECT
        Station_name,
        COUNT(*) as total_fahrten,
        ROUND(AVG(delay_in_min),2) as avg_delay,
        FROM '{DATA_PATH}'
        WHERE delay_in_min IS NOT NULL
        GROUP BY Station_name
        Having COUNT(*) > 5000
        ORDER BY avg_delay DESC
        LIMIT 55
""").fetchdf()
print(result)
############################################################################

############################################################################

result = con.execute(f"""
    SELECT
        CASE
            WHEN HOUR(time) BETWEEN 6 AND 9 THEN 'Morning Rush (6-9)'
            WHEN HOUR(time) BETWEEN 16 AND 19 THEN 'Evening Rush (16-19)'
            ELSE 'NORMAL'
        END AS zeitfenster,

        ROUND(AVG(delay_in_min), 2) AS avg_delay,

        ROUND(
            SUM(CASE WHEN delay_in_min > 15 THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
            2
        ) AS problematic_delay_rate,

        ROUND(
            SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
            2
        ) AS canceled_rate

    FROM '{DATA_PATH}'
    WHERE delay_in_min IS NOT NULL
    GROUP BY zeitfenster
    ORDER BY avg_delay DESC
""").fetchdf()
print(result)

############################################################################
#
############################################################################
print("\n=== Wochenende vs. Wochentag ===")
result = con.execute(f"""
    SELECT
        CASE
        When DAYOFWEEK(time) IN (0, 6) THEN 'Weekend'
        ELSE 'Weekday'
        END AS day_type,
        COUNT(*) as total_fahrten,
        ROUND(AVG(delay_in_min),2) as avg_delay,
        ROUND(SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) *100.0 / COUNT(*),2) as canceled_rate
    FROM '{DATA_PATH}'
    WHERE delay_in_min IS NOT NULL
    GROUP BY day_type
""").fetchdf()
print(result)

############################################################################
#
############################################################################

print("\n=== Durchschnittliche Verspätung pro Wochentag (Mo–So) ===")
result = con.execute(f"""
    WITH daily AS (
        SELECT
            DATE(time) AS datum,
            strftime(time, '%w') AS weekday_num,  -- 0=Sonntag
            ROUND(AVG(delay_in_min), 2) AS avg_delay
        FROM '{DATA_PATH}'
        WHERE delay_in_min IS NOT NULL
        GROUP BY datum, weekday_num
    ),
    stats AS (
        SELECT AVG(avg_delay) AS overall_avg FROM daily
    )
    SELECT
        CASE weekday_num
            WHEN '1' THEN 'Mo'
            WHEN '2' THEN 'Di'
            WHEN '3' THEN 'Mi'
            WHEN '4' THEN 'Do'
            WHEN '5' THEN 'Fr'
            WHEN '6' THEN 'Sa'
            WHEN '0' THEN 'So'
        END AS wochentag,
        ROUND(AVG(avg_delay), 2) AS avg_delay,
        ROUND((AVG(avg_delay) - (SELECT overall_avg FROM stats)) 
              / (SELECT overall_avg FROM stats) * 100, 2) AS pct_diff_vs_avg
    FROM daily
    GROUP BY weekday_num
    ORDER BY weekday_num
""").fetchdf()
print(result)
