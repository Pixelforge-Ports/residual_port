// Compile-only API declaration. Not included in the runtime host.
package com.orangepixel.utils;

public class ArcadeCanvas implements com.badlogic.gdx.ApplicationListener {
    public static boolean argument_noController;
    public static com.orangepixel.plugins.Social mySocial;
    public static com.orangepixel.plugins.OrangePreferences myPreferences;
    public static int GameState;
    public void create() { throw new UnsupportedOperationException(); }
    public void resize(int width, int height) { throw new UnsupportedOperationException(); }
    public void render() { throw new UnsupportedOperationException(); }
    public void pause() { throw new UnsupportedOperationException(); }
    public void resume() { throw new UnsupportedOperationException(); }
    public void dispose() { throw new UnsupportedOperationException(); }
}
