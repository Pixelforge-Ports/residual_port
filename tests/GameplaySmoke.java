package org.portmaster.residual;
import com.badlogic.gdx.*;
import com.badlogic.gdx.backends.lwjgl3.Lwjgl3Application;
public class GameplaySmoke extends Main {
 int frame, play, previous=-1; boolean reached; long started=System.nanoTime();
 public static void main(String[] args) throws Exception { new Lwjgl3Application(new GameplaySmoke(),configuration()); }
 @Override public void render() {
  frame++;
  if (frame>300) {
   if(frame%90==0) Gdx.input.getInputProcessor().keyDown(Input.Keys.X);
   if(frame%90==3) Gdx.input.getInputProcessor().keyUp(Input.Keys.X);
  }
  if(GameState==7) {
   reached=true;play++;
   if(play==1) Gdx.input.getInputProcessor().keyDown(Input.Keys.D);
   if(play==120) Gdx.input.getInputProcessor().keyUp(Input.Keys.D);
   if(play%90==0) Gdx.input.getInputProcessor().keyDown(Input.Keys.W);
   if(play%90==20) Gdx.input.getInputProcessor().keyUp(Input.Keys.W);
  }
  super.render();
  if(GameState!=previous) {System.out.println("STATE "+frame+" "+GameState);previous=GameState;}
  if(frame%600==0) capture(System.getProperty("residual.output")+"/frame"+frame+".png");
  if(play>=240 || frame>=12000) {
   capture(System.getProperty("residual.output")+"/final.png");
   if(!reached) throw new IllegalStateException("Gameplay not reached");
   double seconds=(System.nanoTime()-started)/1e9;
   if(seconds<(frame-2)/60.0) throw new IllegalStateException("Frame cap exceeded");
   if(Boolean.getBoolean("residual.testSave")) {
    com.orangepixel.residual.SaveGameObject.SaveGame();
    com.orangepixel.residual.SaveGameObject saved=com.orangepixel.residual.SaveGameObject.LoadGame(activePlayer.currentSaveFileSlotIdx,false);
    if(saved==null || !saved.hasSaveGame()) throw new IllegalStateException("Save readback failed");
    System.out.println("SAVE_READBACK_OK slot="+saved.saveGameSlotIdx);
   }
   System.out.println("GAMEPLAY_OK frames="+frame+" play="+play+" seconds="+seconds);
   Gdx.app.exit();
  }
 }
}
