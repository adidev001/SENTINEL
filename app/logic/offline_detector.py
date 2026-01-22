# app/logic/offline_detector.py

import socket

def is_offline(timeout: float = 1.0) -> bool:
    """
    Detect offline state by attempting a DNS socket connection.
    """
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return False
    except OSError:
        return True
