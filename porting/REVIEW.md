# Samsung Galaxy S24 FE / One UI 9 — profile review

**Device:** SM-S721B (`r12s`)  
**PDA:** `S721BXXUEEZIF`  
**Build fingerprint:** `samsung/r12sxins/r12s:17/CP2A.260605.016/S721BXXUEEZIF:user/release-keys`  
**Kernel:** `6.1.162-android14-11`  
**Android:** 17 / One UI 9

## Verified from existing records

- Firmware AP package downloaded, exact `boot.img.lz4` extracted, hashes recorded.
- ARM64 kernel and BTF decoded, 115,698 symbols reported.
- Checked `file_operations` and `task_struct` layout offsets match the older firmware reference.
- `page.compound_head = 0x08`, `page.page_type = 0x30`, `slab.slab_cache = 0x18` validated against BTF.
- Runtime `sched_blocked_reason` event ID `106` returned via Shizuku shell.
- Samsung bootloader image extracted and kernel handoff located by offline disassembly.
- Reference target `r12s-S721BXXSCDZF3` compiles with NDK r29; **only the old target**.
- Disassembly of `remove_waiter` raises a kernel patch-status concern, but does **not** demonstrate exploitability.

## Open questions

- Confirm all firmware-specific memory/slide/fingerprint assumptions with independent evidence.
- Confirm kernel security patch status with source-level or maintainer review.
- Confirm KernelSU components and late-loading approach against this exact firmware.
- Establish safe hardware validation and recovery procedures.
- Confirm OneOS compatibility after any separate root-method validation.

## Safety and scope

No built file in this repository is represented as a working exploit for `S721BXXUEEZIF`.
Do not deploy old-firmware `.so` files, bypass profile checks, or flash images from other models.
The research workflow verifies saved report consistency only; it does **not** perform rooting, kernel exploitation, or firmware flashing.

## Maintainer review request

> Requesting an independent compatibility review for Samsung SM-S721B (`r12s`) on `S721BXXUEEZIF`, Android 17, kernel `6.1.162-android14-11`. Firmware, symbols, BTF, runtime trace event ID and older-target build evidence are documented in this repository. Existing older target is not considered compatible. Can maintainers advise what evidence and recovery preparations are required before a candidate could be considered device-testable?
