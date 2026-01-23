# app/ui/components/overload_indicator.py

import flet as ft
from app.ui.theme import Palette

class OverloadIndicator(ft.Container):
    """
    Component to display system overload risk.
    """
    
    def __init__(self):
        super().__init__()
        self.risk_level = "low"
        self.time_to_overload = 999
        self.visible = False
        self.setup_ui()
        
    def setup_ui(self):
        self.padding = 10
        self.border_radius = 8
        self.bgcolor = Palette.with_opacity(0.1, "#FF0000")
        self.border = ft.border.all(1, "#FF0000")
        
        self.icon = ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color="#FF0000")
        self.text = ft.Text(
            "System Overload Risk: Low",
            color="#FF0000",
            weight=ft.FontWeight.BOLD
        )
        self.subtext = ft.Text(
            "Stable",
            size=12,
            color=Palette.with_opacity(0.8, Palette.TEXT_PRIMARY)
        )
        
        self.content = ft.Row(
            [
                self.icon,
                ft.Column(
                    [self.text, self.subtext],
                    spacing=2
                )
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        
    def update_overload_status(self, overload_data: dict):
        """Update display based on overload predictions."""
        if not overload_data:
            self.visible = False
            self.update()
            return

        risk = overload_data.get("risk_level", "low")
        self.risk_level = risk
        
        if risk == "low":
            self.visible = False
        else:
            self.visible = True
            self.text.value = f"Overload Risk: {risk.upper()}"
            
            stressors = overload_data.get("primary_stressors", [])
            time_to = overload_data.get("time_to_overload", 999)
            
            msg = f"Potential issues with {', '.join(stressors)}"
            if time_to < 30:
                msg += f" in ~{time_to:.0f} mins"
                
            self.subtext.value = msg
            
            # Color coding
            # Color coding
            if risk == "critical":
                color = Palette.ERROR # ERROR needs to be defined in Palette or use string
                bg = Palette.with_opacity(0.2, "#FF0000") 
            elif risk == "high":
                color = Palette.NEON_RED # Use defined color or warning
                bg = Palette.with_opacity(0.2, Palette.NEON_RED)
            else:
                color = Palette.NEON_BLUE 
                bg = Palette.with_opacity(0.1, Palette.NEON_BLUE)
                
            self.border = ft.border.all(1, color)
            self.bgcolor = bg
            self.icon.color = color
            self.text.color = color
            
        self.update()
