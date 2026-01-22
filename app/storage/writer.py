# app/storage/writer.py

from typing import Dict
from app.storage.database import get_connection

def write_metrics(timestamp: str, data: Dict[str, float]) -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO metrics (
            timestamp,
            cpu_percent,
            memory_used_mb,
            memory_percent,
            disk_percent,
            read_mb,
            write_mb,
            upload_kb,
            download_kb,
            gpu_percent
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp,
        data.get("cpu_percent"),
        data.get("memory_used_mb"),
        data.get("memory_percent"),
        data.get("disk_percent"),
        data.get("read_mb"),
        data.get("write_mb"),
        data.get("upload_kb"),
        data.get("download_kb"),
        data.get("gpu_percent"),
    ))

    conn.commit()
    conn.close()
