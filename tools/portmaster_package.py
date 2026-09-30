"""Build one universal BYO-data ZIP from an explicit redistributable file list."""
from pathlib import Path
import hashlib
import json
import zipfile

def settings(root):
    return json.loads((Path(root)/'tools/port-config.json').read_text(encoding='utf-8'))

def public_files(root):
    root = Path(root)
    config = settings(root)
    package = root/'package'
    game = config['id']
    names = [config['script'], 'port.json', 'README.md', 'gameinfo.xml', 'screenshot.png', 'cover.png',
             game+'/display.inc', game+'/gamedata/place your game data file here.txt',
             game+'/runtime/'+game+'-host.jar']
    names += [p.relative_to(package).as_posix()
              for p in sorted((package/game/'licenses').iterdir()) if p.is_file()]
    lock = root/'tools/runtime-lock.json'
    if config.get('runtime_libraries'):
        for entry in json.loads(lock.read_text(encoding='utf-8')):
            if entry['test_only']:
                continue
            library_dir = Path(entry.get('directory', 'runtime/lib'))
            if library_dir.is_absolute() or '..' in library_dir.parts:
                raise ValueError('Unsafe runtime library directory: '+str(library_dir))
            name = (Path(game)/library_dir/entry['name']).as_posix()
            if hashlib.sha256((package/name).read_bytes()).hexdigest() != entry['sha256']:
                raise ValueError('Runtime checksum mismatch: '+name)
            names.append(name)
    return {name: (package/name).read_bytes() for name in names}

def public_directories(root):
    config = settings(root)
    return sorted({config['id']+'/'+name.strip('/')+'/'
                   for name in config.get('directories', [])})

def installed_name(name, config):
    if '/' not in name and name != config['script']:
        return config['id']+'/'+(config['id']+'.md' if name == 'README.md' else name)
    return name

def export(root):
    root = Path(root)
    config = settings(root)
    files = public_files(root)
    directories = public_directories(root)
    tree = root/'ports'/config['id']
    manifest = root/'build/portmaster-export.json'
    manifest.parent.mkdir(parents=True, exist_ok=True)
    previous = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else []
    for name in previous:
        path = (tree/name).resolve()
        path.relative_to(tree.resolve())
        if name not in files and path.is_file():
            path.unlink()
    for name in directories:
        (tree/name.rstrip('/')).mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        target = tree/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    manifest.write_text(json.dumps(sorted(files)), encoding='utf-8')
    destination = root/'dist'/config['zip']
    destination.parent.mkdir(exist_ok=True)
    temporary = root/'build'/config['zip']
    with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted([*files, *directories]):
            info = zipfile.ZipInfo(installed_name(name, config), (2026, 9, 12, 0, 0, 0))
            info.create_system = 3
            if name.endswith('/'):
                info.external_attr = (0o40755 << 16) | 0x10
                info.compress_type = zipfile.ZIP_STORED
                archive.writestr(info, b'')
            else:
                info.external_attr = (0o100755 if name.endswith('.sh') else 0o100644) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, files[name])
    temporary.replace(destination)
    print('Built', destination)

if __name__ == '__main__':
    export(Path(__file__).resolve().parents[1])
