import csv
from datetime import datetime, timedelta
from app.storage.reader import read_recent_metrics
from typing import Optional
import os

class CSVExporter:
    """Export system metrics to CSV format."""
    
    @staticmethod
    def export_metrics(
        hours: int = 24,
        include_predictions: bool = False,
        output_dir: str = "exports"
    ) -> tuple[bool, str]:
        """
        Export metrics to CSV file.
        
        Args:
            hours: Number of hours of historical data to export
            include_predictions: Whether to include prediction columns
            output_dir: Directory to save CSV file
        
        Returns:
            (success: bool, file_path_or_error: str)
        """
        try:
            # Create export directory if needed
            os.makedirs(output_dir, exist_ok=True)
            
            # Get metrics
            metrics = read_recent_metrics(minutes=hours * 60)
            
            if not metrics:
                return False, "No data available to export"
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"syssentinel_metrics_{timestamp}.csv"
            filepath = os.path.join(output_dir, filename)
            
            # Write CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'timestamp',
                    'cpu_percent',
                    'memory_percent',
                    'disk_percent',
                    'upload_kb',
                    'download_kb',
                    'gpu_percent'
                ]
                
                if include_predictions:
                    fieldnames.extend([
                        'predicted_cpu',
                        'predicted_memory',
                        'predicted_disk'
                    ])
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for m in metrics:
                    row = {
                        'timestamp': m.get('timestamp', ''),
                        'cpu_percent': m.get('cpu_percent', 0),
                        'memory_percent': m.get('memory_percent', 0),
                        'disk_percent': m.get('disk_percent', 0),
                        'upload_kb': m.get('upload_kb', 0),
                        'download_kb': m.get('download_kb', 0),
                        'gpu_percent': m.get('gpu_percent', 'N/A'),
                    }
                    
                    if include_predictions:
                        # Predictions would be calculated here
                        # For now, just placeholder
                        row['predicted_cpu'] = 0
                        row['predicted_memory'] = 0
                        row['predicted_disk'] = 0
                    
                    writer.writerow(row)
            
            return True, filepath
            
        except Exception as e:
            return False, f"Export failed: {str(e)}"
