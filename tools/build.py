"""Build the Residual PortMaster host and BYO-data ZIP without proprietary game data."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import zipfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SHA256 = '8f8caa7dc36f5ab9c7119046ccce87e3f7a2d61680dc60970fa3d2b2d619ee01'

def add(out, source, target):
    entry = zipfile.ZipInfo(target, (2026, 9, 9, 0, 0, 0))
    entry.create_system = 3
    entry.external_attr = (0o100755 if target.endswith('.sh') else 0o100644) << 16
    entry.compress_type = zipfile.ZIP_DEFLATED
    out.writestr(entry, source.read_bytes())

def sync_package_readme():
    source = (ROOT/'README.md').read_text(encoding='utf-8')
    compile_section = '\n## Compile\n'
    if compile_section not in source:
        raise SystemExit('README.md must contain a Compile section separating source instructions from package instructions')
    package_readme = source.split(compile_section, 1)[0].rstrip() + '\n'
    destination = ROOT/'package/README.md'
    if not destination.is_file() or destination.read_text(encoding='utf-8') != package_readme:
        destination.write_text(package_readme, encoding='utf-8', newline='\n')

def package():
    sync_package_readme()
    from portmaster_package import export
    export(ROOT)
    from verify_package import verify
    verify(ROOT)


DEPENDENCIES = {
    'gdx': 'd5860eaf5787a4083e14183ae47da99d3e6908029ca99691947bbd0852b49264',
    'gdx-backend-lwjgl3': '963d49a2846d294d13a5beb2d9a8e51bd7d32fac78a35bfeca23ebf8f1ec2d64',
}

def dependencies(offline=False):
    folder = ROOT/'build/dependencies'
    folder.mkdir(parents=True, exist_ok=True)
    paths = []
    for artifact, digest in DEPENDENCIES.items():
        name = artifact + '-1.13.1.jar'
        path = folder/name
        if not path.is_file():
            if offline:
                raise SystemExit('Missing cached dependency: ' + str(path))
            url = 'https://repo.maven.apache.org/maven2/com/badlogicgames/gdx/' + artifact + '/1.13.1/' + name
            print('Downloading', name, flush=True)
            with urllib.request.urlopen(url, timeout=60) as response:
                data = response.read()
            if hashlib.sha256(data).hexdigest() != digest:
                raise SystemExit('Dependency checksum mismatch: ' + name)
            path.write_bytes(data)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise SystemExit('Cached dependency checksum mismatch: ' + name)
        paths.append(path)
    return paths

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-jar', type=Path, help='Optional compatibility fingerprint check; never used for compilation')
    parser.add_argument('--jdk', type=Path)
    parser.add_argument('--offline', action='store_true', help='Use only cached compile dependencies')
    parser.add_argument('--package-only', action='store_true')
    args = parser.parse_args()
    if args.package_only:
        if not (ROOT/'package/residual/runtime/residual-host.jar').is_file():
            parser.error('Run a full build before --package-only')
        package()
        return
    if not args.jdk:
        parser.error('--jdk is required')
    if args.game_jar and hashlib.sha256(args.game_jar.read_bytes()).hexdigest() != SHA256:
        parser.error('Unsupported game JAR fingerprint')
    suffix = '.exe' if os.name == 'nt' else ''
    javac = args.jdk.resolve()/'bin'/('javac'+suffix)
    if not javac.is_file():
        parser.error('JDK compiler not found: ' + str(javac) + '. Use the installed JDK directory, quoted with double quotes on Windows.')
    classes = ROOT/'build/classes'
    classes.mkdir(parents=True, exist_ok=True)
    # Drop stale host bytecode after source files are removed or renamed.
    for old in classes.rglob('*.class'):
        old.resolve().relative_to(classes.resolve())
        old.unlink()
    cp = os.pathsep.join(str(p) for p in dependencies(args.offline))
    sources = sorted((ROOT/'compile-api').rglob('*.java')) + sorted((ROOT/'src').rglob('*.java'))
    subprocess.run([str(javac), '--release', '8', '-Xlint:-options', '-encoding', 'UTF-8',
                    '-cp', cp, '-d', str(classes), *map(str, sources)], check=True)
    runtime = ROOT/'package/residual/runtime'
    runtime.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(runtime/'residual-host.jar', 'w') as out:
        # Only adaptation classes ship. Compile declarations and libraries never do.
        for path in sorted((classes/'org/portmaster/residual').rglob('*.class')):
            add(out, path, path.relative_to(classes).as_posix())
    package()

if __name__ == '__main__':
    main()
