"""Run real game input tests at five display sizes using a local Java 17 runtime."""
import argparse, os, shutil, struct, subprocess, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--java',type=Path,required=True);p.add_argument('--jdk',type=Path,required=True);p.add_argument('--game-jar',type=Path,required=True);p.add_argument('--seed-saves',type=Path)
a=p.parse_args();java=a.java.resolve();game=a.game_jar.resolve()
classes=ROOT/'build/test-classes';classes.mkdir(parents=True,exist_ok=True)
compile_cp=ROOT/'build/test-compile-classpath'
compile_cp.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(game) as archive:
 for entry in archive.infolist():
  if entry.filename.endswith('.class'):
   target=(compile_cp/entry.filename).resolve();target.relative_to(compile_cp.resolve())
   target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(archive.read(entry))
cp=os.pathsep.join(map(str,[compile_cp,ROOT/'package/residual/runtime/residual-host.jar']))
subprocess.run([str(a.jdk.resolve()/'bin'/('javac.exe' if os.name=='nt' else 'javac')),'--release','8','-Xlint:-options','-cp',cp,'-d',str(classes),str(ROOT/'tests/GameplaySmoke.java')],check=True)
cp=os.pathsep.join(map(str,[classes,ROOT/'package/residual/runtime/residual-host.jar',game]))
for width,height in [(640,480),(720,480),(720,720),(1024,768),(1280,720)]:
 out=ROOT/'build/resolutions'/f'{width}x{height}';out.mkdir(parents=True,exist_ok=True)
 saves=out/'saves'
 if a.seed_saves and not saves.exists(): shutil.copytree(a.seed_saves,saves)
 command=[str(java),'-Xms32m','-Xmx256m','-XX:+UseSerialGC','-Xlog:class+load=info','-Dresidual.hidden=true',f'-Dresidual.width={width}',f'-Dresidual.height={height}',f'-Dresidual.saves={saves}',f'-Dresidual.output={out}','-cp',cp,'org.portmaster.residual.GameplaySmoke']
 with (out/'run.log').open('w') as log: subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=360)
 log=(out/'run.log').read_text();assert 'GAMEPLAY_OK' in log
 assert 'com.codedisaster.steamworks.SteamAPI source:' not in log
 assert 'com.studiohartman.jamepad.ControllerManager source:' not in log
 assert 'com.orangepixel.residual.desktop.EpicGames source:' not in log
 png=(out/'final.png').read_bytes();assert struct.unpack('>II',png[16:24])==(width,height)
 assert list(saves.rglob('config.prefs'))
 print(f'RESOLUTION_OK {width}x{height}',flush=True)
