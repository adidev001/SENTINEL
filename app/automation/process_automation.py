import psutil
import json
import os
from datetime import datetime
from typing import List, Dict

AUTOMATION_CONFIG_FILE = "automation_config.json"
RESTART_HISTORY_FILE = "restart_history.json"

class ProcessAutomation:
    """Automated process management and restart."""
    
    def __init__(self):
        self.config = self.load_config()
        self.restart_history = self.load_history()
    
    def load_config(self) -> Dict:
        """Load automation configuration."""
        if os.path.exists(AUTOMATION_CONFIG_FILE):
            try:
                with open(AUTOMATION_CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "enabled": False,
            "monitored_processes": [],
            "max_restart_attempts": 3,
            "restart_delay_seconds": 5
        }
    
    def save_config(self):
        """Save automation configuration."""
        try:
            with open(AUTOMATION_CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving automation config: {e}")
    
    def load_history(self) -> List[Dict]:
        """Load restart history."""
        if os.path.exists(RESTART_HISTORY_FILE):
            try:
                with open(RESTART_HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_history(self):
        """Save restart history."""
        try:
            # Keep only last 100 entries
            if len(self.restart_history) > 100:
                self.restart_history = self.restart_history[-100:]
            
            with open(RESTART_HISTORY_FILE, 'w') as f:
                json.dump(self.restart_history, f, indent=2)
        except Exception as e:
            print(f"Error saving restart history: {e}")
    
    def add_monitored_process(self, process_name: str, command: str):
        """Add a process to monitoring list."""
        if process_name not in [p['name'] for p in self.config.get('monitored_processes', [])]:
            self.config['monitored_processes'].append({
                "name": process_name,
                "command": command,
                "restart_count": 0
            })
            self.save_config()
    
    def remove_monitored_process(self, process_name: str):
        """Remove a process from monitoring."""
        self.config['monitored_processes'] = [
            p for p in self.config.get('monitored_processes', [])
            if p['name'] != process_name
        ]
        self.save_config()
    
    def check_and_restart_processes(self) -> List[str]:
        """
        Check monitored processes and restart if needed.
        
        Returns list of restarted processes.
        """
        if not self.config.get('enabled', False):
            return []
        
        restarted = []
        
        for proc_config in self.config.get('monitored_processes', []):
            process_name = proc_config['name']
            
            # Check if process is running
            is_running = any(
                p.name().lower() == process_name.lower()
                for p in psutil.process_iter(['name'])
            )
            
            if not is_running:
                # Check restart attempts
                if proc_config.get('restart_count', 0) >= self.config.get('max_restart_attempts', 3):
                    print(f"Max restart attempts reached for {process_name}")
                    continue
                
                # Attempt restart
                success = self.restart_process(proc_config)
                
                if success:
                    restarted.append(process_name)
                    proc_config['restart_count'] = proc_config.get('restart_count', 0) + 1
                    
                    # Log to history
                    self.restart_history.append({
                        "process": process_name,
                        "timestamp": datetime.now().isoformat(),
                        "success": True
                    })
                    self.save_history()
        
        self.save_config()
        return restarted
    
    def restart_process(self, proc_config: Dict) -> bool:
        """Restart a process using its command."""
        try:
            import subprocess
            import time
            
            command = proc_config.get('command', '')
            
            if not command:
                return False
            
            # Wait before restart
            time.sleep(self.config.get('restart_delay_seconds', 5))
            
            # Start process
            startupinfo = None
            creationflags = 0
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                creationflags = subprocess.CREATE_NO_WINDOW

            subprocess.Popen(
                command, 
                shell=True, 
                startupinfo=startupinfo, 
                creationflags=creationflags
            )
            
            print(f"Restarted process: {proc_config['name']}")
            return True
            
        except Exception as e:
            print(f"Failed to restart {proc_config['name']}: {e}")
            return False
