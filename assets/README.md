# Controller database

The Windows build workflow downloads the current `mdqinc/SDL_GameControllerDB` database and its zlib license before packaging. PadForge points SDL at this database before controller initialization. If a device is not recognized, raw joystick input and manual mapping remain available.
