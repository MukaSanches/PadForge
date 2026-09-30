# Third-party components and references

PadForge does not vendor source code from the emulator/remapper projects used as architectural references. Runtime dependencies are kept behind adapters.

## Runtime dependencies

- **pygame 2.6.1 / SDL2** — physical gamepad input and optional hardware rumble.
- **vgamepad 0.1.0** — virtual Xbox 360 gamepad binding. Its Windows backend uses ViGEmBus and supports force-feedback notifications.
- **ViGEmBus** — current Windows virtual-gamepad bus used behind the replaceable V1 output adapter.
- **psutil** — foreground-process resolution for automatic profile switching.

## Architectural references only

The following projects informed controller normalization, per-game mappings, deadzones, retro workflows and virtual-device design. Their source code is not copied or vendored into PadForge:

- RetroArch / Libretro
- PCSX2
- Dolphin
- DuckStation
- bsnes
- mGBA
- AntiMicroX
- x360ce
- DS4Windows
- Handheld Companion
- HidHide

Any future direct integration must be reviewed for license and API compatibility before redistribution.
