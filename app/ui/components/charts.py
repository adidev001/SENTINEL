import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
import flet as ft
from app.ui.theme import Palette

class NeonChart(ft.Image):
    def __init__(self, initial_data: list[float] = None, color: str = Palette.NEON_GREEN):
        super().__init__(
            src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=", # 1x1 transparent pixel
            fit="fill", # Changed to fill to ensure full container usage
            expand=True,
        )
        self.gapless_playback = True
        self.filter_quality = ft.FilterQuality.HIGH
        self.data_color = color
        self.data = initial_data if initial_data else [0.0]*30
        
        # Determine color code (hex)
        try:
            self.plot_color = color.split('.')[-1] if '.' in color else color
            if not self.plot_color.startswith('#'):
                 # Fallback for predefined colors if not simple hex
                 self.plot_color = "#00FF00" 
        except:
             self.plot_color = "#00FF00"

        # If it's a known palette hex, use it
        if color == Palette.NEON_GREEN: self.plot_color = "#00FF99"
        elif color == Palette.NEON_BLUE: self.plot_color = "#00CCFF"
        elif color == Palette.NEON_PURPLE: self.plot_color = "#BC13FE"
        elif color == Palette.NEON_RED: self.plot_color = "#FF3366"

        self.update_chart(self.data)

    def update_chart(self, data: list[float]):
        self.data = data
        
        try:
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
            
            # Transparent background
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            
            # Plot Line with markers
            ax.plot(self.data, color=self.plot_color, linewidth=2, antialiased=True, marker='o', markersize=3, markerfacecolor=self.plot_color, markeredgecolor='white', markeredgewidth=0.5)
            
            # Add value labels on every 5th point
            for i in range(0, len(self.data), 5):
                ax.annotate(
                    f'{self.data[i]:.0f}',
                    (i, self.data[i]),
                    textcoords="offset points",
                    xytext=(0, 8),
                    ha='center',
                    fontsize=7,
                    color=self.plot_color,
                    weight='bold'
                )
            
            # Fill (gradient emulation via alpha)
            ax.fill_between(range(len(self.data)), self.data, color=self.plot_color, alpha=0.1)
            
            # Limits
            ax.set_ylim(0, 100)
            ax.set_xlim(0, max(len(self.data)-1, 1))
            
            # Remove axes details
            ax.set_axis_off()
            
            # Save to buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
            buf.seek(0)
            
            # Encode
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            
            # Cleanup
            plt.close(fig)
            
            # Update Image src (use data URI format)
            self.src = f"data:image/png;base64,{img_str}"
            
            # Force update (will fail silently if not attached)
            self.update()
            
        except Exception:
            # Silently ignore all errors (race conditions, page detachment, etc.)
            pass
