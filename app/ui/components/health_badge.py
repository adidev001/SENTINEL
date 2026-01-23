import flet as ft
import asyncio
from app.ui.theme import Palette, Fonts

class HealthBadge(ft.Container):
    def __init__(self, status: str = "ok"):
        super().__init__()
        self.status = status
        self.pulse_task = None
        self.setup_ui()
        
    def setup_ui(self):
        # Initial visual state
        visuals = self._get_visuals(self.status)
        
        self.icon = ft.Icon(
            visuals["icon"], 
            size=16, 
            color=visuals["color"]
        )
        
        self.label = ft.Text(
            visuals["text"],
            size=13,
            weight=ft.FontWeight.BOLD,
            color=visuals["color"],
            font_family=Fonts.PRIMARY
        )
        
        # Content Row
        self.content_row = ft.Row(
            [self.icon, self.label],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            visible=True
        )

        # Container styling (Glassmorphism + Neon)
        self.content = self.content_row
        self.padding = ft.padding.symmetric(horizontal=16, vertical=8)
        self.border_radius = ft.border_radius.all(30)
        
        self.border = ft.border.all(1, visuals["color"])
        self.bgcolor = Palette.with_opacity(0.1, visuals["color"])
        
        self.shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=15,
            color=Palette.with_opacity(0.4, visuals["color"]),
            offset=ft.Offset(0,0),
            blur_style=ft.BlurStyle.OUTER
        )
        
        # Animation props
        self.animate_scale = ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT)
        self.animate_opacity = ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT)
        
        # Start Heartbeat
        self.did_mount = self.start_heartbeat

    def _get_visuals(self, status):
        """Map status to visual properties."""
        if status == "ok":
            return {
                "color": Palette.NEON_GREEN,
                "text": "SYSTEM NORMAL",
                "icon": ft.Icons.CHECK_CIRCLE_OUTLINED
            }
        elif status == "warning":
             return {
                "color": Palette.NEON_YELLOW,
                "text": "SYSTEM WARNING",
                "icon": ft.Icons.WARNING_AMBER_ROUNDED
            }
        elif status == "critical":
             return {
                "color": Palette.NEON_RED, # Ensure NEON_RED is defined in Palette or fallbacks
                "text": "CRITICAL FAILURE",
                "icon": ft.Icons.DANGEROUS_OUTLINED
            }
        else: # Unknown or offline
             return {
                "color": Palette.NEON_BLUE,
                "text": "SYSTEM OFFLINE",
                "icon": ft.Icons.WIFI_OFF_ROUNDED
            }

    def start_heartbeat(self):
        """Start the breathing animation."""
        self.pulse_task = asyncio.create_task(self._animate_pulse())

    async def _animate_pulse(self):
        while True:
            try:
                # Exhale (dim)
                self.opacity = 0.8
                self.scale = 0.98
                self.update()
                await asyncio.sleep(1.5)
                
                # Inhale (bright)
                self.opacity = 1.0
                self.scale = 1.02
                self.update()
                await asyncio.sleep(1.5)
            except Exception:
                break

    def set_status(self, status: str):
        if status == self.status:
            return
            
        self.status = status
        visuals = self._get_visuals(status)
        
        # Update styling
        self.border.color = visuals["color"]
        self.bgcolor = Palette.with_opacity(0.1, visuals["color"])
        self.shadow.color = Palette.with_opacity(0.4, visuals["color"])
        
        # Update content
        self.icon.name = visuals["icon"]
        self.icon.color = visuals["color"]
        self.label.value = visuals["text"]
        self.label.color = visuals["color"]
        
        if self.page:
            self.update()
