## Notes

Thanks to [Orangepixel](https://orangepixel.net/) for Residual and its planet exploration and survival gameplay. PortMaster adaptation by **Pixelforge Ports (Ronax)**.

## Get `residual.jar`

**GOG:** Download the Residual offline installer for your OS, install or extract it, then copy `residual.jar`.

**Steam:** Run:

```text
download_depot 1290780 1290782 3716360872293972653
```

Then copy:

```bash
steamapps/content/app_1290780/depot_1290782/residual.jar
```

**Verify:** `83,168,018 bytes` — SHA-256 `8f8caa7dc36f5ab9c7119046ccce87e3f7a2d61680dc60970fa3d2b2d619ee01`

## Install Residual.zip

1. Update PortMaster on compatible **64-bit ARM firmware**. Keep the device online for first launch so PortMaster can provide Java 17 and Westonpack.
2. Install **Residual.zip** through PortMaster.
3. Copy the JAR from the GOG installation or downloaded Steam depot to **`<Port directory>/residual/gamedata/`** on the handheld. Name it **`Residual.jar`** exactly (capital R); keep it intact.
4. Launch **Residual** from Ports. This test build uses gptokeyb2's virtual Xbox 360 mode with the game's built-in controller support; update PortMaster if the controller does not connect.

The launcher detects display size and supports **640x480**, **720x480**, **720x720**, **1024x768**, **1280x720**, and other valid PortMaster dimensions while preserving aspect ratio. If detection is wrong, put the actual size, such as `720x480`, in `residual/resolution.txt`; use `auto` or remove the file to restore automatic detection.

Back up **`residual/saves/`** before updating. If startup fails, check **`residual/log.txt`**. When reporting a problem, include the device, firmware version, resolution, reproduction steps, and log. Keep purchased game files private.

## Controller test

The launcher creates a virtual Xbox 360 controller through gptokeyb2. Controls:

| Button | Action |
|---|---|
| D-pad | Move |
| A | Action |
| B | Back |
| Y | Inventory |
| X | Jump |
| Start | Pause |
| L1 / R1 | Visor navigation |
| Start + Select | Close |

## Compile

Install **Python 3.9 or newer** and a **JDK 17 or newer**, then download or clone this source and open a terminal at its root (the folder containing `src`, `tools` and `package`). The original game JAR is not needed to compile or package the port. The first full build downloads two open-source libGDX 1.13.1 JARs from Maven Central and checks their pinned SHA-256 hashes. No cross compiler, Maven or Gradle installation is needed.

Windows PowerShell:

```powershell
python tools/build.py --jdk 'C:\Program Files\Java\jdk-17'
```

Linux (replace the path with your installed JDK):

```sh
python3 tools/build.py --jdk /path/to/jdk-17
```

The build compiles the adaptation from `src/` and produces only **`dist/Residual.zip`**. Small compile-only API declarations in `compile-api/` describe the game classes used by the host. They contain no game implementation and are excluded from the host and ZIP, as are the downloaded build dependencies. At runtime the real game classes come from the player's own `gamedata/Residual.jar`. Java bytecode is architecture-independent; the supplied game natives and runtime target ARM64. A build on Windows can therefore produce the same handheld package as a build on Linux.

After the first full build, `python tools/build.py --jdk /path/to/jdk-17 --offline` rebuilds using the cached dependencies in `build/dependencies/`. A fresh offline build needs both checksum-matching dependency JARs placed there first. The optional `--game-jar` argument only checks a supplied game file's fingerprint; it is never used as the compiler classpath.

After changing only the launcher or documentation, reuse the compiled host:

```sh
python tools/build.py --package-only
python tools/verify_package.py
python tools/verify_portmaster.py
bash tests/verify_display.sh
bash tests/verify_launcher.sh
```

Both build modes also verify the archive. `package/` holds the public packaging inputs; `ports/residual/` is the generated PortMaster repository layout. Build intermediates, compiled JARs, saves and `dist/` are ignored by Git. Upload the source files directly to your source repository. The build neither publishes files nor creates additional ZIP variants.

Device test status and desktop evidence are recorded in [VALIDATION.md](VALIDATION.md). The Discord testing post is [testing_thread.txt](testing_thread.txt).
