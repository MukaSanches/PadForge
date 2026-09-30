# PadForge

**Any Controller. Any Game.**

PadForge is a lightweight Windows gamepad modernization layer designed to make generic USB controllers useful in modern and retro games. Its first reference device is the common generic PS2-to-USB controller, but the architecture is device-agnostic.

## PadForge 1.0

- Detects generic DirectInput/SDL controllers.
- Live hardware diagnostic view for axes, buttons and hats/D-pad.
- Editable physical-to-logical mapping for controllers whose button numbering differs by manufacturer.
- Xbox 360 virtual output through `vgamepad` on Windows.
- Best-effort force-feedback/rumble passthrough from the virtual Xbox controller to compatible physical controllers.
- Processing pipeline with radial deadzone, anti-deadzone, response curves and Y inversion.
- Turbo support in the output layer.
- JSON game profiles and automatic profile switching based on the foreground executable.
- Built-in profiles for modern games, racing/NFS, football/PES, GTA/third-person, NES, SNES, Mega Drive, N64, GameCube, Dreamcast, Arcade and PlayStation emulation.
- SDL GameControllerDB support in packaged builds plus raw/manual fallback.
- Analog Doctor with persistent center/range/deadzone calibration.
- 250 Hz input/output loop target.
- Dark, lightweight Tkinter interface intended to remain usable on older PCs.
- GitHub Actions Windows build and Inno Setup installer pipeline.

## Architecture

```text
Physical controller
      |
      v
Pygame / SDL2 input
      |
      v
Device Mapping
      |
      v
PadForge Processing Engine
(deadzone / curve / remap / turbo)
      |
      v
Virtual Output Backend
      |
      +--> Xbox 360 / XInput (vgamepad)
      +--> Monitor-only fallback
      |
      v
Game or Emulator
```

The processing engine is intentionally independent from the virtual-controller backend. A future ViGEm replacement can therefore be added without rewriting profiles or controller processing.

## Running from source

Windows 10/11 is the primary supported platform.

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m padforge
```

The official Windows installer bundles the ViGEmBus MSI used by `vgamepad` and installs it before PadForge starts. If virtual output is unavailable for any reason, PadForge still opens in monitor/diagnostic mode.

## Generic PS2 USB setup

1. Connect the controller.
2. Open PadForge and select **Atualizar**.
3. Select the device and choose **Conectar**.
4. Open **Diagnóstico** and press each physical button to see its raw `bN` index.
5. Open **Mapeamento** and assign those indices to A/B/X/Y, shoulders, Start and Back.
6. Save the mapping.
7. Start a game. When its executable matches a profile, PadForge can switch profile automatically.

The default mapping is only a common PS2-USB starting point. Cheap adapters frequently enumerate buttons and axes differently, so the diagnostic/mapping layer is part of the core design rather than a workaround.

## Profiles

Profiles live in `profiles/*.json`. They can define executable names, deadzone, anti-deadzone, stick curve, Y inversion, turbo and logical remapping.

Examples shipped with v1.0 include:

- Universal / Modern
- Racing / NFS
- Football / PES
- GTA / Third Person
- Retro / SNES
- Retro / PlayStation

## Tests

```powershell
python scripts/verify.py
```

The tests validate deadzone behavior, calibration math, remapping, Y inversion, turbo gating and automatic executable-to-profile matching.

## Building the Windows installer

The repository includes `.github/workflows/build-windows.yml`. GitHub Actions builds the Windows application with PyInstaller and then generates an installer with Inno Setup. A tag such as `v1.0.0` is configured to publish the generated installer as a release asset.

## Integrations and inspirations

PadForge is an original project. Its architecture is informed by mature controller ecosystems including SDL/SDL GameControllerDB, RetroArch's universal-pad approach, PCSX2/DuckStation/Dolphin controller handling, and modern controller remappers. Third-party code is not copied into this repository unless its license and attribution requirements are explicitly handled.

## Roadmap after 1.0

- Guided one-button-at-a-time mapping wizard.
- Optional HidHide integration to eliminate double-input in problematic games.
- Additional virtual output backends.
- Community profile database.
- Per-game overlay and latency diagnostics.
- Gyro/motion support where hardware exposes it.

## License

MIT. Third-party dependencies retain their own licenses.
