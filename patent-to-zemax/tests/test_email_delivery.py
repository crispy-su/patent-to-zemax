import importlib.util
import json
import tempfile
import unittest
from email import policy
from email.parser import BytesParser
from pathlib import Path
from types import SimpleNamespace


SCRIPT = Path(__file__).parents[1] / "scripts" / "prepare_email_delivery.py"
SPEC = importlib.util.spec_from_file_location("prepare_email_delivery", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class EmailDeliveryTests(unittest.TestCase):
    def test_package_contains_exact_artifacts_and_never_marks_sent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            patent, report, zmx = root / "p.pdf", root / "r.md", root / "m.zmx"
            patent.write_bytes(b"%PDF-test")
            report.write_text("report", encoding="utf-8")
            zmx.write_text("VERS 230000", encoding="utf-8")
            args = SimpleNamespace(
                patent=str(patent), report=str(report), zmx=str(zmx),
                recipient=["user@example.com"], subject=None, body=None,
                package_name="test", output_dir=str(root / "mail"),
            )
            result = MODULE.build_package(args)
            self.assertEqual(result["delivery_state"], "prepared_not_sent")
            self.assertTrue(result["send_requires_explicit_confirmation"])
            self.assertEqual({x["role"] for x in result["attachments"]},
                             {"original_patent", "final_report", "final_zmx"})
            for item in result["attachments"]:
                self.assertEqual(len(item["sha256"]), 64)

            manifest = json.loads(Path(result["prepared_files"]["manifest"]).read_text(encoding="utf-8"))
            self.assertEqual(manifest["recipients"], ["user@example.com"])
            message = BytesParser(policy=policy.default).parsebytes(
                Path(result["prepared_files"]["eml_draft"]).read_bytes()
            )
            names = {part.get_filename() for part in message.iter_attachments()}
            self.assertEqual(names, {"p.pdf", "r.md", "m.zmx", "test-email-manifest.json"})

    def test_rejects_invalid_recipient(self):
        args = SimpleNamespace(recipient=["not-an-email"])
        with self.assertRaisesRegex(ValueError, "Invalid recipient"):
            MODULE.build_package(args)


if __name__ == "__main__":
    unittest.main()
