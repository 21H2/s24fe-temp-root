#!/usr/bin/env python3
"""Offline analysis of an exact Samsung Android boot.img[.lz4]. No device access."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
import lz4.frame


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def raw_btf(image: bytes) -> tuple[bytes | None, list[dict]]:
    # Raw BTF uses little-endian 0xeb9f; validate full header and section bounds.
    needle = b"\x9f\xeb\x01\x00"
    hits: list[dict] = []
    start = 0
    while (pos := image.find(needle, start)) != -1:
        start = pos + 1
        if pos + 24 > len(image):
            continue
        (magic, version, flags, hdr_len, typ_off, typ_len,
         str_off, str_len) = struct.unpack_from("<HBBIIIII", image, pos)
        if (magic, version, flags) != (0xEB9F, 1, 0) or hdr_len < 24:
            continue
        end = pos + hdr_len + max(typ_off + typ_len, str_off + str_len)
        str_start = pos + hdr_len + str_off
        if end > len(image) or str_start >= end or image[str_start] != 0:
            continue
        if typ_len == 0 or str_len == 0:
            continue
        hits.append({"offset": pos, "end": end, "size": end - pos})
    if len(hits) != 1:
        return None, hits
    item = hits[0]
    return image[item["offset"]:item["end"]], hits


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--report', required=True, type=Path)
    p.add_argument('--firmware', required=True)
    p.add_argument('--kernel-version', required=True)
    args = p.parse_args()

    downloaded = args.input.read_bytes()
    if downloaded.startswith(b'ANDROID!'):
        boot = downloaded
        encoding = 'uncompressed boot.img'
    else:
        boot = lz4.frame.decompress(downloaded)
        encoding = 'LZ4 frame'
    if not boot.startswith(b'ANDROID!'):
        raise SystemExit('Not an Android boot.img after decompression')

    kernel_size = struct.unpack_from('<I', boot, 8)[0]
    header_version = struct.unpack_from('<I', boot, 40)[0]
    if header_version not in (3, 4):
        raise SystemExit(f'Unexpected Android boot header version: {header_version}')
    if not 0 < kernel_size <= len(boot) - 4096:
        raise SystemExit('Kernel length does not fit the v3/v4 boot image')

    kernel = boot[4096:4096 + kernel_size]
    if len(kernel) != kernel_size:
        raise SystemExit('Truncated kernel')
    args.output.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    (args.output / 'kernel').write_bytes(kernel)

    btf, hits = raw_btf(kernel)
    if btf is not None:
        (args.output / 'vmlinux.btf').write_bytes(btf)

    info = {
        'target_device': 'Samsung Galaxy S24 FE / SM-S721B',
        'expected_firmware_from_user': args.firmware,
        'expected_kernel_version_from_user': args.kernel_version,
        'warning': 'An image alone does not verify the phone firmware identity or exploit viability.',
        'boot_format': encoding,
        'boot_header_version': header_version,
        'downloaded_file_sha256': digest(downloaded),
        'boot_image_sha256': digest(boot),
        'kernel_size_bytes': kernel_size,
        'kernel_sha256': digest(kernel),
        'btf_candidate_count': len(hits),
        'btf_candidates': hits,
        'btf_sha256': digest(btf) if btf else None,
        'build_status': 'offline inspection only (unless separate CI build step succeeds)',
    }
    args.report.write_text(json.dumps(info, indent=2) + '\n')
    print(args.report.read_text())


if __name__ == '__main__':
    main()
