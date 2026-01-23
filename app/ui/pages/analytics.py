import flet as ft
from app.storage.reader import read_recent_metrics
from app.ui.components.charts import NeonChart
from app.ui.theme import Palette
from app.ml.forecast import ResourceForecaster
from app.ml.anomaly import AnomalyDetector
import statistics

def view():
    def export_data(e, hours):
        """Handle CSV export."""
        from app.export.csv_exporter import CSVExporter
        
        success, result = CSVExporter.export_metrics(hours=hours)
        
        if success:
            e.page.snack_bar = ft.SnackBar(
                ft.Text(f"✓ Exported to: {result}"),
                open=True,
                bgcolor=ft.Colors.GREEN_700
            )
        else:
            e.page.snack_bar = ft.SnackBar(
                ft.Text(f"❌ {result}"),
                open=True,
                bgcolor=ft.Colors.RED_700
            )
        e.page.update()
    
    metrics = read_recent_metrics(minutes=30)

    if not metrics or len(metrics) < 5:
        return ft.Column(
            [
                ft.Text("Analytics", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("⏳ Collecting data... Please wait a few minutes for sufficient metrics.", size=16),
            ],
            expand=True,
        )

    # Extract data
    cpu_vals = [m["cpu_percent"] for m in metrics if m.get("cpu_percent") is not None]
    mem_vals = [m["memory_percent"] for m in metrics if m.get("memory_percent") is not None]
    disk_vals = [m["disk_percent"] for m in metrics if m.get("disk_percent") is not None]

    # Compute statistics
    avg_cpu = statistics.mean(cpu_vals) if cpu_vals else 0
    peak_mem = max(mem_vals) if mem_vals else 0
    avg_mem = statistics.mean(mem_vals) if mem_vals else 0
    anomaly_count = sum(1 for v in mem_vals if v > 85)
    
    # Forecast all resources
    forecaster = ResourceForecaster()
    
    # Memory Prediction
    try:
        mem_forecast = forecaster.predict_memory(mem_vals[-30:] if len(mem_vals) >= 30 else mem_vals)
        mem_prediction = float(mem_forecast.get("predicted_value", avg_mem))
    except Exception:
        mem_prediction = avg_mem
    
    # CPU Prediction
    try:
        cpu_forecast = forecaster.predict_cpu(cpu_vals[-30:] if len(cpu_vals) >= 30 else cpu_vals)
        cpu_prediction = float(cpu_forecast.get("predicted_value", avg_cpu))
    except Exception:
        cpu_prediction = avg_cpu
    
    # Disk Prediction
    try:
        disk_forecast = forecaster.predict_disk(disk_vals[-30:] if len(disk_vals) >= 30 else disk_vals)
        disk_prediction = float(disk_forecast.get("predicted_value", disk_vals[-1] if disk_vals else 0))
    except Exception:
        disk_prediction = disk_vals[-1] if disk_vals else 0
    
    # Get recent anomalies from database
    recent_anomalies = AnomalyDetector.get_recent_anomalies(limit=10)
    
    def get_prediction_style(value, resource_type="memory"):
        """Return color and icon based on prediction value."""
        if resource_type == "network":
            return ft.Colors.GREEN_400, ft.Icons.CHECK_CIRCLE
        
        if value > 90:
            return ft.Colors.RED_400, ft.Icons.WARNING
        elif value > 75:
            return ft.Colors.ORANGE_400, ft.Icons.TRENDING_UP
        else:
            return ft.Colors.GREEN_400, ft.Icons.CHECK_CIRCLE
    
    mem_color, mem_icon = get_prediction_style(mem_prediction)
    cpu_color, cpu_icon = get_prediction_style(cpu_prediction)
    disk_color, disk_icon = get_prediction_style(disk_prediction)
    
    # Prediction Cards
    prediction_cards = ft.Row(
        [
            # Memory Forecast
            ft.Container(
                content=ft.Row([
                    ft.Icon(mem_icon, color=mem_color, size=30),
                    ft.Column([
                        ft.Text("Memory (10min)", size=12, color=ft.Colors.GREY_400),
                        ft.Text(f"{mem_prediction:.1f}%", size=20, weight=ft.FontWeight.BOLD),
                    ], spacing=2),
                ], spacing=10),
                padding=12,
                bgcolor=ft.Colors.BLUE_GREY_800,
                border_radius=10,
                border=ft.border.all(2, mem_color),
                expand=True,
            ),
            # CPU Forecast
            ft.Container(
                content=ft.Row([
                    ft.Icon(cpu_icon, color=cpu_color, size=30),
                    ft.Column([
                        ft.Text("CPU (10min)", size=12, color=ft.Colors.GREY_400),
                        ft.Text(f"{cpu_prediction:.1f}%", size=20, weight=ft.FontWeight.BOLD),
                    ], spacing=2),
                ], spacing=10),
                padding=12,
                bgcolor=ft.Colors.BLUE_GREY_800,
                border_radius=10,
                border=ft.border.all(2, cpu_color),
                expand=True,
            ),
            # Disk Forecast
            ft.Container(
                content=ft.Row([
                    ft.Icon(disk_icon, color=disk_color, size=30),
                    ft.Column([
                        ft.Text("Disk (1hr)", size=12, color=ft.Colors.GREY_400),
                        ft.Text(f"{disk_prediction:.1f}%", size=20, weight=ft.FontWeight.BOLD),
                    ], spacing=2),
                ], spacing=10),
                padding=12,
                bgcolor=ft.Colors.BLUE_GREY_800,
                border_radius=10,
                border=ft.border.all(2, disk_color),
                expand=True,
            ),
        ],
        spacing=15,
    )
    
    # Determine trend
    if len(mem_vals) >= 10:
        recent_avg = statistics.mean(mem_vals[-5:])
        older_avg = statistics.mean(mem_vals[-10:-5])
        trend = "↑ Increasing" if recent_avg > older_avg else "↓ Decreasing" if recent_avg < older_avg else "→ Stable"
    else:
        trend = "→ Stable"
    
    # Create charts
    cpu_chart = NeonChart(cpu_vals[-30:] if len(cpu_vals) >= 30 else cpu_vals, color=Palette.NEON_BLUE)
    mem_chart = NeonChart(mem_vals[-30:] if len(mem_vals) >= 30 else mem_vals, color=Palette.NEON_PURPLE)
    
    # Anomaly History Section
    def build_anomaly_row(anomaly):
        severity = anomaly.get("severity", "info")
        severity_color = ft.Colors.RED_400 if severity == "critical" else ft.Colors.ORANGE_400 if severity == "warning" else ft.Colors.BLUE_400
        severity_icon = ft.Icons.ERROR if severity == "critical" else ft.Icons.WARNING if severity == "warning" else ft.Icons.INFO
        
        timestamp = anomaly.get("timestamp", "")[:16].replace("T", " ")  # Truncate and format
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(severity_icon, color=severity_color, size=20),
                ft.Text(timestamp, size=12, color=ft.Colors.GREY_400, width=120),
                ft.Text(anomaly.get("anomaly_type", "Unknown"), size=12, weight=ft.FontWeight.BOLD, expand=True),
                ft.Text(f"Score: {anomaly.get('score', 0):.0f}", size=12, color=severity_color),
            ], spacing=10),
            padding=8,
            bgcolor=ft.Colors.BLUE_GREY_900,
            border_radius=5,
            border=ft.border.only(left=ft.BorderSide(3, severity_color)),
        )
    
    anomaly_rows = [build_anomaly_row(a) for a in recent_anomalies[:5]] if recent_anomalies else [
        ft.Text("No anomalies detected yet.", color=ft.Colors.GREY_500, italic=True)
    ]

    return ft.Column(
        [
            ft.Text("Analytics & Predictions", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            # Stats Row
            ft.Row(
                [
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Avg CPU", color=ft.Colors.GREY_400),
                            ft.Text(f"{avg_cpu:.1f}%", size=24, weight=ft.FontWeight.BOLD),
                        ]),
                        padding=15,
                        bgcolor=ft.Colors.BLUE_GREY_900,
                        border_radius=10,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Peak Memory", color=ft.Colors.GREY_400),
                            ft.Text(f"{peak_mem:.1f}%", size=24, weight=ft.FontWeight.BOLD),
                        ]),
                        padding=15,
                        bgcolor=ft.Colors.BLUE_GREY_900,
                        border_radius=10,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Trend", color=ft.Colors.GREY_400),
                            ft.Text(trend, size=24, weight=ft.FontWeight.BOLD),
                        ]),
                        padding=15,
                        bgcolor=ft.Colors.BLUE_GREY_900,
                        border_radius=10,
                        expand=True,
                    ),
                ]
            ),
            
            # Prediction Cards (All Resources)
            ft.Text("Resource Predictions", size=18, weight=ft.FontWeight.BOLD),
            prediction_cards,
            
            ft.Divider(),
            
            # Anomaly History Section
            ft.Text("🔍 Anomaly Detection History", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column(anomaly_rows, spacing=5),
                padding=10,
                bgcolor=ft.Colors.BLUE_GREY_800,
                border_radius=10,
            ),
            
            ft.Divider(),
            
            # Export Section
            ft.Row([
                ft.Text("Export Data", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Export Last 24h to CSV",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: export_data(e, 24),
                ),
            ]),
            
            # CPU Chart
            ft.Text("CPU Usage Trend (Last 30 readings)", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=cpu_chart,
                height=200,
                bgcolor="#11ffffff",
                border_radius=10,
                padding=10,
            ),
            
            # Memory Chart
            ft.Text("Memory Usage Trend (Last 30 readings)", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=mem_chart,
                height=200,
                bgcolor="#11ffffff",
                border_radius=10,
                padding=10,
            ),
            
            ft.Text(
                "💡 Tip: Charts update in real-time. Watch for upward trends to predict resource exhaustion.",
                color=ft.Colors.GREY_400,
                size=12,
            ),
        ],
        expand=True,
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
    )

