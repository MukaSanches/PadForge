# PadForge architecture

```text
SDL physical device
      | RawState
      v
ControllerConfigStore
mapping + learned hardware calibration
      | CanonicalState
      v
ProcessingEngine
per-game curve + sensitivity + remap + turbo
      |
      v
OutputBackend
      |
      +-- VigemXboxOutput --> virtual X360 device
                               |
                               +-- rumble callback --> SDL physical rumble
```

## Hardware configuration vs game profile

`ControllerConfig` belongs to the physical hardware and is keyed by a stable hash of SDL GUID + device name. It stores raw axis/button indexes, D-pad representation, center/range/deadzone and axis inversion.

`Profile` belongs to gameplay. It stores executable names, output backend, curves, sensitivity, remaps and turbo.

Switching games therefore cannot destroy controller calibration.

## Runtime rules

- Poll input on a dedicated thread.
- Limit physical-to-virtual routing to four pads in V1.
- Remove stale virtual outputs after hot-unplug.
- Return to the manual fallback profile when no foreground process matches.
- Treat a missing virtual driver as an output error, not an application-fatal error.

## Replaceable virtual backend

V1 uses vgamepad/ViGEm for practical XInput emulation and rumble notifications. The integration is isolated in `padforge/output/vigem.py`, so a future virtual backend does not require rewriting mapping, profiles or calibration.
