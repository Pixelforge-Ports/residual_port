"""Exercise launch behavior using fake PortMaster runtimes; no game data needed."""
from pathlib import Path
import json, os, shutil, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[1]
config = json.loads((ROOT/'tools/port-config.json').read_text(encoding='utf-8'))
game = config['id']
bash = shutil.which('bash') if os.name != 'nt' else r'C:\Program Files\Git\bin\bash.exe'

def shell_path(path):
    value = Path(path).resolve().as_posix()
    return '/'+value[0].lower()+value[2:] if os.name == 'nt' else value

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write(text)

for case in ['missing-data','success','no-getconf','game-error','bad-data','bad-resolution','no-mount-firmware','missing-portmaster','missing-java-portmaster']:
    folder = ROOT/'build'/'launcher-tests'/case
    folder.mkdir(parents=True, exist_ok=True)
    fixtures = Path(tempfile.mkdtemp(prefix='run-', dir=folder))
    (fixtures/'events').touch()
    sf = shell_path(fixtures)
    pm = fixtures/'home/.local/share/PortMaster'
    data = fixtures/'ports'/game
    data.mkdir(parents=True,exist_ok=True)
    write(data/'libs.aarch64/libjpeg.so.8','test library fixture')
    (pm/'libs').mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/'package'/game/'display.inc',data/'display.inc')
    if case != 'missing-data': write(data/config['game_file'],'test fixture, not game data')
    if case == 'bad-resolution': write(data/'resolution.txt','invalid')
    if case != 'missing-portmaster':
        write(pm/'libs/weston_pkg_0.2.squashfs','')
    if case != 'missing-java-portmaster':
        write(pm/'libs/zulu17.54.21-ca-jre17.0.13-linux.squashfs','')
    if case not in ('missing-portmaster','missing-java-portmaster'):
        write(pm/'harbourmaster','#!/bin/bash\nexit 17\n')
    control = '''get_controls() { :; }
pm_message() { echo "$*"; }
pm_finish() { echo finish >> "$TEST_ROOT/events"; }
pm_platform_helper() { echo platform >> "$TEST_ROOT/events"; }
getconf() { [[ "$TEST_CASE" == no-getconf ]] && return 127; echo 64; }
sleep() { :; }
mount() {
  echo "mount $2" >> "$TEST_ROOT/events"
  if [[ "$TEST_CASE" == mount-error && "$2" == */java ]]; then return 12; fi
  mkdir -p "$2/bin"
  if [[ "$1" == *weston* ]]; then
    cp "$TEST_ROOT/probes/westonwrap.sh" "$2/westonwrap.sh"
  else
    cp "$TEST_ROOT/probes/java" "$2/bin/java"
  fi
}
umount() { echo "unmount $1" >> "$TEST_ROOT/events"; }
ESUDO=
test_mapper() { export TEST_MAPPER=1; exec "$TEST_ROOT/probes/mapper" "$@"; }
GPTOKEYB2=test_mapper
directory="$TEST_ROOT"
DEVICE_ARCH=aarch64
PM_CAN_MOUNT=Y
[[ "$TEST_CASE" == no-mount-firmware ]] && PM_CAN_MOUNT=N
CFW_NAME=test
DISPLAY_WIDTH=720
DISPLAY_HEIGHT=480
sdl_controllerconfig=test-controller
'''
    write(pm/'control.txt',control)
    write(fixtures/'probes/java','''#!/bin/bash
[[ "$TEST_CASE" == bad-data ]] && exit 8
if [[ "$TEST_GAME" == mewnbase ]]; then printf '1.0.1' > "$TEST_ROOT/ports/mewnbase/game-version.txt"; fi
exit 0
''')
    write(fixtures/'probes/mapper','''#!/bin/bash
[[ "$TEST_MAPPER" == 1 && "$1" == java && "$2" == -x ]] || exit 2
echo mapper >> "$TEST_ROOT/events"
exit 0
''')
    write(fixtures/'probes/westonwrap.sh','''#!/bin/bash
if [[ "$1" == cleanup ]]; then
  echo cleanup >> "$TEST_ROOT/events"
  exit 0
fi
[[ "$1 $2 $3 $4" == 'headless noop kiosk crusty_glx_gl4es' ]] || exit 3
[[ "$CRUSTY_BLOCK_INPUT" == 1 ]] || exit 8
[[ "$LD_LIBRARY_PATH" == "$TEST_ROOT/ports/$TEST_GAME/libs.aarch64:"* ]] || exit 10
[[ -f "$TEST_ROOT/ports/$TEST_GAME/libs.aarch64/libjpeg.so.8" ]] || exit 11
[[ "$WESTON_HEADLESS_WIDTH" == 720 && "$WESTON_HEADLESS_HEIGHT" == 480 ]] || exit 4
[[ "$*" == *"-D$TEST_GAME.width=720"* && "$*" == *"-D$TEST_GAME.height=480"* ]] || exit 5
if [[ "$TEST_GAME" == gunslugs3 ]]; then [[ "$*" == *'runtime/lib/*:'* ]] || exit 6; fi
if [[ "$TEST_GAME" == mewnbase ]]; then
  [[ "$PWD" == */userdata/1.0.1 && "$*" == *'-Dmewnbase.data='* ]] || exit 7
fi
for count in {1..50}; do
  grep -q '^mapper$' "$TEST_ROOT/events" && break
  /usr/bin/sleep 0.01
done
echo game >> "$TEST_ROOT/events"
[[ "$TEST_CASE" == game-error ]] && exit 9
exit 0
''')
    launcher=(ROOT/'package'/config['script']).read_text(encoding='utf-8')
    launcher=launcher.replace('weston_dir=/tmp/weston','weston_dir="'+sf+'/weston"').replace('/tmp/javaruntime/',sf+'/java')
    # Force fixture discovery even on a machine with a real PortMaster installed.
    launcher=launcher.replace('/opt/system/Tools/PortMaster',sf+'/absent1').replace('/opt/tools/PortMaster',sf+'/absent2')
    write(fixtures/'launcher.sh',launcher)
    env=dict(os.environ,TEST_ROOT=sf,TEST_CASE=case,TEST_GAME=game)
    command='export PATH=/usr/bin:$PATH; export HOME="$TEST_ROOT/home" XDG_DATA_HOME="$TEST_ROOT/home/.local/share"; chmod +x "$TEST_ROOT/probes/"* "$TEST_ROOT/home/.local/share/PortMaster/harbourmaster"; bash "$TEST_ROOT/launcher.sh"'
    result=subprocess.run([bash,'-c',command],env=env,capture_output=True,text=True,timeout=20)
    write(fixtures/'test.log',result.stdout+result.stderr)
    events=(fixtures/'events').read_text(encoding='utf-8').splitlines()
    expected=0 if case in ('success','no-getconf','game-error','no-mount-firmware') else 1
    assert result.returncode==expected,(game,case,result.returncode,result.stdout,result.stderr)
    assert events.count('finish')==int(case in ('success','no-getconf','game-error','no-mount-firmware')),(case,events)
    ran=case in ('success','no-getconf','game-error','no-mount-firmware')
    assert ('game' in events)==ran and events.count('cleanup')==int(ran),(case,events)
    if expected == 1:
        assert 'Residual:' in result.stdout and 'fail: command not found' not in result.stderr,(case,result.stdout,result.stderr)
    if ran:
        assert 'mapper' in events and 'platform' in events,events
        game_index=events.index('game')
        cleanup_index=events.index('cleanup')
        finish_index=events.index('finish')
        assert game_index < cleanup_index < finish_index,(case,events)
        unmount_indexes=[i for i,event in enumerate(events) if event.startswith('unmount ')]
        if case == 'no-mount-firmware':
            assert not unmount_indexes,(case,events)
        else:
            assert len(unmount_indexes)==4,(case,events)
            assert all(i<game_index for i in unmount_indexes[:2]),(case,events)
            assert all(cleanup_index<i<finish_index for i in unmount_indexes[2:]),(case,events)
    if case in ('missing-data','missing-portmaster'):
        assert not any(e.startswith('mount ') for e in events),events
    if case == 'missing-java-portmaster':
        assert sum(e.startswith('mount ') for e in events)==1 and events.count('finish')==0,(case,events)
    if case in ('success','no-getconf','game-error','no-mount-firmware'):
        assert sum(e.startswith('mount ') for e in events)==2,events
    if case in ('bad-data','bad-resolution'):
        assert sum(e.startswith('mount ') for e in events)==2,events
        assert 'finish' not in events and 'cleanup' not in events,events
    launcher_source=(ROOT/'package'/config['script']).read_text(encoding='utf-8')
    assert 'fail() {' not in launcher_source and 'fail "' not in launcher_source
    assert '$ESUDO "$weston_dir/westonwrap.sh" cleanup' in launcher_source
    print('LAUNCHER_OK',game,case,flush=True)
