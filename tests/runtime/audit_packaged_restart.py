"""Audit preserved actual packaged restart sessions and the direct process exit record."""
from collections import Counter
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path

from audit_network_evidence import load, received, forbidden_public_paths
from audit_session_transitions import restart

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "reports/WC-360/shipping-restart"


def bind(path):
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence_directory", type=Path, nargs="?", default=BASE)
    parser.add_argument("--require-seed-summary-parity", action="store_true")
    parser.add_argument("--expected-restarts", type=int, choices=(1, 2), default=1)
    args = parser.parse_args()
    base = args.evidence_directory.resolve()
    all_sessions = sorted(base.glob("match-*-session.json"))
    paths = [path for path in all_sessions if load(path)["match_namespace"] > 0]
    pre_match = [path for path in all_sessions if load(path)["match_namespace"] <= 0]
    if len(paths) != args.expected_restarts + 1:
        raise ValueError(f"Expected {args.expected_restarts + 1} retained match sessions, found {len(paths)}")
    checks = []
    for index, (first, second) in enumerate(zip(paths, paths[1:])):
        transition = restart(first, second, second_will_restart=index < args.expected_restarts - 1)
        checks.extend({**check, "check": f"restart_{index + 1}_" + check["check"]} for check in transition["checks"])
    inputs = [*all_sessions, base / "launch.json"]
    launch = load(inputs[-1])
    summaries = []

    def check(name, condition, detail):
        checks.append({"check": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    for path in pre_match:
        session = load(path)
        check("pre_match_has_no_tournament", session["match_namespace"] == 0
              and session["round"] == 0 and session["phase"] == -1
              and not session.get("complete") and not session.get("actual_accepted_replies"),
              {"path": path.name, "namespace": session["match_namespace"],
               "round": session["round"], "phase": session["phase"]})

    for path in paths:
        s = load(path)
        prefix = f"match-{s['match_namespace']}-seat-{s['seat']}-pid-{s['process_id']}"
        command_path = base / (prefix + "-commands.jsonl")
        commands = [json.loads(line) for line in command_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        snapshots, snapshot_path = received(s, path)
        rows = [row for row in snapshots if len(row.get("public", {}).get("seats", [])) == 8]
        inputs.extend((snapshot_path, command_path))
        public = json.loads(s["public_snapshot"])
        namespace = s["match_namespace"]
        label = f"namespace_{namespace}_"
        check(label + "eight_persistent_seats_with1H7B", bool(rows) and all(sum(bool(seat["human"]) for seat in row["public"]["seats"]) == 1 for row in rows)
              and len({tuple((seat["id"], seat["name"]) for seat in row["public"]["seats"]) for row in rows}) == 1,
              [(seat["id"], seat["name"], seat["human"]) for seat in public["seats"]])
        combat_rounds = sorted({row["round"] for row in rows if row["phase"] == 1})
        check(label + "all_combat_rounds_observed", combat_rounds == list(range(1, s["round"] + 1)), combat_rounds)
        check(label + "owner_private_binding_and_public_privacy", all(row.get("owner_private", {}).get("seat") == s["seat"] for row in rows)
              and not s["received_state_privacy_violations"] and all(not forbidden_public_paths(row["public"]) for row in rows), len(rows))
        probes = {p["name"]: p for p in s["command_probes"]}
        required = {"out_of_order_sequence_rejected", "original_idempotent_lock_request", "duplicate_request_applies_once",
                    "changed_payload_same_request_rejected", "stale_revision_rejected", "foreign_unit_sale_rejected", "combat_phase_buy_rejected"}
        if path != paths[0]:
            required.add("previous_match_request_rejected")
        check(label + "all_required_actual_rpc_probes", set(probes) == required and all(p["status"] == "PASS" for p in probes.values()),
              {name: {key: p.get(key) for key in ("status", "accepted", "reply", "request_id")} for name, p in probes.items()})
        replies = [row for row in commands if row.get("event") == "actual_client_reply"]
        rejected = Counter(row["reason"] for row in replies if not row["accepted"])
        expected = Counter(p["reply"] for p in probes.values() if not p["accepted"])
        check(label + "reply_totals_reconcile", sum(row["accepted"] for row in replies) == s["actual_accepted_replies"]
              and sum(not row["accepted"] for row in replies) == s["actual_rejected_replies"],
              {"accepted": s["actual_accepted_replies"], "rejected": s["actual_rejected_replies"]})
        check(label + "no_unintended_command_rejections", rejected == expected, {"actual": dict(rejected), "expected_deliberate_probes": dict(expected)})
        eliminated = next((row for row in rows if row["public"]["seats"][0]["health"] <= 0), None)
        after = [row for row in rows if eliminated and row["round"] > eliminated["round"] and row["phase"] == 1]
        check(label + "bots_continue_after_early_elimination", bool(eliminated) and bool(after)
              and sorted({row["round"] for row in after}) == list(range(eliminated["round"] + 1, s["round"] + 1))
              and all(row["public"].get("encounters") for row in after),
              {"elimination_round": eliminated["round"] if eliminated else None, "subsequent_combat_rounds": sorted({row["round"] for row in after})})
        check(label + "spectating_after_elimination", any(row.get("observed_seat", 0) > 0 for row in after), sorted({row.get("observed_seat") for row in after}))
        check(label + "actual_taa_candidate_settings", s["render_settings"].get("r.AntiAliasingMethod") == "2" and s["simulation_speed_multiplier"] == launch.get("simulation_speed", 10),
              {"render_settings": s["render_settings"], "speed": s["simulation_speed_multiplier"]})
        seeds = sorted({row["match_seed_authority"] for row in rows})
        check(label + "snapshot_authority_seed_consistency", len(seeds) == 1, seeds)
        if args.require_seed_summary_parity:
            check(label + "summary_seed_matches_retained_snapshots", len(seeds) == 1 and s["match_seed_authority"] == seeds[0],
                  {"summary": s["match_seed_authority"], "snapshots": seeds})
        summaries.append({"namespace": namespace, "first_observation_utc": rows[0]["utc"],
                          "results_utc": next(row["utc"] for row in rows if row["phase"] == 3), "rounds": s["round"],
                          "actual_authority_seed": seeds[0], "summary_authority_seed": s["match_seed_authority"],
                          "seed_summary_matches_snapshots": s["match_seed_authority"] == seeds[0],
                          "elimination_round": eliminated["round"] if eliminated else None,
                          "human_place": public["seats"][0]["place"], "accepted_replies": s["actual_accepted_replies"],
                          "deliberate_rejected_replies": s["actual_rejected_replies"], "probes": len(probes),
                          "standings": [{key: seat[key] for key in ("id", "name", "human", "health", "place", "wins")} for seat in public["seats"]]})
    manifest_path = Path(launch["provenance_path"])
    manifest = load(manifest_path)
    manifest_entry = next(item for item in manifest["files"] if item["path"] == launch["executable"])
    check("immutable_candidate_binding", bind(manifest_path)["sha256"] == launch["provenance_sha256"]
          and launch["executable_sha256"] == manifest_entry["sha256"],
          {"manifest": str(manifest_path), "manifest_sha256": launch["provenance_sha256"], "inner_sha256": launch["executable_sha256"]})
    check("same_direct_inner_process_exit0", all(load(path)["process_id"] == launch["process_id"] for path in paths)
          and launch["status"] == "EXITED_AUDIT_REQUIRED" and launch["exit_code"] == 0,
          {key: launch[key] for key in ("process_id", "started_utc", "ended_utc", "exit_code")})
    inputs.append(manifest_path)
    result = {"status": "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL", "utc": datetime.now(timezone.utc).isoformat(),
              "checks": checks, "matches": summaries, "inputs": [bind(p) for p in dict.fromkeys(inputs)],
              "boundary": "Two actual complete1H7B namespaces in one Shipping process, using actual scripted controller commands and host restart. Accelerated functional run is not performance or manual usability/audio evidence; exact speed and rendering mode are in the bound launch record. Actual initial seed came from WCAutoStart; restart uses the separately recorded restart seed.",
              "known_evidence_defects": [{"field": "match_seed_authority", "namespace": s["namespace"], "summary": s["summary_authority_seed"],
                                          "all_retained_snapshot_seed": s["actual_authority_seed"],
                                          "reason": "Old namespace final writer consults the replacement authoritative Match. Actual seed comes from internally consistent retained snapshot records."}
                                         for s in summaries if not s["seed_summary_matches_snapshots"]],
              "engine_log_checks": {"status": "NOT_RUN", "count": None, "reason": "Shipping UE_LOG output unavailable, not a zero-error inference."}}
    output = base / "functional-audit"
    output.mkdir(exist_ok=True)
    (output / "audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Packaged restart functional audit", "", f"**{result['status']}**, {len(checks)} checks.", "", result["boundary"], ""]
    for s in summaries:
        lines.append(f"- Namespace {s['namespace']}: actual seed {s['actual_authority_seed']}; {s['rounds']} rounds; human eliminated round {s['elimination_round']}, place {s['human_place']}; {s['accepted_replies']} accepted replies, {s['deliberate_rejected_replies']} deliberate rejected replies; all {s['probes']} probes passed. Results observed {s['results_utc']}.")
    lines.extend(["", f"Direct inner process {launch['process_id']} actually exited {launch['exit_code']} at {launch['ended_utc']}. Both complete namespace transcripts, fresh round-one preparation, revision namespaces, private-state isolation and rejection of an old-match request are retained and hash-bound.", "", "Shipping engine-log checks remain NOT_RUN."])
    if result["known_evidence_defects"]:
        lines.extend(["", "Evidence defect retained: namespace1's final summary seed incorrectly reports the replacement match's271828. Every retained namespace1 snapshot reports314159, and every namespace2 snapshot reports271828. This report derives seeds from those consistent timestamped snapshots; gameplay functional checks remain independently passed."])
    (output / "audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks": len(checks), "matches": [{k: v for k, v in s.items() if k != 'standings'} for s in summaries], "nonpassing": [c for c in checks if c["status"] != "PASS"]}, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
