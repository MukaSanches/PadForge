# Third-party notices

PadForge is MIT-licensed. Dependencies and bundled data retain their own licenses.

- **SDL_GameControllerDB** — community controller mapping database, zlib license. Source: `mdqinc/SDL_GameControllerDB`. The Windows build workflow downloads the current database and its license into `assets/` before packaging.
- **Pygame / SDL2** — used for physical joystick input and SDL controller mappings; distributed under their upstream licenses.
- **vgamepad** — MIT-licensed Python virtual gamepad library. On Windows it uses the ViGEm virtual gamepad framework/driver.
- **psutil** — used only to resolve the active foreground process for automatic game profile switching.

No source code from RetroArch, PCSX2, DuckStation, Dolphin, AntiMicroX or DS4Windows is copied into PadForge. Those projects were architectural references only.
