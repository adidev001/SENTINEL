import pystray
from PIL import Image
import threading
import sys


def start_tray(on_restore):
    image = Image.new("RGB", (64, 64), color=(30, 144, 255))

    def restore(icon, item):
        on_restore()

    def exit_app(icon, item):
        icon.stop()
        sys.exit(0)

    menu = pystray.Menu(
        pystray.MenuItem("Open SysSentinel", restore),
        pystray.MenuItem("Exit", exit_app),
    )

    icon = pystray.Icon("SysSentinel", image, "SysSentinel AI", menu)
    threading.Thread(target=icon.run, daemon=True).start()
