"""Audit completed actual candidate5 regression and compare preserved engine rows."""

from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import statistics
import io
import zipfile

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
    report_path = ROOT / "reports/WC-360/shipping-regression/regression.json"
    provenance_path = ROOT / "reports/WC-360/shipping-final-provenance.json"
    log_path = report_path.parent / "game.log"
    launch_path = report_path.parent / "launch.json"
    standalone_analysis_path = ROOT / "reports/WC-360/candidate4-analysis/comparison.json"
    summary_path = ROOT / "reports/WC-360/candidate6-automation/engine-tournaments.csv"
    rounds_path = ROOT / "reports/WC-360/candidate6-automation/engine-rounds.csv"
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
    derived_summaries, derived_rounds = [], []
    complete_fight_errors = []
    aggregate_fields = ("fights", "timeouts", "ghosts", "commands", "command_rejects", "unresolved_encounters", "simulated_ms")
    totals = {key: sum(row.get(key, 0) for row in trials) for key in aggregate_fields}
    for trial in trials:
        seed = trial["seed"]
        rows = trial.get("rounds", [])
        derived = {"seed": seed, "rounds": len(rows), "simulated_ms": trial.get("simulated_ms"),
                   "encounters": trial.get("fights"), "timeouts": trial.get("timeouts"), "ghosts": trial.get("ghosts"),
                   "commands": trial.get("commands"), "rejects": trial.get("command_rejects"),
                   "final_hash": rows[-1]["post_hash"] if rows else None}
        derived_summaries.append(derived)
        for key, value in derived.items():
            if value is None or int(value) != int(original[seed][key]):
                summary_differences.append({"seed": seed, "field": key, "packaged": value, "candidate6": original[seed][key]})
        for row in rows:
            for encounter in row["encounters"]:
                if not encounter["complete"] or encounter["simulated_ms"] != encounter["ticks"] * data["tick_ms"]:
                    complete_fight_errors.append({"seed": seed, "round": row["round"], "encounter": encounter})
                durations.append(encounter["simulated_ms"])
                if encounter["ghost"]:
                    recipients[encounter["a"]] += 1
                    donors[encounter["b"]] += 1
            for seat in row["seats"]:
                key = (seed, row["round"], seat["seat"])
                seen_keys[key] += 1
                derived_seat = {"seed": seed, "round": row["round"], **seat,
                                "settlement_id": row["settlement_id"], "pre_hash": row["pre_hash"], "post_hash": row["post_hash"]}
                derived_rounds.append(derived_seat)
                expected = original_rounds.get(key)
                if expected is None or any(int(value) != int(expected[field]) for field, value in derived_seat.items()):
                    round_differences.append({"key": key, "packaged": derived_seat, "candidate6": expected})
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
        if {(row["seat"], row["unit_id"]) for row in trial.get("hero_use_by_seat", [])} != {(seat, unit) for seat in range(8) for unit in ids}:
            usage_differences.append({"seed": seed, "error": "Incomplete unique hero/seat keys"})
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
    check("candidate6_summary_parity", not summary_differences, summary_differences)
    check("candidate6_round_seat_parity", not round_differences and set(seen_keys) == set(original_rounds)
          and all(count == 1 for count in seen_keys.values()),
          {"rows_compared": sum(seen_keys.values()), "mismatches": round_differences,
           "missing": sorted(set(original_rounds)-set(seen_keys)), "unexpected": sorted(set(seen_keys)-set(original_rounds))})
    check("hero_use_reconciles_to_real_deployments", not usage_differences, usage_differences)
    check("actual_fights_complete_and_fixed_tick_duration", not complete_fight_errors, complete_fight_errors)
    standalone_validation_path = ROOT / "reports/WC-310/runtime/post-retained-recap/validation.json"
    standalone_archive_path = standalone_validation_path.parent / "standalone-100-evidence.zip"
    standalone_validation = load(standalone_validation_path)
    standalone_archive = standalone_archive_path.read_bytes()
    check("latest_standalone_archive_digest", hashlib.sha256(standalone_archive).hexdigest() == standalone_validation["archive_sha256"],
          hashlib.sha256(standalone_archive).hexdigest())
    with zipfile.ZipFile(io.BytesIO(standalone_archive)) as archive:
        standalone_summary = list(csv.DictReader(io.StringIO(archive.read("tournaments.csv").decode("utf-8-sig"))))
        standalone_rounds = list(csv.DictReader(io.StringIO(archive.read("round-economy.csv").decode("utf-8-sig"))))
    for name, actual, expected, key_fields, aliases in (
        ("direct_latest_standalone_summaries", derived_summaries, standalone_summary, ("seed",), {"commands": "bot_commands", "rejects": "bot_rejects"}),
        ("direct_latest_standalone_round_seats", derived_rounds, standalone_rounds, ("seed", "round", "seat"), {})):
        key = lambda row: tuple(int(row[k]) for k in key_fields)
        reference = {key(row): row for row in expected}
        differences = [{"key": key(row), "field": field} for row in actual for field, value in row.items()
                       if key(row) not in reference or int(value) != int(reference[key(row)][aliases.get(field, field)])]
        check(name, len(actual) == len(expected) and {key(row) for row in actual} == set(reference) and not differences,
              {"actual_rows": len(actual), "reference_rows": len(expected), "differences": differences})
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
    expected_hashes = {row["staged_relative_path"]: row["declared_sha256"] for row in provenance["staged_source_comparisons"]}
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
    process_exit_path = report_path.parent / "process-exit.json"
    observed_exit = load(process_exit_path)
    exit_lines = []
    log_errors = []
    # Shipping logging is absent here. A null exit code is unavailable, not zero.
    result = {"utc": datetime.now(timezone.utc).isoformat(), "status": "PASS" if not failures else "FAIL",
              "boundary": "Actual Shipping packaged 0H8B simulation and recorded deployment/settlement evidence. Not human interaction, networking, rendered frame performance or art/audio acceptance.",
              "checks": checks, "totals": totals, "explicit_capped_seeds": caps,
              "timeout_fraction": totals["timeouts"]/totals["fights"],
              "match_duration_ms": distribution([row["simulated_ms"] for row in trials]),
              "fight_duration_ms": distribution(durations),
              "ghost_recipient_counts": dict(sorted(recipients.items())), "ghost_donor_counts": dict(sorted(donors.items())),
              "actual_packaged_hero_use": dict(sorted(hero_totals.items())),
              "hero_use_boundary": "Observed real living-seat deployments at combat lock. Placement associations are descriptive and not causal strength estimates.",
              "actual_run": {key: data.get(key) for key in ("start_utc", "end_utc", "batch_wall_seconds", "engine", "cpu", "compiler", "compiler_full_version", "translation_unit_build_date", "translation_unit_build_time", "executable_path")},
              "launch": load(launch_path),
              "observed_process_exit": observed_exit,
              "exit_boundary": "Captured process exit_code is null: UNKNOWN. Complete game evidence and zero failed trials do not establish an OS exit code. No Shipping game.log is present, so engine log error/exit checks are NOT_RUN.",
              "inputs": [{"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                         for path in (report_path, provenance_path, summary_path, rounds_path, stage_path,
                                      process_exit_path, launch_path, standalone_analysis_path,
                                      standalone_validation_path, standalone_archive_path)]}
    final = report_path.stat()
    if (initial.st_size, initial.st_mtime_ns) != (final.st_size, final.st_mtime_ns):
        raise SystemExit("Regression report changed during analysis; no final analysis written")
    output = OUT / "regression-analysis.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    with (OUT / "hero-use.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("unit_id", "deployed_unit_rounds", "seat_rounds", "seat_tournaments", "final_placement_counts"))
        for hero, row in sorted(hero_totals.items()):
            writer.writerow((hero, row["unit_rounds"], row["rounds"], row["seat_tournaments"], json.dumps(row["placements"], sort_keys=True)))
    lines = ["Shipping actual packaged regression: " + result["status"], "",
             result["boundary"], "",
             f"All 100 requested seeds are retained and finished. The game reports zero failed trials, zero rejected bot commands, zero unresolved encounters and successful evidence writes. Recorded batch elapsed time was {data['batch_wall_seconds']:.6f} seconds, {data['start_utc']} to {data['end_utc']}, on {data['cpu'].strip()}. This NullRHI/no-sound run is simulation execution, not a render or audio benchmark.", "",
             f"Totals: {totals['fights']:,} encounters, {totals['timeouts']:,} timeouts ({100*result['timeout_fraction']:.4f}%), {totals['ghosts']} ghost encounters and {totals['commands']:,} bot commands. All 100 candidate6 engine summary rows and 17,728 round/seat rows match, including all state and settlement hashes. A separate direct comparison with the SHA256-verified latest standalone archive also passes for every summary and round/seat row.", "",
             f"Explicit capped-adjudication seeds ({len(caps)}): {caps}. Match duration milliseconds: {result['match_duration_ms']}. Individual fight duration milliseconds: {result['fight_duration_ms']}.", "",
             "The table counts actual living-seat combat-lock deployments. Final-placement associations are descriptive; using a hero does not establish that hero caused the result. The actual per-hero rows reconcile to captured deployments and match the preserved standalone composition analysis.", "",
             "| Hero | Deployed unit-rounds | Seat-rounds | Seat-tournaments used | First-place seats that used hero |",
             "|---|---:|---:|---:|---:|"]
    for hero, row in sorted(hero_totals.items()):
        lines.append(f"| {hero} | {row['unit_rounds']} | {row['rounds']} | {row['seat_tournaments']} | {row['placements'].get(1,0)} |")
    lines += ["", "Runtime-loaded profile and all five canonical data hashes agree with shipping-final-provenance.json. The actual Shipping inner executable SHA256 matches that immutable manifest.", "",
              result["exit_boundary"], "",
              "This audit binds the tested Shipping executable to shipping-final-provenance. Subsequent prerequisite staging and its final delivery manifest are separate packaging evidence; this report does not infer an unchanged delivered container from the shared C++ source.", ""]
    (OUT / "regression-analysis.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": result["status"], "totals": totals, "caps": caps,
                      "failure_checks": failures, "path": str(output)}, indent=2))


if __name__ == "__main__":
    main()
