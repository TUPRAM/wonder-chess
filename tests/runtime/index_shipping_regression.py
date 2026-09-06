"""Bind the required compact100-match index to already executed Shipping evidence."""
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "reports/WC-360/native-taa-regression/regression.json"
AUDIT = ROOT / "reports/WC-360/native-taa-analysis/regression-analysis.json"
PROVENANCE = ROOT / "reports/WC-360/native-taa-provenance.json"
PROCESS = RAW.parent / "process-exit.json"
OUTPUT = ROOT / "reports/WC-360/100-engine-matches.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def bind(path):
    return {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument("--audit", type=Path, default=AUDIT)
    parser.add_argument("--provenance", type=Path, default=PROVENANCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--previous-index", type=Path, default=ROOT / "reports/WC-360/shipping-startup-fixed-analysis/100-engine-matches-index.json")
    args = parser.parse_args()
    raw_path, audit_path, provenance_path = (p.resolve() for p in (args.raw, args.audit, args.provenance))
    process_path = raw_path.parent / "process-exit.json"
    raw, audit, provenance, process = map(load, (raw_path, audit_path, provenance_path, process_path))
    trials = raw["trials"]
    assert raw["complete"] and audit["status"] == "PASS" and len(trials) == raw["requested"] == raw["attempted"] == 100
    assert raw["failed"] == 0 and all(trial["pass"] for trial in trials)
    for source in audit["inputs"]:
        assert hashlib.sha256(Path(source["path"]).read_bytes()).hexdigest() == source["sha256"]
    executable = Path(raw["executable_path"])
    actual_exe_hash = hashlib.sha256(executable.read_bytes()).hexdigest()
    bound_exe = next(item for item in provenance["files"] if Path(item["path"]) == executable)
    assert actual_exe_hash == bound_exe["sha256"]
    recorded_encounters = [encounter for trial in trials for row in trial["rounds"] for encounter in row["encounters"]]
    totals = audit["totals"]
    result = {
        "schema": "wonder_chess_actual_shipping_100_match_index_v2",
        "created_utc": datetime.now(timezone.utc).isoformat(), "status": "PASS",
        "boundary": "Compact index of preserved actual packaged Shipping C++ execution. No fixtures were regenerated to produce these tournaments; this headless run is not render or audio acceptance.",
        "requested": raw["requested"], "attempted": raw["attempted"], "retained_trials": len(trials), "failed": raw["failed"],
        "game_report_complete": raw["complete"], "completed_finished_trials": sum(trial["phase"] == 3 for trial in trials),
        "evidence_write_failed": raw["evidence_write_failed"], "seeds": [trial["seed"] for trial in trials],
        "rounds": sum(len(trial["rounds"]) for trial in trials), "encounters": totals["fights"], "combat_timeouts": totals["timeouts"],
        "ghost_encounters": totals["ghosts"], "capped_tournaments": len(audit["explicit_capped_seeds"]), "capped_seeds": audit["explicit_capped_seeds"],
        "cap_timeout_boundary": "A combat timeout and a tournament cap are supported rule outcomes, not failed or unresolved simulations. Failed and unresolved fields are measured separately.",
        "unresolved_encounters": totals["unresolved_encounters"], "incomplete_recorded_encounters": sum(not encounter["complete"] for encounter in recorded_encounters),
        "bot_commands": totals["commands"], "bot_command_rejects": totals["command_rejects"], "simulated_match_ms_total": totals["simulated_ms"],
        "actual_batch_wall_seconds": raw["batch_wall_seconds"], "start_utc": raw["start_utc"], "end_utc": raw["end_utc"],
        "process_exit_code": process["exit_code"], "process_exit_boundary": audit["exit_boundary"],
        "hardware": {"cpu": raw["cpu"].strip(), "engine": raw["engine"], "compiler": raw["compiler"], "compiler_full_version": raw["compiler_full_version"], "rendering": "NullRHI; audio disabled"},
        "profile": {"id": raw["profile_id"], "schema": raw["schema_version"], "balance": raw["balance_version"], "catalog_digest": raw["digest"], "tick_ms": raw["tick_ms"]},
        "match_duration_ms": audit["match_duration_ms"], "fight_duration_ms": audit["fight_duration_ms"], "hero_use": audit["actual_packaged_hero_use"], "hero_use_boundary": audit["hero_use_boundary"],
        "parity_checks": [row for row in audit["checks"] if any(term in row["check"] for term in ("parity", "standalone", "hero_use"))],
        "executable_binding": {"path": str(executable), "actual_sha256": actual_exe_hash, "immutable_manifest_sha256": bound_exe["sha256"], "matches": True},
        "raw_regression": bind(raw_path), "audit": bind(audit_path), "tested_provenance": bind(provenance_path), "delivery_provenance": bind(provenance_path), "process_observation": bind(process_path),
        "previous_index_preserved": bind(args.previous_index.resolve())}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "path": str(args.output), "bytes": args.output.stat().st_size, "actual_exe_sha256": actual_exe_hash, "matches": result["retained_trials"], "process_exit": result["process_exit_code"]}, indent=2))


if __name__ == "__main__":
    main()
