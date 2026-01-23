import flet as ft

# -----------------------------------------------------------------------------
# Color Palette (Neon / Glassmorphism)
# -----------------------------------------------------------------------------
class Palette:
    
    @staticmethod
    def with_opacity(opacity: float, color: str) -> str:
        """Returns color with alpha channel locally (Hex: #AARRGGBB)"""
        if color.startswith("#"):
            color = color.lstrip("#")
        
        # Handle short hex #RGB
        if len(color) == 3:
            color = "".join(c*2 for c in color)
            
        alpha = int(opacity * 255)
        return f"#{alpha:02X}{color}"

    # Backgrounds
    BG_DARK = "#050510"  # Deep Void
    BG_SECONDARY = "#0f0f1e" 
    SURFACE = "#151525"
    
    # Accents
    NEON_GREEN = "#00FF9D" 
    NEON_PURPLE = "#7B2CBF"
    NEON_BLUE = "#00D4FF"
    NEON_RED = "#FF2A6D"
    NEON_YELLOW = "#FFD166"

    # Text
    TEXT_PRIMARY = "#FFFFFF"

# Delayed definitions to allow using static method
Palette.GLASS_BG = Palette.with_opacity(0.05, "#FFFFFF")
Palette.GLASS_BORDER = Palette.with_opacity(0.1, "#FFFFFF")
Palette.TEXT_SECONDARY = Palette.with_opacity(0.7, "#FFFFFF")
Palette.TEXT_DISABLED = Palette.with_opacity(0.3, "#FFFFFF")

# -----------------------------------------------------------------------------
# Typography
# -----------------------------------------------------------------------------
class Fonts:
    PRIMARY = "Segoe UI"  
    MONOSPACE = "Consolas"

# -----------------------------------------------------------------------------
# Loading Page Colors
# -----------------------------------------------------------------------------
class LoadingPageColors:
    """Color scheme for loading page matching app theme."""
    
    # Background colors (matching background.png)
    BACKGROUND_DARK = "#0A0A0A"
    BACKGROUND_OVERLAY = Palette.with_opacity(0.7, "#000000")
    
    # Accent colors (neon/cyberpunk theme matching Palette)
    PRIMARY_CYAN = Palette.NEON_BLUE
    SECONDARY_BLUE = "#0080FF"
    HIGHLIGHT_GREEN = Palette.NEON_GREEN
    
    # Text colors
    TITLE_PRIMARY = PRIMARY_CYAN
    TITLE_SECONDARY = Palette.TEXT_PRIMARY
    SUBTITLE_TEXT = Palette.TEXT_SECONDARY
    
    # Button colors
    BUTTON_BG = Palette.with_opacity(0.8, "#001133")
    BUTTON_HOVER = Palette.with_opacity(0.9, "#002244")
    BUTTON_TEXT = PRIMARY_CYAN

# -----------------------------------------------------------------------------
# Themes
# -----------------------------------------------------------------------------
DARK_THEME = ft.Theme(
    color_scheme_seed=Palette.NEON_GREEN,
    visual_density=ft.VisualDensity.COMFORTABLE,
    page_transitions=ft.PageTransitionsTheme(
        windows=ft.PageTransitionTheme.CUPERTINO
    ),
)
