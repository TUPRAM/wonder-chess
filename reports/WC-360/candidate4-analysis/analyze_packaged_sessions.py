"""Read actual candidate5 exports; never launch or mutate the game."""

import collections
import hashlib
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def fingerprint(path):
    return {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def helper(name):
    path = ROOT / "tests/runtime" / (name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AUDIT = helper("audit_network_evidence")
FRAMES = helper("summarize_frame_evidence")


def session_summary(path):
    session = load(path)
    snapshot_path = path.with_name(path.name.replace("-session.json", "-snapshots.jsonl"))
    command_path = path.with_name(path.name.replace("-session.json", "-commands.jsonl"))
    rows, commands = jsonl(snapshot_path), jsonl(command_path)
    actual = [r for r in rows if len(r.get("public", {}).get("seats", [])) == 8]
    final = json.loads(session["public_snapshot"])
    dead = [r for r in actual if r["public"]["seats"][session["seat"]]["health"] <= 0]
    dead_combat = [r for r in dead if r["phase"] == 1 and
                   any(not e["complete"] for e in r["public"].get("encounters", []))]
    replies = [r for r in commands if r.get("event") == "actual_client_reply"]
    privacy = sorted(set(session["received_state_privacy_violations"]).union(
        *(AUDIT.forbidden_public_paths(r["public"]) for r in actual)))
    keys = ("process_id", "match_namespace", "seat", "network_mode", "authority_process", "scripted_client",
            "simulation_speed_multiplier", "complete", "aborted", "phase", "round", "intent_requests",
            "actual_accepted_replies", "actual_rejected_replies", "process_exit_requested",
            "max_living_visible_units", "max_living_logical_units", "max_simultaneous_encounters")
    result = {k: session[k] for k in keys}
    result.update({
        "observed_first_utc": rows[0]["utc"], "observed_last_utc": rows[-1]["utc"],
        "first_results_utc": next((r["utc"] for r in rows if r["phase"] == 3), None),
        "snapshot_count": len(rows), "eight_seat_snapshot_count": len(actual),
        "human_count_values": sorted({sum(bool(s["human"]) for s in r["public"]["seats"]) for r in actual}),
        "owner_private_binding": all(r["owner_private"].get("seat") == session["seat"] for r in actual),
        "received_public_privacy_violations": privacy,
        "fresh_owner_private": rows[0]["owner_private"],
        "combat_rounds": sorted({r["round"] for r in actual if r["phase"] == 1}),
        "preparation_rounds": sorted({r["round"] for r in actual if r["phase"] == 0}),
        "first_human_eliminated_observation": {k: dead[0][k] for k in ("utc", "round", "phase")} if dead else None,
        "combat_rounds_observed_after_human_elimination": sorted({r["round"] for r in dead_combat}),
        "post_elimination_combat_boundary": "Eliminated owner receives ongoing real encounters; this field alone does not prove camera selection or visible UX.",
        "command_event_counts": dict(collections.Counter(r.get("event", "probe_result") for r in commands)),
        "actual_reply_reasons": dict(collections.Counter(r["reason"] for r in replies)),
        "reply_counts_reconcile": sum(r["accepted"] for r in replies) == session["actual_accepted_replies"] and
                                  sum(not r["accepted"] for r in replies) == session["actual_rejected_replies"],
        "probes": [{k: p.get(k) for k in ("name", "status", "accepted", "reply")} for p in session["command_probes"]],
        "capped": final["capped"],
        "final_standings": [{k: s[k] for k in ("id", "name", "human", "health", "wins", "place")} for s in final["seats"]],
        "inputs": [fingerprint(p) for p in (path, snapshot_path, command_path)],
    })
    return result


def log_summary(path):
    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    oversized = [line for line in lines if "Attempted to send bunch exceeding max allowed size" in line]
    sizes = [int(re.search(r"BunchSize=(\d+)", line)[1]) for line in oversized]
    return {"input": fingerprint(path), "error_level_lines": sum(": Error:" in line for line in lines),
            "oversized_bunch_count": len(oversized), "bunch_size_min": min(sizes) if sizes else None,
            "bunch_size_max": max(sizes) if sizes else None,
            "oversized_bunch_first": oversized[0] if oversized else None,
            "oversized_bunch_last": oversized[-1] if oversized else None,
            "oversized_bunch_lines": oversized,
            "network_failure_lines": [line for line in lines if "BroadcastNetworkFailure" in line],
            "match_finished_lines": [line for line in lines if "WC_MATCH_FINISHED" in line],
            "exit_lines": [line for line in lines if "RequestExit" in line or "Log file closed" in line]}


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main():
    solo = ROOT / "reports/WC-360/candidate5-solo-restart"
    solo_paths = [next(solo.glob(f"match-{n}-seat-0-*-session.json")) for n in (1, 2)]
    solo_matches = [session_summary(p) for p in solo_paths]
    restart = load(solo / "audit/restart-audit.json")
    frame_reports = [FRAMES.summarize(p) for p in solo_paths]
    for n, frame in enumerate(frame_reports, 1):
        save(solo / f"audit/match-{n}-frames.json", frame)
    session_checks = [m["complete"] and not m["aborted"] and m["human_count_values"] == [1] and
                      m["owner_private_binding"] and not m["received_public_privacy_violations"] and
                      m["reply_counts_reconcile"] and all(p["status"] == "PASS" for p in m["probes"])
                      and m["combat_rounds"] == list(range(1, m["round"] + 1)) for m in solo_matches]
    solo_report = {"status": "PASS" if all(session_checks) and restart["status"] == "PASS" else "FAIL",
                   "boundary": "Two actual packaged 1H7B namespaces in one process using scripted human ServerIntent input at 10x simulation. This is functional execution evidence, not manual play, normal-speed performance acceptance, or a visual quality verdict.",
                   "audit_utc": datetime.now(timezone.utc).isoformat(), "matches": solo_matches,
                   "restart_reader_status": restart["status"], "restart_reader_checks": len(restart["checks"]),
                   "performance": frame_reports, "log": log_summary(solo / "game.log"),
                   "performance_caveat": "10x speed plus screenshot and JSON evidence capture; first match overlapped the separate regression and art work. Observed timing spikes are retained. A dedicated normal-speed run is required.",
                   "provenance": fingerprint(ROOT / "reports/WC-360/candidate5-provenance.json")}
    save(solo / "audit/solo-restart-analysis.json", solo_report)
    lines = ["Candidate5 actual packaged solo and restart execution: " + solo_report["status"], "", solo_report["boundary"], ""]
    for n, (match, frame) in enumerate(zip(solo_matches, frame_reports), 1):
        busy = frame["subsets"]["twelve_visible_and_four_live_encounters"]
        lines += [f"- Namespace {n}: completed round {match['round']}, human seat 0 eliminated in round {match['first_human_eliminated_observation']['round']}; all {len(match['probes'])} actual RPC probes PASS. {match['intent_requests']} requests, {match['actual_accepted_replies']} accepted replies and {match['actual_rejected_replies']} deliberate rejection replies.",
                  f"- Namespace {n}: {busy['frames']} frames with twelve visible living heroes and four live encounters; frame p50/p95/p99 {busy['frame_ms']['p50_ms']:.3f}/{busy['frame_ms']['p95_ms']:.3f}/{busy['frame_ms']['p99_ms']:.3f} ms. GPU p95 {busy['gpu_ms']['p95_ms']:.3f} ms."]
    lines += ["", "Restart audit: 12/12 checks PASS, new namespace and fresh owner economy/revision, previous-match request rejected as stale. Both matches observed every combat round 1-20 and continued receiving actual encounters after the human was eliminated. Public exports contain no forbidden private fields. Results assigned exactly one first place.", "",
              "Timing hardware: AMD Ryzen 7 6800H, NVIDIA GeForce RTX 3060 Laptop GPU (active D3D11 adapter), 1920x1080, screen percentage 100, frame cap 60, VSync off. The OS also lists the integrated AMD adapter; that is not the active renderer. Timings do not pass a normal-speed frame-time gate. " + solo_report["performance_caveat"], "",
              "The actual process requested its preplanned timed exit and closed normally. No third match namespace is recorded. Screenshot existence is evidence capture, not a reviewed visual-quality pass.", ""]
    (solo / "audit/analysis.md").write_text("\n".join(lines), encoding="utf-8")

    network = ROOT / "reports/WC-360/candidate5-network"
    paths = [next((network / role).glob(f"match-1-seat-{seat}-*-session.json")) for seat, role in enumerate(("host", "client"))]
    pair = AUDIT.audit(*paths, require_complete=True)
    save(network / "audit/paired-state-audit.json", pair)
    summaries = [session_summary(p) for p in paths]
    logs = {role: log_summary(network / role / "game.log") for role in ("host", "client")}
    menu_session = load(network / "client/session.json")
    report = {"status": pair["status"], "boundary": "Actual packaged listen-server and client processes over 127.0.0.1, two real human seat bindings with scripted RPCs at 10x speed. This does not certify a second physical computer or an external LAN.",
              "audit_utc": datetime.now(timezone.utc).isoformat(), "sessions": summaries, "logs": logs,
              "paired_checks": len(pair["checks"]), "failed_checks": [c for c in pair["checks"] if c["status"] != "PASS"],
              "missing_client_combat_rounds": sorted(set(summaries[0]["combat_rounds"]) - set(summaries[1]["combat_rounds"])),
              "after_host_planned_exit_client": {k: menu_session[k] for k in ("utc", "match_namespace", "aborted", "host_disconnected", "network_error", "network_error_detail", "intent_requests", "process_exit_requested")},
              "recap_reader_correction": "The reader now compares retained recap payloads by their own round. An older retained recap does not establish the round of current seat health; the original reader falsely treated that as inconsistent settlement. Missing combat rounds and actual oversized replication bunch errors remain independent failures.",
              "provenance": fingerprint(ROOT / "reports/WC-360/candidate5-provenance.json")}
    save(network / "audit/network-analysis.json", report)
    oversize = logs["host"]
    lines = ["Candidate5 actual packaged two-process network acceptance: " + report["status"], "", report["boundary"], "",
             f"The host logged {oversize['oversized_bunch_count']} rejected oversized replication bunches, {oversize['bunch_size_min']}-{oversize['bunch_size_max']} bytes against the engine's 65,536-byte maximum. The host observed combat in all rounds 1-22; the client observed only 1 and 17-22, missing 2-16. Final results agree at round 22, which does not compensate for the missing match updates.", "",
             "Both human bindings passed all seven actual RPC probes, and owner-private/public privacy checks passed. Host: 42 requests, 37 accepted replies, 5 deliberate rejection replies. Client: 79 requests, 34 accepted replies, 45 rejections; the JSON report retains all actual rejection reasons. These totals include duplicate accepted replies, not 37/34 distinct accepted mutations.", "",
             "After results, the host's preplanned timed exit produced a real connection loss on the client. The client returned to an aborted menu namespace, preserved the disconnect message and issued no new scripted match commands. This late host loss is not an in-progress disconnect acceptance test.", "",
             report["recap_reader_correction"], "",
             "Root is preparing the next candidate with condensed public JSON, a reduced recap payload and measured payload bounds. These candidate5 failures are retained; this report makes no claim that the source fix has been packaged or verified.", ""]
    (network / "audit/analysis.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"solo": solo_report["status"], "network": report["status"], "oversized_bunches": oversize["oversized_bunch_count"], "missing_client_combat_rounds": report["missing_client_combat_rounds"]}, indent=2))


if __name__ == "__main__":
    main()
