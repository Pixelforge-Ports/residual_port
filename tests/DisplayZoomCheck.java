package org.portmaster.residual;
public class DisplayZoomCheck {
 public static void main(String[] args) {
  for(int[] size:new int[][]{{640,480},{720,480},{720,720},{1024,768},{1280,720}}) {
   DisplayLayout l=new DisplayLayout();l.resize(size[0],size[1]);
   int normal=(int)(l.gameHeight/Math.floor(l.gameHeight/480.0));
   int enlarged=(int)(l.gameHeight/Math.floor(l.gameHeight/320.0));
   if(normal!=480 || enlarged!=320) throw new AssertionError("HUD zoom collapsed");
   if(l.width>size[0] || l.height>size[1]) throw new AssertionError("Viewport exceeds display");
   if(Math.abs(l.inputX(l.cursorX(l.gameWidth/2))-l.gameWidth/2)>2) throw new AssertionError("X mapping");
   if(Math.abs(l.inputY(l.cursorY(l.gameHeight/2))-l.gameHeight/2)>2) throw new AssertionError("Y mapping");
  }
  System.out.println("HUD_ZOOM_OK: distinct 480/320 HUD spaces at five resolutions");
 }
}
