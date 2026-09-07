"""Audit actual Shipping process exports; unavailable UE_LOG is never counted as zero errors."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
from pathlib import Path, PureWindowsPath

import audit_network_evidence as paired
import summarize_frame_evidence as frames
from audit_shipping_payload import payload_checks, catalog_checks, round_kind

ROOT = Path(__file__).resolve().parents[2]


def fingerprint(path):
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}


def physical_identity_checks(launches, sessions, provenance, provenance_hash):
    """Bind per-machine records without assuming PIDs are globally unique."""
    checks = []

    def check(name, passed, detail):
        checks.append({'check': name, 'status': 'PASS' if passed else 'FAIL', 'detail': detail})

    names = [str(row.get('hardware', {}).get('hostname', '')).strip().casefold() for row in launches]
    check('physical_distinct_recorded_hostnames', all(names) and len(set(names)) == 2, names)
    identities = [(name, session.get('process_id')) for name, session in zip(names, sessions)]
    check('physical_distinct_machine_processes', all(name and isinstance(pid, int) and pid > 0 for name, pid in identities)
          and len(set(identities)) == 2, identities)
    root = PureWindowsPath(provenance.get('package_root', ''))
    expected = {}
    invalid = []
    for row in provenance.get('files', []):
        if row.get('group') != 'packaged_payload':
            continue
        try:
            relative = PureWindowsPath(row['path']).relative_to(root).as_posix().casefold()
            if '..' in PureWindowsPath(relative).parts or relative in expected:
                raise ValueError('Duplicate or escaping path')
            expected[relative] = (row['sha256'], row['bytes'])
        except (ValueError, KeyError) as error:
            invalid.append(str(error))
    check('physical_successful_complete_provenance', bool(expected) and not invalid
          and provenance.get('configuration') == 'Shipping' and provenance.get('input_files_stable_during_capture') is True
          and provenance.get('package_report', {}).get('exit_code') == 0, {'files': len(expected), 'errors': invalid})
    address = launches[0].get('host_address')
    try:
        parsed = ipaddress.ip_address(address)
        private = parsed.version == 4 and any(parsed in ipaddress.ip_network(network) for network in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'))
    except ValueError:
        private = False
    check('physical_nonloopback_private_target', private and launches[1].get('host_address') == address
          and launches[0].get('port') == launches[1].get('port') and isinstance(launches[0].get('port'), int)
          and 1024 <= launches[0]['port'] <= 65535, {'address': address, 'ports': [row.get('port') for row in launches]})
    for index, (role, launch, session) in enumerate(zip(('host', 'client'), launches, sessions)):
        local = {row.get('IPAddress') for row in launch.get('local_ipv4', [])}
        check(role + '_physical_role_address', launch.get('role') == role and ((address in local) if index == 0 else (address not in local)), sorted(str(x) for x in local))
        arguments = launch.get('arguments', [])
        route_valid = ('-WCHost' in arguments and f'-Port={launch.get("port")}' in arguments and not any(value.startswith('-WCJoin') for value in arguments)) if index == 0 else (f'-WCJoin={address}:{launch.get("port")}' in arguments and '-WCHost' not in arguments)
        check(role + '_physical_route_arguments', route_valid, arguments)
        check(role + '_physical_session_process_binding', launch.get('process_id') == session.get('process_id')
              and launch.get('status') == 'EXITED_AUDIT_REQUIRED' and launch.get('exit_code') == 0,
              {'recorded_pid': launch.get('process_id'), 'session_pid': session.get('process_id'), 'status': launch.get('status'), 'exit': launch.get('exit_code')})
        check(role + '_physical_manifest_binding', launch.get('provenance_sha256') == provenance_hash
              and launch.get('catalog_digest') == provenance.get('catalog_digest'), launch.get('provenance_sha256'))
        for label, field in (('preflight', 'relocated_payload_verification'), ('post_run', 'post_run_relocated_payload_verification')):
            record = launch.get(field, {})
            entries = record.get('mapping', [])
            actual = {str(row.get('relative_path', '')).replace('\\', '/').casefold(): (row.get('expected_sha256'), row.get('expected_bytes')) for row in entries}
            payload = record.get('payload', {})
            files = {str(row.get('path', '')).replace('\\', '/').casefold(): (row.get('sha256'), row.get('bytes')) for row in payload.get('files', [])}
            mapped_files = {str(row.get('current_path', '')).replace('\\', '/').casefold(): (row.get('expected_sha256'), row.get('expected_bytes')) for row in entries}
            mapping_valid = PureWindowsPath(record.get('original_package_root', '')) == root and all(
                PureWindowsPath(row.get('original_path', '')) == root / row.get('relative_path', '')
                and PureWindowsPath(row.get('current_path', '')) == PureWindowsPath(record.get('current_package_root', '')) / row.get('relative_path', '') for row in entries)
            check(role + '_physical_' + label + '_all_payload_bytes_recorded', record.get('status') == 'PASS' and payload.get('status') == 'PASS'
                  and mapping_valid and bool(expected) and actual == expected and len(entries) == len(expected) and files == mapped_files
                  and len(files) == len(expected) and payload.get('file_count') == len(expected),
                  {'expected_count': len(expected), 'mapping_count': len(entries), 'hashed_count': len(files),
                   'boundary': 'Launcher-recorded local hashes bound to immutable provenance; reviewer does not assume access to either relocated machine path.'})
    uuids = [row.get('hardware', {}).get('smbios_uuid_sha256') for row in launches]
    check('physical_hardware_identity_not_known_duplicate', not all(uuids) or uuids[0] != uuids[1], uuids)
    listener = launches[0].get('listen_owner') or []
    check('physical_host_listener_binding', any(row.get('OwningProcess') == sessions[0].get('process_id') and row.get('LocalPort') == launches[0].get('port') for row in listener), listener)
    return checks


def audit_physical(base, provenance_path):
    """Read copied exports from two PCs; never synthesize a loopback trial file."""
    candidates = [sorted((base / role).glob(f'match-1-seat-{seat}-*-session.json')) for seat, role in enumerate(('host', 'client'))]
    if any(len(paths) != 1 for paths in candidates):
        return {'status': 'INCOMPLETE', 'reason': 'Expected exactly one first-match session in each host/client directory'}
    output = base / 'physical-audit'
    if output.exists():
        raise ValueError('Preserve the existing physical audit; use a fresh review directory')
    paths = [items[0] for items in candidates]
    launch_paths = [base / role / 'physical-launch.json' for role in ('host', 'client')]
    launches, sessions = [paired.load(path) for path in launch_paths], [paired.load(path) for path in paths]
    provenance = paired.load(provenance_path)
    identity = physical_identity_checks(launches, sessions, provenance, fingerprint(provenance_path)['sha256'])
    comparison = paired.audit(*paths, require_complete=True)
    # Keep the raw lower-level result. Only the new derived physical evaluation
    # substitutes machine+PID for the same-host PID rule; source exports are read-only.
    identity_valid = all(row['status'] == 'PASS' for row in identity)
    combined = [row for row in comparison['checks'] if row['check'] != 'distinct_processes']
    combined += identity + catalog_checks(list(zip(('host', 'client'), sessions)), provenance)
    if not identity_valid:
        combined.append({'check': 'physical_identity_required_for_composite_pid', 'status': 'FAIL', 'detail': 'Recorded physical identity, address and immutable payload bindings must all validate'})
    statuses = [row['status'] for row in combined]
    status = 'FAIL' if any(value in ('FAIL', 'FAILED') for value in statuses) else 'INCOMPLETE' if any(value != 'PASS' for value in statuses) else 'PASS'
    result = {'status': status, 'evidence_kind': 'PHYSICAL_LAN_RECORDED_RECEIVED_STATE_AND_RPC',
              'boundary': 'Functional audit of recorded two-machine identity, private LAN target, payload bindings, received states and real RPC replies. This does not independently observe two physical devices or certify manual play, graphics, audio or performance.',
              'physical_device_observation': 'NOT_RUN_BY_ANALYZER', 'physical_lan_release_acceptance': 'REQUIRES_OPERATOR_PHYSICAL_DEVICE_EVIDENCE_AND_RELEASE_REVIEW',
              'checks': combined, 'raw_same_host_paired_reader': comparison,
              'inputs': [fingerprint(path) for path in paths + launch_paths + [provenance_path]],
              'hardware': [row.get('hardware') for row in launches]}
    output.mkdir()
    (output / 'physical-network-analysis.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return {'status': status, 'checks': len(combined), 'output': str(output), 'physical_device_observation': 'NOT_RUN_BY_ANALYZER'}


def audit(base):
    trial = paired.load(base / "trial.json")
    candidates = [sorted((base / role).glob(f"match-1-seat-{seat}-*-session.json")) for seat, role in enumerate(("host", "client"))]
    if any(len(paths) != 1 for paths in candidates):
        return {"status": "INCOMPLETE", "reason": "Expected one retained match-1 session per launched host/client", "candidates": [[str(p) for p in paths] for paths in candidates]}
    paths = [items[0] for items in candidates]
    sessions = [paired.load(path) for path in paths]
    if not all(session.get("complete") for session in sessions):
        return {"status": "IN_PROGRESS", "sessions": [{key: s.get(key) for key in ("utc", "seat", "phase", "round", "complete", "aborted")} for s in sessions]}
    output = base / "audit"
    output.mkdir(exist_ok=True)
    comparison = paired.audit(*paths, require_complete=True)
    (output / "paired-state-audit.json").write_text(json.dumps(comparison, indent=2) + "\n", encoding="utf-8")
    results, inputs, additional = [], [], []
    provenance, payload = payload_checks(trial)
    additional.extend(payload)
    additional.extend(catalog_checks(list(zip(("host", "client"), sessions)), provenance))

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
        neutral_rounds = sorted({row["round"] for row in snapshots if row["phase"] == 1 and row["public"].get("neutralRound") is True})
        pvp_rounds = sorted({row["round"] for row in snapshots if row["phase"] == 1 and row["public"].get("neutralRound") is False})
        expected_neutrals = [number for number in range(1, session["round"] + 1) if number <= 3 or number % 5 == 0]
        check(role + "_neutral_schedule_observed", neutral_rounds == expected_neutrals and set(neutral_rounds) | set(pvp_rounds) == set(combat_rounds),
              {"actual_neutral_rounds": neutral_rounds, "actual_pvp_rounds": pvp_rounds, "expected_neutral_rounds": expected_neutrals})
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
        terminal_path = path.parent / "session.json"
        terminal = paired.load(terminal_path)
        result = {"role": role, **{key: session.get(key) for key in ("process_id", "seat", "network_mode", "authority_process", "match_namespace", "phase", "round", "complete", "aborted", "intent_requests", "actual_accepted_replies", "actual_rejected_replies", "simulation_speed_multiplier", "resolution_x", "resolution_y", "max_living_visible_units", "max_living_logical_units", "max_simultaneous_encounters", "observed_seat", "music_component_playing", "music_volume")},
                  "first_observed_utc": snapshots[0]["utc"], "first_results_utc": next(row["utc"] for row in snapshots if row["phase"] == 3),
                  "last_observed_utc": snapshots[-1]["utc"], "snapshot_count": len(snapshots), "combat_rounds": combat_rounds, "recap_rounds": recap_rounds,
                  "neutral_combat_rounds": neutral_rounds, "pvp_combat_rounds": pvp_rounds,
                  "stale_retained_recaps": stale, "actual_reply_reasons": dict(Counter(row["reason"] for row in replies)),
                  "probes": {probe["name"]: probe["status"] for probe in session["command_probes"]},
                  "public_payload": {key: session.get(key) for key in ("public_json_chars_current", "public_json_chars_max", "public_json_utf8_bytes_current", "public_json_utf8_bytes_max", "distinct_public_payload_samples")},
                  "projected_component_bounds": bound_summary,
                  "engine_log_transport_check": {"status": "NOT_RUN", "oversized_bunch_count": None, "error_log_count": None, "reason": "This Shipping binary does not emit UE_LOG files. Actual received-state coverage and payload sizes are audited separately; no absence-of-log pass is inferred."},
                  "final_standings": [{key: seat[key] for key in ("id", "name", "human", "health", "wins", "place")} for seat in public["seats"]],
                  "screenshot_count": len(screenshots), "skill_screenshot_requests": skill_requests,
                  "screenshot_boundary": "Actual files and runtime capture metadata only. Visual, animation, release-timing and human-audition acceptance require independent inspection.",
                  "terminal_process_snapshot": {key: terminal.get(key) for key in ("utc", "process_id", "match_namespace", "phase", "round", "complete", "aborted", "host_disconnected", "network_error", "network_error_detail")},
                  "terminal_snapshot_boundary": "The completed match namespace is audited above. The latest process snapshot can be a subsequent menu after the host's planned process exit; it does not overwrite the retained completed tournament.",
                  "profiling": frame_summary}
        results.append(result)
        inputs += [fingerprint(source) for source in [path, snapshot_path, commands_path, terminal_path] + skill_metadata]
    lifecycle_complete = trial.get("status") == "PROCESSES_EXITED_AUDIT_REQUIRED"
    lifecycle = []
    for process in trial["processes"]:
        lifecycle.append({key: process.get(key) for key in ("role", "bootstrap_pid", "inner_pid", "exit_observed", "exit_code", "inner_exit_observed", "inner_exit_code", "exit_observed_utc", "inner_exit_observed_utc")})
    if lifecycle_complete:
        check("both_planned_process_exits_observed", all(row["exit_observed"] for row in lifecycle), lifecycle)
        check("bootstrap_exit_codes_zero", all(row["exit_code"] == 0 for row in lifecycle), lifecycle)
    else:
        check("planned_process_lifecycle_finished", False, trial.get("status"))
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
                         "Lifecycle records distinguish bootstrap and inner process observations. An unavailable inner exit code remains unknown; bootstrap success does not replace it.",
                         "Accepted replies include an intentional idempotent duplicate; they are not a count of distinct mutations.",
                         "Projected skeletal component bounds are conservative geometry, not proof of lack of pixel occlusion or satisfactory hero art.",
                         "Native engine log error and oversized-bunch counts are unavailable for Shipping and remain null/NOT_RUN.",
                         "Prior package evidence is retained separately and does not certify this payload."]}
    (output / "network-analysis.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Actual routed Shipping two-process network check", "", f"Functional received-state/RPC audit: **{final_status}**. Process lifecycle complete: **{lifecycle_complete}**.", "", result["boundary"], "",
             f"The paired reader completed {len(comparison['checks'])} checks with status {comparison['status']}. Listener ownership and the entire packaged payload have separate checks in network-analysis.json.", ""]
    for session in results:
        lines += [f"- {session['role']}: PID{session['process_id']}, seat{session['seat']}, network mode{session['network_mode']}; completed round{session['round']}. All combat rounds observed: {session['combat_rounds']}.",
                  f"- {session['role']}: {session['actual_accepted_replies']} accepted / {session['actual_rejected_replies']} rejected actual replies; probes {session['probes']}.",
                  f"- {session['role']}: maximum actual public JSON {session['public_payload']['public_json_chars_max']} characters / {session['public_payload']['public_json_utf8_bytes_max']} UTF8 bytes; {len(session['stale_retained_recaps'])} stale retained recaps."]
        terminal = session["terminal_process_snapshot"]
        if terminal["match_namespace"] != session["match_namespace"]:
            lines.append(f"- {session['role']}: latest process snapshot subsequently returned to namespace{terminal['match_namespace']} / phase{terminal['phase']}, aborted={terminal['aborted']}, after the host's planned exit. Completed round{session['round']} results remain retained in the audited match namespace. The current error message is recorded exactly in network-analysis.json.")
    lines += ["", "Both engine log oversized-bunch/error counts are **NOT_RUN**, not zero. Shipping provides received-state, real-RPC, frame and screenshot evidence through the game's explicit verification writer.", "", str(result["profiling_confounders"]),
              "The optional concurrency.json inventory records any additional actual concurrent functional processes, including a root-owned restart run when present.", "", "## Limits", ""]
    lines += ["- " + value for value in result["limits"]]
    (output / "analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"status": final_status, "lifecycle_complete": lifecycle_complete, "paired_checks": len(comparison["checks"]), "additional_checks": len(additional),
            "sessions": [{key: session[key] for key in ("role", "process_id", "round", "combat_rounds", "public_payload")} for session in results]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence_directory", type=Path)
    parser.add_argument('--physical', action='store_true', help='Read host/client physical-launch.json instead of a loopback trial')
    parser.add_argument('--provenance', type=Path, help='Unchanged provenance JSON available on this review machine; required with --physical')
    args = parser.parse_args()
    if args.physical and not args.provenance:
        parser.error('--physical requires --provenance')
    result = audit_physical(args.evidence_directory.resolve(), args.provenance.resolve()) if args.physical else audit(args.evidence_directory.resolve())
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 2 if result["status"] == "IN_PROGRESS" else 1)
