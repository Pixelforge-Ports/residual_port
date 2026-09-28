// Compile-only API declaration. Not included in the runtime host.
package com.orangepixel.residual.desktop;

public class DesktopPreferences implements com.orangepixel.plugins.OrangePreferences {
    public String getDefaultPreferencesDirectory() { throw new UnsupportedOperationException(); }
    public com.badlogic.gdx.Files.FileType getDefaultPreferencesFileType() { throw new UnsupportedOperationException(); }
}
