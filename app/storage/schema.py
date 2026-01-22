# app/storage/schema.py

from app.storage.database import get_connection

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS metrics (
    timestamp TEXT NOT NULL,
    cpu_percent REAL,
    memory_used_mb REAL,
    memory_percent REAL,
    disk_percent REAL,
    read_mb REAL,
    write_mb REAL,
    upload_kb REAL,
    download_kb REAL
);

CREATE TABLE IF NOT EXISTS anomalies (
    timestamp TEXT NOT NULL,
    resource TEXT,
    score INTEGER,
    severity TEXT,
    details TEXT
);
"""

def init_schema() -> None:
    """
    Initialize database schema.
    """
    conn = get_connection()
    cur = conn.cursor()

    for stmt in SCHEMA_SQL.strip().split(";"):
        if stmt.strip():
            cur.execute(stmt)

    conn.commit()
    conn.close()
