# app/storage/reader.py

from typing import List, Dict
from app.storage.database import get_connection

def read_recent_metrics(minutes: int) -> List[Dict]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM metrics
        WHERE timestamp >= datetime('now', ?)
        ORDER BY timestamp ASC
    """, (f"-{minutes} minutes",))

    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows
