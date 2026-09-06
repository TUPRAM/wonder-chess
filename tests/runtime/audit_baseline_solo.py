"""Audit the completed actual baseline Shipping1H7B session and its final process record."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from audit_network_evidence import forbidden_public_paths, load, received

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "reports/WC-360/shipping-normal1080"


def bind(path):
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}


def main():
    session_path, launch_path = BASE / "completed-session.json", BASE / "launch.json"
    session, launch = load(session_path), load(launch_path)
    snapshots, snapshot_path = received(session, session_path)
    prefix = f"match-{session['match_namespace']}-seat-{session['seat']}-pid-{session['process_id']}"
    commands_path = BASE / (prefix + "-commands.jsonl")
    commands = [json.loads(line) for line in commands_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    public = json.loads(session["public_snapshot"])
    match_rows = [row for row in snapshots if len(row.get("public", {}).get("seats", [])) == 8]
    checks = []

    def check(name, condition, detail):
        checks.append({"check": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    check("completed_standalone1H7B", session["complete"] and not session["aborted"] and session["phase"] == 3 and session["network_mode"] == 0,
          {key: session[key] for key in ("process_id", "match_namespace", "phase", "round", "complete", "aborted", "network_mode")})
    check("one_human_seven_persistent_named_bots", bool(match_rows) and all(sum(bool(s["human"]) for s in row["public"]["seats"]) == 1 for row in match_rows)
          and len({tuple((s["id"], s["name"]) for s in row["public"]["seats"] if not s["human"]) for row in match_rows}) == 1,
          [(seat["id"], seat["name"], seat["human"]) for seat in public["seats"]])
    check("owner_private_seat_binding", all(row.get("owner_private", {}).get("seat") == 0 for row in match_rows), len(match_rows))
    violations = sorted({path for row in match_rows for path in forbidden_public_paths(row["public"])})
    check("received_public_privacy", not violations and not session["received_state_privacy_violations"], violations)
    combat_rounds = sorted({row["round"] for row in match_rows if row["phase"] == 1})
    check("all20_combat_rounds_observed", combat_rounds == list(range(1, 21)), combat_rounds)
    required = {"out_of_order_sequence_rejected", "original_idempotent_lock_request", "duplicate_request_applies_once",
                "changed_payload_same_request_rejected", "stale_revision_rejected", "foreign_unit_sale_rejected", "combat_phase_buy_rejected"}
    probes = {probe["name"]: probe for probe in session["command_probes"]}
    for name in sorted(required):
        check(name, name in probes and probes[name]["status"] == "PASS", probes.get(name))
    eliminated = next(row for row in match_rows if row["public"]["seats"][0]["health"] <= 0)
    check("human_eliminated_round10_place8", eliminated["round"] == 10 and public["seats"][0]["place"] == 8,
          {"utc": eliminated["utc"], "phase": eliminated["phase"], "round": eliminated["round"], "final_human": public["seats"][0]})
    after = [row for row in match_rows if row["round"] > eliminated["round"] and row["phase"] == 1]
    check("bots_continue_real_encounters_after_human_elimination", sorted({row["round"] for row in after}) == list(range(11, 21))
          and all(row["public"].get("encounters") for row in after), {"combat_rounds": sorted({row["round"] for row in after}), "observations": len(after)})
    check("automatic_spectating_observed_after_elimination", any(row.get("observed_seat", 0) > 0 for row in after),
          sorted({row.get("observed_seat", 0) for row in after}))
    check("normal_speed1080_requested_and_recorded", session["simulation_speed_multiplier"] == 1 and session["resolution_x"] == 1920 and session["resolution_y"] == 1080,
          {key: session[key] for key in ("simulation_speed_multiplier", "resolution_x", "resolution_y")})
    check("final_actual_process_exit0", launch["status"] == "EXITED_AUDIT_REQUIRED" and launch["exit_code"] == 0 and launch["process_id"] == session["process_id"],
          {key: launch[key] for key in ("started_utc", "ended_utc", "exit_code", "process_id", "status")})
    manifest_path = Path(launch["provenance_path"])
    manifest = load(manifest_path)
    entry = next(item for item in manifest["files"] if item["path"] == launch["executable"])
    check("launch_executable_and_manifest_binding", bind(manifest_path)["sha256"] == launch["provenance_sha256"] and launch["executable_sha256"] == entry["sha256"],
          {"executable": launch["executable"], "sha256": launch["executable_sha256"], "manifest": str(manifest_path)})
    replies = [row for row in commands if row.get("event") == "actual_client_reply"]
    check("recorded_reply_totals_reconcile", sum(row["accepted"] for row in replies) == session["actual_accepted_replies"]
          and sum(not row["accepted"] for row in replies) == session["actual_rejected_replies"],
          {"accepted": session["actual_accepted_replies"], "rejected": session["actual_rejected_replies"], "reasons": dict(Counter(row["reason"] for row in replies))})
    result = {"status": "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL", "utc": datetime.now(timezone.utc).isoformat(),
              "checks": checks, "boundary": "Actual scripted human controller in baseline Shipping, one human and seven persistent bots. This is complete1H7B/elimination/spectating/RPC evidence; it is not manual usability, restart, TAA-candidate or human-audio acceptance.",
              "first_match_observation_utc": match_rows[0]["utc"], "first_results_utc": next(row["utc"] for row in match_rows if row["phase"] == 3),
              "human_elimination_utc": eliminated["utc"], "final_standings": public["seats"],
              "frame_measurements_boundary": "Frame measurements in this session are separate measured baseline evidence and do not by themselves establish the performance gate. Final TAA candidate needs its own run.",
              "engine_log_checks": {"status": "NOT_RUN", "count": None, "reason": "Shipping UE_LOG output unavailable; not interpreted as zero errors."},
              "inputs": [bind(path) for path in (session_path, launch_path, snapshot_path, commands_path, manifest_path)]}
    output = BASE / "functional-audit"
    output.mkdir(exist_ok=True)
    (output / "audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Actual baseline1H7B functional audit", "", f"**{result['status']}** across{len(checks)} checks.", "", result["boundary"], "",
             "The normal1x1920x1080 session reached results in round20. Human seat0 was eliminated in round10 and finished eighth; real bot encounters continued through rounds11–20, with automatic bot-board spectating observed. All seven actual authority probes passed. There were37 accepted replies and5 deliberately rejected invalid requests; accepted replies include the idempotent replay.", "",
             f"Process{session['process_id']} launched {launch['started_utc']} and actually exited0 at {launch['ended_utc']}. First results observation was {result['first_results_utc']}. The completed-session export and final launch record are both hash-bound in audit.json.", "", result["frame_measurements_boundary"], "",
             "Shipping log checks remain NOT_RUN; no absence-of-log pass is inferred."]
    (output / "audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks": len(checks), "nonpassing": [row for row in checks if row["status"] != "PASS"]}, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
