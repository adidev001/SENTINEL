import flet as ft
import json
import os
import threading
import time
from app.ai.model_manager import ModelManager

CONFIG_FILE = "config.json"

def load_config():
    """Load configuration from file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"ai_mode": "local", "api_key": ""}

def save_config(config):
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")

def view(on_toggle_theme=None, on_ai_mode_change=None):
    config = load_config()
    
    # API Status indicator
    api_status = ft.Row([
        ft.Icon(ft.Icons.CIRCLE, size=12, color=ft.Colors.GREY_500),
        ft.Text("Not validated", size=12, color=ft.Colors.GREY_400)
    ], spacing=5)
    
    api_key_field = ft.TextField(
        label="OpenRouter API Key",
        password=True,
        can_reveal_password=True,
        value=config.get("api_key", ""),
        hint_text="sk-or-...",
        visible=config.get('ai_mode') == 'cloud',
        width=400,
    )
    
    def validate_api_key():
        """Validate API key and show status."""
        if not api_key_field.value:
            api_status.controls[0].color = ft.Colors.GREY_500
            api_status.controls[1].value = "Not validated"
            api_status.update()
            return
        
        # Test API key
        from app.intelligence.cloud_ai import CloudAIEngine
        try:
            engine = CloudAIEngine(api_key=api_key_field.value)
            # Simple test call
            response = engine.generate("test", "")
            
            if "⚠️" not in response:  # If no error
                api_status.controls[0].color = ft.Colors.GREEN_400
                api_status.controls[1].value = "✓ Working - mistralai/mistral-7b-instruct"
                api_status.controls[1].color = ft.Colors.GREEN_400
            else:
                api_status.controls[0].color = ft.Colors.RED_400
                api_status.controls[1].value = "✗ Invalid or expired"
                api_status.controls[1].color = ft.Colors.RED_400
        except:
            api_status.controls[0].color = ft.Colors.RED_400
            api_status.controls[1].value = "✗ Validation failed"
            api_status.controls[1].color = ft.Colors.RED_400
        
        api_status.update()
    
    # Create selection cards for AI modes
    def build_mode_card(mode_key, title, description, icon):
        is_selected = config.get('ai_mode', 'rag') == mode_key
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=32, color=ft.Colors.BLUE_400 if is_selected else ft.Colors.GREY_400),
                ft.Text(title, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE if is_selected else ft.Colors.GREY_300),
                ft.Text(description, size=12, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            width=180,
            height=140,
            border=ft.border.all(2, ft.Colors.BLUE_400 if is_selected else ft.Colors.TRANSPARENT),
            bgcolor=ft.Colors.BLUE_900 if is_selected else ft.Colors.BLUE_GREY_900,
            border_radius=10,
            on_click=lambda e: select_mode(mode_key),
            animate=ft.Animation(200, "easeOut"),
        )
    
    def select_mode(mode_key):
        config['ai_mode'] = mode_key
        save_config(config)
        
        # Update UI visibility
        api_key_field.visible = mode_key == 'cloud'
        save_api_btn.visible = mode_key == 'cloud'
        
        # Refresh the view
        if hasattr(mode_label, 'page'):
             mode_label.page.update()
             # We need to trigger a full rebuild or manually update controls
             # Simplified: Force page update to reflect visual changes if possible, 
             # but Flet state management inside a function is tricky without stateful widgets.
             # We'll update the components we have references to.
             
             # Rebuild the row of cards (manual update)
             cards_row.controls = [
                 build_mode_card("rag", "RAG", "Offline • Fast • System Data", ft.Icons.MEMORY),
                 build_mode_card("local", "Local AI", "Offline • Slower • Private", ft.Icons.SMART_TOY),
                 build_mode_card("cloud", "Cloud AI", "Online • Smartest • Requires Key", ft.Icons.CLOUD_QUEUE)
             ]
             cards_row.update()
             api_key_field.update()
             save_api_btn.update()
             mode_label.value = f"Current Mode: {mode_key.upper()}"
             mode_label.update()
        
        if on_ai_mode_change:
            on_ai_mode_change(config['ai_mode'], config.get('api_key', ''))

    mode_label = ft.Text(f"Current Mode: {config.get('ai_mode', 'rag').upper()}", size=16, weight=ft.FontWeight.BOLD)
    
    cards_row = ft.Row([
        build_mode_card("rag", "RAG", "Offline • Fast • System Data", ft.Icons.MEMORY),
        build_mode_card("local", "Local AI", "Offline • Slower • Private", ft.Icons.SMART_TOY),
        build_mode_card("cloud", "Cloud AI", "Online • Smartest • Requires Key", ft.Icons.CLOUD_QUEUE)
    ], alignment=ft.MainAxisAlignment.CENTER)

    if config.get('api_key') and config.get('ai_mode') == 'cloud':
         pass 

    def save_single_setting(key, value):
        config[key] = value
        save_config(config)

    # Refs for alert inputs
    cpu_warn_ref = ft.Ref[ft.TextField]()
    cpu_crit_ref = ft.Ref[ft.TextField]()
    mem_warn_ref = ft.Ref[ft.TextField]()
    mem_crit_ref = ft.Ref[ft.TextField]()
    restart_delay_ref = ft.Ref[ft.TextField]()
    max_retries_ref = ft.Ref[ft.TextField]()

    def save_alert_config(e):
        try:
           # Update config from refs
           # Note: We need to ensure refs are attached. 
           # If refs are recreated on every rebuild, this might be tricky if not careful.
           # But since we defined refs outside, they should hold the current control.
           
           if cpu_warn_ref.current: config["cpu_warning"] = float(cpu_warn_ref.current.value)
           if cpu_crit_ref.current: config["cpu_critical"] = float(cpu_crit_ref.current.value)
           if mem_warn_ref.current: config["mem_warning"] = float(mem_warn_ref.current.value)
           if mem_crit_ref.current: config["mem_critical"] = float(mem_crit_ref.current.value)
           if restart_delay_ref.current: config["restart_delay"] = int(restart_delay_ref.current.value)
           if max_retries_ref.current: config["max_retries"] = int(max_retries_ref.current.value)
           
           save_config(config)
           
           e.page.snack_bar = ft.SnackBar(ft.Text("Configuration saved!"), open=True, bgcolor=ft.Colors.GREEN_700)
           e.page.update()
        except ValueError:
             e.page.snack_bar = ft.SnackBar(ft.Text("Invalid values. Please enter numbers."), open=True, bgcolor=ft.Colors.RED_700)
             e.page.update() 

    def save_api_key(e):
        config['api_key'] = api_key_field.value
        save_config(config)
        
        # Validate after saving
        validate_api_key()
        
        e.control.page.snack_bar = ft.SnackBar(
            ft.Text("API Key saved!"),
            open=True
        )
        e.control.page.update()
        
        if on_ai_mode_change:
            on_ai_mode_change(config['ai_mode'], config['api_key'])

    save_api_btn = ft.ElevatedButton(
        "Save & Validate API Key",
        on_click=save_api_key,
        visible=config.get('ai_mode') == 'cloud',
        icon=ft.Icons.SAVE
    )
    

    # Custom Metrics logic
    from app.metrics.custom_metrics import CustomMetricsManager
    metrics_manager = CustomMetricsManager()
    
    metric_name_ref = ft.Ref[ft.TextField]()
    metric_cmd_ref = ft.Ref[ft.TextField]()
    metrics_list_ref = ft.Ref[ft.Column]()
    
    def render_metrics_list():
        if not metrics_list_ref.current: return
        
        metrics = metrics_manager.load_metrics()
        controls = []
        for m in metrics:
            controls.append(
                ft.Row([
                    ft.Text(m['name'], weight=ft.FontWeight.BOLD, width=150),
                    ft.Text(m['command'], size=12, color=ft.Colors.GREY_400, expand=True, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.IconButton(
                        icon=ft.Icons.DELETE, 
                        icon_color=ft.Colors.RED_400, 
                        on_click=lambda e, mid=m['id']: delete_metric(e, mid)
                    )
                ])
            )
        
        if not controls:
            controls.append(ft.Text("No custom metrics defined.", italic=True, color=ft.Colors.GREY_500))
            
        metrics_list_ref.current.controls = controls
        metrics_list_ref.current.update()

    def add_custom_metric(e):
        name = metric_name_ref.current.value
        cmd = metric_cmd_ref.current.value
        
        if not name or not cmd:
            e.page.snack_bar = ft.SnackBar(ft.Text("Name and Command required"), open=True)
            e.page.update()
            return
            
        metrics_manager.add_metric(name, "gauge", cmd)
        metric_name_ref.current.value = ""
        metric_cmd_ref.current.value = ""
        metric_name_ref.current.update()
        metric_cmd_ref.current.update()
        render_metrics_list()
        
    # Local AI Management UI
    def create_local_ai_section():
        
        status_text = ft.Text("", weight=ft.FontWeight.BOLD)
        progress_bar = ft.ProgressBar(width=400, color=ft.Colors.BLUE_400, value=0, visible=False)
        download_btn = ft.ElevatedButton("Download Model (~4GB)", icon=ft.Icons.DOWNLOAD)
        
        def update_ui():
            # Check safely to prevent "Control must be added to page first"
            if not status_text.page: return

            if ModelManager.is_model_installed():
                status_text.value = "✓ Installed: orca-mini-3b"
                status_text.color = ft.Colors.GREEN_400
                download_btn.visible = False
                download_btn.text = "Model Installed"
                download_btn.disabled = True
                progress_bar.visible = False
            elif ModelManager.is_downloading():
                status_text.value = "Downloading..."
                status_text.color = ft.Colors.ORANGE_400
                download_btn.visible = False
                progress_bar.visible = True
            else:
                status_text.value = "✗ Not Installed (Required for Local Mode)"
                status_text.color = ft.Colors.RED_400
                download_btn.visible = True
                download_btn.disabled = False
                progress_bar.visible = False
            
            try:
                status_text.update()
                progress_bar.update()
                download_btn.update()
            except Exception:
                pass # safely ignore race conditions on unmount

        def monitor_download():
            while ModelManager.is_downloading():
                # Only update if control is still on the page
                if progress_bar.page:
                    progress_bar.value = ModelManager.get_download_progress()
                    progress_bar.update()
                time.sleep(0.5)
            
            # Final update if still mounted
            if status_text.page:
                update_ui()
            
        def start_download_handler(e):
            if ModelManager.is_model_installed(): return
            
            ModelManager.start_download()
            update_ui()
            threading.Thread(target=monitor_download, daemon=True).start()

        download_btn.on_click = start_download_handler
        
        # Initial State
        # Hook into did_mount to trigger first update safely
        def on_container_mount():
             # Force one update when mounted
             update_ui()
             
             # Resume monitoring if needed
             if ModelManager.is_downloading():
                 threading.Thread(target=monitor_download, daemon=True).start()

        container = ft.Container(
            content=ft.Column([
                ft.Text("Download the local LLM to use AI offline.", color=ft.Colors.GREY_400),
                ft.Row([status_text]),
                progress_bar,
                download_btn
            ]),
            padding=15,
            bgcolor=ft.Colors.BLUE_GREY_900,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.BLUE_400),
            on_click=None # harmless prop to potential ensure interactivity
        )
        container.did_mount = on_container_mount
        
        # Set initial values *without* calling .update()
        # This ensures correct initial render state
        if ModelManager.is_model_installed():
             status_text.value = "✓ Installed: orca-mini-3b"
             status_text.color = ft.Colors.GREEN_400
             download_btn.visible = False
        elif ModelManager.is_downloading():
             status_text.value = "Downloading (Resuming)..."
             status_text.color = ft.Colors.ORANGE_400
             progress_bar.visible = True
             download_btn.visible = False
        else:
             status_text.value = "✗ Not Installed (Required for Local Mode)"
             status_text.color = ft.Colors.RED_400
             progress_bar.visible = False
             
        return container


    def delete_metric(e, mid):
        metrics_manager.remove_metric(mid)
        render_metrics_list()

    # Footer Content
    footer = ft.Container(
        content=ft.Column(
            [
                ft.Text("Made with love by Devansh and Jahnavi", color=ft.Colors.PINK_200, italic=True),
                ft.ElevatedButton(
                    "GitHub", 
                    icon=ft.Icons.CODE, 
                    url="https://github.com/adidev001/SENTINEL.git",
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_GREY_800
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        ),
        padding=ft.padding.only(top=20, bottom=20),
        alignment=ft.alignment.Alignment(0, 0)
    )
    
    # Append footer to the main column controls before returning
    main_column = ft.Column(
        [
            ft.Text("Settings", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            # AI Engine Section
            ft.Text("AI Engine Configuration", size=20, weight=ft.FontWeight.BOLD),
            mode_label,
            ft.Container(height=10),
            cards_row,
            ft.Container(height=10),
            
            # API Key Section
            api_key_field,
            api_status,
            ft.Row([save_api_btn]),
            ft.Divider(),
            
            # Alerts & Automation Section
            ft.Text("Alerts & Automation", size=20, weight=ft.FontWeight.BOLD),
            
            ft.Text("Windows Notifications", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Switch(
                    label="Enable alert notifications",
                    value=config.get("alerts_enabled", True),
                    on_change=lambda e: save_single_setting("alerts_enabled", e.control.value)
                ),
                ft.Checkbox(
                    label="Sound alerts", 
                    value=config.get("sound_enabled", True),
                    on_change=lambda e: save_single_setting("sound_enabled", e.control.value)
                ),
            ]),
            
            ft.Text("Alert Thresholds", size=14),
            ft.Row([
                ft.TextField(label="CPU Warning %", value=str(config.get("cpu_warning", 75)), width=120, ref=cpu_warn_ref),
                ft.TextField(label="CPU Critical %", value=str(config.get("cpu_critical", 90)), width=120, ref=cpu_crit_ref),
                ft.TextField(label="Memory Warning %", value=str(config.get("mem_warning", 80)), width=120, ref=mem_warn_ref),
                ft.TextField(label="Memory Critical %", value=str(config.get("mem_critical", 95)), width=120, ref=mem_crit_ref),
            ]),
            
            ft.Divider(),
            
            # Process Automation Section
            ft.Text("Process Automation", size=16, weight=ft.FontWeight.BOLD),
            ft.Switch(label="Auto-restart crashed processes", value=config.get("automation_enabled", False), on_change=lambda e: save_single_setting("automation_enabled", e.control.value)),
            ft.TextField(
                label="Max restart attempts",
                value=str(config.get("max_retries", 3)),
                width=150,
                hint_text="Maximum retry count",
                ref=max_retries_ref
            ),
            ft.TextField(
                label="Restart delay (seconds)",
                value=str(config.get("restart_delay", 5)),
                width=150,
                hint_text="Wait time before restart",
                ref=restart_delay_ref # Ensure this ref matches
            ),
            
            ft.Divider(),
            
            # Custom Metrics Section
            ft.Text("Custom Metrics", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("Add shell commands or Python expressions (start with 'python:')", size=12, color=ft.Colors.GREY_400),
            
            ft.Row([
                ft.TextField(label="Metric Name", width=150, hint_text="e.g. WiFi Signal", ref=metric_name_ref),
                ft.TextField(label="Command / Expression", expand=True, hint_text="python: psutil.sensors_battery().percent", ref=metric_cmd_ref),
                ft.IconButton(icon=ft.Icons.ADD, on_click=lambda e: add_custom_metric(e)),
            ]),
            
            ft.Container(
                content=ft.Column([], ref=metrics_list_ref), 
                bgcolor=ft.Colors.BLUE_GREY_900,
                border_radius=5,
                padding=10,
            ),
            
            ft.ElevatedButton(
                "Save Configuration",
                icon=ft.Icons.SAVE,
                on_click=lambda e: save_alert_config(e)
            ),
            
            ft.Divider(),
            
            # AI Comparison Info
            ft.Container(
                content=ft.Column([
                    ft.Text("💡 Local AI", weight=ft.FontWeight.BOLD),
                    ft.Text("✔ Full privacy - no data leaves your machine"),
                    ft.Text("✔ Works offline"),
                    ft.Text("✖ Slower, less sophisticated responses"),
                    ft.Divider(),
                    ft.Text("☁️ Cloud AI (OpenRouter)", weight=ft.FontWeight.BOLD),
                    ft.Text("✔ Faster, more accurate responses"),
                    ft.Text("✔ Access to GPT-4 level models"),
                    ft.Text("✖ Requires API key (get one at openrouter.ai)"),
                    ft.Text("✖ Sends system metrics to cloud"),
                ]),
                padding=15,
                bgcolor=ft.Colors.BLUE_GREY_900,
                border_radius=10,
                border=ft.border.all(1, ft.Colors.BLUE_400),
            ),
            
            ft.Divider(),

            # Local AI Capabilities
            ft.Text("Local AI Capabilities", size=20, weight=ft.FontWeight.BOLD),
            (lambda: create_local_ai_section())(),
            
            ft.Divider(),
            
            # Theme Section
            ft.Text("Appearance", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Theme: Dark Mode (Locked)", color=ft.Colors.GREY_400),

            ft.Divider(),
            footer
        ],
        expand=True,
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
    )

    return main_column
