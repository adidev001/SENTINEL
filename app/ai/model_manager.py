# app/ai/model_manager.py

import os
import sys
import threading
import requests
from pathlib import Path

# Using application data directory for standalone persistence
if getattr(sys, 'frozen', False):
    # If packaged (EXE), use user's AppData
    app_data = Path(os.getenv('APPDATA')) / "SENTINEL"
else:
    # If development, use project root
    app_data = Path(__file__).resolve().parent.parent.parent

MODELS_DIR = app_data / "models"
MODEL_NAME = "orca-mini-3b-gguf2-q4_0.gguf"
MODEL_URL = "https://gpt4all.io/models/gguf/orca-mini-3b-gguf2-q4_0.gguf" 
# Note: Using a direct link or GPT4All's repo link is required. 
# Providing a known working mirror or official source.

class ModelManager:
    _downloading = False
    _progress = 0.0
    _error = None
    
    @staticmethod
    def is_model_installed() -> bool:
        """Check if the local model exists."""
        return (MODELS_DIR / MODEL_NAME).exists()
    
    @staticmethod
    def get_model_path() -> str:
        """Get the full path to the model file."""
        return str(MODELS_DIR)

    @staticmethod
    def get_download_progress() -> float:
        """Get current download progress (0.0 to 1.0)."""
        return ModelManager._progress

    @staticmethod
    def is_downloading() -> bool:
        return ModelManager._downloading

    @staticmethod
    def start_download(callback=None):
        """Start downloading the model in a background thread."""
        if ModelManager._downloading or ModelManager.is_model_installed():
            return

        ModelManager._downloading = True
        ModelManager._error = None
        ModelManager._progress = 0.0
        
        thread = threading.Thread(target=ModelManager._download_worker, args=(callback,))
        thread.start()

    @staticmethod
    def _download_worker(callback):
        try:
            MODELS_DIR.mkdir(parents=True, exist_ok=True)
            target_file = MODELS_DIR / MODEL_NAME
            
            # Using stream to track progress
            response = requests.get(MODEL_URL, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024 * 1024 # 1MB chunks
            wrote = 0
            
            with open(target_file, 'wb') as f:
                for data in response.iter_content(block_size):
                    wrote += len(data)
                    f.write(data)
                    if total_size > 0:
                        ModelManager._progress = wrote / total_size
            
            ModelManager._progress = 1.0
            
        except Exception as e:
            ModelManager._error = str(e)
            print(f"Download failed: {e}")
            # Clean up partial file
            if (MODELS_DIR / MODEL_NAME).exists():
                os.remove(MODELS_DIR / MODEL_NAME)
        finally:
            ModelManager._downloading = False
            if callback:
                callback()
