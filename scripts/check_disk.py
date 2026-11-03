#!/usr/bin/env python3
import argparse
import shutil
p = argparse.ArgumentParser()
p.add_argument('--min-gib', type=float, default=25.)
p.add_argument('--path', default='.')
a = p.parse_args()
usage = shutil.disk_usage(a.path)
free = usage.free / 1024 ** 3
print(f'Available: {free:.2f} GiB, required minimum: {a.min_gib} GiB')
if free < a.min_gib:
    p.error('Not enough space on this GitHub runner. Use a larger runner with >=30 GiB free, '
            'or move this workflow to a cloud VM. The downloader cannot fetch a 21.1 GB archive here.')
