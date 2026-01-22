# app/security/command_whitelist.py

from typing import Dict

# Canonical list of allowed commands
COMMAND_WHITELIST: Dict[str, Dict[str, object]] = {
    "analyze_top_processes": {
        "description": "Analyze processes with highest resource usage",
        "impact": "low",
        "requires_confirmation": False
    },
    "open_analytics": {
        "description": "Navigate to analytics view",
        "impact": "low",
        "requires_confirmation": False
    },
    "terminate_process": {
        "description": "Terminate a user-level process",
        "impact": "high",
        "requires_confirmation": True
    }
}
