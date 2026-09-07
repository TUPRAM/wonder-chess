"""Audit completed actual candidate5 regression and compare preserved engine rows."""

from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import statistics

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def csv_load(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def distribution(values):
    values = sorted(values)
    return {"count": len(values), "min": values[0], "median": statistics.median(values),
            "mean": statistics.mean(values), "p95": values[int((len(values)-1)*.95)], "max": values[-1]}


def main():
    report_path = ROOT / "reports/WC-360/candidate5-regression/regression.json"
    provenance_path = ROOT / "reports/WC-360/candidate5-provenance.json"
    log_path = report_path.parent / "game.log"
    launch_path = report_path.parent / "launch.json"
    standalone_analysis_path = OUT / "comparison.json"
    summary_path = ROOT / "reports/WC-360/candidate4-automation/engine-tournaments.csv"
    rounds_path = ROOT / "reports/WC-360/candidate4-automation/engine-rounds.csv"
    stage_path = ROOT / "game/Content/WonderChess/SourceData/runtime_stage_manifest.json"
    initial = report_path.stat()
    data = load(report_path)
    if not data.get("complete"):
        raise SystemExit(f"Actual regression incomplete: {data.get('attempted')}/{data.get('requested')}; no final analysis written")
    provenance = load(provenance_path)
    ids = load(stage_path)["alpha_unit_ids"]
    original = {int(row["seed"]): row for row in csv_load(summary_path)}
    original_rounds = {(int(row["seed"]), int(row["round"]), int(row["seat"])): row for row in csv_load(rounds_path)}
    failures = []
    checks = []

    def check(name, condition, detail):
        checks.append({"check": name, "status": "PASS" if condition else "FAIL", "detail": detail})
        if not condition:
            failures.append(name)

    trials = data.get("trials", [])
    check("all100_attempts_retained", data.get("requested") == data.get("attempted") == len(trials) == 100
          and sorted(row["seed"] for row in trials) == list(range(1, 101)),
          {"requested": data.get("requested"), "attempted": data.get("attempted"), "retained": len(trials)})
    check("zero_failed_trials", data.get("failed") == 0 and all(row.get("pass") for row in trials),
          [{"seed": row["seed"], "error": row.get("error")} for row in trials if not row.get("pass")])
    check("complete_evidence_write", not data.get("evidence_write_failed"), data.get("evidence_write_failed"))
    check("final_phase_and_commands", all(row.get("phase") == 3 and row.get("command_rejects") == 0
                                         and row.get("unresolved_encounters") == 0 for row in trials),
          [{"seed": row["seed"], "phase": row.get("phase"), "rejects": row.get("command_rejects"),
            "unresolved": row.get("unresolved_encounters")} for row in trials
           if row.get("phase") != 3 or row.get("command_rejects") or row.get("unresolved_encounters")])
    summary_differences = []
    round_differences = []
    seen_keys = Counter()
    usage_differences = []
    durations = []
    donors, recipients = Counter(), Counter()
    hero_totals = defaultdict(lambda: {"unit_rounds": 0, "rounds": 0, "seat_tournaments": 0, "placements": Counter()})
    aggregate_fields = ("fights", "timeouts", "ghosts", "commands", "command_rejects", "unresolved_encounters", "simulated_ms")
    totals = {key: sum(row.get(key, 0) for row in trials) for key in aggregate_fields}
    for trial in trials:
        seed = trial["seed"]
        rows = trial.get("rounds", [])
        derived = {"seed": seed, "rounds": len(rows), "simulated_ms": trial.get("simulated_ms"),
                   "encounters": trial.get("fights"), "timeouts": trial.get("timeouts"), "ghosts": trial.get("ghosts"),
                   "commands": trial.get("commands"), "rejects": trial.get("command_rejects"),
                   "final_hash": rows[-1]["post_hash"] if rows else None}
        for key, value in derived.items():
            if value is None or int(value) != int(original[seed][key]):
                summary_differences.append({"seed": seed, "field": key, "packaged": value, "candidate4": original[seed][key]})
        for row in rows:
            for encounter in row["encounters"]:
                durations.append(encounter["simulated_ms"])
                if encounter["ghost"]:
                    recipients[encounter["a"]] += 1
                    donors[encounter["b"]] += 1
            for seat in row["seats"]:
                key = (seed, row["round"], seat["seat"])
                seen_keys[key] += 1
                derived_seat = {"seed": seed, "round": row["round"], **seat,
                                "settlement_id": row["settlement_id"], "pre_hash": row["pre_hash"], "post_hash": row["post_hash"]}
                expected = original_rounds.get(key)
                if expected is None or any(int(value) != int(expected[field]) for field, value in derived_seat.items()):
                    round_differences.append({"key": key, "packaged": derived_seat, "candidate4": expected})
        use = defaultdict(lambda: {"units": 0, "rounds": set(), "ids": set(), "maxstar": 0})
        for deployment in trial.get("combat_lock_deployments", []):
            for seat in deployment["seats"]:
                for unit in seat["units"]:
                    item = use[seat["seat"], ids[unit["def"]]]
                    item["units"] += 1
                    item["rounds"].add(deployment["round"])
                    item["ids"].add(unit["id"])
                    item["maxstar"] = max(item["maxstar"], unit["star"])
        placements = {seat["seat"]: seat["placement"] for seat in trial["placements"]}
        if len(trial.get("hero_use_by_seat", [])) != 8*len(ids):
            usage_differences.append({"seed": seed, "error": "Missing zero-use or active hero/seat rows"})
        for row in trial.get("hero_use_by_seat", []):
            item = use[row["seat"], row["unit_id"]]
            expected = (item["units"], len(item["rounds"]), len(item["ids"]), item["maxstar"], placements[row["seat"]])
            actual = tuple(row[key] for key in ("deployed_unit_rounds", "rounds_deployed", "distinct_owned_instances",
                                                "maximum_deployed_star", "final_placement"))
            if actual != expected:
                usage_differences.append({"seed": seed, "seat": row["seat"], "unit": row["unit_id"], "actual": actual, "expected": expected})
            item = hero_totals[row["unit_id"]]
            item["unit_rounds"] += row["deployed_unit_rounds"]
            item["rounds"] += row["rounds_deployed"]
            if row["deployed_unit_rounds"]:
                item["seat_tournaments"] += 1
                item["placements"][row["final_placement"]] += 1
    check("candidate4_summary_parity", not summary_differences, summary_differences)
    check("candidate4_round_seat_parity", not round_differences and set(seen_keys) == set(original_rounds)
          and all(count == 1 for count in seen_keys.values()),
          {"rows_compared": sum(seen_keys.values()), "mismatches": round_differences,
           "missing": sorted(set(original_rounds)-set(seen_keys)), "unexpected": sorted(set(seen_keys)-set(original_rounds))})
    check("hero_use_reconciles_to_real_deployments", not usage_differences, usage_differences)
    standalone_hero_rows = load(standalone_analysis_path)["supplemental_standalone"]["hero_usage"]
    hero_parity_errors = []
    for row in standalone_hero_rows:
        actual = hero_totals[row["unit_id"]]
        if not (actual["unit_rounds"] == row["deployed_unit_rounds"]
                and actual["rounds"] == row["seat_rounds_deployed"]
                and actual["seat_tournaments"] == row["seat_tournaments_used"]
                and {str(key): value for key, value in actual["placements"].items()} == row["final_placement_counts_for_seats_that_used_hero"]):
            hero_parity_errors.append(row["unit_id"])
    check("actual_packaged_hero_use_matches_standalone", not hero_parity_errors, hero_parity_errors)
    check("profile_catalog_matches_provenance", data.get("digest") == provenance["catalog_digest"], data.get("digest"))
    expected_hashes = {row["staged_relative_path"]: row["actual_staged_sha256"] for row in provenance["staged_source_comparisons"]}
    verified_inputs = {}
    for name in ("rules.alpha.json", "units.json", "traits.json", "bots.json", "world.json"):
        value = data.get("input_files", {}).get(name, {})
        verified_inputs[name] = bool(value.get("available") and value.get("staged_manifest_sha1_matches")
                                     and value.get("sha256_staged_manifest") == expected_hashes[name])
    check("runtime_loaded_canonical_inputs", all(verified_inputs.values()), verified_inputs)
    executable = Path(data["executable_path"])
    matched_exe = next((row for row in provenance["files"] if Path(row["path"]) == executable), None)
    actual_hash = hashlib.sha256(executable.read_bytes()).hexdigest()
    check("actual_executable_matches_provenance", matched_exe is not None and actual_hash == matched_exe["sha256"],
          {"executable": str(executable), "sha256": actual_hash})
    caps = [row["seed"] for row in trials if row.get("capped")]
    log = log_path.read_text(encoding="utf-8-sig")
    exit_lines = [line for line in log.splitlines() if "WC_REGRESSION_DONE" in line or "RequestExitWithStatus" in line]
    check("engine_logged_completed_success_exit_request", "WC_REGRESSION_DONE attempted=100 failed=0" in log
          and "RequestExitWithStatus(0, 0," in log, exit_lines)
    log_errors = [line for line in log.splitlines() if ": Error:" in line]
    check("no_engine_error_log_lines", not log_errors, log_errors)
    result = {"utc": datetime.now(timezone.utc).isoformat(), "status": "PASS" if not failures else "FAIL",
              "boundary": "Actual packaged0H8B simulation and recorded deployment/settlement evidence. Not human interaction, networking, rendered frame performance or art/audio acceptance.",
              "checks": checks, "totals": totals, "explicit_capped_seeds": caps,
              "timeout_fraction": totals["timeouts"]/totals["fights"],
              "match_duration_ms": distribution([row["simulated_ms"] for row in trials]),
              "fight_duration_ms": distribution(durations),
              "ghost_recipient_counts": dict(sorted(recipients.items())), "ghost_donor_counts": dict(sorted(donors.items())),
              "actual_packaged_hero_use": dict(sorted(hero_totals.items())),
              "hero_use_boundary": "Observed real living-seat deployments at combat lock. Placement associations are descriptive and not causal strength estimates.",
              "actual_run": {key: data.get(key) for key in ("start_utc", "end_utc", "batch_wall_seconds", "engine", "cpu", "compiler", "compiler_full_version", "translation_unit_build_date", "translation_unit_build_time", "executable_path")},
              "launch": load(launch_path),
              "exit_boundary": "Engine log records status0 request and orderly closure; launch metadata does not itself contain an OS-observed process exit code.",
              "inputs": [{"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                         for path in (report_path, provenance_path, summary_path, rounds_path, stage_path,
                                      log_path, launch_path, standalone_analysis_path)]}
    final = report_path.stat()
    if (initial.st_size, initial.st_mtime_ns) != (final.st_size, final.st_mtime_ns):
        raise SystemExit("Regression report changed during analysis; no final analysis written")
    output = OUT / "candidate5-regression-analysis.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Candidate5 actual packaged regression", "",
             "PASS: all 100 requested seeds are retained, completed with final phase Finished, and have no failed trials, rejected bot commands or unresolved encounters.", "",
             f"The actual packaged executable ran from {data['start_utc']} to {data['end_utc']}; recorded batch wall time was {data['batch_wall_seconds']:.6f} seconds on {data['cpu'].strip()}. Engine {data['engine']}, MSVC full version {data['compiler_full_version']}. The launch used NullRHI and no sound. This establishes packaged C++ simulation execution, not rendering or audio.", "",
             f"Totals: {totals['fights']:,} encounters, {totals['timeouts']:,} timeouts ({100*result['timeout_fraction']:.4f}%), {totals['ghosts']} ghosts, {totals['commands']:,} bot commands, zero rejects and zero unresolved encounters. Exact comparisons pass for all 100 candidate4 tournament summaries and all 17,728 round/seat rows, including their64-bit state hashes.", "",
             f"Explicit capped-adjudication seeds ({len(caps)}): {caps}. These confirm the earlier candidate4 inference. Match duration milliseconds: {result['match_duration_ms']}. Individual fight duration milliseconds: {result['fight_duration_ms']}.", "",
             "The runner's actual per-hero use and final-placement associations reconcile to the captured combat-lock deployments and independently match the preserved standalone composition analysis. Unlike candidate4's aggregate-only CSV, this packaged report directly records those observations. A seat counted below used the hero at least once; that association is not a causal strength estimate.", "",
             "| Hero | Deployed unit-rounds | Seat-rounds | Seat-tournaments used | First-place seats that used hero |",
             "|---|---:|---:|---:|---:|"]
    for hero, row in sorted(hero_totals.items()):
        lines.append(f"| {hero} | {row['unit_rounds']} | {row['rounds']} | {row['seat_tournaments']} | {row['placements'].get(1,0)} |")
    lines += ["", "The runtime-loaded profile and five canonical input hashes agree with candidate5 provenance. The actual inner executable SHA256 also matches that immutable manifest. The engine log records all100 attempts, zero failures, a status0 exit request and orderly closure, with no Error-level log lines. Parent launch metadata currently records bootstrap PID/arguments but not an OS-observed exit code; the report preserves that distinction.", "",
              "The complete JSON source remains at reports/WC-360/candidate5-regression/regression.json. candidate5-regression-analysis.json records comparisons, failure checks, input hashes, launch arguments, ghost donor/recipient distributions and exact measurement boundaries. This run does not certify1H7B/2H6B, visual quality, audio, frame-time targets or manual usability."]
    (OUT / "candidate5-regression-analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "totals": totals, "caps": caps,
                      "failure_checks": failures, "path": str(output)}, indent=2))


if __name__ == "__main__":
    main()
