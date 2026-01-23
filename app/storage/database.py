# app/storage/database.py

import sqlite3
from pathlib import Path

import os

# Use APPDATA for persistent storage
app_data = Path(os.getenv("APPDATA")) / "SENTINEL"
DB_PATH = app_data / "data" / "sys_sentinel.db"

def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    cpu_percent REAL,
    memory_used_mb REAL,
    memory_percent REAL,
    disk_percent REAL,
    read_mb REAL,
    write_mb REAL,
    upload_kb REAL,
    download_kb REAL,
    gpu_percent REAL
);

CREATE TABLE IF NOT EXISTS anomaly_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    anomaly_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    score REAL,
    description TEXT,
    resource_values TEXT
);

CREATE TABLE IF NOT EXISTS alert_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    title TEXT,
    message TEXT,
    acknowledged INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS overload_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    confidence REAL,
    time_to_overload REAL,
    primary_stressors TEXT,
    predicted_values TEXT,
    actual_outcome TEXT,
    prevention_taken TEXT
);

CREATE TABLE IF NOT EXISTS system_stress_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    stress_index REAL,
    cpu_stress REAL,
    memory_stress REAL,
    disk_stress REAL,
    network_stress REAL,
    gpu_stress REAL
);
"""

def initialize_database() -> None:
    conn = get_connection()
    try:
        # Check if gpu_percent column exists, if not add it
        try:
            cur = conn.cursor()
            cur.execute("SELECT gpu_percent FROM metrics LIMIT 1")
        except sqlite3.OperationalError:
            # Column missing, add it
            try:
                conn.execute("ALTER TABLE metrics ADD COLUMN gpu_percent REAL")
                print("Migrated database: added gpu_percent column")
            except:
                pass # Table might not exist yet, createscript will handle it

        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()
