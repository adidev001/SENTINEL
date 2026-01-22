# app/ui/sidebar.py

import flet as ft

def build_sidebar(on_navigate):
    return ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD,
                label="Dashboard",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SPEED,
                label="Performance",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.INSIGHTS,
                label="Analytics",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CHAT,
                label="AI",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
        ],
        on_change=on_navigate,
    )
