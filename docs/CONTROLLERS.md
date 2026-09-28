# Controller support

This device-test build uses PortMaster's gptokeyb2 Xbox 360 emulation mode (-x) instead of a keyboard/mouse mapping file. The launcher sets CRUSTY_BLOCK_INPUT=1 to avoid delivering both the handheld's raw controller and the virtual controller to the game. Main leaves Residual's built-in controller path enabled.

Please test the in-game controller settings, menu navigation, movement, actions, both analog sticks, and the exit shortcut. Report the device, firmware, whether controls are missing or duplicated, and the game's detected controller layout.

The keyboard mapping file is not used or included in this build. This is a device-test path; button behavior still needs confirmation on the target handheld.

References:
- https://github.com/PortsMaster/gptokeyb2/blob/master/ADVANCED_USAGE.md
- https://github.com/PortsMaster/gptokeyb2/blob/master/src/main.c
