# app/security/validator.py

from typing import Dict
from app.security.command_whitelist import COMMAND_WHITELIST

def validate_command(command_id: str) -> Dict[str, object]:
    """
    Validate a command against the whitelist.
    """
    if command_id not in COMMAND_WHITELIST:
        raise ValueError(f"Command '{command_id}' is not allowed")

    return COMMAND_WHITELIST[command_id]
