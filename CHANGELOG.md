# Changelog

## 1.0.0

### Controller engine
- SDL2/pygame generic USB controller detection.
- Stable per-controller identity using GUID + device name.
- Guided physical mapping for face buttons, shoulders, sticks and D-pad.
- HAT/POV and button-based D-pad support.
- Analog Doctor center/range/deadzone learning.
- Hardware mapping/calibration separated from game profiles.
- Up to four physical controllers and four virtual X360 outputs.

### Game modernization
- Xbox 360 virtual output through an isolated vgamepad backend.
- Rumble passthrough from virtual XInput feedback to compatible physical controllers.
- Linear, precision, aggressive, quadratic and S-curve response shaping.
- Logical remapping and turbo in the processing/profile engine.
- Automatic foreground-game profile switching and fallback after game exit.

### Profiles
- Universal, Racing, Football, GTA San Andreas and FPS presets.
- NES, SNES, Mega Drive, Nintendo 64, PS1, PS2, Dreamcast, GameCube/Wii and Arcade presets.
- Diagnostic profile without virtual output.

### UI and distribution
- Lightweight Tk interface.
- Guided controller mapping.
- Analog Doctor telemetry/calibration.
- Always-on-top overlay.
- Windows autostart.
- In-app virtual driver install/repair flow.
- GitHub Actions test/build pipeline.
- PyInstaller single-file executable and Inno Setup installer configuration.

### Public baseline boundary
- OS-level keyboard/mouse injection is intentionally disabled in the public V1 baseline; the auxiliary-action adapter is isolated for future opt-in implementations.
