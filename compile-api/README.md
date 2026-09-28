# Compile-only game API

These handwritten declarations describe only the game types, fields and methods
referenced by the host. They contain no game implementation or assets. Method
bodies throw an exception and must never be used at runtime. This is a deliberately
minimal compilation surface, not a complete declaration of every game API member.

The compiler also uses the public gdx and gdx-backend-lwjgl3 1.13.1 artifacts from
Maven Central. Their SHA-256 hashes are pinned in tools/build.py. Cached dependencies
live under build/dependencies and are not checked into source control.

Only org/portmaster/residual classes are written to residual-host.jar. All
com/orangepixel declarations and open-source dependencies are excluded. The player
supplies the unchanged supported `Residual.jar` at
`residual/gamedata/Residual.jar` for the real runtime implementation.

When editing these declarations, match binary names, field types, static modifiers,
method signatures and relevant inheritance to the supported game API. The current
host bytecode has been compared with compilation against the original game classes
and matches exactly. This does not establish compatibility with other game versions.
