import flet as ft


def view(
    cpu_card: ft.Control,
    mem_card: ft.Control,
    disk_card: ft.Control,
    net_card: ft.Control,
    gpu_card: ft.Control,
    health_badge: ft.Control,
    cpu_chart: ft.Control,
    mem_chart: ft.Control,
):
    # Disk scan results area
    disk_scan_results = ft.Column([
        ft.Text("Select a drive and click 'Scan' to analyze storage consumption", color=ft.Colors.GREY_400, size=13)
    ])
    
    # Get available drives
    from app.system.disk_scanner import DiskScanner
    drives = DiskScanner.get_all_drives()
    
    # Drive selection dropdown
    drive_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option(d['mountpoint'], f"{d['device']} ({d['mountpoint']}) - {d['used_gb']:.0f}/{d['total_gb']:.0f} GB")
            for d in drives
        ],
        value=drives[0]['mountpoint'] if drives else "C:\\",
        width=400,
    )
    
    def scan_disks(e):
        """Perform disk scan and display results."""
        selected_drive = drive_dropdown.value
        
        disk_scan_results.controls.clear()
        disk_scan_results.controls.append(ft.Text(f"Scanning {selected_drive}... please wait", color=ft.Colors.BLUE_400))
        disk_scan_results.update()
        
        # Scan selected drive
        large_dirs = DiskScanner.get_largest_directories(selected_drive, limit=10)
        
        disk_scan_results.controls.clear()
        disk_scan_results.controls.append(ft.Text(f"Largest Directories ({selected_drive})", size=14, weight=ft.FontWeight.BOLD))
        
        if not large_dirs:
            disk_scan_results.controls.append(ft.Text("No accessible directories found", color=ft.Colors.GREY_400))
        else:
            for dir_info in large_dirs:
                def open_folder(path):
                    """Open folder in file explorer."""
                    import subprocess
                    import os
                    try:
                        if os.name == 'nt':  # Windows
                            subprocess.run(['explorer', path])
                        elif os.name == 'posix':  # macOS/Linux
                            subprocess.run(['xdg-open', path])
                    except Exception as e:
                        print(f"Failed to open folder: {e}")
                
                disk_scan_results.controls.append(
                    ft.Row([
                        ft.Icon(ft.Icons.FOLDER, size=16, color=ft.Colors.YELLOW_700),
                        ft.Text(dir_info['name'], size=13, expand=True),
                        ft.Text(f"{dir_info['size_gb']:.2f} GB", size=13, color=ft.Colors.BLUE_400),
                        ft.IconButton(
                            icon=ft.Icons.OPEN_IN_NEW,
                            icon_size=16,
                            tooltip="Open in Explorer",
                            on_click=lambda e, p=dir_info['path']: open_folder(p)
                        ),
                    ])
                )
        
        disk_scan_results.update()
    
    return ft.Column(
        [
            # Header
            ft.Row(
                [
                    ft.Text("System Dashboard", size=32, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True), # Spacer
                    health_badge
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Divider(color="transparent", height=10),
            
            # Metric Cards Area (Responsive Wrap)
            ft.Row(
                [
                    cpu_card,
                    mem_card,
                    disk_card,
                    net_card,
                    gpu_card,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
                run_spacing=20, # Vertical spacing when wrapped
                wrap=True,      # Allow wrapping on smaller screens
            ),
            
            ft.Divider(color="transparent", height=20),

            # Charts Area - Side by Side
            ft.Row(
                [
                    # CPU Chart
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Real-time CPU Usage", size=14, color="white54"),
                            ft.Container(
                                content=cpu_chart,
                                height=250,
                                expand=True,
                            )
                        ]),
                        padding=15,
                        bgcolor="#11ffffff",
                        border_radius=15,
                        expand=True,
                    ),
                    # Memory Chart
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Real-time Memory Usage", size=14, color="white54"),
                            ft.Container(
                                content=mem_chart,
                                height=250,
                                expand=True,
                            )
                        ]),
                        padding=15,
                        bgcolor="#11ffffff",
                        border_radius=15,
                        expand=True,
                    ),
                ],
                spacing=20,
            ),
            
            # Disk Scanner Section
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Storage Analysis", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        drive_dropdown,
                        ft.ElevatedButton(
                            "Scan",
                            icon=ft.Icons.SEARCH,
                            on_click=lambda e: scan_disks(e)
                        ),
                    ]),
                    ft.Divider(),
                    disk_scan_results,
                ]),
                padding=15,
                bgcolor="#11ffffff",
                border_radius=15,
            ),
        ],
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO # Enable scrolling if content overflows
    )
