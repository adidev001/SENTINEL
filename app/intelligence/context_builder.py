from app.storage.reader import read_recent_metrics
from typing import Dict, List, Optional
import statistics

class ContextBuilder:
    """Build rich context for AI conversations."""
    
    @staticmethod
    def build_system_context() -> str:
        """Generate comprehensive system overview."""
        metrics = read_recent_metrics(minutes=10)
        
        if not metrics or len(metrics) < 2:
            return "System monitoring just started. Limited historical data available."
        
        # Extract values
        cpu_vals = [m["cpu_percent"] for m in metrics if m.get("cpu_percent") is not None]
        mem_vals = [m["memory_percent"] for m in metrics if m.get("memory_percent") is not None]
        disk_vals = [m["disk_percent"] for m in metrics if m.get("disk_percent") is not None]
        
        # Compute statistics
        cpu_avg = statistics.mean(cpu_vals) if cpu_vals else 0
        cpu_peak = max(cpu_vals) if cpu_vals else 0
        mem_avg = statistics.mean(mem_vals) if mem_vals else 0
        mem_peak = max(mem_vals) if mem_vals else 0
        disk_current = disk_vals[-1] if disk_vals else 0
        
        # Determine trends
        cpu_trend = ContextBuilder._calculate_trend(cpu_vals)
        mem_trend = ContextBuilder._calculate_trend(mem_vals)
        
        # Detect anomalies
        high_cpu_events = sum(1 for v in cpu_vals if v > 80)
        high_mem_events = sum(1 for v in mem_vals if v > 85)
        
        # Get Top Processes
        from app.system.process_manager import ProcessManager
        top_procs = ProcessManager.get_top_processes(limit=5)
        
        cpu_procs = "\n".join([f"  - {p['name']} (PID {p['pid']}): {p['value']:.1f}%" for p in top_procs['cpu']])
        mem_procs = "\n".join([f"  - {p['name']} (PID {p['pid']}): {p['value']:.0f} MB" for p in top_procs['memory']])
        
        context = f"""
SYSTEM OVERVIEW (Last 10 minutes)
==================================
CPU:
  - Current: {cpu_vals[-1] if cpu_vals else 0:.1f}%
  - Average: {cpu_avg:.1f}%
  - Peak: {cpu_peak:.1f}%
  - Trend: {cpu_trend}
  - High Usage Events (>80%): {high_cpu_events}

TOP CPU CONSUMERS:
{cpu_procs}

Memory:
  - Current: {mem_vals[-1] if mem_vals else 0:.1f}%
  - Average: {mem_avg:.1f}%
  - Peak: {mem_peak:.1f}%
  - Trend: {mem_trend}
  - High Usage Events (>85%): {high_mem_events}

TOP MEMORY CONSUMERS:
{mem_procs}

Disk:
  - Current: {disk_current:.1f}%

AVAILABLE OPERATIONS:
- You can TERMINATE any process by name or PID
- To terminate: Tell the user to go to Performance tab -> Click ⋮ menu -> Select "Terminate"
- You do NOT need command line (taskkill/kill) instructions, use the UI
- You CAN identify process PIDs from the list above

Total Samples: {len(metrics)}
"""
        return context.strip()
    
    @staticmethod
    def build_process_context(pid: int, name: str, cpu: float, mem: float) -> str:
        """Generate detailed process context."""
        context = f"""
PROCESS DETAILS
===============
Name: {name}
PID: {pid}
CPU Usage: {cpu:.1f}%
Memory: {mem:.0f} MB

Resource Classification:
"""
        if cpu > 50:
            context += f"  - ⚠️ HIGH CPU usage ({cpu:.1f}% is above normal threshold)\n"
        else:
            context += f"  - ✓ CPU usage is normal\n"
            
        if mem > 500:
            context += f"  - ⚠️ HIGH MEMORY usage ({mem:.0f} MB is significant)\n"
        else:
            context += f"  - ✓ Memory usage is normal\n"
        
        return context.strip()
    
    @staticmethod
    def build_combined_context(
        pid: Optional[int] = None,
        name: Optional[str] = None, 
        cpu: Optional[float] = None,
        mem: Optional[float] = None
    ) -> str:
        """Build complete context combining system + process + disk info."""
        parts = [ContextBuilder.build_system_context()]
        
        # Add disk information
        try:
            from app.system.disk_scanner import DiskScanner
            parts.append("\n\n")
            parts.append(DiskScanner.get_summary())
        except Exception:
            pass
        
        if pid and name:
            parts.append("\n\n")
            parts.append(ContextBuilder.build_process_context(pid, name, cpu or 0, mem or 0))
        
        return "".join(parts)
    
    @staticmethod
    def _calculate_trend(values: List[float]) -> str:
        """Determine if values are increasing, decreasing, or stable."""
        if len(values) < 10:
            return "Stable (insufficient data)"
        
        recent = statistics.mean(values[-5:])
        older = statistics.mean(values[-10:-5])
        
        diff = recent - older
        
        if diff > 5:
            return f"↑ Increasing (up {diff:.1f}%)"
        elif diff < -5:
            return f"↓ Decreasing (down {abs(diff):.1f}%)"
        else:
            return "→ Stable"
