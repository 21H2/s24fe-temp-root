#!/usr/bin/env python3
"""Verify consistency of already-collected S24 FE research reports.

Does NOT test exploitability, compile payloads, or interact with devices.
"""
import argparse
import json
import re
import sys
from pathlib import Path

EXPECTED = {
    "model": "SM-S721B",
    "codename": "r12s",
    "firmware": "S721BXXUEEZIF",
    "android": 17,
    "kernel": "6.1.162-android14-11",
    "page_size": 4096,
    "trace_event_id": 106,
}
HASH_RE = re.compile(r"^[a-f0-9]{64}$")


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def assess(folder):
    """Return findings without asserting that exploitation works."""
    failures, observations, warnings = [], [], []
    device_path = folder / "device-verified.json"
    boot_path = folder / "boot-analysis.json"
    extraction_path = folder / "extraction.json"
    for path in (device_path, boot_path, extraction_path):
        if not path.is_file():
            failures.append(f"Required report missing: {path.name}")
    if failures:
        return {"result": "fail", "failures": failures,
                "observations": observations, "warnings": warnings,
                "temporary_root_verified": False}

    try:
        device = load_json(device_path)
        boot = load_json(boot_path)
        extraction = load_json(extraction_path)
    except (json.JSONDecodeError, OSError) as exc:
        failures.append(f"Cannot parse reports: {exc}")
        return {"result": "fail", "failures": failures,
                "observations": observations, "warnings": warnings,
                "temporary_root_verified": False}

    for k, expected in EXPECTED.items():
        observed = device.get(k)
        if observed != expected:
            failures.append(f"device.{k}: expected {expected!r}, found {observed!r}")
        else:
            observations.append(f"Device {k}: {observed}")

    fp = device.get("fingerprint", "")
    expected_fp = f"samsung/r12sxins/r12s:17/CP2A.260605.016/{EXPECTED['firmware']}:user/release-keys"
    if fp != expected_fp:
        failures.append("Device fingerprint does not match the recorded exact build")
    else:
        observations.append("Exact build fingerprint matches")

    if device.get("temporary_root_verified") is not False:
        failures.append("temporary_root_verified must remain false until independent device validation")
    if boot.get("expected_firmware_from_user") != EXPECTED["firmware"]:
        failures.append("Boot report firmware differs from device firmware")
    if boot.get("expected_kernel_version_from_user") != EXPECTED["kernel"]:
        failures.append("Boot report kernel version differs from device report")
    if extraction.get("model") != EXPECTED["model"] or extraction.get("pda") != EXPECTED["firmware"]:
        failures.append("Extracted boot image metadata differs from expected model/build")

    extracted = extraction.get("extracted") or {}
    boot_hash = boot.get("downloaded_file_sha256", "")
    extraction_hash = extracted.get("sha256", "")
    if not HASH_RE.fullmatch(boot_hash) or boot_hash != extraction_hash:
        failures.append("Boot-image SHA-256 missing, invalid, or inconsistent across reports")
    else:
        observations.append("Boot image SHA-256 consistent between reports")
    if boot.get("btf_candidate_count") != 1:
        failures.append("Expected exactly one BTF candidate in boot-analysis report")
    else:
        observations.append("One BTF candidate recorded")

    nested_path = folder / "btf-nested-verified.txt"
    if nested_path.is_file():
        nested = nested_path.read_text(encoding="utf-8")
        for entry in ("page.compound_head: 0x8 [MATCH]",
                      "page.page_type: 0x30 [MATCH]",
                      "slab.slab_cache: 0x18 [MATCH]"):
            if entry not in nested:
                warnings.append(f"BTF assertion not present: {entry}")
        if not any("BTF assertion" in x for x in warnings):
            observations.append("Three recorded nested BTF offsets matched")
    else:
        warnings.append("BTF nested-field comparison report missing")

    offsets_path = folder / "offset-comparison.txt"
    if offsets_path.is_file():
        offsets_text = offsets_path.read_text(encoding="utf-8")
        changed = len(re.findall(r"\| CHANGED\s*$", offsets_text, re.M))
        same = len(re.findall(r"\| SAME\s*$", offsets_text, re.M))
        observations.append(f"Recorded offset comparisons: {changed} changed, {same} same")
        if changed != 6 or same != 1:
            warnings.append("Symbol comparison results differ from prior recorded 6/1 tally")
    else:
        warnings.append("Symbol offset comparison report missing")

    warnings.extend([
        "Historical reports do not prove vulnerability or exploitable root access.",
        "Kernel memory-map assumptions and firmware-specific fingerprints remain unverified.",
        "KernelSU compatibility and OneOS support remain unverified.",
        "An offline build is not a device compatibility or safety test.",
    ])
    return {
        "result": "fail" if failures else "pass",
        "failures": failures,
        "observations": observations,
        "warnings": warnings,
        "temporary_root_verified": False,
    }


def markdown_report(result):
    lines = ["# S24 FE One UI 9 research verification", "",
             f"**Consistency checks:** {result['result'].upper()}",
             "", "**Temporary root:** NOT VERIFIED", "",
             "This verifies the consistency of previously collected reports only. It does not test an exploit.", ""]
    for title, entries in (("Failures", result["failures"]),
                           ("Observed evidence", result["observations"]),
                           ("Limitations", result["warnings"])):
        lines.append(f"## {title}")
        lines.extend(f"- {s}" for s in entries) if entries else lines.append("- None")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--reports", type=Path, default=Path("reports"))
    p.add_argument("--json", type=Path)
    p.add_argument("--markdown", type=Path)
    args = p.parse_args(argv)
    report = assess(args.reports)
    md = markdown_report(report)
    print(md)
    for path, content in ((args.json, json.dumps(report, indent=2) + "\n"),
                          (args.markdown, md)):
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
