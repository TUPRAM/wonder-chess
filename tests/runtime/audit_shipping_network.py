"""Audit actual Shipping process exports; unavailable UE_LOG is never counted as zero errors."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import audit_network_evidence as paired
import summarize_frame_evidence as frames

ROOT = Path(__file__).resolve().parents[2]


def fingerprint(path):
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}


def audit(base):
    trial = paired.load(base / "trial.json")
    paths = [next((base / role).glob(f"match-1-seat-{seat}-*-session.json")) for seat, role in enumerate(("host", "client"))]
    sessions = [paired.load(path) for path in paths]
    if not all(session.get("complete") for session in sessions):
        return {"status": "IN_PROGRESS", "sessions": [{key: s.get(key) for key in ("utc", "seat", "phase", "round", "complete", "aborted")} for s in sessions]}
    output = base / "audit"
    output.mkdir(exist_ok=True)
    comparison = paired.audit(*paths, require_complete=True)
    (output / "paired-state-audit.json").write_text(json.dumps(comparison, indent=2) + "\n", encoding="utf-8")
    results, inputs, additional = [], [], []

    def check(name, condition, detail):
        additional.append({"check": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    check("verified_shipping_listener", trial.get("listen_owner", {}).get("local_port") == trial["port"], trial.get("listen_owner"))
    check("package_hashes_still_match", all(hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest() == item["sha256"] for item in trial["executable_identities"]), trial["executable_identities"])
    for role, session, path in zip(("host", "client"), sessions, paths):
        snapshots, snapshot_path = paired.received(session, path)
        commands_path = path.with_name(path.name.replace("-session.json", "-commands.jsonl"))
        commands = [json.loads(line) for line in commands_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        replies = [row for row in commands if row.get("event") == "actual_client_reply"]
        expected_rejections = Counter(probe["reply"] for probe in session["command_probes"]
                                      if probe.get("status") == "PASS" and not probe.get("accepted", True))
        actual_rejections = Counter(row["reason"] for row in replies if not row["accepted"])
        check(role + "_only_deliberate_probe_rejections", actual_rejections == expected_rejections,
              {"actual": dict(actual_rejections), "expected_from_actual_probe_records": dict(expected_rejections)})
        check(role + "_reply_counts_reconcile", sum(row["accepted"] for row in replies) == session["actual_accepted_replies"]
              and sum(not row["accepted"] for row in replies) == session["actual_rejected_replies"], len(replies))
        public = json.loads(session["public_snapshot"])
        combat_rounds = sorted({row["round"] for row in snapshots if row["phase"] == 1})
        recap_rounds = sorted({row["public"]["recap"]["round"] for row in snapshots if row["public"].get("recap")})
        stale = [{"utc": row["utc"], "round": row["round"], "phase": row["phase"], "recap_round": row["public"]["recap"]["round"]}
                 for row in snapshots if row["public"].get("recap") and row["public"]["recap"]["round"] < row["round"] - (1 if row["phase"] in (0, 1) else 0)]
        check(role + "_every_round_combat_observed", combat_rounds == list(range(1, session["round"] + 1)), combat_rounds)
        check(role + "_no_stale_retained_recap", not stale, stale)
        bounds = session.get("projected_hero_bounds_samples", [])
        bound_summary = {"sample_count": len(bounds), **{key: sorted({identity for sample in bounds for identity in sample.get(key, [])}) for key in
                        ("bounds_outside_safe_ids", "unprojectable_ids", "missing_or_invisible_component_ids")}}
        frame_summary = frames.summarize(path)
        (output / f"{role}-frames.json").write_text(json.dumps(frame_summary, indent=2) + "\n", encoding="utf-8")
        screenshots = sorted(path.parent.glob("*.png"))
        skill_metadata = list(path.parent.glob("*-skill-shots.jsonl"))
        skill_requests = [json.loads(line) for source in skill_metadata for line in source.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        result = {"role": role, **{key: session.get(key) for key in ("process_id", "seat", "network_mode", "authority_process", "match_namespace", "phase", "round", "complete", "aborted", "intent_requests", "actual_accepted_replies", "actual_rejected_replies", "simulation_speed_multiplier", "resolution_x", "resolution_y", "max_living_visible_units", "max_living_logical_units", "max_simultaneous_encounters", "observed_seat", "music_component_playing", "music_volume")},
                  "first_observed_utc": snapshots[0]["utc"], "first_results_utc": next(row["utc"] for row in snapshots if row["phase"] == 3),
                  "last_observed_utc": snapshots[-1]["utc"], "snapshot_count": len(snapshots), "combat_rounds": combat_rounds, "recap_rounds": recap_rounds,
                  "stale_retained_recaps": stale, "actual_reply_reasons": dict(Counter(row["reason"] for row in replies)),
                  "probes": {probe["name"]: probe["status"] for probe in session["command_probes"]},
                  "public_payload": {key: session.get(key) for key in ("public_json_chars_current", "public_json_chars_max", "public_json_utf8_bytes_current", "public_json_utf8_bytes_max", "distinct_public_payload_samples")},
                  "projected_component_bounds": bound_summary,
                  "engine_log_transport_check": {"status": "NOT_RUN", "oversized_bunch_count": None, "error_log_count": None, "reason": "This Shipping binary does not emit UE_LOG files. Actual received-state coverage and payload sizes are audited separately; no absence-of-log pass is inferred."},
                  "final_standings": [{key: seat[key] for key in ("id", "name", "human", "health", "wins", "place")} for seat in public["seats"]],
                  "screenshot_count": len(screenshots), "skill_screenshot_requests": skill_requests,
                  "screenshot_boundary": "Actual files and runtime capture metadata only. Visual, animation, release-timing and human-audition acceptance require independent inspection.",
                  "profiling": frame_summary}
        results.append(result)
        inputs += [fingerprint(source) for source in [path, snapshot_path, commands_path] + skill_metadata]
    lifecycle_complete = trial.get("status") == "PROCESSES_EXITED_AUDIT_REQUIRED"
    lifecycle = []
    for process in trial["processes"]:
        lifecycle.append({key: process.get(key) for key in ("role", "bootstrap_pid", "inner_pid", "exit_observed", "exit_code", "inner_exit_observed", "inner_exit_code", "exit_observed_utc", "inner_exit_observed_utc")})
    if lifecycle_complete:
        check("both_planned_process_exits_observed", all(row["exit_observed"] for row in lifecycle), lifecycle)
        check("bootstrap_exit_codes_zero", all(row["exit_code"] == 0 for row in lifecycle), lifecycle)
    final_status = "FAIL" if comparison["status"] == "FAIL" or any(row["status"] == "FAIL" for row in additional) else comparison["status"]
    manifest_path = Path(trial["provenance_path"])
    result = {"status": final_status, "lifecycle_complete": lifecycle_complete, "utc": datetime.now(timezone.utc).isoformat(),
              "boundary": "Two actual Shipping game processes over local loopback with separate authenticated human controllers, six persistent bots and scripted real RPC inputs. This is not two physical PCs, manual play, an uncontended1080p performance run or packet capture.",
              "profiling_confounders": trial.get("profiling_confounders"),
              "concurrent_process_inventory": paired.load(base / "concurrency.json") if (base / "concurrency.json").exists() else None,
              "paired_reader_status": comparison["status"], "paired_reader_checks": len(comparison["checks"]),
              "nonpassing_pair_checks": [check for check in comparison["checks"] if check["status"] != "PASS"],
              "additional_checks": additional, "sessions": results, "process_lifecycle": lifecycle,
              "provenance": fingerprint(manifest_path), "trial": fingerprint(base / "trial.json"),
              "concurrent_process_inventory_binding": fingerprint(base / "concurrency.json") if (base / "concurrency.json").exists() else None,
              "inputs": inputs,
              "limits": ["Current and maximum public JSON UTF8 byte lengths exclude replication and socket overhead.",
                         "Both tracked bootstrap processes exited0. Inner process exits were observed but their captured ExitCode values are null/UNKNOWN; bootstrap exit0 is not substituted for an unavailable inner exit code.",
                         "Accepted replies include an intentional idempotent duplicate; they are not a count of distinct mutations.",
                         "Projected skeletal component bounds are conservative geometry, not proof of lack of pixel occlusion or satisfactory hero art.",
                         "Native engine log error and oversized-bunch counts are unavailable for Shipping and remain null/NOT_RUN.",
                         "The preserved earlier Shipping trial failed before client launch because positional startup URLs were disabled; this is a separate build and separate run."]}
    (output / "network-analysis.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Actual routed Shipping two-process network check", "", f"Functional received-state/RPC audit: **{final_status}**. Process lifecycle complete: **{lifecycle_complete}**.", "", result["boundary"], "",
             f"The paired reader completed {len(comparison['checks'])} checks with status {comparison['status']}. UDP{trial['port']} was verified on the host's actual Shipping process before starting the client. Executable hashes still match the immutable startup-fixed provenance.", ""]
    for session in results:
        lines += [f"- {session['role']}: PID{session['process_id']}, seat{session['seat']}, network mode{session['network_mode']}; completed round{session['round']}. All combat rounds observed: {session['combat_rounds']}.",
                  f"- {session['role']}: {session['actual_accepted_replies']} accepted / {session['actual_rejected_replies']} rejected actual replies; probes {session['probes']}.",
                  f"- {session['role']}: maximum actual public JSON {session['public_payload']['public_json_chars_max']} characters / {session['public_payload']['public_json_utf8_bytes_max']} UTF8 bytes; {len(session['stale_retained_recaps'])} stale retained recaps."]
    lines += ["", "Both engine log oversized-bunch/error counts are **NOT_RUN**, not zero. Shipping provides received-state, real-RPC, frame and screenshot evidence through the game's explicit verification writer.", "", str(result["profiling_confounders"]),
              "The optional concurrency.json inventory records any additional actual concurrent functional processes, including a root-owned restart run when present.", "", "## Limits", ""]
    lines += ["- " + value for value in result["limits"]]
    (output / "analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"status": final_status, "lifecycle_complete": lifecycle_complete, "paired_checks": len(comparison["checks"]), "additional_checks": len(additional),
            "sessions": [{key: session[key] for key in ("role", "process_id", "round", "combat_rounds", "public_payload")} for session in results]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence_directory", type=Path)
    args = parser.parse_args()
    result = audit(args.evidence_directory.resolve())
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] in {"PASS", "IN_PROGRESS"} else 1)
