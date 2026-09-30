# Profile format

Built-in profiles live in `padforge/data/presets.json`. User overrides are stored in `%APPDATA%\PadForge\profiles.json`.

Minimal profile:

```json
{
  "id": "my-game",
  "name": "My Game",
  "match_processes": ["game.exe"],
  "output": "x360"
}
```

Optional fields:

- `calibration`: canonical post-normalization tuning (deadzone, curve, sensitivity, anti-deadzone).
- `remap`: canonical button-to-button map.
- `turbo_hz`: repetition frequency per source button.
- `extra_bindings`: edge-triggered keyboard/mouse/macro actions.
- `metadata`: descriptive data ignored by the engine.

Physical controller indexes should not be added to new game profiles. They belong in `controllers.json` and are managed by the first-run mapping wizard.
