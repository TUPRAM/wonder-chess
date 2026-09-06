"""Audit two real WCVerification process exports; fixtures cannot certify networking."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def forbidden_public_paths(value, path="public"):
    forbidden = {"gold", "xp", "shop", "bench", "sequence", "revision", "shopRng", "botRng"}
    found = set()
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{path}.{key}"
            if key in forbidden:
                found.add(child)
            found.update(forbidden_public_paths(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.update(forbidden_public_paths(item, f"{path}[{index}]"))
    return found


def received(session, path):
    prefix = f"match-{session['match_namespace']}-seat-{session['seat']}-pid-{session['process_id']}"
    snapshots = path.parent / (prefix + "-snapshots.jsonl")
    rows = []
    if snapshots.exists():
        for index, line in enumerate(snapshots.read_text(encoding="utf-8-sig").splitlines(), 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as error:
                    raise ValueError(f"{snapshots}:{index}: invalid evidence JSON") from error
    return rows, snapshots


def sets_by(rows, category):
    values = defaultdict(set)
    for row in rows:
        public = row.get("public", {})
        round_number = public.get("round", 0)
        if category == "pairing" and public.get("pairs"):
            values[round_number].add(encoded(public["pairs"]))
        elif category == "settlement" and public.get("recap"):
            key = public["recap"]["round"]
            # The retained recap can precede the current seat state. Compare its
            # own payload rather than associating a later health total with it.
            values[key].add(encoded(public["recap"]))
        elif category == "combat" and public.get("phase") == 1 and public.get("encounters"):
            fights = public["encounters"]
            key = (round_number, tuple((e["a"], e["b"], e["ghost"], e["tick"]) for e in fights))
            values[key].add(encoded(fights))
    return values


def audit(first_path: Path, second_path: Path, require_complete=False):
    sessions = [load(first_path), load(second_path)]
    rows_and_paths = [received(s, p) for s, p in zip(sessions, [first_path, second_path])]
    checks = []

    def check(name, status, detail):
        checks.append({"check": name, "status": status, "detail": detail})

    def expect(name, condition, detail):
        check(name, "PASS" if condition else "FAIL", detail)

    expect("distinct_processes", sessions[0]["process_id"] != sessions[1]["process_id"],
           [s["process_id"] for s in sessions])
    expect("distinct_human_seats", {s["seat"] for s in sessions} == {0, 1}, [s["seat"] for s in sessions])
    expect("listen_server_and_client", {s["network_mode"] for s in sessions} == {2, 3}
           and {s["authority_process"] for s in sessions} == {True, False},
           [{"mode": s["network_mode"], "authority": s["authority_process"]} for s in sessions])
    expect("shared_nonzero_match_namespace", sessions[0]["match_namespace"] == sessions[1]["match_namespace"]
           and sessions[0]["match_namespace"] > 0, [s["match_namespace"] for s in sessions])

    for index, (session, (rows, _)) in enumerate(zip(sessions, rows_and_paths)):
        label = f"process_{index}"
        actual = [r for r in rows if len(r.get("public", {}).get("seats", [])) == 8]
        if not actual:
            check(label + "_eight_seat_snapshots", "NOT_RUN", "No actual eight-seat snapshots recorded")
        else:
            expect(label + "_two_humans_six_bots", all(
                sum(bool(s["human"]) for s in r["public"]["seats"]) == 2 for r in actual),
                {"observed_snapshots": len(actual)})
            private = [r.get("owner_private", {}) for r in actual]
            expect(label + "_owner_private_binding", all(p.get("seat") == session["seat"] for p in private),
                   {"observed_private_snapshots": len(private)})
            revisions = [int(p["revision"]) >> 32 for p in private if "revision" in p]
            # Replication routes can arrive separately: the first public match snapshot can precede
            # the owner's new private state. Such transient stale state is reported, not a leak claim.
            expect(label + "_current_private_namespace_seen", session["match_namespace"] in revisions,
                   {"observed_revision_namespaces": sorted(set(revisions))})
        violations = set(session.get("received_state_privacy_violations", []))
        for row in rows:
            violations.update(forbidden_public_paths(row.get("public", {})))
        if violations or actual:
            expect(label + "_received_state_privacy", not violations, sorted(violations))
        else:
            check(label + "_received_state_privacy", "NOT_RUN", "No received match snapshots to inspect")
        expected_names = {"out_of_order_sequence_rejected", "original_idempotent_lock_request",
                          "duplicate_request_applies_once", "changed_payload_same_request_rejected"}
        if session.get("extended_authority_checks"):
            expected_names.update({"stale_revision_rejected", "foreign_unit_sale_rejected",
                                   "combat_phase_buy_rejected"})
            if session.get("prior_match_namespace", -1) > 0:
                expected_names.add("previous_match_request_rejected")
        probes = {p["name"]: p for p in session.get("command_probes", [])}
        for name in sorted(expected_names):
            item = probes.get(name)
            check(label + "_" + name, item["status"] if item else "NOT_RUN", item or "No recorded probe")
        expect(label + "_actual_commands_received", session.get("actual_accepted_replies", 0) > 0,
               {"accepted": session.get("actual_accepted_replies"), "rejected": session.get("actual_rejected_replies")})
        complete = bool(session.get("complete"))
        check(label + "_complete_tournament", "PASS" if complete else "FAIL" if require_complete else "NOT_RUN",
              {"complete": complete, "aborted": session.get("aborted"), "last_round": session.get("round")})

    combat_rounds = [{int(r["public"]["round"]) for r in rows
                      if r.get("public", {}).get("phase") == 1}
                     for rows, _ in rows_and_paths]
    expect("received_combat_round_coverage", combat_rounds[0] == combat_rounds[1]
           and bool(combat_rounds[0]),
           {"host_observed": sorted(combat_rounds[0]), "client_observed": sorted(combat_rounds[1]),
            "missing_on_client": sorted(combat_rounds[0] - combat_rounds[1]),
            "missing_on_host": sorted(combat_rounds[1] - combat_rounds[0]),
            "boundary": "Sampled public combat presence, not every replicated tick or packet."})

    transport_inputs = []
    for label, session_path in [("host", first_path), ("client", second_path)]:
        log_path = session_path.parent / "game.log"
        if log_path.exists():
            transport_inputs.append(log_path)
            oversize = [line for line in log_path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
                        if "Attempted to send bunch exceeding max allowed size" in line]
            expect(label + "_no_oversized_replication_bunches", not oversize,
                   {"count": len(oversize), "first": oversize[0] if oversize else None,
                    "last": oversize[-1] if oversize else None})

    for category in ["pairing", "settlement", "combat"]:
        left, right = [sets_by(rows, category) for rows, _ in rows_and_paths]
        common = set(left) & set(right)
        if not common:
            check(category + "_public_state_agreement", "NOT_RUN", "No identically keyed observations in both processes")
            continue
        mismatches = [str(key) for key in common if left[key] != right[key]]
        unstable = [str(key) for key in common if len(left[key]) != 1 or len(right[key]) != 1]
        expect(category + "_public_state_agreement", not mismatches and not unstable,
               {"matched_keys": len(common), "mismatches": mismatches, "internally_inconsistent_keys": unstable})

    if all(s.get("complete") for s in sessions):
        public = [json.loads(s["public_snapshot"]) for s in sessions]
        standings = [[(x["id"], x["health"], x["wins"], x["place"]) for x in p["seats"]] for p in public]
        expect("complete_results_agree", standings[0] == standings[1], standings)
    else:
        check("complete_results_agree", "NOT_RUN", "Both processes must reach results")
    statuses = [c["status"] for c in checks]
    result = {
        "status": "FAIL" if any(s in {"FAIL", "FAILED"} for s in statuses) else
                  "INCOMPLETE" if any(s in {"NOT_RUN", "INCONCLUSIVE"} for s in statuses) else "PASS",
        "boundary": "Actual exported received state and real RPC replies. Not packet capture, human usability, or disconnect certification.",
        "checks": checks,
        "inputs": [{"path": str(p.resolve()), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                   for p in [first_path, second_path] + [p for _, p in rows_and_paths] + transport_inputs if p.exists()],
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host_session", type=Path)
    parser.add_argument("client_session", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    result = audit(args.host_session, args.client_session, args.require_complete)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks": len(result["checks"]), "output": str(args.output)}, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
