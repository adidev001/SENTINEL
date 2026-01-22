# app/storage/retention.py

from app.storage.database import get_connection

def prune_old_data(days: int = 10) -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM metrics
        WHERE timestamp < datetime('now', ?)
    """, (f"-{days} days",))

    cur.execute("""
        DELETE FROM anomalies
        WHERE timestamp < datetime('now', ?)
    """, (f"-{days} days",))

    conn.commit()
    conn.close()
