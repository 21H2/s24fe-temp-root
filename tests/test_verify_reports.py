import json
import tempfile
import unittest
from pathlib import Path
from tools.verify_reports import assess, EXPECTED


class ResearchChecksTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        device = dict(EXPECTED, fingerprint="samsung/r12sxins/r12s:17/CP2A.260605.016/S721BXXUEEZIF:user/release-keys", temporary_root_verified=False)
        boot = dict(expected_firmware_from_user=EXPECTED["firmware"], expected_kernel_version_from_user=EXPECTED["kernel"], downloaded_file_sha256="a"*64, btf_candidate_count=1)
        extracted = dict(model=EXPECTED["model"], pda=EXPECTED["firmware"], extracted=dict(sha256="a"*64))
        for n, data in (("device-verified.json", device), ("boot-analysis.json", boot), ("extraction.json", extracted)):
            (self.folder/n).write_text(json.dumps(data))

    def tearDown(self):
        self.temp.cleanup()

    def test_consistent_reports_pass_but_never_claim_root(self):
        res = assess(self.folder)
        self.assertEqual(res["result"], "pass")
        self.assertIs(res["temporary_root_verified"], False)

    def test_wrong_firmware_fails(self):
        p = self.folder/"device-verified.json"
        data = json.loads(p.read_text())
        data["firmware"] = "S721BXXSCDZF3"
        p.write_text(json.dumps(data))
        self.assertEqual(assess(self.folder)["result"], "fail")

    def test_mismatched_boot_hash_fails(self):
        p = self.folder/"extraction.json"
        data = json.loads(p.read_text())
        data["extracted"]["sha256"] = "b"*64
        p.write_text(json.dumps(data))
        self.assertEqual(assess(self.folder)["result"], "fail")

    def test_missing_report_fails(self):
        (self.folder/"boot-analysis.json").unlink()
        self.assertEqual(assess(self.folder)["result"], "fail")


if __name__ == "__main__":
    unittest.main()
