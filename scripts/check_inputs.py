#!/usr/bin/env python3
"""Refuse to download the wrong Samsung firmware."""
import argparse
import re

p = argparse.ArgumentParser()
p.add_argument('--version', required=True)
p.add_argument('--pda', required=True)
a = p.parse_args()
parts = a.version.strip().split('/')
if len(parts) not in (3, 4) or any(not re.fullmatch(r'[A-Z0-9]+', x) for x in parts):
    p.error('Version must be PDA/CSC/MODEM, optionally /PDA, in uppercase.')
if parts[0] != a.pda or (len(parts) == 4 and parts[3] != a.pda):
    p.error(f'Firmware PDA does not match {a.pda}; stopping to avoid a wrong kernel!')
if not parts[1].startswith('S721B') or not parts[2].startswith('S721B'):
    p.error('The CSC and modem must both belong to an SM-S721B firmware version.')
print('Validated FUS request:', a.version)
