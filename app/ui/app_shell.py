import asyncio
import psutil
import flet as ft

from app.ui.sidebar import build_sidebar
from app.ui.theme import DARK_THEME, Palette
from app.ui.components import MetricCard, HealthBadge, NeonChart
from app.ui.components.overload_indicator import OverloadIndicator

from app.ui.pages import dashboard, performance, analytics, ai_chat, settings

from app.storage.reader import read_recent_metrics

from app.ml.features import batch_features, FEATURE_ORDER
from app.ml.normalizer import FeatureNormalizer
from app.ml.anomaly import AnomalyDetector
from app.ml.forecast import ResourceForecaster

from app.intelligence.anomaly_engine import interpret_anomalies
from app.intelligence.forecast_engine import interpret_forecast
from app.intelligence.health_state import compute_health_state

from app.alerts.alert_manager import AlertManager
from app.automation.process_automation import ProcessAutomation
import json

def run_ui(page: ft.Page):
    # Initialize Managers
    alert_manager = AlertManager()
    automation = ProcessAutomation()
    
    # helper to load config for thresholds
    def get_config():
        try:
           with open("config.json", "r") as f: return json.load(f)
        except: return {}

    # --------------------------------------------------
    # Window & theme
    # --------------------------------------------------
    page.title = "SENTINEL"
    page.window_width = 1280
    page.window_height = 850
    page.theme = DARK_THEME
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = Palette.BG_DARK
    page.padding = 0

    # --------------------------------------------------
    # Shared AI context
    # --------------------------------------------------
    ai_context = {
        "source": None,
        "payload": None,
    }

    # --------------------------------------------------
    # Dashboard widgets (Metric Cards)
    # --------------------------------------------------
    cpu_card = MetricCard("CPU Usage", "0%", ft.Icons.MEMORY, trend="--")
    mem_card = MetricCard("Memory", "0%", ft.Icons.STORAGE, trend="--")
    disk_card = MetricCard("Disk", "0%", ft.Icons.DISC_FULL, trend="--")
    net_card = MetricCard("Network", "0 KB/s", ft.Icons.NETWORK_CHECK)
    gpu_card = MetricCard("GPU", "N/A", ft.Icons.GRAPHIC_EQ)

    health_badge = HealthBadge(status="ok")
    overload_indicator = OverloadIndicator()
    
    # Chart Data (Stores last 30 points)
    chart_data = [0.0] * 30
    main_chart = NeonChart(chart_data, color=Palette.NEON_PURPLE)
    
    cpu_chart_data = [0.0] * 30
    cpu_chart = NeonChart(cpu_chart_data, color=Palette.NEON_BLUE)

    # --------------------------------------------------
    # Performance table
    # --------------------------------------------------
    # --------------------------------------------------
    # Performance tables
    # --------------------------------------------------
    def create_table():
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("PID")),
                ft.DataColumn(ft.Text("Process")),
                ft.DataColumn(ft.Text("CPU %")),
                ft.DataColumn(ft.Text("Memory (MB)")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            rows=[],
            expand=True,
            heading_row_color=Palette.with_opacity(0.1, Palette.NEON_BLUE),
            data_text_style=ft.TextStyle(color=Palette.TEXT_PRIMARY),
        )

    apps_table = create_table()
    services_table = create_table()

    # --------------------------------------------------
    # Prime psutil
    # --------------------------------------------------
    psutil.cpu_percent(interval=None)
    
    # --------------------------------------------------
    # Page container
    # --------------------------------------------------
    content_area = ft.Container(
        expand=True,
        padding=30,
    )

    # --------------------------------------------------
    # ML components
    # --------------------------------------------------
    normalizer = FeatureNormalizer()
    detector = AnomalyDetector()
    forecaster = ResourceForecaster()

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------
    def toast(msg: str):
        page.snack_bar = ft.SnackBar(ft.Text(msg), open=True, bgcolor=Palette.SURFACE)
        page.update()

    # --------------------------------------------------
    # Process Actions Handlers
    # --------------------------------------------------
    def ask_ai_handler(pid, name, cpu, mem):
        ai_context["source"] = "process"
        ai_context["payload"] = {
            "pid": pid,
            "name": name,
            "cpu_percent": cpu,
            "memory_mb": mem,
            "health": health_badge.label.value,
        }
        sidebar.selected_index = 3
        content_area.content = ai_chat.view(ai_context)
        page.update()

    def terminate_handler(pid, name, cpu, mem):
        from app.system.process_manager import ProcessManager
        
        def close_dialog(e):
            if page.dialog:
                page.dialog.open = False
                page.update()
        
        def do_terminate(e):
            from app.system.process_manager import ProcessManager
            success, message = ProcessManager.terminate_process(pid)
            close_dialog(e)
            toast(message)
        
        if ProcessManager.is_critical_process(name):
            dlg_content = ft.Text(f"'{name}' is critical. Force terminate?")
            actions = [
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Force", on_click=do_terminate, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ]
            title = ft.Text("⚠️ Critical Process")
        else:
            dlg_content = ft.Text(f"Terminate '{name}' (PID {pid})?")
            actions = [
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Terminate", on_click=do_terminate, style=ft.ButtonStyle(color=ft.Colors.ORANGE)),
            ]
            title = ft.Text("Confirm Termination")

        if page.dialog:
            page.dialog.open = False
            page.update()

        page.dialog = ft.AlertDialog(title=title, content=dlg_content, actions=actions, modal=True)
        page.dialog.open = True
        page.update()

    def create_process_menu(pid, name, cpu, mem):
        return ft.PopupMenuButton(
            icon=ft.Icons.MORE_VERT,
            icon_color=Palette.TEXT_SECONDARY,
            items=[
                ft.PopupMenuItem(content=ft.Text("Ask AI"), on_click=lambda _: ask_ai_handler(pid, name, cpu, mem)),
                ft.PopupMenuItem(),
                ft.PopupMenuItem(content=ft.Text("Terminate"), on_click=lambda _: terminate_handler(pid, name, cpu, mem)),
            ]
        )

    # --------------------------------------------------
    # Background: metrics + health
    # --------------------------------------------------
    async def refresh_metrics_and_health():
        await asyncio.sleep(1)
        from app.core.logger import logger
        while True:
            try:
                rows = read_recent_metrics(minutes=10)
                if rows:
                    latest = rows[-1]
                    logger.debug(f"UI Read Metric: CPU={latest.get('cpu_percent')}")
                    cpu_val = latest.get('cpu_percent', 0)
                    cpu_card.update_value(f"{cpu_val:.1f}%")
                    mem_val = latest.get('memory_percent', 0)
                    mem_card.update_value(f"{mem_val:.1f}%")
                    disk_val = latest.get('disk_percent', 0)
                    disk_usage = psutil.disk_usage('/')
                    disk_card.update_value(f"{disk_val:.1f}% ({disk_usage.used // (1024**3)}/{disk_usage.total // (1024**3)} GB)")
                    net_card.update_value(f"↑{latest.get('upload_kb',0)/1024:.1f} ↓{latest.get('download_kb',0)/1024:.1f} Mbps")
                    gpu = latest.get("gpu_percent")
                    if gpu is not None: 
                        gpu_card.update_value(f"{gpu:.1f}%")
                    else:
                        gpu_card.update_value("N/A")
                    
                    # Update charts
                    chart_data.pop(0)
                    chart_data.append(float(mem_val))
                    main_chart.update_chart(chart_data)
                    cpu_chart_data.pop(0)
                    cpu_chart_data.append(float(cpu_val))
                    cpu_chart.update_chart(cpu_chart_data)

                    # ---------------------------
                    # Alerts & Automation
                    # ---------------------------
                    config = get_config()
                    
                    if config.get("alerts_enabled", True):
                        # CPU Alert
                        cpu_crit = config.get("cpu_critical", 90)
                        cpu_warn = config.get("cpu_warning", 75)
                        if cpu_val >= cpu_crit:
                            alert_manager.trigger_alert("cpu_crit", "Critical CPU Usage", f"CPU is at {cpu_val:.1f}%", "critical")
                        elif cpu_val >= cpu_warn:
                            alert_manager.trigger_alert("cpu_warn", "High CPU Usage", f"CPU is at {cpu_val:.1f}%", "warning")
                            
                        # Memory Alert
                        mem_crit = config.get("mem_critical", 95)
                        mem_warn = config.get("mem_warning", 80)
                        if mem_val >= mem_crit:
                            alert_manager.trigger_alert("mem_crit", "Critical Memory Usage", f"Memory is at {mem_val:.1f}%", "critical")
                        elif mem_val >= mem_warn:
                            alert_manager.trigger_alert("mem_warn", "High Memory Usage", f"Memory is at {mem_val:.1f}%", "warning")
                    
                    # Process Automation
                    if config.get("automation_enabled", False):
                        restarted = automation.check_and_restart_processes()
                        if restarted:
                            for proc in restarted:
                                alert_manager.trigger_alert(f"restart_{proc}", "Process Restarted", f"Successfully restarted {proc}", "info")
                    
                    # ML Anomaly Detection
                    if len(rows) >= 5:
                        try:
                            # Build feature matrix
                            X = batch_features(rows)
                            Xn = normalizer.fit_transform(X)
                            
                            # Fit detector if not fitted
                            if not detector.fitted:
                                detector.fit(Xn)
                            
                            # Score and detect anomalies
                            scores = detector.score(Xn)
                            anomalies = interpret_anomalies(
                                scores[-len(FEATURE_ORDER):],
                                FEATURE_ORDER,
                            )
                            
                            # Save detected anomalies to database
                            for anomaly in anomalies:
                                if anomaly.get("score", 0) >= 70:  # Only save significant anomalies
                                    from app.ml.anomaly import AnomalyDetector as AD
                                    AD.save_anomaly(
                                        anomaly_type=anomaly.get("feature", "unknown"),
                                        severity="critical" if anomaly.get("score", 0) >= 90 else "warning",
                                        score=anomaly.get("score", 0),
                                        description=anomaly.get("message", ""),
                                        resource_values={
                                            "cpu": cpu_val,
                                            "memory": mem_val,
                                            "disk": disk_val
                                        }
                                    )
                            
                            # Forecasting
                            mem_series = [r["memory_percent"] for r in rows if r.get("memory_percent")]
                            forecast_raw = forecaster.predict(mem_series)
                            forecast = interpret_forecast("memory", forecast_raw, 95.0)
                            
                            # Compute health state
                            health = compute_health_state(anomalies, [forecast])
                            status = health["overall_status"]
                            health_badge.set_status(status)
                            
                            health_badge.set_status(health["overall_status"])
                            
                        except Exception as e:
                            # Fallback to simple health
                            health = compute_health_state([], [])
                            health_badge.set_status(health["overall_status"])

                    # Update Overload Indicator
                    from app.storage.reader import read_latest_overload_prediction
                    overload_data = read_latest_overload_prediction()
                    overload_indicator.update_overload_status(overload_data)
                        
                else:
                    logger.warning("UI Read: No metrics found in last 10 minutes")
                        
                page.update()
            except Exception as e:
                logger.error(f"UI Loop Error: {e}", exc_info=True)
            await asyncio.sleep(2)

    # --------------------------------------------------
    # Background: process list
    # --------------------------------------------------
    async def refresh_processes():
        await asyncio.sleep(1)
        import os
        current_user = os.getlogin().lower()
        
        while True:
            try:
                app_rows = []
                service_rows = []
                
                # Fetch username to distinguish apps
                for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "username"]):
                    try:
                        cpu = p.info["cpu_percent"] or 0.0
                        mem_info = p.info["memory_info"]
                        mem = mem_info.rss / (1024 * 1024) if mem_info else 0.0
                        username = (p.info.get("username") or "").lower()
                        name = p.info["name"] or ""

                        # Heuristic: Apps are usually run by the current user and not one of the critical system processes
                        # Services/System are usually SYSTEM, NETWORK SERVICE, or critical processes
                        from app.system.process_manager import CRITICAL_PROCESSES
                        is_system = name.lower() in CRITICAL_PROCESSES or "service" in username or "system" in username
                        
                        # Further refinement: If user matches current login, it's likely an App, unless it's a known background task
                        is_app = current_user in username and not is_system
                        
                        # Highlight resource hogs
                        is_hog = cpu > 50 or mem > 500
                        
                        row = ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(p.info["pid"]))),
                                ft.DataCell(ft.Text(name, weight=ft.FontWeight.BOLD if is_hog else None)),
                                ft.DataCell(ft.Text(f"{cpu:.1f}")),
                                ft.DataCell(ft.Text(f"{mem:.0f}")),
                                ft.DataCell(
                                    create_process_menu(
                                        p.info["pid"],
                                        name,
                                        cpu,
                                        mem,
                                    )
                                ),
                            ],
                        )
                        
                        if is_app:
                            app_rows.append(row)
                        else:
                            service_rows.append(row)

                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                # Sort by memory usage
                apps_table.rows = app_rows[:50] 
                services_table.rows = service_rows[:50]
                
                if page.control: 
                     page.update()
            except Exception as e:
                # print("refresh_processes error:", e)
                pass

            await asyncio.sleep(3)

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------
    def on_navigate(e):
        idx = e.control.selected_index
        if idx == 0:
            content_area.content = dashboard.view(
                cpu_card, mem_card, disk_card, net_card, gpu_card, health_badge, cpu_chart, main_chart, overload_indicator
            )
        elif idx == 1:
            content_area.content = performance.view(apps_table, services_table)
        elif idx == 2:
            content_area.content = analytics.view()
        elif idx == 3:
            content_area.content = ai_chat.view(ai_context)
        elif idx == 4:
            content_area.content = settings.view(on_toggle_theme=lambda _: None) # Theme locked to Dark
            
        page.update()

    # --------------------------------------------------
    # Layout Construction
    # --------------------------------------------------
    sidebar = build_sidebar(on_navigate)
    sidebar.bgcolor = "transparent" # Make sidebar transparent
    
    # Initialize Dashboard View
    content_area.content = dashboard.view(
        cpu_card, mem_card, disk_card, net_card, gpu_card, health_badge, cpu_chart, main_chart, overload_indicator
    )

    # Ambient Background
    background_layer = ft.Stack(
        controls=[
            # Base Image
            ft.Image(
                src="background.png", 
                fit="cover", 
                width=float("inf"),
                height=float("inf"),
                expand=True,
                opacity=0.8,
            ),
            # Overlay to ensure text readability (slight dark tint)
            ft.Container(bgcolor=Palette.with_opacity(0.3, Palette.BG_DARK), expand=True)
        ],
        expand=True
    )

    # Main Row overlay
    main_layout = ft.Row(
        controls=[
            ft.Container(
                content=sidebar,
                width=80, # Compact sidebar
                padding=ft.padding.only(top=20)
            ),
            # ft.VerticalDivider(width=1, color=Palette.GLASS_BORDER),
            content_area,
        ],
        expand=True,
        spacing=0
    )

    # Root Stack
    page.add(
        ft.Stack(
            controls=[
                background_layer,
                main_layout
            ],
            expand=True
        )
    )

    # --------------------------------------------------
    # Start tasks
    # --------------------------------------------------
    page.run_task(refresh_metrics_and_health)
    page.run_task(refresh_processes)
