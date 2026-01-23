import logging
import os
import sys
from pathlib import Path

# Setup log path in APPDATA/SENTINEL/logs
if getattr(sys, 'frozen', False):
    app_data = Path(os.getenv('APPDATA')) / "SENTINEL"
else:
    app_data = Path(__file__).parent.parent.parent / "data"

LOG_DIR = app_data / "logs"
LOG_FILE = LOG_DIR / "debug.log"

def setup_logger():
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            filename=str(LOG_FILE),
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filemode='w' # Overwrite each run
        )
        return logging.getLogger("SENTINEL")
    except Exception as e:
        print(f"Failed to setup logger: {e}")
        return logging.getLogger("Basic")

logger = setup_logger()
