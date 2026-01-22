# app/security/permissions.py

CRITICAL_PROCESS_NAMES = {
    "System",
    "System Idle Process",
    "csrss.exe",
    "wininit.exe",
    "winlogon.exe",
    "services.exe",
    "lsass.exe"
}

def is_process_terminable(process_name: str) -> bool:
    """
    Determine if a process is safe to terminate.
    """
    if not process_name:
        return False

    return process_name.lower() not in {
        name.lower() for name in CRITICAL_PROCESS_NAMES
    }
