# Contributing

1. Keep hardware-specific mapping out of game profiles.
2. Add tests for every processing or persistence change.
3. Do not add blocking work to the controller polling loop.
4. Prefer data-only profiles for new games/emulators.
5. Do not vendor GPL code into this MIT repository without an explicit licensing decision.
6. Keep the application usable without a working virtual driver so diagnostics remain available.

Run before opening a pull request:

```powershell
python -m unittest discover -s tests -v
python -m compileall -q padforge main.py
```
