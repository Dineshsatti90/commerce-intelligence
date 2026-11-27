"""Evaluate the data-contract scope gate without any model or network access.

Two measurements:

* **Gate only** on every question set, including the held-out v3 set:
  unsupported-question refusal and supported-question false refusal.
* **Replay** of the recorded raw-model runs (``policy_mode == model_only``): a
  question the gate refuses becomes a refusal; every other question keeps the
  model's recorded output unchanged. No model output is re-generated or edited.

Usage::

    python evaluate_gate.py
    python evaluate_gate.py --cases my_blind_questions.json   # gate-only, any set
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scope_gate import scope_decision

ROOT = Path(__file__).resolve().parent

SETS = {
    "regression": ("eval/questions.json", "tuning (seen)"),
    "v1_reused": ("eval/fresh_questions.json", "tuning (seen)"),
    "v2_first_pass": ("eval/fresh_questions_v2.json", "tuning (seen)"),
    "holdout_v3": ("eval/holdout_questions_v3.json", "held out; same author as gate"),
}
RUNS = {
    ("qwen2.5:3b", "regression"): "eval/runs/qwen3b_references_regression.json",
    ("qwen2.5:3b", "v1_reused"): "eval/runs/qwen3b_references_v1_reused.json",
    ("qwen2.5:3b", "v2_first_pass"): "eval/runs/qwen3b_references_v2_first_pass.json",
    ("llama3:8b", "regression"): "eval/runs/llama8b_references_regression.json",
    ("llama3:8b", "v1_reused"): "eval/runs/llama8b_references_v1_reused.json",
    ("llama3:8b", "v2_first_pass"): "eval/runs/llama8b_references_v2_first_pass.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gate_only(cases: list[dict]) -> dict:
    rows = []
    for case in cases:
        allowed, reason = scope_decision(case["question"])
        unsupported = case["expected"] == "unsupported"
        rows.append(
            {
                "id": case["id"],
                "expected": case["expected"],
                "allowed": allowed,
                "reason": reason,
                "correct": allowed != unsupported,
            }
        )
    unsupported = [r for r in rows if r["expected"] == "unsupported"]
    supported = [r for r in rows if r["expected"] != "unsupported"]
    return {
        "cases": len(rows),
        "unsupported_refusal_rate": sum(not r["allowed"] for r in unsupported) / max(1, len(unsupported)),
        "supported_false_refusal_rate": sum(not r["allowed"] for r in supported) / max(1, len(supported)),
        "misses": [r for r in rows if not r["correct"]],
        "decisions": {str(r["id"]): r["reason"] for r in rows},
    }


def replay(run_path: Path, questions_path: Path) -> dict:
    run = json.loads(run_path.read_text(encoding="utf-8"))
    if run.get("policy_mode") != "model_only":
        raise ValueError(f"{run_path} is not a raw model-only run")
    if run.get("questions_sha256") != sha(questions_path):
        raise ValueError(f"{run_path} was recorded on different questions")
    raw_pass = gated_pass = raw_refused = gated_refused = n_unsupported = 0
    raw_wrong_display = gated_wrong_display = 0
    for row in run["results"]:
        allowed, _ = scope_decision(row["question"])
        unsupported = row["expected"] == "unsupported"
        raw_ok = bool(row.get("routing_correct") and row.get("evidence_valid"))
        displayed = (not row.get("routing_correct")) and row.get("answer", {}).get("status") == "answered"
        raw_pass += raw_ok
        raw_wrong_display += displayed
        if unsupported:
            n_unsupported += 1
            raw_refused += row.get("actual") == "unsupported"
        if allowed:
            gated_pass += raw_ok
            gated_wrong_display += displayed
            gated_refused += unsupported and row.get("actual") == "unsupported"
        else:
            gated_pass += unsupported
            gated_refused += unsupported
    n = len(run["results"])
    return {
        "run_file": str(run_path.relative_to(ROOT)).replace("\\", "/"),
        "cases": n,
        "raw_pass_rate": raw_pass / n,
        "gated_pass_rate": gated_pass / n,
        "raw_unsupported_refusal_rate": raw_refused / max(1, n_unsupported),
        "gated_unsupported_refusal_rate": gated_refused / max(1, n_unsupported),
        "raw_wrong_route_displayable": raw_wrong_display,
        "gated_wrong_route_displayable": gated_wrong_display,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, help="Score the gate alone on any question file")
    args = parser.parse_args()
    if args.cases:
        result = gate_only(json.loads(args.cases.read_text(encoding="utf-8")))
        print(json.dumps({k: v for k, v in result.items() if k != "decisions"}, indent=2))
        return
    report = {
        "gate_source_sha256": sha(ROOT / "scope_gate.py"),
        "method": "Deterministic data-contract allowlist + documented-limitation refusals; no model or network.",
        "caveat": (
            "The gate was tuned on the regression, v1 and v2 sets. The v3 set was written and fingerprinted "
            "before the gate code, but by the same author, who knew those questions while writing rules. "
            "Treat v3 as an upper bound, not an independent generalization estimate. Score blind questions "
            "written by someone else with --cases."
        ),
        "gate_only": {},
        "replay_of_recorded_raw_runs": [],
    }
    for split, (path, role) in SETS.items():
        result = gate_only(json.loads((ROOT / path).read_text(encoding="utf-8")))
        report["gate_only"][split] = {"role": role, "questions_sha256": sha(ROOT / path), **result}
    for (model, split), run_path in RUNS.items():
        report["replay_of_recorded_raw_runs"].append(
            {"model": model, "split": split, **replay(ROOT / run_path, ROOT / SETS[split][0])}
        )
    out = ROOT / "reports/scope_gate_evaluation.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for split, r in report["gate_only"].items():
        print(
            f"{split:14} refusal {r['unsupported_refusal_rate']:.0%}  "
            f"false refusal {r['supported_false_refusal_rate']:.0%}  ({r['role']})"
        )
    for r in report["replay_of_recorded_raw_runs"]:
        print(
            f"{r['model']:11} {r['split']:14} pass {r['raw_pass_rate']:.0%} -> {r['gated_pass_rate']:.0%}  "
            f"refusal {r['raw_unsupported_refusal_rate']:.0%} -> {r['gated_unsupported_refusal_rate']:.0%}  "
            f"wrong displayed {r['raw_wrong_route_displayable']} -> {r['gated_wrong_route_displayable']}"
        )


if __name__ == "__main__":
    main()
