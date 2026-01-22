import flet as ft
from app.ui.theme import Palette, Fonts

class HealthBadge(ft.Container):
    def __init__(self, status: str = "ok"):
        self.status = status
        
        color_map = {
            "ok": Palette.NEON_GREEN,
            "warning": Palette.NEON_YELLOW,
            "critical": Palette.NEON_RED,
        }
        
        self.accent_color = color_map.get(status, Palette.NEON_BLUE)
        
        self.label = ft.Text(
            "SYSTEM NORMAL",
            size=12,
            weight=ft.FontWeight.BOLD,
            color=Palette.BG_DARK, # Text on neon bg
        )

        super().__init__(
            content=self.label,
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=ft.border_radius.all(20),
            bgcolor=self.accent_color,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=self.accent_color,
                offset=ft.Offset(0,0),
                blur_style=ft.BlurStyle.OUTER
            ),
            animate=ft.Animation(200, "easeOut"),
        )

    def set_status(self, status: str):
        try:
            if not self.page:
                return
            
            if status == self.status:
                return
                
            color_map = {
                "ok": (Palette.NEON_GREEN, "SYSTEM NORMAL"),
                "warning": (Palette.NEON_YELLOW, "WARNING DETECTED"),
                "critical": (Palette.NEON_RED, "CRITICAL FAILURE"),
            }
            
            color, text = color_map.get(status, (Palette.NEON_BLUE, "UNKNOWN"))
            
            self.bgcolor = color
            # Update shadow color
            self.shadow.color = color
            self.label.value = text
            self.update()
        except Exception:
            pass
