from __future__ import annotations

import threading
from typing import Callable, Optional


class TrayManager:
    """Windows system-tray bridge kept independent from Tk.

    pystray callbacks run on its worker thread, so UI callbacks are expected to
    marshal themselves back to Tk. PadForgeApp does this with after().
    """

    def __init__(
        self,
        show_callback: Callable[[], None],
        restart_callback: Callable[[], None],
        exit_callback: Callable[[], None],
    ) -> None:
        self._show_callback = show_callback
        self._restart_callback = restart_callback
        self._exit_callback = exit_callback
        self._icon = None
        self._thread: Optional[threading.Thread] = None

    @staticmethod
    def _image():
        from PIL import Image, ImageDraw

        size = 64
        image = Image.new("RGBA", (size, size), (11, 15, 20, 255))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((4, 4, 60, 60), radius=14, fill=(24, 33, 44, 255))
        draw.ellipse((12, 12, 52, 52), fill=(74, 163, 255, 255))
        draw.rounded_rectangle((21, 17, 31, 47), radius=4, fill=(7, 17, 27, 255))
        draw.rounded_rectangle((29, 17, 45, 29), radius=5, fill=(7, 17, 27, 255))
        draw.ellipse((35, 20, 41, 26), fill=(74, 163, 255, 255))
        return image

    def start(self) -> bool:
        if self._icon is not None:
            return True
        try:
            import pystray
        except Exception:
            return False

        menu = pystray.Menu(
            pystray.MenuItem("Abrir PadForge", lambda _icon, _item: self._show_callback(), default=True),
            pystray.MenuItem("Reiniciar motor", lambda _icon, _item: self._restart_callback()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Sair", lambda _icon, _item: self._exit_callback()),
        )
        self._icon = pystray.Icon("PadForge", self._image(), "PadForge — Any Controller. Any Game.", menu)

        def runner() -> None:
            try:
                self._icon.run()
            finally:
                self._icon = None

        self._thread = threading.Thread(target=runner, name="PadForgeTray", daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        icon = self._icon
        if icon is None:
            return
        try:
            icon.stop()
        except Exception:
            pass
        self._icon = None
