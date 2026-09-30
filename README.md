# PadForge

> **Any Controller. Any Game.**

PadForge is a Windows gamepad modernization layer focused on generic USB/DirectInput controllers, including common PlayStation 2-to-USB adapters.

It learns the real layout and analog behavior of each physical controller, normalizes it into a stable PadForge layout, applies game-specific tuning and can expose the result as a virtual Xbox 360 controller.

## PadForge 1.0

- Generic USB gamepad discovery through pygame/SDL2.
- Stable controller identity from GUID + device name.
- Guided physical mapping for face buttons, shoulders, sticks and D-pad.
- D-pad support as SDL HAT/POV or four separate buttons.
- **Analog Doctor** calibration for center, range, drift and physical deadzone.
- Physical mapping/calibration stored independently from game profiles.
- Xbox 360/XInput virtual output through an isolated vgamepad backend.
- Up to four physical controllers routed to four virtual X360 devices.
- Best-effort rumble passthrough to SDL devices that expose vibration.
- Deadzone, sensitivity and response curves: linear, precision, aggressive, quadratic and S-curve.
- Logical button remapping and turbo support in the processing engine/profile format.
- Automatic profile switching from the Windows foreground executable, including fallback to the user's manual profile when the game closes.
- Presets for modern games, racing/NFS, football/PES, GTA SA, FPS, NES, SNES, Mega Drive, N64, PS1, PS2, Dreamcast, GameCube/Wii and Arcade/MAME.
- Always-on-top live overlay.
- Windows startup option.
- Virtual-driver install/repair and probe actions.
- Windows CI, PyInstaller single-file build and Inno Setup release workflow.

## First run

1. Connect the controller.
2. Start PadForge.
3. Select **Configurar controle completo** and follow each requested button/axis.
4. Run **Analog Doctor — calibrar** and move both sticks through their full range.
5. If virtual Xbox output is unavailable, select **Instalar / reparar driver virtual**.
6. Choose a profile or keep **Perfil automático pelo jogo** enabled.
7. Start the game.

The mapping is saved by stable controller identity, so SDL instance IDs changing after a reboot do not destroy the configuration.

## Architecture

```text
Physical USB gamepad
        |
        v
 pygame / SDL2 input
        |
        v
 Per-device mapping + calibration
        |
        v
 Canonical PadForge controller state
        |
        v
 Game profile processing
 deadzone / curve / sensitivity / remap / turbo
        |
        v
 Replaceable output backend
        |
        +--> Xbox 360 virtual controller (vgamepad / ViGEm)
                    |
                    +--> rumble request --> compatible physical SDL controller
```

The physical-controller layer and game-profile layer are separate by design. Changing from PES to NFS, an emulator or another game never overwrites the hardware calibration.

## Built-in profiles

| Profile | Typical targets |
| --- | --- |
| Universal — Xbox 360 | Most Windows games |
| Corrida — Precisão | NFS Most Wanted/Carbon/Underground 2 |
| Futebol — PES/FIFA | PES 5/6 and similar football games |
| GTA San Andreas | GTA SA |
| FPS — Analógico preciso | XInput FPS/gamepad titles |
| Retro — NES/Famicom | Mesen, Nestopia, FCEUX |
| Retro — Super Nintendo | Snes9x, bsnes, Mesen |
| Retro — Mega Drive/Genesis | Gens/Fusion-style emulators |
| Retro — Nintendo 64 | Project64/Mupen64Plus |
| Retro — PlayStation 1 | DuckStation/ePSXe |
| Retro — PlayStation 2 | PCSX2 |
| Retro — Dreamcast | Flycast/Redream |
| Retro — GameCube/Wii | Dolphin |
| Retro — Arcade/MAME | MAME |
| Diagnóstico | Input testing without a virtual controller |

## Run from source

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Portable mode

Run `PadForge.exe --portable` or create an empty `portable.flag` beside the executable. Configuration will then be stored in `PadForgeData` beside the program instead of `%APPDATA%\PadForge`.

## Build

```powershell
.\scripts\build.ps1
```

The build sets `VGAMEPAD_SKIP_VIGEMBUS_INSTALL=true` so CI does not try to install a kernel driver. Driver setup is a user-initiated action inside PadForge.

## Tests

```powershell
python -m unittest discover -s tests -v
python -m compileall -q padforge main.py
```

The public baseline tests calibration, persistent controller identity, HAT/button D-pad translation, response curves, remapping, trigger conversion, profile merging, automatic game-profile fallback and the virtual-output/rumble callback.

Real hardware validation still requires a Windows PC, the actual controller and virtual-driver installation.

## Compatibility

- Windows 10/11: primary virtual-Xbox target.
- Older Windows versions: SDL input/diagnostics may work, but virtual-driver support is not guaranteed.

## Design rules

1. Physical calibration never belongs to a game profile.
2. Never assume two generic PS2 adapters expose the same button indexes.
3. Prefer data-driven game profiles.
4. Never block the controller polling loop.
5. Hot-unplug must not crash the app.
6. Virtual-controller backends must remain replaceable.
7. Keep the UI light enough for older PCs.

## Public V1 auxiliary actions

The public V1 baseline deliberately keeps OS-level keyboard/mouse injection disabled. Controller-to-controller remapping, curves, turbo, XInput conversion and rumble remain part of the core. A future auxiliary-action backend can be added behind an explicit opt-in boundary without coupling it to the real-time engine.

## License

MIT. See [THIRD_PARTY.md](THIRD_PARTY.md) for runtime dependencies and architectural references.
