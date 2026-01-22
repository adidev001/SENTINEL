import json
import os
from datetime import datetime
from typing import List, Dict

# Use absolute path to ensure file is found regardless of CWD
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up one level from 'storage' to 'app', then up to root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHAT_HISTORY_FILE = os.path.join(ROOT_DIR, "chat_history.json")

class ChatHistory:
    """Manage persistent chat message history."""
    
    def __init__(self):
        self.messages = self.load_history()
    
    def load_history(self) -> List[Dict]:
        """Load chat history from file."""
        if os.path.exists(CHAT_HISTORY_FILE):
            try:
                with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading chat history: {e}")
        return []
    
    def save_history(self):
        """Save chat history to file."""
        try:
            # Keep only last 100 messages
            if len(self.messages) > 100:
                self.messages = self.messages[-100:]
            
            with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving chat history: {e}")
    
    def add_message(self, text: str, sender: str):
        """Add a message to history."""
        self.messages.append({
            "text": text,
            "sender": sender,
            "timestamp": datetime.now().isoformat()
        })
        self.save_history()
    
    def clear_history(self):
        """Clear all chat history."""
        self.messages = []
        self.save_history()
    
    def get_messages(self) -> List[Dict]:
        """Get all messages."""
        return self.messages
