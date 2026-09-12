"""Reconcile real native/packaged tournaments; do not infer human or release acceptance."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path


ENCOUNTER_KINDS = {0: "pvp", 1: "ghost", 2: "neutral"}


def read_csv(path: Path) -> list[dict[str, int]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return [{key: int(value) for key, value in row.items()} for row in csv.DictReader(stream)]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyze(native: Path, engine: Path | None = None) -> dict:
    result = json.loads((native / "summary.json").read_text(encoding="utf-8-sig"))
    process = json.loads((native / "process.json").read_text(encoding="utf-8-sig"))
    tournaments = read_csv(native / "tournaments.csv")
    encounters = read_csv(native / "encounters.csv")
    rounds = read_csv(native / "rounds.csv")
    errors: list[str] = []
    count = result["actual_combat_tournaments"]
    first_seed = result.get("first_seed", 1)
    if result.get("profile") != "wonder_vnext":
        errors.append("Native profile identity is not wonder_vnext")
    if process["compile_exit"] or process["process_exit"] or process["requested_tournaments"] != count:
        errors.append("Native process did not verify the requested tournament count")
    if process.get("first_seed", 1) != first_seed or first_seed < 1 or first_seed + count - 1 > 10000:
        errors.append("Native seed range identity is invalid")
    if not process.get("source_stable", False):
        errors.append("Native source stability was not verified")
    if [row["seed"] for row in tournaments] != list(range(first_seed, first_seed + count)):
        errors.append("Native seed coverage is incomplete or duplicated")
    if count < 1:
        raise ValueError("Native analysis requires at least one actual tournament")
    if len(encounters) != result["encounters"] or sum(row["timeout"] for row in encounters) != result["timeouts"]:
        errors.append("Native encounter totals do not reconcile")
    counter_totals = {field: sum(row[field] for row in tournaments)
                      for field in ("relic_choices", "relic_equips", "command_rejects")}
    for field, total in counter_totals.items():
        if result.get(field) != total:
            errors.append(f"Native {field} total does not reconcile")
    round_map = {(r["seed"], r["round"]): r for r in rounds}
    fight_map = {(r["seed"], r["round"], r["index"]): r for r in encounters}
    rounds_by_seed, fights_by_seed, fights_by_round = defaultdict(list), defaultdict(list), defaultdict(list)
    for row in rounds:
        rounds_by_seed[row["seed"]].append(row)
    for row in encounters:
        fights_by_seed[row["seed"]].append(row)
        fights_by_round[row["seed"], row["round"]].append(row)
        if row.get("kind") not in ENCOUNTER_KINDS:
            errors.append(f"Unknown native encounter kind at {(row['seed'], row['round'], row['index'])}")
    expected_seeds = set(range(first_seed, first_seed + count))
    if set(rounds_by_seed) != expected_seeds or set(fights_by_seed) != expected_seeds:
        errors.append("Native history includes missing or orphaned seeds")
    if len(round_map) != len(rounds) or len(fight_map) != len(encounters):
        errors.append("Duplicate native round or fight records")
    if set(fights_by_round) != set(round_map):
        errors.append("Native encounter history includes missing or orphaned rounds")
    for key, fights in fights_by_round.items():
        if [row["index"] for row in fights] != list(range(len(fights))):
            errors.append(f"Native encounter indexes are not contiguous at {key}")
    for row in tournaments:
        seed = row["seed"]
        owned_rounds = rounds_by_seed[seed]
        owned_fights = fights_by_seed[seed]
        if [r["round"] for r in owned_rounds] != list(range(1, row["rounds"] + 1)):
            errors.append(f"Round coverage mismatch at seed {seed}")
        if len(owned_fights) != row["encounters"] or sum(r["timeout"] for r in owned_fights) != row["timeouts"]:
            errors.append(f"Encounter coverage mismatch at seed {seed}")
        if sum(row[p + "_ms"] for p in ("preparation", "combat", "settlement")) != row["simulated_ms"]:
            errors.append(f"Phase durations do not reconcile at seed {seed}")
        if any(row[p + "_ms"] < 0 for p in ("preparation", "combat", "settlement")) or row["simulated_ms"] <= 0:
            errors.append(f"Invalid phase duration at seed {seed}")
        if row["command_rejects"]:
            errors.append(f"Bot commands rejected at seed {seed}")
        if any(row[field] < 0 for field in counter_totals):
            errors.append(f"Negative command counter at seed {seed}")
    median_minutes = statistics.median(r["simulated_ms"] / 60000 for r in tournaments)
    timeout_rate = result["timeouts"] / result["encounters"] if result["encounters"] else None
    output = {
        "schema": "wonder_vnext.run_analysis.1",
        "catalog_digest": result["catalog_digest"],
        "native_tournaments": count,
        "first_seed": first_seed,
        "last_seed": first_seed + count - 1,
        "native_encounters": len(encounters),
        "native_timeouts": result["timeouts"],
        "timeout_rate": timeout_rate,
        "capped_tournaments": sum(r["capped"] for r in tournaments),
        "median_simulated_minutes": median_minutes,
        "median_phase_minutes": {p: statistics.median(r[p + "_ms"] / 60000 for r in tournaments)
                                 for p in ("preparation", "combat", "settlement")},
        "native_relic_choices": counter_totals["relic_choices"],
        "native_relic_equips": counter_totals["relic_equips"],
        "sample_targets": {"median_duration_35_to_45": 35 <= median_minutes <= 45,
                           "combat_timeout_below_two_percent": timeout_rate is not None and timeout_rate < .02},
        "inputs_sha256": {str(native / name): digest(native / name) for name in
                          ("summary.json", "process.json", "tournaments.csv", "rounds.csv", "encounters.csv")},
        "boundary": "Six-hero laboratory sample with provisional traits and neutral behavior; accelerated simulated clocks. No human duration, fun, performance or full-roster release acceptance.",
    }
    if engine:
        report = json.loads(engine.read_text(encoding="utf-8-sig"))
        output["inputs_sha256"][str(engine)] = digest(engine)
        trials = report.get("trials", [])
        if report.get("digest") != result["catalog_digest"] or report.get("profile_id") != "wonder_vnext":
            errors.append("Engine and native catalog/profile identity differ")
        if not report.get("complete") or report.get("failed") or report.get("evidence_write_failed"):
            errors.append("Engine batch incomplete or failed")
        expected_count = report["requested"]
        if expected_count < 1 or expected_count > count or first_seed != 1:
            errors.append("Engine comparison requires a positive bounded tournament count")
        if len(trials) != expected_count or [t["seed"] for t in trials] != list(range(1, expected_count + 1)):
            errors.append("Engine seed coverage incomplete or duplicated")
        compared_rounds = compared_fights = 0
        for trial in trials:
            seed = trial["seed"]
            if not trial["pass"] or trial["command_rejects"] or trial["unresolved_encounters"]:
                errors.append(f"Engine runtime failure at seed {seed}")
            native_trial = next((t for t in tournaments if t["seed"] == seed), None)
            if not native_trial or trial["simulated_ms"] != native_trial["simulated_ms"]:
                errors.append(f"Engine/native clock mismatch at seed {seed}")
            actual_rounds = trial["rounds"]
            if not native_trial or [r["round"] for r in actual_rounds] != list(range(1, native_trial["rounds"] + 1)):
                errors.append(f"Engine round coverage mismatch at seed {seed}")
            for row in actual_rounds:
                key = seed, row["round"]
                reference = round_map.get(key)
                if not reference or any(int(row[h]) != reference[h] for h in ("pre_hash", "post_hash")):
                    errors.append(f"Engine/native logical state mismatch at {key}")
                compared_rounds += 1
                expected_fights = fights_by_round[key]
                if len(expected_fights) != len(row["encounters"]):
                    errors.append(f"Engine fight coverage mismatch at {key}")
                for index, fight in enumerate(row["encounters"]):
                    reference = fight_map.get((*key, index))
                    fields = ("a", "b", "winner", "ticks", "timeout", "survivors_a", "survivors_b")
                    if not reference or not fight["complete"] or any(int(fight[f]) != reference[f] for f in fields):
                        errors.append(f"Engine/native encounter mismatch at {(*key, index)}")
                    if (fight.get("kind") not in ENCOUNTER_KINDS.values() or not reference
                            or fight.get("kind") != ENCOUNTER_KINDS.get(reference.get("kind"))):
                        errors.append(f"Engine/native encounter kind mismatch at {(*key, index)}")
                    compared_fights += 1
        output["engine_comparison"] = {"tournaments": len(trials), "rounds": compared_rounds,
                                       "encounters": compared_fights, "executable": report["executable_path"]}
    output["verification_errors"] = errors
    output["technical_reconciliation_passed"] = not errors
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, nargs="+", required=True)
    parser.add_argument("--engine", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Use a fresh output file to preserve evidence")
    output = analyze(args.native[0], args.engine) if len(args.native) == 1 else analyze_batches(args.native, args.engine)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in output.items() if k != "inputs_sha256"}, indent=2))
    return 0 if output["technical_reconciliation_passed"] else 1


def analyze_batches(paths: list[Path], engine: Path | None = None) -> dict:
    batches = [analyze(path, engine if index == 0 else None) for index, path in enumerate(paths)]
    errors = [error for batch in batches for error in batch["verification_errors"]]
    processes = [json.loads((path / "process.json").read_text(encoding="utf-8-sig")) for path in paths]
    if not processes[0].get("source_hashes") or any(p.get("source_hashes") != processes[0]["source_hashes"] for p in processes):
        errors.append("Batch compiled-source identities differ or are missing")
    next_seed = 1
    for batch in batches:
        if batch["first_seed"] != next_seed:
            errors.append("Combined batches have gaps, overlaps or reordered seed ranges")
        next_seed = batch["last_seed"] + 1
        if batch["catalog_digest"] != batches[0]["catalog_digest"]:
            errors.append("Batch catalog identities differ")
    rows = [row for path in paths for row in read_csv(path / "tournaments.csv")]
    encounters = sum(batch["native_encounters"] for batch in batches)
    timeouts = sum(batch["native_timeouts"] for batch in batches)
    minutes = statistics.median(row["simulated_ms"] / 60000 for row in rows)
    rate = timeouts / encounters if encounters else None
    output = {"schema": "wonder_vnext.batch_analysis.1", "catalog_digest": batches[0]["catalog_digest"],
              "native_tournaments": len(rows), "first_seed": 1, "last_seed": next_seed - 1,
              "native_encounters": encounters, "native_timeouts": timeouts, "timeout_rate": rate,
              "capped_tournaments": sum(row["capped"] for row in rows), "median_simulated_minutes": minutes,
              "median_phase_minutes": {phase: statistics.median(row[phase + "_ms"] / 60000 for row in rows)
                                       for phase in ("preparation", "combat", "settlement")},
              "native_relic_choices": sum(batch["native_relic_choices"] for batch in batches),
              "native_relic_equips": sum(batch["native_relic_equips"] for batch in batches),
              "sample_targets": {"median_duration_35_to_45": 35 <= minutes <= 45,
                                 "combat_timeout_below_two_percent": rate is not None and rate < .02},
              "source_hashes": processes[0].get("source_hashes"), "batches": batches,
              "boundary": batches[0]["boundary"], "verification_errors": errors,
              "technical_reconciliation_passed": not errors}
    if "engine_comparison" in batches[0]:
        output["engine_comparison"] = batches[0]["engine_comparison"]
    return output


if __name__ == "__main__":
    raise SystemExit(main())
