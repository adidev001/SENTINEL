import flet as ft
from app.ui.theme import Palette, Fonts
from app.ui.components.glass import GlassContainer

class MetricCard(GlassContainer):
    def __init__(
        self,
        title: str,
        value: str,
        icon: str,
        trend: str = None, # "+5%" etc
        trend_color: str = Palette.NEON_GREEN,
        width: int = 200,
        height: int = 120,
    ):
        
        self.value_text = ft.Text(
            value, 
            size=28, 
            weight=ft.FontWeight.BOLD, 
            font_family=Fonts.PRIMARY,
            color=Palette.TEXT_PRIMARY
        )
        
        self.trend_text = ft.Text(
            trend if trend else "",
            size=12,
            color=trend_color,
            visible=bool(trend)
        )

        content = ft.Column(
            controls=[
                # Header: Icon + Title
                ft.Row(
                    controls=[
                        ft.Icon(icon, size=16, color=Palette.TEXT_SECONDARY),
                        ft.Text(title, size=14, color=Palette.TEXT_SECONDARY)
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=8
                ),
                ft.Container(height=10), # Spacer
                # Value
                self.value_text,
                # Trend / Footer
                self.trend_text
            ],
            spacing=0,
        )

        super().__init__(
            content=content,
            width=width,
            height=height,
            opacity=0.03, # Slightly darker/transparent
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        )

    def update_value(self, new_value: str, new_trend: str = None, trend_color: str = None):
        try:
            if not self.page:
                return
            self.value_text.value = new_value
            if new_trend:
                self.trend_text.value = new_trend
                self.trend_text.visible = True
                if trend_color:
                    self.trend_text.color = trend_color
            self.update()
        except Exception:
            # Squelch race conditions where card is removed during update
            pass
