"""Re-evaluate preserved D controlled browser records with current C routing; no API."""
import argparse
import hashlib
import json
from pathlib import Path
from agent.diagnostics import route_failure

DEFAULT=Path(__file__).resolve().parents[1]/"docs/d_reviews/c_guard_evidence.json"
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence",type=Path,default=DEFAULT)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError("Choose a new output file")
    data=json.loads(args.evidence.read_text(encoding="utf-8"));rows=[]
    for case in data["cases"]:
        values={}
        for name in ["frozen_plan.json","browser_verification.json"]:
            entry=case["files"][name];raw=entry["text"].encode("utf-8")
            if hashlib.sha256(raw).hexdigest()!=entry["sha256"]:raise ValueError("Evidence hash mismatch")
            values[name]=json.loads(raw)
        before=json.dumps(values,sort_keys=True)
        route=route_failure(values["browser_verification.json"],plan=values["frozen_plan.json"])
        if before!=json.dumps(values,sort_keys=True):raise ValueError("Original records changed")
        rows.append({"case":case["case"],"route":route,"expected_action":"stop_test_review",
                     "matches":route["action"]=="stop_test_review"})
    report={"model_api_calls":0,"new_browser_runs":0,"cases":rows,
            "scope":"Preserved controlled trace reclassification, not formal game acceptance"}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    return 0 if all(r["matches"] for r in rows) else 1
if __name__=="__main__":raise SystemExit(main())
