"""Published-evidence integrity and offline reproducibility; no API or browser."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from evals.step_evidence_replay import DEFAULT, replay


class PublishedEvidenceTests(unittest.TestCase):
    def test_original_published_trace_reproduces_without_api(self):
        with TemporaryDirectory() as temporary, patch("agent.provider.ChatClient.ask_json", side_effect=AssertionError("No API")):
            report = replay(DEFAULT, Path(temporary) / "replay")
        self.assertTrue(report["original_run_unchanged"])
        self.assertEqual(report["audit_model_api_calls"], 0)
        self.assertEqual(report["browser_manifests_audited"], 1)
        record = report["records"][0]
        self.assertTrue(record["plan_hash_matches"])
        self.assertTrue(record["game_hash_matches"])
        self.assertEqual(record["audit"]["supported_pass_tests"], 6)
        self.assertEqual(record["audit"]["unsupported_pass_tests"], 0)
        self.assertEqual(len(record["controlled_probes"]), 5)
        self.assertTrue(all(c["detected"] and c["baseline_gate_passed"] for c in record["controlled_probes"]))

    def test_changed_artifact_is_rejected_before_writing(self):
        data = json.loads(DEFAULT.read_text())
        data["files"]["game/game.js"]["text"] += "\n// changed"
        with TemporaryDirectory() as temporary:
            source, output = Path(temporary) / "evidence.json", Path(temporary) / "output"
            source.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                replay(source, output)
            self.assertFalse(output.exists())

    def test_unexpected_path_and_existing_output_are_rejected(self):
        data = json.loads(DEFAULT.read_text())
        data["files"]["../outside.json"] = {"text": "{}", "sha256": "invalid"}
        with TemporaryDirectory() as temporary:
            source, output = Path(temporary) / "evidence.json", Path(temporary) / "output"
            source.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                replay(source, output)
            self.assertFalse(output.exists())
            with self.assertRaises(ValueError):
                replay(DEFAULT, Path(temporary))


if __name__ == "__main__":
    unittest.main()
