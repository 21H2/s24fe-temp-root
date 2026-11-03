# S24 FE cloud-only firmware extraction

**Device:** SM-S721B / r12s · One UI 9 · PDA `S721BXXUEEZIF` · kernel reported by owner `6.1.162-android14-11`.

No firmware or boot image upload is required. GitHub Actions can download Samsung firmware from Samsung FUS using [samloader-rs 2.2.0](https://github.com/topjohnwu/samloader-rs), unpack `boot.img.lz4` from the encrypted/decrypted package and upload the boot image as an artifact. Only the firmware-analysis steps run in the cloud: this does **not** give temporary root, install OneOS or bypass model compatibility.

## Run

1. Create/open your repo `s24fe-temp-root` and upload the files **inside** this ZIP, preserving `.github/workflows/cloud-boot.yml` and `scripts/`.
2. Open **Actions → S24 FE - Cloud firmware to boot.img.lz4 → Run workflow**.
3. Leave `task=extract_boot` and `firmware_version=S721BXXUEEZIF/S721BODMEEZIG/S721BXXUEEZIF`.
4. If successful, open the run, scroll down to **Artifacts**, download `S24FE-OneUI9-cloud-firmware`, and find `boot.img.lz4`, the extraction report, and boot analysis.
5. If Samsung's FUS backend rejects the 3-part version, run `task=list_versions` and inspect `reports/available-versions.txt`; select the **exact** 3/4-part record whose PDA matches `S721BXXUEEZIF`. Do not substitute the newest build.

## Disk requirements

The full firmware is ~21.1 GB. Standard GitHub-hosted runner specifications say 14 GB disk. This workflow attempts to free space, checks for **25 GiB available**, and refuses to download if the runner still lacks space. This is intentional. If the runner fails the capacity check, use a GitHub larger runner or cloud VM with >=30 GiB free; disk cleanup does not guarantee capacity. The extract script **streams** the AP tar from the ZIP and writes just `boot.img.lz4`, so no extra 20+ GB AP tar is needed.

## Caveats

- The `S721BXXUEEZIF/S721BODMEEZIG/S721BXXUEEZIF` version is assembled from public AP, CSC and CP filenames. The Samsung backend must still accept it; we cannot verify the remote download until Actions executes.
- The updater may no longer serve the older One UI 9 PDA. The workflow will report the backend failure instead of silently downloading a different revision.
- The previous analyzer is experimental; it expects an Android boot v3/v4 image. If analysis fails, the extracted image and preceding artifacts may still be available.
- Large downloads may use significant GitHub Actions minutes, network bandwidth and cloud storage.
- **Never flash** the extracted boot image. A stock image is for offline research, not temporary root.

### Alternative: check availability first

In **Run workflow**, choose `task=list_versions`. This queries Samsung's list without downloading 21 GB. It's a good first run to verify that the exact PDA is still available.
