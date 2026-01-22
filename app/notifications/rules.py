# app/notifications/rules.py

from typing import Dict

def should_notify(decision: Dict[str, object]) -> bool:
    """
    Determine whether a notification should be shown.
    """
    return bool(decision.get("notify", False))
