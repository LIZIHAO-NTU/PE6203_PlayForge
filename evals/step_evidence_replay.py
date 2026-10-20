"""Re-audit the published D development trace without an API or browser call."""
import argparse
import hashlib
import json
from pathlib import Path

from evals.step_evidence import audit_run


DEFAULT = Path(__file__).resolve().parent.parent / "docs/d_step_evidence/flash-evidence.json"
EXPECTED_FILES = {
    "summary.json", "game/index.html", "game/game.js",
    "traces/attempts/01/game/index.html", "traces/attempts/01/game/game.js",
    "traces/attempts/01/evidence/replay.json",
}


def replay(evidence, output):
    evidence, output = Path(evidence).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError("Choose a new output directory")
    data = json.loads(evidence.read_text(encoding="utf-8"))
    files = data.get("files")
    if data.get("kind") != "d_published_development_evidence" or not isinstance(files, dict) or set(files) != EXPECTED_FILES:
        raise ValueError("Unexpected evidence layout")
    payloads = {}
    for name, entry in files.items():
        if not isinstance(entry, dict) or not isinstance(entry.get("text"), str):
            raise ValueError("Invalid evidence entry")
        payload = entry["text"].encode("utf-8")
        if hashlib.sha256(payload).hexdigest() != entry.get("sha256"):
            raise ValueError("Published evidence fingerprint mismatch")
        payloads[name] = payload
    output.mkdir(parents=True)
    run = output / "run"
    for name, payload in payloads.items():
        target = run / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    return audit_run(run, output / "audit")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=DEFAULT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    report = replay(args.evidence, args.output)
    print(json.dumps({
        "audit_model_api_calls": report["audit_model_api_calls"],
        "browser_manifests_audited": report["browser_manifests_audited"],
        "original_run_unchanged": report["original_run_unchanged"],
        "records": [{
            "plan_hash_matches": r["plan_hash_matches"],
            "game_hash_matches": r["game_hash_matches"],
            "supported_pass_tests": r["audit"]["supported_pass_tests"],
            "unsupported_pass_tests": r["audit"]["unsupported_pass_tests"],
            "controlled_probes_detected": sum(c["detected"] for c in r["controlled_probes"]),
        } for r in report["records"]],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
