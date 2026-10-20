"""D experiment: audit step evidence without changing the Agent's verdict or game.

live: one bounded real-model run, then a read-only audit of raw browser manifests.
audit: audit an existing run; no model calls. Controlled mutations affect copies only.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

from agent.config import Config, load_dotenv
from agent.contracts import compare, lookup, test_steps, validate_plan
from agent.evidence import file_hashes, runtime_metadata
from agent.quality import completion_gate


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SPEC = ROOT / "examples/d_evidence/pulse_counter.md"
OBSERVATIONS = {"assert", "assert_consistent", "assert_stable", "wait_until", "key_until", "move_to"}
INPUTS = {"click", "key", "keys", "drag", "fill", "select_option"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def equal(a, b):
    try:
        return json.dumps(a, sort_keys=True, allow_nan=False) == json.dumps(b, sort_keys=True, allow_nan=False)
    except (ValueError, TypeError):
        return False


def audit_test(test, result):
    """A supported pass needs every planned step and observation; never infer gameplay truth."""
    if result.get("passed") is not True:
        return {"id": test["id"], "verdict": "recorded_nonpass", "issues": []}
    issues = []
    steps = test_steps(test)
    actions, observations = result.get("actions"), result.get("observations")
    if not isinstance(actions, list):
        actions = []
        issues.append("missing_actions")
    if not isinstance(observations, list):
        observations = []
        issues.append("missing_observations")
    indices = [a.get("step") for a in actions if isinstance(a, dict)]
    if (len(actions) != len(steps) or any(type(i) is not int for i in indices) or
            indices != list(range(1, len(steps) + 1))):
        issues.append("action_sequence_incomplete_or_duplicated")
    expected_obs = [i for i, step in enumerate(steps, 1) if step["action"] in OBSERVATIONS]
    observed_indices = [o.get("step") for o in observations if isinstance(o, dict)]
    if (len(observations) != len(expected_obs) or any(type(i) is not int for i in observed_indices) or
            observed_indices != expected_obs):
        issues.append("observation_sequence_incomplete_or_duplicated")
    captures = {}
    for i, step in enumerate(steps, 1):
        matches = [a for a in actions if isinstance(a, dict) and type(a.get("step")) is int and a["step"] == i]
        if len(matches) != 1:
            continue
        action = matches[0]
        if action.get("action") != step["action"] or not equal(action.get("arguments"), step):
            issues.append(f"step_{i}:action_does_not_match_plan")
        if action.get("stage") != ("setup" if i <= len(test.get("setup_steps", [])) else "check"):
            issues.append(f"step_{i}:wrong_stage")
        if action.get("ok") is not True or action.get("error"):
            issues.append(f"step_{i}:action_not_successful")
        elapsed = action.get("elapsed_ms")
        if type(elapsed) not in {int, float} or not math.isfinite(elapsed) or elapsed < 0:
            issues.append(f"step_{i}:missing_or_invalid_duration")
        if step["action"] == "capture":
            if isinstance(action.get("result"), dict):
                captures[step["name"]] = action["result"]
            else:
                issues.append(f"step_{i}:missing_capture")
        if step["action"] == "sample":
            samples = action.get("result", {}).get("samples", []) if isinstance(action.get("result"), dict) else []
            if not isinstance(samples, list) or len(samples) != step.get("samples", 3) or any(not isinstance(s, dict) or "state" not in s for s in samples):
                issues.append(f"step_{i}:missing_samples")
            elif samples:
                captures[step["name"] + "_start"] = samples[0]["state"]
                captures[step["name"] + "_end"] = samples[-1]["state"]
        if step["action"] not in OBSERVATIONS:
            continue
        seen = [o for o in observations if isinstance(o, dict) and type(o.get("step")) is int and o["step"] == i]
        if len(seen) != 1:
            continue
        observation = seen[0]
        try:
            if observation.get("passed") is not True:
                raise ValueError("observation did not pass")
            if step["action"] == "assert_stable":
                samples = observation.get("samples", [])
                if len(samples) != step.get("samples", 3):
                    raise ValueError("missing stability samples")
                first = samples[0]["actual"]
                if not all(compare(s["actual"], "eq", first) for s in samples):
                    raise ValueError("inconsistent stability samples")
                if not equal(observation["expected"], first) or not equal(observation["actual"], samples[-1]["actual"]):
                    raise ValueError("stability summary mismatch")
                op, expected = "eq", first
            elif step["action"] == "assert_consistent":
                if observation.get("state_path") != step["state_path"]:
                    raise ValueError("wrong state path")
                op, expected = "eq", observation["expected"]
            else:
                condition = step.get("until", step)
                op = condition["op"]
                ref = condition.get("value_from")
                expected = lookup(captures[ref["capture"]], ref["path"]) if ref else condition["value"]
            if observation["op"] != op or not equal(observation["expected"], expected):
                raise ValueError("comparison differs from frozen plan")
            if not compare(observation["actual"], op, expected):
                raise ValueError("actual value does not support pass")
        except (KeyError, IndexError, TypeError, ValueError):
            issues.append(f"step_{i}:missing_or_contradictory_observation")
    return {"id": test["id"], "verdict": "unsupported_pass" if issues else "supported_pass",
            "planned_steps": len(steps), "recorded_steps": len(actions),
            "planned_observations": len(expected_obs), "recorded_observations": len(observations),
            "issues": issues}


def audit_result(plan, result):
    plan = validate_plan(plan)
    tests = result.get("tests", [])
    malformed = not isinstance(tests, list) or any(not isinstance(t, dict) for t in tests)
    tests = [t for t in tests if isinstance(t, dict)] if isinstance(tests, list) else []
    gate_result = {**result, "tests": tests}
    records = []
    for test in plan["tests"]:
        matches = [t for t in tests if isinstance(t, dict) and t.get("id") == test["id"]]
        if len(matches) != 1:
            records.append({"id": test["id"], "verdict": "missing_or_duplicate_test", "issues": ["test_record_count"]})
        else:
            records.append(audit_test(test, matches[0]))
    known = {t["id"] for t in plan["tests"]}
    unknown = [t.get("id") for t in tests if isinstance(t, dict) and t.get("id") not in known]
    gate = completion_gate(plan, gate_result, "valid")
    supported = gate["passed"] and not malformed and not unknown and all(r["verdict"] == "supported_pass" for r in records)
    return {"original_reported_ok": result.get("ok"), "baseline_gate_passed": gate["passed"],
            "step_supported_overall_pass": bool(supported),
            "planned_tests": len(plan["tests"]),
            "claimed_pass_tests": sum(t.get("passed") is True for t in tests if isinstance(t, dict)),
            "supported_pass_tests": sum(r["verdict"] == "supported_pass" for r in records),
            "unsupported_pass_tests": sum(r["verdict"] == "unsupported_pass" for r in records),
            "malformed_test_records": malformed,
            "unknown_test_ids": unknown, "tests": records,
            "note": "Record consistency only; complete logs do not prove actual browser events, correct expectations or full gameplay."}


def mutation_matrix(plan, result):
    """Controlled record-corruption probes, never edit games or original verification files."""
    passing = [r for r in audit_result(plan, result)["tests"] if r["verdict"] == "supported_pass"]
    target = next((t for t in plan["tests"] if any(p["id"] == t["id"] for p in passing) and
                   any(s["action"] in INPUTS for s in test_steps(t)) and
                   any(s["action"] in OBSERVATIONS for s in test_steps(t))), None)
    if target is None:
        return {"status": "not_run_no_suitable_supported_pass", "cases": []}
    variants = []
    for kind in ("delete_input", "delete_observation", "failed_input_marked_pass", "duplicate_action", "changed_arguments"):
        variant = deepcopy(result)
        item = next(t for t in variant["tests"] if t["id"] == target["id"])
        action = next(a for a in item["actions"] if a["action"] in INPUTS)
        if kind == "delete_input":
            item["actions"].remove(action)
        elif kind == "delete_observation":
            item["observations"].pop()
        elif kind == "failed_input_marked_pass":
            action["ok"] = False
            action["error"] = "CONTROLLED_EVIDENCE_PROBE: action failure"
        elif kind == "duplicate_action":
            item["actions"].append(deepcopy(action))
        else:
            action["arguments"]["probe_changed_argument"] = True
        audit = audit_result(plan, variant)
        record = next(t for t in audit["tests"] if t["id"] == target["id"])
        variants.append({"name": kind, "controlled_record_copy": True,
                         "target_test": target["id"], "baseline_gate_passed": audit["baseline_gate_passed"],
                         "detected": record["verdict"] == "unsupported_pass", "audit": audit,
                         "altered_record": variant})
    return {"status": "completed", "cases": variants,
            "note": "Corruptions are synthetic even when their parent trace came from a real model/browser."}


def audit_run(run_dir, output):
    run_dir, output = Path(run_dir).resolve(), Path(output).resolve()
    if output.exists() or output == run_dir or run_dir in output.parents:
        raise ValueError("Audit output must be a NEW directory outside the original run")
    if not (run_dir / "summary.json").is_file():
        raise ValueError("Missing original run summary")
    originals = file_hashes(run_dir)
    summary = json.loads((run_dir / "summary.json").read_text())
    output.mkdir(parents=True)
    records = []
    for path in sorted((run_dir / "traces/attempts").glob("*/**/replay.json")):
        raw = json.loads(path.read_text())
        plan, result = raw["plan"], raw["result"]
        case_name = path.parent.parent.name + "_" + path.parent.name
        audit = audit_result(plan, result)
        plan_hash_ok = digest(json.dumps(plan, sort_keys=True).encode()) == raw.get("plan_content_sha256")
        game = path.parent.parent / "game"
        game_hash_ok = game.is_dir() and file_hashes(game) == raw.get("game_sha256")
        save(output / case_name / "audit.json", audit)
        matrix = mutation_matrix(plan, result)
        save(output / case_name / "controlled_mutations.json", matrix)
        records.append({"manifest": path.relative_to(run_dir).as_posix(),
                        "manifest_sha256": digest(path.read_bytes()), "plan_hash_matches": plan_hash_ok,
                        "game_hash_matches": game_hash_ok, "audit": audit,
                        "mutation_status": matrix["status"],
                        "controlled_probes": [{k: v for k, v in c.items() if k not in {"altered_record", "audit"}}
                                              for c in matrix["cases"]]})
    integrity = originals == file_hashes(run_dir)
    report = {"kind": "d_step_evidence_audit", "original_run_status": summary.get("status"),
              "original_automated_checks_passed": summary.get("automated_checks_passed"),
              "original_usage": summary.get("usage"), "audit_model_api_calls": 0,
              "original_run_unchanged": integrity, "original_source_files": originals,
              "browser_manifests_audited": len(records), "records": records,
              "coverage_status": "audited_recorded_browser_manifests" if records else "not_verified_no_browser_manifests",
              "limitations": ["No replay manifest means no step audit, not a passing audit.",
                  "Failure records remain failures; later unexecuted steps are not invented.",
                  "The observer audits logs; it cannot authenticate a malicious verifier or prove physical clicks.",
                  "This does not validate game-rule expectations or complete gameplay.",
                  "Controlled evidence mutations do not count as real model failures or game samples."]}
    save(output / "AUDIT.json", report)
    lines = ["# D 逐步执行证据审计", "", f"- 原 Agent 状态：{summary.get('status')}",
             f"- 浏览器原始清单数：{len(records)}", f"- 原运行文件未改动：{integrity}",
             "- 审计及证据副本实验的模型调用：0（原生成运行的用量另列于 AUDIT.json）", "",
             "| 原清单 | 原始通过标记 | 旧门禁通过 | 步骤证据支持整体通过 | 缺证据的通过项 | 计划/源码指纹 |",
             "|---|---|---|---|---|---|"]
    for r in records:
        a = r["audit"]
        lines.append(f"| {r['manifest']} | {a['original_reported_ok']} | {a['baseline_gate_passed']} | "
                     f"{a['step_supported_overall_pass']} | {a['unsupported_pass_tests']} | "
                     f"{r['plan_hash_matches']}/{r['game_hash_matches']} |")
    lines += ["", "证据副本实验不是实际模型犯错；完整记录也不证明游戏规则正确。",
              "若没有合适的原始通过项，副本实验明确为未执行，不修改标准以凑结果。"]
    (output / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def live(output, spec=DEFAULT_SPEC, max_calls=5, max_rounds=3, max_seconds=360):
    """A real Agent run; no replacement model, no manual repair, no production gate change."""
    from agent.runner import run
    load_dotenv(ROOT / ".env")
    config = Config.from_env()
    if not config.api_key or config.api_key == "FILL_KEY_LOCALLY":
        raise ValueError("Fill LLM_API_KEY locally in .env before live execution")
    if config.base_url != "https://openrouter.ai/api/v1":
        raise ValueError("This prepared experiment is configured only for the approved OpenRouter endpoint")
    if not (1 <= max_calls <= 5 and 1 <= max_rounds <= 3 and 30 <= max_seconds <= 360):
        raise ValueError("Pilot cap: <=5 attempts, <=3 rounds, <=360 seconds")
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("Output exists; choose a new experiment directory")
    if not spec.is_file():
        raise ValueError("Missing development specification")
    output.mkdir(parents=True)
    manifest = {"kind": "real_model_pilot", "started_utc": datetime.now(timezone.utc).isoformat(),
                "baseline_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "working_files": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).splitlines(),
                "runtime": runtime_metadata(), "experiment_source_sha256": digest(Path(__file__).read_bytes()),
                "spec_sha256": digest(spec.read_bytes()), "model": config.model, "base_url": config.base_url,
                "limits": {"max_calls": max_calls, "max_rounds": max_rounds, "max_seconds": max_seconds},
                "features": {"strict_plan": True, "verify_repeats": 1, "lessons": False,
                             "plan_audit": False, "diagnose": False},
                "note": "No credential values or HTTP headers are recorded in this manifest."}
    save(output / "EXPERIMENT.json", manifest)
    code = None
    try:
        code = run(config, spec.resolve(), output / "run", max_calls=max_calls,
                   max_rounds=max_rounds, max_seconds=max_seconds, strict_plan=True)
        manifest["agent_exit_code"] = code
    finally:
        if (output / "run/summary.json").is_file():
            audit_run(output / "run", output / "audit")
        manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
        save(output / "EXPERIMENT.json", manifest)
    return code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("live", help="Real API pilot; consumes credits")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    p.add_argument("--max-calls", type=int, default=5)
    p.add_argument("--max-rounds", type=int, default=3)
    p.add_argument("--max-seconds", type=int, default=360)
    p = sub.add_parser("audit", help="Existing run only; zero API calls")
    p.add_argument("run", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "live":
            return live(args.output, args.spec, args.max_calls, args.max_rounds, args.max_seconds)
        audit_run(args.run, args.output)
        return 0
    except (ValueError, RuntimeError, OSError):
        # Do not expose exception bodies that could echo third-party content or secrets.
        print("Experiment stopped. Check local configuration/browser and preserved reports; no automatic rerun.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
