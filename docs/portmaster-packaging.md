# Residual packaging

Run tools/build.py as documented in the source README. Its only distribution
artifact is dist/Residual.zip, a BYO-data PortMaster install ZIP.

The package directory contains the standard metadata, README, real 640x480
capture, launcher, control mapping, display helper, host and component licenses.
The exporter uses an explicit file list; original game data, saves, logs and
build/test files cannot be picked up by recursive copying.

The install ZIP contains an empty `residual/gamedata/` directory. Copy the
player-owned, supported `Residual.jar` there after installation; the private
archive is ignored by Git and excluded from every package build.

PortMaster repository metadata stays at the top of ports/residual/. In the
install ZIP it is relocated beneath residual/, with README.md named residual.md.
The launcher remains at the ZIP root. The canonical catalogue name in port.json
is residual.zip; the downloadable distribution filename is Residual.zip.
The metadata items list contains only Residual.sh and residual.

Runtime names match the PortMaster catalogue, including its .squashfs suffixes.
The launcher uses the firmware helpers, gptokeyb2, Java 17 and Westonpack's GLX
compatibility mode. It leaves graphics and audio driver selection to firmware.

The source-root testing_thread.txt is the Discord post text, not an installed
runtime file. Copy its text and attach Residual.zip when posting for testing.
Device results belong in VALIDATION.md and the testing checklist.

Reference: https://portmaster.games/packaging.html
