# app/notifications/toast.py

from typing import List

def show_toast(
    title: str,
    message: str,
    actions: List[str] | None = None
) -> None:
    """
    Display a Windows toast notification.

    NOTE:
    Actual Windows Toast integration will be implemented later.
    This function is a stable interface placeholder.
    """
    # Placeholder implementation
    # Replace with real Windows Toast API integration
    print(f"[TOAST] {title}: {message}")
    if actions:
        print(f"[ACTIONS] {', '.join(actions)}")
