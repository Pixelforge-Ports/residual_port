"""Validate redistributable boundaries, metadata, licenses and installation layout."""
import io
import json
from pathlib import Path
import struct
import xml.etree.ElementTree as ET
import zipfile
from portmaster_package import settings, public_files, public_directories, installed_name

def require(condition, message):
    if not condition:
        raise ValueError(message)

def verify(root):
    root = Path(root)
    config = settings(root)
    game = config['id']
    files = public_files(root)
    expected = {installed_name(n, config): data for n, data in files.items()}
    directories = {installed_name(n, config) for n in public_directories(root)}
    with zipfile.ZipFile(root/'dist'/config['zip']) as archive:
        require(archive.testzip() is None, 'Damaged ZIP')
        require(len(archive.namelist()) == len(expected)+len(directories), 'Duplicate/extra ZIP entry')
        require(set(archive.namelist()) == set(expected)|directories, 'Unexpected ZIP contents')
        for entry in archive.infolist():
            mode = (entry.external_attr >> 16) & 0o777
            if entry.is_dir():
                require(entry.filename in directories and archive.read(entry) == b'', 'Unexpected directory: '+entry.filename)
                require(mode == 0o755, 'Wrong directory permissions')
            else:
                require(archive.read(entry) == expected[entry.filename], 'Stale file: '+entry.filename)
                require(mode == (0o755 if entry.filename.endswith('.sh') else 0o644), 'Wrong Unix permissions')
            require(entry.filename.startswith(game+'/') or entry.filename == config['script'], 'Unsafe path')
    require(sorted(p.name for p in (root/'dist').iterdir()) == [config['zip']], 'dist must contain only the universal ZIP')
    metadata = json.loads(files['port.json'])
    attr = metadata['attr']
    require(set(metadata) == {'version', 'name', 'items', 'items_opt', 'attr'}, 'Wrong PortMaster metadata fields')
    require(metadata['version'] == 4 and metadata['name'] == config['zip'], 'Wrong metadata version/name')
    require(metadata['items'] == [config['script'], game], 'Wrong items')
    require(metadata['items_opt'] == [], 'Unexpected optional package items')
    require(set(attr) == {'title', 'porter', 'desc', 'desc_md', 'inst', 'inst_md', 'genres', 'image', 'rtr', 'exp', 'runtime', 'store', 'availability', 'reqs', 'arch', 'min_glibc'}, 'Wrong PortMaster attribute fields')
    require(directories == {game+'/gamedata/'}, 'BYO game-data folder missing from ZIP')
    require(attr['porter'] == ['Pixelforge ports (Ronax)'], 'Wrong porter')
    require(attr['availability'] == 'paid' and attr['rtr'] is False and attr['exp'] is False, 'Wrong BYO flags')
    require(attr['arch'] == ['aarch64'], 'Wrong architecture')
    require(attr['runtime'] == ['weston_pkg_0.2.squashfs', 'zulu17.54.21-ca-jre17.0.13-linux.squashfs'], 'Wrong runtimes')
    require(isinstance(attr['inst_md'], str) and all(term in attr['inst_md'] for term in (
        '<Port directory>/residual/gamedata/Residual.jar',
        'download_depot 1290780 1290782 3716360872293972653',
        '83,168,018 bytes',
        '8f8caa7dc36f5ab9c7119046ccce87e3f7a2d61680dc60970fa3d2b2d619ee01'
    )), 'Missing detailed game-data installation instructions')
    require(all(set(s) == {'name','gameurl','developerurl'} for s in attr['store']), 'Invalid store objects')
    require({s['name'] for s in attr['store']} == {'GOG', 'Steam'}, 'Missing game store source')
    require(files['README.md'].startswith(b'## Notes\n'), 'README must start with Notes')
    source_readme = (root/'README.md').read_text(encoding='utf-8')
    compile_section = '\n## Compile\n'
    require(compile_section in source_readme, 'Source README must separate build instructions with a Compile heading')
    expected_readme = source_readme.split(compile_section, 1)[0].rstrip() + '\n'
    packaged_readme = files['README.md'].decode('utf-8')
    require(packaged_readme == expected_readme, 'Package README must match source README before Compile')
    required_readme = [
        '## Get `residual.jar`',
        'download_depot 1290780 1290782 3716360872293972653',
        'steamapps/content/app_1290780/depot_1290782/residual.jar',
        '83,168,018 bytes',
        '8f8caa7dc36f5ab9c7119046ccce87e3f7a2d61680dc60970fa3d2b2d619ee01',
        '| D-pad | Move |', '| A | Action |', '| B | Back |', '| Y | Inventory |',
        '| X | Jump |', '| Start | Pause |', '| L1 / R1 | Visor navigation |',
        '| Start + Select | Close |'
    ]
    require(all(item in packaged_readme for item in required_readme), 'README missing requested game-data or controller instructions')
    require((root/'package/testing_thread.txt').read_bytes() == (root/'testing_thread.txt').read_bytes(), 'Stale testing thread')
    for name, data in files.items():
        if name.endswith(('.sh','.ini','.inc','.md','.json','.xml','.txt')):
            require(b'\r' not in data and not data.startswith(b'\xef\xbb\xbf'), 'Use UTF-8 without BOM and LF: '+name)
    png = files['screenshot.png']
    require(png.startswith(b'\x89PNG\r\n\x1a\n'), 'Missing PNG screenshot')
    width, height = struct.unpack('>II', png[16:24])
    require(width >= 640 and height >= 480, 'Screenshot below 640x480')
    cover = files['cover.png']
    require(cover.startswith(b'\x89PNG\r\n\x1a\n'), 'Missing PNG cover')
    require(struct.unpack('>II', cover[16:24]) == (640, 480), 'Cover must be 640x480')
    xml = ET.fromstring(files['gameinfo.xml']).find('game')
    require(xml.findtext('path') == './'+config['script'], 'Wrong gameinfo path')
    require(xml.findtext('image') == './'+game+'/cover.png', 'Wrong image path')
    require(xml.findtext('developer') and xml.findtext('desc'), 'Incomplete gameinfo')
    launcher = files[config['script']].decode('utf-8')
    require('$GPTOKEYB2 java -x &' in launcher and '$GPTOKEYB2 java -c ' not in launcher, 'Launcher must use gptokeyb2 Xbox 360 mode')
    require('$GPTOKEYB ' not in launcher and 'TEXTINPUTINTERACTIVE' not in launcher, 'Legacy mapper setup')
    require('CRUSTY_BLOCK_INPUT=1' in launcher, 'Raw controller input must be blocked to avoid duplicate input')
    require('LD_LIBRARY_PATH=$GAMEDIR/libs.${DEVICE_ARCH}:$LD_LIBRARY_PATH' in launcher, 'Weston must load port-specific architecture libraries')
    require('GAMEDATADIR="$GAMEDIR/gamedata"' in launcher and 'jar_filename="Residual.jar"' in launcher, 'Wrong game-data location or filename')
    require('"$GAMEDATADIR/$jar_filename"' in launcher and ':$GAMEDATADIR/$jar_filename' in launcher, 'Launcher must use the BYO JAR from gamedata/')
    require('fail() {' not in launcher and '|| fail "' not in launcher, 'Launcher must use inline pm_message errors')
    cleanup_line = '$ESUDO "$weston_dir/westonwrap.sh" cleanup'
    require(launcher.count(cleanup_line) == 1 and launcher.rfind(cleanup_line) < launcher.rfind('pm_finish'), 'Weston cleanup must precede final pm_finish')
    require(not any(n.endswith(('.gptk','.ini')) for n in files), 'Xbox 360 mode must not ship an unused keyboard mapping')
    main_source = (root/'src/org/portmaster/residual/Main.java').read_text(encoding='utf-8')
    require('argument_noController = false;' in main_source, 'Host must enable the game controller path')
    require('Gdx.app = (Application)Proxy.newProxyInstance' not in main_source, 'Preserve the backend Application identity for controller-manager lookup')
    require('input=gptokeyb2 Xbox 360' in main_source, 'Startup log must report the active controller mode')
    license_root = game+'/licenses/'
    license_files = {name[len(license_root):] for name in files if name.startswith(license_root)}
    require(license_files == {'LICENSE-'+game+'-host.txt', 'LICENSE-libjpeg-turbo.txt'}, 'Package must include the host and libjpeg licenses')
    host_license = files[license_root+'LICENSE-'+game+'-host.txt']
    require(b'MIT License' in host_license and b'Component: residual-host.jar' in host_license, 'Missing host JAR MIT license')
    jpeg_license = files[license_root+'LICENSE-libjpeg-turbo.txt']
    require(b'Independent JPEG Group' in jpeg_license and b'NO WARRANTY' in jpeg_license, 'Missing libjpeg license terms')
    jpeg = files[game+'/libs.aarch64/libjpeg.so.8']
    require(jpeg[:4] == b'\x7fELF' and jpeg[4] == 2 and struct.unpack('<H', jpeg[18:20])[0] == 183, 'libjpeg must be an AArch64 ELF library')
    require('Independent JPEG Group' in packaged_readme, 'README must acknowledge the bundled JPEG implementation')
    with zipfile.ZipFile(io.BytesIO(files[game+'/runtime/'+game+'-host.jar'])) as host:
        require(bool(host.namelist()), 'Empty host')
        require(all(n.startswith('org/portmaster/'+game+'/') and n.endswith('.class') for n in host.namelist()), 'Game or compile-only classes leaked into host')
    for name, data in files.items():
        require((root/'ports'/game/name).read_bytes() == data, 'Stale public tree: '+name)
    for name in public_directories(root):
        require((root/'ports'/game/name.rstrip('/')).is_dir(), 'Missing public directory: '+name)
    print('PACKAGE_OK', config['zip'], len(expected), 'public files')

if __name__ == '__main__':
    verify(Path(__file__).resolve().parents[1])
