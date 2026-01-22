import flet as ft
from app.ui.theme import Palette

class GlassContainer(ft.Container):
    def __init__(
        self,
        content: ft.Control,
        width: int | None = None,
        height: int | None = None,
        padding: int = 15,
        opacity: float = 0.05,
        blur: int = 10,
        border_color: str = Palette.GLASS_BORDER,
        **kwargs
    ):
        super().__init__(
            content=content,
            width=width,
            height=height,
            padding=padding,
            bgcolor=Palette.with_opacity(opacity, "#FFFFFF"),
            blur=ft.Blur(blur, blur),
            border=ft.border.all(1, border_color),
            border_radius=ft.border_radius.all(12),
            **kwargs
        )
