import flet as ft
import json
import os

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
                    value=True,
                ),
                ft.Checkbox(label="Sound alerts", value=True),
            ]),
            
            ft.Text("Alert Thresholds", size=14),
            ft.Row([
                ft.TextField(label="CPU Warning %", value="75", width=120),
                ft.TextField(label="CPU Critical %", value="90", width=120),
                ft.TextField(label="Memory Warning %", value="80", width=120),
                ft.TextField(label="Memory Critical %", value="95", width=120),
            ]),
            
            ft.Divider(),
            
            # Process Automation Section
            ft.Text("Process Automation", size=16, weight=ft.FontWeight.BOLD),
            ft.Switch(label="Auto-restart crashed processes", value=False),
            ft.TextField(
                label="Max restart attempts",
                value="3",
                width=150,
                hint_text="Maximum retry count"
            ),
            ft.TextField(
                label="Restart delay (seconds)",
                value="5",
                width=150,
                hint_text="Wait time before restart"
            ),
            
            ft.ElevatedButton(
                "Save Configuration",
                icon=ft.Icons.SAVE,
                # on_click=lambda e: save_alert_config(e) # Assuming this function exists or just a placeholder
                on_click=lambda e: None 
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
