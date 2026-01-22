import flet as ft
from app.ui.components import GlassContainer

def view(apps_table: ft.DataTable, services_table: ft.DataTable):
    # Content containers
    apps_content = GlassContainer(
        content=ft.Column(
            controls=[apps_table],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        ),
        expand=True,
        padding=10,
        visible=True  # Initially visible
    )
    
    services_content = GlassContainer(
        content=ft.Column(
            controls=[services_table],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        ),
        expand=True,
        padding=10,
        visible=False # Initially hidden
    )

    # Tab references to update styling
    tab_apps = ft.Ref[ft.ElevatedButton]()
    tab_services = ft.Ref[ft.ElevatedButton]()

    def change_tab(idx):
        # Update visibility
        apps_content.visible = (idx == 0)
        services_content.visible = (idx == 1)
        apps_content.update()
        services_content.update()
        
        # Update button styles
        if tab_apps.current and tab_services.current:
            tab_apps.current.bgcolor = ft.Colors.BLUE_900 if idx == 0 else ft.Colors.BLUE_GREY_800
            tab_services.current.bgcolor = ft.Colors.BLUE_900 if idx == 1 else ft.Colors.BLUE_GREY_800
            tab_apps.current.update()
            tab_services.current.update()

    return ft.Column(
        [
            ft.Text("Active Processes", size=28, weight=ft.FontWeight.BOLD),
            # Custom Tab Bar
            ft.Container(
                content=ft.Row(
                    [
                        ft.ElevatedButton(
                            "Apps", 
                            icon=ft.Icons.APPS,
                            ref=tab_apps,
                            on_click=lambda _: change_tab(0),
                            bgcolor=ft.Colors.BLUE_900, # Initial active
                            color=ft.Colors.WHITE,
                        ),
                        ft.ElevatedButton(
                            "Background", 
                            icon=ft.Icons.SETTINGS_APPLICATIONS, 
                            ref=tab_services,
                            on_click=lambda _: change_tab(1),
                            bgcolor=ft.Colors.BLUE_GREY_800,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                ),
                padding=ft.padding.only(bottom=10)
            ),
            ft.Stack(
                [
                    apps_content,
                    services_content
                ],
                expand=True
            )
        ],
        expand=True,
        spacing=10,
    )

