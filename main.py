from __future__ import annotations

import os
import sys


def resource_path(relative: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base, relative)


def main() -> int:
    from padforge.ui.app import PadForgeApp

    start_hidden = "--minimized" in sys.argv or "--tray" in sys.argv
    app = PadForgeApp(
        resource_path(os.path.join("padforge", "data", "presets.json")),
        start_hidden=start_hidden,
    )
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
