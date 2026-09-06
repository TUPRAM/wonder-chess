"""Audit actual restart/disconnect exports. Does not launch or simulate a game."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from audit_network_evidence import encoded, forbidden_public_paths, load, received


class Audit:
    def __init__(self, paths):
        self.paths = paths
        self.checks = []

    def check(self, name, condition, detail, absent=False):
        self.checks.append({"check": name, "status": "NOT_RUN" if absent else
                            "PASS" if condition else "FAIL", "detail": detail})

    def finish(self, mode):
        states = {c["status"] for c in self.checks}
        return {"status": "FAIL" if "FAIL" in states else "INCOMPLETE" if "NOT_RUN" in states else "PASS",
                "mode": mode,
                "boundary": "Actual process exports only. Resource observations are sampled, not an atomic Logout trace. This does not certify visible messaging, physical LAN transport, or packet capture.",
                "checks": self.checks,
                "inputs": [{"path": str(p.resolve()), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                           for p in dict.fromkeys(self.paths) if p.exists()]}


def public(session):
    value = session.get("public_snapshot", {})
    return json.loads(value) if isinstance(value, str) and value else value


def restart(first_path: Path, second_path: Path):
    first, second = load(first_path), load(second_path)
    a = Audit([first_path, second_path])
    a.check("same_process_and_human_seat", first["process_id"] == second["process_id"]
            and first["seat"] == second["seat"], [first["process_id"], second["process_id"], first["seat"], second["seat"]])
    a.check("distinct_positive_namespaces", 0 < first["match_namespace"] < second["match_namespace"],
            [first["match_namespace"], second["match_namespace"]])
    a.check("both_matches_finished", all(s.get("complete") and not s.get("aborted") for s in (first, second)),
            [{k: s.get(k) for k in ("complete", "aborted", "round")} for s in (first, second)])
    a.check("one_restart_requested", first.get("restart_requested_from_this_match") is True
            and second.get("restart_requested_from_this_match") is False,
            [first.get("restart_requested_from_this_match"), second.get("restart_requested_from_this_match")])
    a.check("prior_namespace_recorded", second.get("prior_match_namespace") == first["match_namespace"],
            second.get("prior_match_namespace"))
    probes = [p for p in second.get("command_probes", []) if p.get("name") == "previous_match_request_rejected"]
    a.check("previous_match_request_rejected", bool(probes) and all(p.get("status") == "PASS" for p in probes),
            probes, absent=not probes)
    for index, (path, session) in enumerate(((first_path, first), (second_path, second))):
        rows, snapshots = received(session, path)
        a.paths.append(snapshots)
        preparation = [r for r in rows if r.get("public", {}).get("phase") == 0
                       and r.get("public", {}).get("round") == 1]
        a.check(f"match_{index}_fresh_preparation_seen", bool(preparation),
                {"round_one_preparation_snapshots": len(preparation)}, absent=not rows)
        bound = [int(r["owner_private"]["revision"]) >> 32 for r in preparation
                 if "revision" in r.get("owner_private", {})]
        a.check(f"match_{index}_private_revision_namespace", session["match_namespace"] in bound,
                sorted(set(bound)), absent=not bound)
        violations = sorted({p for r in rows for p in forbidden_public_paths(r.get("public", {}))})
        a.check(f"match_{index}_received_public_privacy", not violations, violations, absent=not rows)
    return a.finish("restart")


def disconnect(host_path: Path, client_path: Path, mode: str):
    host, client = load(host_path), load(client_path)
    a = Audit([host_path, client_path])
    a.check("distinct_processes", host["process_id"] != client["process_id"],
            [host["process_id"], client["process_id"]])
    a.check("host_listen_authority", host.get("authority_process") is True and host.get("network_mode") == 2,
            {k: host.get(k) for k in ("network_mode", "authority_process", "seat")})
    rows = []
    # A client may have returned to a fresh local menu, so inspect its retained match files too.
    client_paths = sorted(client_path.parent.glob("match-*-session.json")) + [client_path]
    connected = []
    for path in dict.fromkeys(client_paths):
        session = load(path)
        if session.get("process_id") == client["process_id"] and session.get("network_mode") == 3:
            connected.append(session)
            observed, snapshots = received(session, path)
            rows.extend(observed)
            a.paths.extend([path, snapshots])
    a.check("client_was_connected_to_this_match", any(s.get("match_namespace") == host["match_namespace"]
            and s.get("seat") == 1 for s in connected),
            [{k: s.get(k) for k in ("seat", "match_namespace", "network_mode")} for s in connected], absent=not connected)
    violations = sorted({p for row in rows for p in forbidden_public_paths(row.get("public", {}))})
    a.check("client_received_public_privacy", not violations, violations, absent=not rows)
    if mode == "client-loss":
        a.check("client_requested_real_process_exit", client.get("process_exit_requested") is True,
                client.get("process_exit_requested"))
        a.check("host_remained_unaborted", not host.get("aborted"), host.get("aborted"))
        transitions = [e for e in host.get("authority_takeover_transitions", []) if e.get("departed_seat") == 1]
        a.check("human_to_bot_takeover_observed", bool(transitions) and all(
            e.get("before", {}).get("human") is True and e.get("after", {}).get("human") is False
            and e.get("after", {}).get("takeover") is True for e in transitions), transitions, absent=not transitions)
        for index, event in enumerate(transitions):
            before, after = event.get("before", {}), event.get("after", {})
            fields = set(before) | set(after)
            resources_equal = all(encoded(before.get(key)) == encoded(after.get(key))
                                  for key in fields - {"human", "takeover", "revision"})
            conclusive = event.get("status") != "INCONCLUSIVE"
            a.check(f"takeover_{index}_resources_preserved", resources_equal and event.get("status") == "PASS",
                    {"recorded_status": event.get("status"), "resources_equal": resources_equal,
                     "boundary": event.get("boundary")}, absent=not conclusive)
        last = max((e.get("elapsed_wall_seconds", 0) for e in transitions), default=0)
        a.check("authority_continued_after_departure", bool(transitions)
                and host.get("elapsed_wall_seconds", 0) >= last + 2,
                {"takeover_wall_seconds": last, "final_wall_seconds": host.get("elapsed_wall_seconds")}, absent=not transitions)
    elif mode == "host-loss":
        a.check("host_requested_real_process_exit", host.get("process_exit_requested") is True,
                host.get("process_exit_requested"))
        a.check("client_marked_host_loss", client.get("host_disconnected") is True
                and client.get("aborted") is True and not client.get("complete"),
                {k: client.get(k) for k in ("host_disconnected", "aborted", "complete", "network_error", "network_error_detail")})
        a.check("client_retained_concrete_failure", bool(client.get("network_error"))
                and bool(client.get("network_error_detail")), client.get("network_error_detail"))
    else:
        raise ValueError(mode)
    return a.finish(mode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["restart", "client-loss", "host-loss"])
    parser.add_argument("first_session", type=Path)
    parser.add_argument("second_session", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = restart(args.first_session, args.second_session) if args.mode == "restart" else disconnect(
        args.first_session, args.second_session, args.mode)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks": len(result["checks"]), "output": str(args.output)}, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
