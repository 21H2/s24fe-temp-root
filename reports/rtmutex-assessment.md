# Galaxy S24 FE — rtmutex Assessment

Device: SM-S721B (r12s)
Firmware: S721BXXUEEZIF
Android: 17 / One UI 9
Kernel: 6.1.162-android14-11

## CVE-2026-43499

Status: Vulnerable code pattern likely present.

Static disassembly observations:
- remove_waiter reads SP_EL0 into x20.
- pi_blocked_on is cleared relative to x20.
- rt_mutex_adjust_prio_chain receives x20.
- The upstream waiter->task fix appears absent.

## Other verified information

- 115,698 kernel symbols recovered.
- BTF structure checks matched the older profile.
- Trace event ID 106 verified on-device.
- ARM64 bootloader handoff identified.

## Limitations

Exploitability has not been demonstrated.
KernelSU compatibility is unverified.
No working temporary-root payload exists for this build.
