# S24 FE research verification package

Copy `.github/`, `tools/`, `tests/`, and `porting/REVIEW.md` into the existing `s24fe-temp-root` repository. Do not overwrite your existing reports or `porting/STATUS.md`.

Run locally in Codespaces:

```bash
python -m unittest discover -s tests -v
python tools/verify_reports.py --reports reports --json artifacts/compatibility-summary.json --markdown artifacts/compatibility-summary.md
```

Push to trigger `S24 FE research consistency` in GitHub Actions.

This validation checks documented firmware identity, metadata/hash consistency, and reported offline checks. It **does not compile or execute a root payload**, verify CVE exploitability, or claim temporary root is achieved.
