import os
import psutil
from pathlib import Path
from typing import List, Dict

class DiskScanner:
    """Scan disks and analyze storage consumption."""
    
    @staticmethod
    def get_largest_directories(path: str = "C:\\", limit: int = 10) -> List[Dict]:
        """
        Scan directory and return largest subdirectories.
        
        Args:
            path: Root path to scan
            limit: Number of top results to return
        
        Returns:
            List of dicts with 'path', 'size_gb', 'size_bytes'
        """
        results = []
        
        try:
            # Scan immediate subdirectories
            for entry in os.scandir(path):
                if entry.is_dir():
                    try:
                        size_bytes = DiskScanner._get_directory_size(entry.path)
                        size_gb = size_bytes / (1024**3)
                        
                        results.append({
                            'path': entry.path,
                            'name': entry.name,
                            'size_bytes': size_bytes,
                            'size_gb': size_gb
                        })
                    except (PermissionError, OSError):
                        # Skip directories we can't access
                        continue
            
            # Sort by size descending
            results.sort(key=lambda x: x['size_bytes'], reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            print(f"Disk scan error: {e}")
            return []
    
    @staticmethod
    def _get_directory_size(path: str) -> int:
        """Calculate total size of directory (non-recursive scan, faster)."""
        total = 0
        try:
            # Just scan immediate files, not recursive
            with os.scandir(path) as entries:
                for entry in entries:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            total += entry.stat().st_size
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            pass
        
        return total
    
    @staticmethod
    def get_all_drives() -> List[Dict]:
        """Get all mounted drives with usage info."""
        drives = []
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                drives.append({
                    'mountpoint': partition.mountpoint,
                    'device': partition.device,
                    'total_gb': usage.total / (1024**3),
                    'used_gb': usage.used / (1024**3),
                    'free_gb': usage.free / (1024**3),
                    'percent': usage.percent
                })
            except (PermissionError, OSError):
                continue
        
        return drives
    
    @staticmethod
    def get_summary() -> str:
        """Get formatted summary of disk usage for AI context."""
        drives = DiskScanner.get_all_drives()
        
        summary = "DISK STORAGE SUMMARY\n" + "="*50 + "\n\n"
        
        for drive in drives:
            summary += f"{drive['device']} ({drive['mountpoint']})\n"
            summary += f"  Total: {drive['total_gb']:.1f} GB\n"
            summary += f"  Used: {drive['used_gb']:.1f} GB ({drive['percent']:.1f}%)\n"
            summary += f"  Free: {drive['free_gb']:.1f} GB\n\n"
        
        # Get largest directories on C:
        if any(d['mountpoint'] == 'C:\\' for d in drives):
            summary += "LARGEST DIRECTORIES (C:\\)\n" + "-"*50 + "\n"
            large_dirs = DiskScanner.get_largest_directories("C:\\", limit=5)
            
            for dir_info in large_dirs:
                summary += f"  {dir_info['name']}: {dir_info['size_gb']:.2f} GB\n"
        
        return summary
