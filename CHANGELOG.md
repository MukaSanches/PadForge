# Changelog

## 1.0.0

Initial functional Windows release.

### Input
- Generic SDL/DirectInput-compatible USB controller discovery.
- SDL GameControllerDB-assisted automatic mapping.
- Raw/manual fallback for unknown PS2-to-USB adapters.
- Live axes, buttons and hat/D-pad diagnostics.
- Persistent physical-to-logical mapping.
- Analog Doctor calibration with saved center, range and deadzone.

### Processing
- Radial deadzone.
- Anti-deadzone.
- Configurable response curves.
- Y-axis inversion.
- Logical remapping.
- Turbo gating.
- 250 Hz target processing loop.

### Output
- Xbox 360/XInput virtual controller output.
- Monitor-only fallback when the virtual controller backend is unavailable.
- Force-feedback/rumble passthrough to compatible physical controllers.

### Game intelligence
- Automatic profile selection from the foreground executable.
- Built-in profiles for modern games, racing/NFS, football/PES, GTA/third-person, NES, SNES, Mega Drive, N64, GameCube, Dreamcast, Arcade and PlayStation.

### Distribution
- Native Windows x64 application built with PyInstaller.
- Inno Setup installer.
- ViGEmBus driver bundled with the installer.
- Windows CI tests and reproducible build artifact.
