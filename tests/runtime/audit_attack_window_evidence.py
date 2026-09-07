"""Audit observed Unreal Attack-window telemetry; partial capture never certifies a release."""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
MAX_JSON_INTEGER = 9007199254740991
STAMP = re.compile(r"\[(\d{4}\.\d\d\.\d\d-\d\d\.\d\d\.\d\d:\d{3})\]")
FIELDS = ("unit hero action ordinal window snapshot release_tick elapsed position start release end reconstructed").split()
INTEGER_FIELDS = set("unit action ordinal window snapshot release_tick reconstructed".split())


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def utc(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Evidence timestamp must carry a UTC offset")
    return result.astimezone(timezone.utc)


def fingerprint(path):
    path = Path(path).resolve(strict=True)
    before = path.stat()
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError(f"Evidence changed during hashing: {path}")
    return {"path": str(path), "bytes": after.st_size, "sha256": digest.hexdigest()}


def safe_integer(value, minimum=0):
    return (not isinstance(value, bool) and isinstance(value, (int, float))
            and math.isfinite(value) and minimum <= value <= MAX_JSON_INTEGER and int(value) == value)


def parse_log(text):
    records, errors, catalog = [], [], []
    for number, line in enumerate(text.splitlines(), 1):
        if "WC_CATALOG_LOADED" in line:
            found = re.search(r"digest=([0-9a-f]{64})", line)
            if found:
                catalog.append(found[1])
        if "WC_ATTACK_WINDOWS_INVALID" in line:
            errors.append({"line": number, "reason": "Runtime rejected Attack markers", "text": line})
        if "WC_ATTACK_WINDOW " not in line:
            continue
        try:
            stamp = STAMP.search(line)
            if not stamp:
                raise ValueError("Unreal UTC log timestamp is missing")
            fields = line.split("WC_ATTACK_WINDOW ", 1)[1].split()
            pairs = [part.split("=", 1) for part in fields]
            if any(len(pair) != 2 for pair in pairs) or [pair[0] for pair in pairs] != FIELDS:
                raise ValueError("Unexpected, duplicate or missing telemetry field")
            item = dict(pairs)
            for key in FIELDS:
                if key != "hero":
                    item[key] = int(item[key]) if key in INTEGER_FIELDS else float(item[key])
                    if not math.isfinite(item[key]):
                        raise ValueError("Nonfinite telemetry number")
            if any(not safe_integer(item[key]) for key in INTEGER_FIELDS):
                raise ValueError("Invalid integral identity/tick")
            if not item["unit"] or not item["action"] or not item["ordinal"]:
                raise ValueError("Attack identity cannot be zero")
            if item["window"] not in (0, 1) or item["reconstructed"] not in (0, 1):
                raise ValueError("Invalid window or reconstruction flag")
            item.update(line=number, utc=datetime.strptime(stamp[1], "%Y.%m.%d-%H.%M.%S:%f").replace(tzinfo=timezone.utc).isoformat())
            records.append(item)
        except (ValueError, OverflowError) as error:
            errors.append({"line": number, "reason": str(error)})
    return records, errors, catalog


def analyze(records, snapshots, units, rules, expected_digest, process_id, max_snapshot_gap=1.1):
    """Pure consistency reader. Callers separately bind immutable inputs and actual launch."""
    checks, observations = [], []
    def check(name, passed, detail):
        checks.append({"check": name, "status": "PASS" if passed else "FAIL", "detail": detail})
    hero_by_id = {unit["id"]: unit for unit in units["units"]}
    ordered = rules["alpha_unit_ids"]
    tick_ms = rules["simulation"]["tick_ms"]
    by_identity = defaultdict(list)
    context_rows = defaultdict(list)
    event_index, visual_index = defaultdict(dict), defaultdict(list)
    for index, row in enumerate(snapshots):
        public = row["public"]
        check(f"snapshot_{index}_binding", row.get("process_id") == process_id
              and row.get("match_namespace") == public.get("matchNamespace")
              and public.get("contentDigest") == expected_digest
              and public.get("protocolVersion") == rules["network"]["protocol_version"]
              and public.get("schemaVersion") == rules["schema_version"],
              {"pid": row.get("process_id"), "namespace": row.get("match_namespace"), "utc": row["utc"]})
        context = (public["matchNamespace"], public.get("round", 0))
        context_rows[context].append(row)
        for encounter in public.get("encounters", []):
            for unit in encounter.get("units", []):
                ordinal = unit.get("basicAttackOrdinal")
                if not safe_integer(ordinal):
                    check(f"snapshot_{index}_ordinal_{unit.get('id')}", False, ordinal)
                    continue
                key = (unit["id"], unit["action"], ordinal)
                by_identity[key].append((row, encounter, unit))
            for action in encounter.get("visualActions", []):
                if action.get("basicAttack"):
                    visual_index[context + (action["source"], action["action"])].append(action)
            for event in encounter.get("events", []):
                if not event.get("basicAttack"):
                    continue
                key = context + (event["source"], event["action"])
                identity = (event["tick"], event["target"], event["effect"])
                prior = event_index[key].get(identity)
                if prior and prior != event:
                    check("repeated_event_payload_stable", False, {"action": key, "prior": prior, "current": event})
                event_index[key][identity] = event
    grouped, windows = defaultdict(list), defaultdict(dict)
    unmatched, skipped = [], []
    for record in records:
        label = f"log_line_{record['line']}"
        hero = hero_by_id.get(record["hero"])
        check(label + "_known_hero", hero is not None, record["hero"])
        if not hero:
            continue
        check(label + "_ordinal_parity", record["window"] == (record["ordinal"] - 1) % 2,
              {"ordinal": record["ordinal"], "window": record["window"]})
        windup = hero["stats"]["attack_windup_ms"] / 1000
        check(label + "_canonical_window", 0 <= record["start"] < record["release"] < record["end"]
              and abs(record["release"] - record["start"] - windup) <= 0.0001
              and (record["window"] != 0 or abs(record["start"]) <= 0.0001), record)
        position = record["start"] + min(max(record["elapsed"], 0), record["end"] - record["start"])
        check(label + "_bounded_position", record["elapsed"] >= 0 and record["start"] - 0.0001 <= record["position"] <= record["end"] + 0.0001
              and abs(record["position"] - position) <= 0.0001, {"expected": position, "actual": record["position"]})
        authoritative = max(0, record["snapshot"] - record["release_tick"] + math.ceil(windup * 1000 / tick_ms)) * tick_ms / 1000
        check(label + "_snapshot_clock", authoritative - 0.0001 <= record["elapsed"] <= authoritative + tick_ms / 1000 + 0.0001,
              {"authoritative": authoritative, "elapsed": record["elapsed"]})
        landmarks = tuple(record[key] for key in ("start", "release", "end"))
        prior = windows[record["hero"]].get(record["window"])
        check(label + "_stable_landmarks", prior is None or prior == landmarks, landmarks)
        windows[record["hero"]][record["window"]] = landmarks
        candidates = by_identity[(record["unit"], record["action"], record["ordinal"])]
        candidates = [entry for entry in candidates if abs((utc(entry[0]["utc"]) - utc(record["utc"])).total_seconds()) <= max_snapshot_gap]
        if not candidates:
            unmatched.append(record)
            continue
        # Exact tick is preferred, otherwise nearest persisted same-action snapshot; never interpolate a state.
        candidates.sort(key=lambda entry: (entry[2]["snapshotTick"] != record["snapshot"], abs((utc(entry[0]["utc"]) - utc(record["utc"])).total_seconds())))
        row, encounter, unit = candidates[0]
        context = (row["public"]["matchNamespace"], row["public"]["round"])
        check(label + "_snapshot_identity", not unit.get("neutral") and 0 <= unit["def"] < len(ordered)
              and ordered[unit["def"]] == record["hero"] and unit["releaseTick"] == record["release_tick"], unit)
        key = context + (record["unit"], record["action"])
        grouped[key].append((record, candidates))
        observations.append({"line": record["line"], "context": list(context), "unit": record["unit"], "action": record["action"],
                             "snapshot_utc": row["utc"], "snapshot_tick_exact": unit["snapshotTick"] == record["snapshot"],
                             "snapshot_state": unit["state"], "observed_seat": row["observed_seat"],
                             "time_gap_seconds": abs((utc(row["utc"]) - utc(record["utc"])).total_seconds())})
    for hero, data in windows.items():
        if 0 in data and 1 in data:
            check(hero + "_contiguous_observed_windows", abs(data[0][2] - data[1][0]) <= .0001, data)
    coverage = {}
    def cover(name, count, boundary):
        coverage[name] = {"status": "OBSERVED" if count else "NOT_RUN", "count": count, "boundary": boundary}
    recovery, packets, commits, release_samples, interrupted, defeated, scout_returns = 0, 0, 0, 0, 0, 0, 0
    no_packet, no_commit = [], []
    per_unit = defaultdict(list)
    for key, entries in grouped.items():
        logs = [entry[0] for entry in entries]
        action_ordinals = {(record["ordinal"], record["window"], record["release_tick"]) for record in logs}
        check("one_action_one_window", len(action_ordinals) == 1, {"action": key, "identities": sorted(action_ordinals)})
        all_candidates = [candidate for _, candidates in entries for candidate in candidates]
        states = {candidate[2]["state"] for candidate in all_candidates}
        recovery += int({3, 4}.issubset(states))
        interrupted += int(7 in states)
        defeated += int(8 in states)
        record = logs[0]
        per_unit[key[:3]].append((utc(record["utc"]), record["ordinal"], record["action"]))
        release_samples += sum(abs(item["position"] - item["release"]) <= .0001 for item in logs)
        actions = visual_index.get(key, [])
        if actions:
            commits += 1
            check("observed_visual_commit_matches_release", all(item["releaseTick"] == record["release_tick"] for item in actions), {"action": key})
        else:
            no_commit.append(list(key))
        events = list(event_index.get(key, {}).values())
        if events:
            packets += 1
            expected_tick = record["release_tick"] + math.ceil(hero_by_id[record["hero"]]["stats"]["projectile_travel_ms"] / tick_ms)
            check("observed_basic_action_one_damage_packet", len(events) == 1 and all(event["tick"] == expected_tick for event in events),
                  {"action": key, "expected_tick": expected_tick, "observed_events": events})
        else:
            no_packet.append(list(key))
        if len(logs) > 1 and any(log["reconstructed"] for log in logs[1:]):
            first, last = min(utc(log["utc"]) for log in logs), max(utc(log["utc"]) for log in logs)
            seats = [row["observed_seat"] for row in context_rows[key[:2]] if first <= utc(row["utc"]) <= last]
            scout_returns += int(len(set(seats)) > 1)
    for key, entries in per_unit.items():
        entries.sort()
        for earlier, later in zip(entries, entries[1:]):
            check("observed_ordinal_increases_for_new_basic", later[1] > earlier[1], {"unit_context": key, "before": earlier[1:], "after": later[1:]})
            if later[1] > earlier[1] + 1:
                skipped.append({"unit_context": key, "before": earlier[1], "after": later[1], "unobserved_basic_actions": later[1] - earlier[1] - 1})
    cover("telemetry_rows", len(records), "Only new presentation/release-crossing samples are logged; this is not continuous pose review.")
    cover("contemporaneous_snapshot_matches", len(observations), f"Same unit/action/ordinal within {max_snapshot_gap}s; exact-tick matches are separately labeled.")
    cover("distinct_bound_basic_actions", len(grouped), "Only actions with contemporaneous public snapshots.")
    cover("both_windows", sum(len(value) == 2 for value in windows.values()), "Count of heroes with both logged windows, not every attack or every hero.")
    cover("windup_and_recovery_same_action", recovery, "Both states actually persisted for the same action; missing windup is not inferred.")
    cover("exact_release_position_samples", release_samples, "Exact sampled marker position only; logs can cross a release after its exact frame.")
    cover("visual_commit_links", commits, "Observed public visualActions only; provisional intent is not a delivered hit.")
    cover("basic_damage_packet_links", packets, "Observed deduplicated basic events only; missing events do not imply canceled, blocked or defeated attacks.")
    cover("stunned_same_action", interrupted, "State observation only; does not establish cancellation semantics.")
    cover("defeated_same_action", defeated, "State observation only; does not establish whether a released projectile persisted.")
    cover("scouting_reconstruction_same_action", scout_returns, "Requires reconstruction, same action and persisted observed-seat change; a new-round reconstruction is insufficient.")
    cover("continuous_visual_review", 0, "No images or movies are reviewed by this telemetry reader.")
    cover("full_168_clip_or_packaged_lan_acceptance", 0, "Outside this narrow evidence audit.")
    return {"checks": checks, "coverage": coverage, "observations": observations, "unmatched_telemetry": unmatched,
            "skipped_action_gaps": skipped, "actions_without_observed_packet": no_packet, "actions_without_observed_visual_commit": no_commit}


def audit(launch_path, log_path, snapshot_paths, binding_path, units_path, rules_path, catalog_path, root=ROOT):
    paths = [Path(path).resolve(strict=True) for path in [launch_path, log_path, binding_path, units_path, rules_path, catalog_path, *snapshot_paths]]
    if len(paths) != len(set(paths)) or any(not path.is_relative_to(root.resolve()) for path in paths):
        raise ValueError("Inputs must be distinct existing files inside the workspace")
    launch, binding, units, rules, catalog = map(load, [launch_path, binding_path, units_path, rules_path, catalog_path])
    checks, inputs = [], [fingerprint(path) for path in paths]
    def check(name, passed, detail):
        checks.append({"check": name, "status": "PASS" if passed else "FAIL", "detail": detail})
    started, ended = utc(launch["started_utc"]), utc(launch["ended_utc"])
    pid = launch.get("process_id", launch.get("pid"))
    check("actual_closed_launch", safe_integer(pid, 1) and launch.get("exit_code") == 0 and started < ended, {"pid": pid, "exit": launch.get("exit_code")})
    check("prelaunch_binding_identity", fingerprint(binding_path)["sha256"] == launch.get("payload_binding_sha256")
          and utc(binding["captured_utc"]) <= started, str(binding_path))
    bound = {}
    for row in binding["files"]:
        path = Path(row["path"]).resolve(strict=True)
        if not path.is_relative_to(root.resolve()) or path in bound:
            raise ValueError("Payload manifest contains outside-workspace or duplicate files")
        actual = fingerprint(path)
        check("bound_file_bytes", actual["sha256"] == row["sha256"] and actual["bytes"] == row["bytes"], actual)
        inputs.append(actual)
        bound[path] = row
    module = Path(launch["module_path"]).resolve(strict=True)
    check("launch_module_binding", module in bound and bound[module]["group"] == "module"
          and fingerprint(module)["sha256"] == launch.get("module_sha256"), str(module))
    required = [Path(path).resolve() for path in (units_path, rules_path, catalog_path)]
    check("captured_data_files_bound", all(path in bound for path in required), list(map(str, required)))
    payload = [row for row in bound.values() if row.get("group") == "runtime_payload"]
    check("declared_runtime_payload_bound", bool(payload), {"count": len(payload), "scope": binding.get("payload_scope")})
    digest = catalog["combined_sha256"]
    combined = hashlib.sha256(json.dumps(catalog["source_sha256"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    # compile_catalog's combined digest uses sorted name/hash lines, checked below from its exact contract.
    check("catalog_and_binding_digest", binding.get("catalog_digest") == digest
          and catalog["source_sha256"]["data/units.json"] == fingerprint(units_path)["sha256"]
          and catalog["source_sha256"]["data/rules.alpha.json"] == fingerprint(rules_path)["sha256"], digest)
    args = [str(value).strip('"').lower() for value in launch["arguments"]]
    check("rendered_normal_speed_window_audit_flags", "-wcwindowaudit" in args and "-wcexercise" in args
          and "-wcfast=1" in args and "-nullrhi" not in args and "-wcreviewmotion" not in args
          and not any(value.startswith(("-usefixedtimestep", "-fps=")) for value in args), args)
    records, errors, loaded = parse_log(Path(log_path).read_text(encoding="utf-8-sig"))
    check("telemetry_log_format", not errors, errors)
    check("runtime_catalog_digest", bool(loaded) and all(item == digest for item in loaded), loaded)
    snapshots = []
    for path in snapshot_paths:
        for number, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
            if line.strip():
                try:
                    snapshots.append(json.loads(line))
                except json.JSONDecodeError as error:
                    raise ValueError(f"Malformed snapshot {path}:{number}") from error
    check("snapshot_capture_exists", bool(snapshots), len(snapshots))
    check("contemporaneous_launch_interval", all(started <= utc(row["utc"]) <= ended for row in snapshots + records), {"start": started.isoformat(), "end": ended.isoformat()})
    report = analyze(records, snapshots, units, rules, digest, pid)
    report["checks"] = checks + report["checks"]
    failed = [item for item in report["checks"] if item["status"] == "FAIL"]
    report.update(status="FAIL" if failed else "OBSERVED_PARTIAL" if report["observations"] else "NOT_RUN",
                  audit_version=1, created_utc=datetime.now(timezone.utc).isoformat(), failed_checks=len(failed),
                  inputs=list({row["path"]: row for row in inputs}.values()),
                  payload_scope=binding.get("payload_scope", "declared files only"),
                  boundary="Hash-bound launch telemetry and sampled public state only. Declared Editor asset payload does not certify package completeness, geometry, visual timing, audio, human play or LAN.")
    # Detect inputs changing while the reader was working, including launch/snapshot/log files.
    for row in report["inputs"]:
        if fingerprint(row["path"]) != row:
            raise ValueError("Input changed during audit: " + row["path"])
    return report


def save(report, directory, root=ROOT):
    directory = Path(directory).resolve()
    if not directory.is_relative_to(root.resolve() / "reports") or directory == root.resolve() / "reports":
        raise ValueError("Output must be a fresh child directory inside workspace reports")
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "attack-window-audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["# Attack-window evidence", "", f"Status: {report['status']}", "", report["boundary"], "", "Observed coverage:", ""]
    lines += [f"- {name}: {item['status']} ({item['count']}). {item['boundary']}" for name, item in report["coverage"].items()]
    lines += ["", f"Failed checks: {report['failed_checks']}. See JSON for every input hash, sample match and omitted action."]
    (directory / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("launch", "log", "binding", "units", "rules", "catalog", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--snapshots", type=Path, nargs="+", required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output exists; prior evidence must be preserved")
    try:
        report = audit(args.launch, args.log, args.snapshots, args.binding, args.units, args.rules, args.catalog)
        save(report, args.output)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, str(error) + "\n")
    print(json.dumps({"status": report["status"], "failed_checks": report["failed_checks"], "output": str(args.output.resolve())}))
    raise SystemExit(1 if report["status"] == "FAIL" else 0 if report["status"] == "OBSERVED_PARTIAL" else 2)


if __name__ == "__main__":
    main()
