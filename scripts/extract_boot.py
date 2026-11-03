#!/usr/bin/env python3
"""Extract boot.img.lz4 from Samsung ZIP -> AP.tar.md5 in a streaming manner.

Does not extract the huge AP tar to disk and does not contact any device.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tarfile
import zipfile


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def extract(firmware_zip, expected_pda, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(firmware_zip) as zf:
        ap_matches = [i for i in zf.infolist() if not i.is_dir()
                      and Path(i.filename).name.startswith('AP_')
                      and expected_pda in Path(i.filename).name
                      and Path(i.filename).name.endswith(('.tar.md5', '.tar'))]
        if len(ap_matches) != 1:
            candidates = [i.filename for i in zf.infolist() if '/AP_' in '/'+i.filename]
            raise RuntimeError(f'Expected ONE AP tar for {expected_pda}, found {len(ap_matches)}. AP entries: {candidates}')
        ap = ap_matches[0]
        print(f'Streaming {ap.filename} ({ap.file_size / (1024**3):.2f} GiB uncompressed tar)')
        found = None
        with zf.open(ap) as ap_stream:
            with tarfile.open(fileobj=ap_stream, mode='r|') as tar:
                for member in tar:
                    if not member.isfile():
                        continue
                    if Path(member.name).name != 'boot.img.lz4':
                        continue
                    if member.size <= 0 or member.size > 1024**3:
                        raise ValueError(f'Unexpected boot image size: {member.size}')
                    in_file = tar.extractfile(member)
                    if in_file is None:
                        raise ValueError('Could not read boot.img.lz4 from AP')
                    output = out_dir / 'boot.img.lz4'
                    with in_file, open(output, 'wb') as out:
                        shutil.copyfileobj(in_file, out, length=4*1024*1024)
                    found = {'member': member.name, 'size_bytes': member.size,
                             'sha256': sha256(output), 'AP_filename': ap.filename}
                    print(f'Extracted {member.name}: {member.size:,} bytes')
                    break
        if not found:
            raise RuntimeError('AP package has no boot.img.lz4. Inspect its member names / boot format.')
        return found


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--firmware-zip', required=True, type=Path)
    p.add_argument('--pda', required=True)
    p.add_argument('--output-dir', required=True, type=Path)
    p.add_argument('--report', required=True, type=Path)
    a=p.parse_args()
    found=extract(a.firmware_zip,a.pda,a.output_dir)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps({'model':'SM-S721B', 'pda':a.pda,
             'source':'Samsung firmware AP tar', 'extracted':found,
             'warning':'Extracting the boot image does NOT provide root or prove OneOS compatibility.'},indent=2)+'\n')
    print(a.report.read_text())

if __name__=='__main__': main()
