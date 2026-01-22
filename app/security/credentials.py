# app/security/credentials.py

import keyring
from typing import Optional

SERVICE_NAME = "SysSentinelAI"

def store_api_key(key: str) -> None:
    keyring.set_password(SERVICE_NAME, "cloud_api_key", key)

def get_api_key() -> Optional[str]:
    return keyring.get_password(SERVICE_NAME, "cloud_api_key")

def delete_api_key() -> None:
    keyring.delete_password(SERVICE_NAME, "cloud_api_key")
