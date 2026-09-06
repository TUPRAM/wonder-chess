"""Audit actual Shipping disconnect exports without inferring unavailable UE_LOG evidence."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from audit_network_evidence import load
from audit_session_transitions import disconnect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trial", type=Path)
    args = parser.parse_args()
    directory = args.trial
    trial = load(directory / "trial.json")
    host_path, client_path = directory / "host/session.json", directory / "client/session.json"
    report = disconnect(host_path, client_path, trial["mode"])
    inputs = [directory / "trial.json"]

    def check(name, condition, detail):
        report["checks"].append({"check": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    check("port_unowned_before_launch", trial.get("port_unowned_before_launch") is True, trial["port"])
    check("planned_processes_exited_zero", trial["status"] == "PROCESSES_EXITED_AUDIT_REQUIRED" and
          all(p["exit_observed"] and p["exit_code"] == 0 for p in trial["processes"]),
          [{k: p.get(k) for k in ("role", "bootstrap_pid", "exit_observed", "exit_code", "planned_exit_after_seconds")} for p in trial["processes"]])
    host, client = load(host_path), load(client_path)
    project = Path(__file__).resolve().parents[2]
    provenance_path = Path(trial["provenance_path"])
    provenance = load(provenance_path)
    inputs.append(provenance_path)
    executable_hashes = []
    identities = {item["path"]: item["sha256"] for item in trial["executable_identities"]}
    for item in provenance["files"]:
        path = Path(item["path"])
        if item["path"] in identities:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            executable_hashes.append({"path": str(path), "expected_sha256": item["sha256"], "actual_sha256": digest,
                                      "matches": digest == item["sha256"]})
    check("packaged_executables_match_immutable_manifest", len(executable_hashes) == 2 and
          all(item["matches"] for item in executable_hashes), executable_hashes)
    check("manifest_identity_matches_launch", hashlib.sha256(provenance_path.read_bytes()).hexdigest() == trial["provenance_sha256"], trial["provenance_sha256"])
    check("actual_shipping_udp_listener", trial.get("listen_owner", {}).get("local_port") == trial["port"]
          and Path(trial.get("listen_owner", {}).get("executable_path", "")) == Path(provenance["packaged_game_executable"]),
          trial.get("listen_owner"))
    check("departure_occurred_before_tournament_results", not host["complete"] and not client["complete"],
          {"host_complete": host["complete"], "client_complete": client["complete"]})
    if trial["mode"] == "client-loss":
        transitions = [t for t in host["authority_takeover_transitions"] if t["departed_seat"] == 1]
        check("takeover_during_quiescent_combat", bool(transitions) and all(t["phase"] == 1 and t["status"] == "PASS"
              and not t["intervening_bot_commands"] for t in transitions),
              [{k: t.get(k) for k in ("phase", "round", "status", "intervening_bot_commands")} for t in transitions])
        late_path = directory / "late-join/session.json"
        if late_path.exists():
            late = load(late_path)
            public = json.loads(late["public_snapshot"])
            inputs.append(late_path)
            check("late_join_after_takeover", trial["late_join_launched_after_observed_takeover"] is True,
                  {"takeover_observed_utc": trial.get("takeover_observed_utc")})
            check("late_join_separate_real_process", len({host["process_id"], client["process_id"], late["process_id"]}) == 3,
                  [host["process_id"], client["process_id"], late["process_id"]])
            check("late_join_rejected_with_concrete_reason", late["aborted"] is True and
                  "does not support joining or rejoining a running tournament" in late["network_error"],
                  {k: late.get(k) for k in ("network_error", "network_error_detail", "aborted")})
            check("late_join_no_active_match_or_commands", late["match_namespace"] == 0 and late["intent_requests"] == 0
                  and public.get("phase") == -1 and public.get("seats") == [],
                  {"namespace": late["match_namespace"], "requests": late["intent_requests"], "public": public})
            check("late_join_planned_exit", late["process_exit_requested"] is True, late["process_exit_requested"])
            final = json.loads(host["public_snapshot"])
            check("host_kept_bot_takeover_after_late_join", len(final["seats"]) == 8 and
                  final["seats"][1]["takeover"] and not final["seats"][1]["human"] and not host["aborted"],
                  {"human_seats": [s["id"] for s in final["seats"] if s["human"]],
                   "takeover_seats": [s["id"] for s in final["seats"] if s["takeover"]], "round": final["round"]})
        else:
            check("late_join_actual_evidence", False, "No late-join session file")
    else:
        check("host_departed_during_combat", host["phase"] == 1, {"phase": host["phase"], "round": host["round"]})
        public = json.loads(client["public_snapshot"])
        check("aborted_client_did_not_autostart", client["match_namespace"] == 0 and client["intent_requests"] == 0
              and public.get("phase") == -1 and not public.get("seats"),
              {"namespace": client["match_namespace"], "requests": client["intent_requests"], "public": public})
        check("client_planned_exit_after_abort", client["process_exit_requested"] is True, client["process_exit_requested"])
    logs = {}
    for process in trial["processes"]:
        path = directory / process["role"] / "game.log"
        inputs += [directory / process["role"] / "launch.json"]
        logs[process["role"]] = {"status": "NOT_RUN", "oversized_bunch_count": None, "error_count": None,
                                 "reason": "This Shipping binary has no UE_LOG output. Absence is not interpreted as zero errors; actual received-state and process evidence are checked separately."}
    states = {c["status"] for c in report["checks"]}
    report["status"] = "FAIL" if "FAIL" in states else "INCOMPLETE" if "NOT_RUN" in states else "PASS"
    report["audit_utc"] = datetime.now(timezone.utc).isoformat()
    report["lifecycle"] = trial
    report["logs"] = logs
    report["boundary"] += " Shipping engine-log checks are unavailable/NOT_RUN. Bootstrap exit codes are observed separately and do not establish unobserved inner exit codes. No manual UI or audio review occurred; no render-performance acceptance is inferred."
    for path in inputs:
        report["inputs"].append({"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    output = directory / "audit.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    failed = [c for c in report["checks"] if c["status"] != "PASS"]
    text = [f"Shipping actual {trial['mode']} trial: {report['status']}", "", report["boundary"], "",
            f"{len(report['checks'])} checks evaluated. Actual local UDP listen port: {trial['port']}. All launches, timed exit observations and exact process identities are in trial.json. Resource and privacy evidence is in audit.json.", "",
            f"Non-passing checks: {json.dumps(failed)}", ""]
    (directory / "audit.md").write_text("\n".join(text), encoding="utf-8")
    print(json.dumps({"status": report["status"], "checks": len(report["checks"]), "nonpassing": failed, "output": str(output)}, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
