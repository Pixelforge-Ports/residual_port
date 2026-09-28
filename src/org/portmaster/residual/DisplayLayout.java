package org.portmaster.residual;

/** Preserve the game's square minimum view with a logical height divisible by 160, 240, 320 and 480 for distinct HUD zoom levels. */
public final class DisplayLayout {
    public int screenWidth = 640, screenHeight = 480;
    public int gameWidth = 960, gameHeight = 960;
    public int x, y, width = 640, height = 360;
    public void resize(int w, int h) {
        if (w < 160 || h < 160) return;
        screenWidth = w; screenHeight = h;
        gameWidth = Math.max(960, (int)Math.round(960.0 * w / h));
        double scale = Math.min((double)w / gameWidth, (double)h / gameHeight);
        width = (int)Math.round(gameWidth * scale);
        height = (int)Math.round(gameHeight * scale);
        x = (w - width) / 2; y = (h - height) / 2;
    }
    public int viewportX(int value) { return x + (int)Math.round((double)value * width / gameWidth); }
    public int viewportY(int value) { return y + (int)Math.round((double)value * height / gameHeight); }
    public int viewportWidth(int value) { return (int)Math.round((double)value * width / gameWidth); }
    public int viewportHeight(int value) { return (int)Math.round((double)value * height / gameHeight); }
    public int inputX(int value) { return (int)((double)(value - x) * gameWidth / width); }
    public int inputY(int value) {
        return (int)((double)(value - (screenHeight - y - height)) * gameHeight / height);
    }
    public int cursorX(int value) { return viewportX(value); }
    public int cursorY(int value) { return screenHeight - y - height + viewportHeight(value); }
}
