import psutil
from typing import Optional

# Critical Windows processes that should never be terminated
CRITICAL_PROCESSES = {
    "system", "csrss.exe", "smss.exe", "lsass.exe", "services.exe",
    "winlogon.exe", "wininit.exe", "dwm.exe", "explorer.exe"
}

class ProcessManager:
    """Safe process management with validation."""
    
    @staticmethod
    def is_critical_process(name: str) -> bool:
        """Check if process is critical to system operation."""
        return name.lower() in CRITICAL_PROCESSES
    
    @staticmethod
    def terminate_process(pid: int) -> tuple[bool, str]:
        """
        Safely terminate a process.
        
        Returns:
            (success: bool, message: str)
        """
        try:
            process = psutil.Process(pid)
            name = process.name()
            
            # Check if critical
            if ProcessManager.is_critical_process(name):
                return False, f"❌ Cannot terminate critical system process: {name}"
            
            # Attempt graceful termination
            process.terminate()
            
            # Wait up to 3 seconds for termination
            process.wait(timeout=3)
            
            return True, f"✓ Process {name} (PID {pid}) terminated successfully"
            
        except psutil.NoSuchProcess:
            return False, "❌ Process not found (already terminated?)"
        except psutil.AccessDenied:
            return False, "❌ Access denied. Run as administrator to terminate this process."
        except psutil.TimeoutExpired:
            # Force kill if graceful termination failed
            try:
                process.kill()
                return True, f"✓ Process forcefully killed (PID {pid})"
            except Exception as e:
                return False, f"❌ Failed to kill process: {str(e)}"
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
    
    @staticmethod
    def get_process_info(pid: int) -> Optional[dict]:
        """Get detailed process information."""
        try:
            process = psutil.Process(pid)
            return {
                "pid": pid,
                "name": process.name(),
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_mb": process.memory_info().rss / (1024 * 1024),
                "status": process.status(),
                "num_threads": process.num_threads(),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    @staticmethod
    def get_top_processes(limit: int = 5) -> dict:
        """
        Get lists of top processes by CPU and Memory.
        
        Returns:
            {
                "cpu": [{"name": str, "pid": int, "value": float}, ...],
                "memory": [{"name": str, "pid": int, "value": float}, ...]
            }
        """
        processes = []
        for p in psutil.process_iter(['name', 'cpu_percent', 'memory_info', 'pid']):
            try:
                # CPU percent needs a tiny interval or it returns 0.0 first time
                # But calling it on all processes is slow. 
                # Better approach: use ones with cached values or accept 0 for new ones
                p_info = p.info
                p_info['memory_mb'] = p_info['memory_info'].rss / (1024 * 1024)
                processes.append(p_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by Memory
        by_mem = sorted(processes, key=lambda x: x['memory_mb'], reverse=True)[:limit]
        
        # Sort by CPU (Note: cpu_percent might be 0 without interval, but good enough for snapshot)
        by_cpu = sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:limit]
        
        return {
            "cpu": [
                {"name": p['name'], "pid": p['pid'], "value": p['cpu_percent']} 
                for p in by_cpu
            ],
            "memory": [
                {"name": p['name'], "pid": p['pid'], "value": p['memory_mb']} 
                for p in by_mem
            ]
        }
