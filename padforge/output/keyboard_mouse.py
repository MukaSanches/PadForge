from __future__ import annotations

class KeyboardMouseActions:
    """Optional auxiliary action backend.

    The core PadForge V1.0 build keeps gamepad processing independent from OS input
    injection. This backend is intentionally inert in the public baseline and can be
    replaced by an explicitly enabled platform adapter later.
    """
    def execute(self, action: str) -> None:
        return
