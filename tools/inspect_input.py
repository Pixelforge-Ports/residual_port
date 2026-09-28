"""Inventory every input file and every JAR member without executing the Windows build."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def record(name, data):
    info = {'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    if data[:2] == b'MZ': info['format'] = 'Windows PE'
    elif data[:4] == b'\x7fELF':
        info['format'] = 'ELF'
        info['elf_bits'] = 32 if data[4] == 1 else 64
        info['elf_machine'] = int.from_bytes(data[18:20],'little' if data[5] == 1 else 'big')
        info['symbol_versions'] = sorted(set(v.decode() for v in re.findall(rb'(?:GLIBC|GLIBCXX|CXXABI)_[0-9.]+',data)))
    elif name.endswith('.class') and data[:4] == b'\xca\xfe\xba\xbe':
        info['format'] = 'Java class'; info['class_major'] = int.from_bytes(data[6:8],'big')
    elif data[:4] == b'PK\x03\x04': info['format'] = 'ZIP/JAR'
    else: info['format'] = 'data/text'
    return info

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    args = parser.parse_args()
    source = args.input.resolve(); out = ROOT/'build/audit'; out.mkdir(parents=True,exist_ok=True)
    files = []
    for path in sorted(source.rglob('*')):
        if not path.is_file(): continue
        files.append(record(path.relative_to(source).as_posix(),path.read_bytes()))
    (out/'input-files.json').write_text(json.dumps(files,indent=2),encoding='utf-8')
    for filename in ('residual.jar','webcache.zip'):
        with zipfile.ZipFile(source/filename) as archive:
            assert archive.testzip() is None, filename
            entries = [record(n,archive.read(n)) for n in archive.namelist()]
        (out/(filename+'.json')).write_text(json.dumps(entries,indent=2),encoding='utf-8')
        print(filename, len(entries), 'entries checked')
    print(len(files),'input files inventoried; reports in',out)

if __name__ == '__main__': main()
