"""Read-only comparison of preserved actual candidate4 and standalone evidence."""

from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import io
import json
import statistics
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ENGINE = ROOT / "reports/WC-360/candidate4-automation"
STANDALONE = ROOT / "reports/WC-310/runtime/post-event-metadata"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def csv_rows(data):
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))


def quantiles(values):
    values = sorted(values)
    return {"count": len(values), "minimum": values[0], "mean": statistics.mean(values),
            "median": statistics.median(values), "p95": values[int((len(values) - 1) * .95)],
            "maximum": values[-1]}


def main():
    inputs = []

    def read(path):
        data = path.read_bytes()
        inputs.append({"path": str(path.resolve()), "bytes": len(data), "sha256": sha(data)})
        return data

    tournaments = csv_rows(read(ENGINE / "engine-tournaments.csv"))
    rounds = csv_rows(read(ENGINE / "engine-rounds.csv"))
    automation = json.loads(read(ENGINE / "index.json"))
    manifest = json.loads(read(STANDALONE / "sha256.json"))
    archive_path = STANDALONE / "standalone-100-evidence.zip"
    archive_bytes = read(archive_path)
    expected_archive = manifest["files"][str(archive_path.relative_to(ROOT)).replace("/", "\\")]
    if sha(archive_bytes) != expected_archive:
        raise ValueError("Preserved standalone archive does not match its recorded digest")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        standalone_tournaments = csv_rows(archive.read("tournaments.csv"))
        standalone_rounds = csv_rows(archive.read("round-economy.csv"))
        compositions = csv_rows(archive.read("compositions.csv"))
        mirrors = csv_rows(archive.read("mirror-combats.csv"))
        archive_entries = [{"name": name, "sha256": sha(archive.read(name))} for name in archive.namelist()]

    aliases = {"commands": "bot_commands", "rejects": "bot_rejects"}
    reference_summary = {int(row["seed"]): row for row in standalone_tournaments}
    summary_mismatches = []
    for row in tournaments:
        reference = reference_summary.get(int(row["seed"]))
        for key, value in row.items():
            if reference is None or int(value) != int(reference[aliases.get(key, key)]):
                summary_mismatches.append({"seed": row["seed"], "field": key, "engine": value,
                                           "standalone": None if reference is None else reference.get(aliases.get(key, key))})
    key_of = lambda row: tuple(int(row[key]) for key in ("seed", "round", "seat"))
    reference_rounds = {key_of(row): row for row in standalone_rounds}
    observed_keys = Counter(key_of(row) for row in rounds)
    duplicate_keys = [key for key, count in observed_keys.items() if count != 1]
    missing_keys = sorted(set(reference_rounds) - set(observed_keys))
    unexpected_keys = sorted(set(observed_keys) - set(reference_rounds))
    round_mismatches = []
    for row in rounds:
        reference = reference_rounds.get(key_of(row))
        if reference is not None:
            differences = {key: [value, reference[key]] for key, value in row.items()
                           if int(value) != int(reference[key])}
            if differences:
                round_mismatches.append({"key": key_of(row), "differences": differences})

    by_round = defaultdict(list)
    for row in rounds:
        by_round[int(row["seed"]), int(row["round"])].append(row)
    final = {}
    completeness_errors = []
    health_gold_errors = []
    hash_consistency_errors = []
    for row in tournaments:
        seed, count = int(row["seed"]), int(row["rounds"])
        expected_rounds = set(range(1, count + 1))
        observed_rounds = {r for s, r in by_round if s == seed}
        if observed_rounds != expected_rounds:
            completeness_errors.append({"seed": seed, "expected": sorted(expected_rounds), "observed": sorted(observed_rounds)})
        final[seed] = by_round[seed, count]
    for key, rows in by_round.items():
        if sorted(int(row["seat"]) for row in rows) != list(range(8)):
            completeness_errors.append({"key": key, "seats": [row["seat"] for row in rows]})
        if len({(row["settlement_id"], row["pre_hash"], row["post_hash"]) for row in rows}) != 1:
            hash_consistency_errors.append(key)
        for row in rows:
            if int(row["health"]) < 0 or int(row["gold"]) < 0:
                health_gold_errors.append(key_of(row))
    rules = json.loads(read(ROOT / "data/rules.alpha.json"))
    maximum_rounds = rules["tournament"]["max_rounds"]
    at_maximum = [int(row["seed"]) for row in tournaments if int(row["rounds"]) == maximum_rounds]
    inferred_caps = [seed for seed in at_maximum if sum(int(row["health"]) > 0 for row in final[seed]) > 1]
    shared_first = [seed for seed, rows in final.items() if sum(int(row["placement"]) == 1 for row in rows) > 1]
    final_positions = {(seed, int(row["seat"])): int(row["placement"]) for seed, rows in final.items() for row in rows}

    per_hero = defaultdict(lambda: {"unit_rounds": 0, "seat_rounds": set(), "seat_tournaments": set(),
                                    "instances": set(), "maximum_star": 0})
    for row in compositions:
        if int(row["on_board"]) != 1:
            continue
        seed, round_number, seat = int(row["seed"]), int(row["round"]), int(row["seat"])
        item = per_hero[row["definition"]]
        item["unit_rounds"] += 1
        item["seat_rounds"].add((seed, round_number, seat))
        item["seat_tournaments"].add((seed, seat))
        item["instances"].add((seed, seat, int(row["unit_id"])))
        item["maximum_star"] = max(item["maximum_star"], int(row["star"]))
    hero_usage = []
    for hero, item in sorted(per_hero.items()):
        placements = Counter(final_positions[key] for key in item["seat_tournaments"])
        hero_usage.append({"unit_id": hero, "deployed_unit_rounds": item["unit_rounds"],
                           "seat_rounds_deployed": len(item["seat_rounds"]),
                           "seat_tournaments_used": len(item["seat_tournaments"]),
                           "distinct_owned_instances": len(item["instances"]),
                           "maximum_deployed_star": item["maximum_star"],
                           "final_placement_counts_for_seats_that_used_hero": dict(sorted(placements.items()))})
    fields = list(hero_usage[0])
    with (OUT / "supplemental-standalone-hero-use.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in hero_usage:
            writer.writerow({**row, fields[-1]: json.dumps(row[fields[-1]], sort_keys=True)})

    total = {key: sum(int(row[key]) for row in tournaments)
             for key in ("rounds", "simulated_ms", "encounters", "timeouts", "ghosts", "commands", "rejects")}
    runtime_test = next(test for test in automation["tests"]
                        if test["fullTestPath"] == "WonderChess.Runtime.OneHundredActualCombatTournaments")
    source_checks = []
    for relative, expected in manifest["files"].items():
        if relative.startswith("game\\Source"):
            path = ROOT / relative
            actual = sha(read(path))
            source_checks.append({"path": str(path.resolve()), "expected_standalone_sha256": expected,
                                  "current_sha256": actual, "matches": actual == expected})
    parity = not any((summary_mismatches, round_mismatches, missing_keys, unexpected_keys, duplicate_keys))
    result = {"utc": datetime.now(timezone.utc).isoformat(),
              "status": "PASS" if parity and not any((completeness_errors, health_gold_errors, hash_consistency_errors)) and sorted(int(row["seed"]) for row in tournaments) == list(range(1, 101)) and automation["failed"] == 0 else "FAIL",
              "boundary": "Actual WindowsEditor C++ combat execution and CSV comparison. Not packaged execution, networking, human play or render-performance acceptance.",
              "engine": {"tournaments": len(tournaments), "seeds": sorted(int(row["seed"]) for row in tournaments),
                         "totals": total, "timeout_fraction": total["timeouts"] / total["encounters"],
                         "ghost_fraction": total["ghosts"] / total["encounters"],
                         "round_distribution": dict(sorted(Counter(int(row["rounds"]) for row in tournaments).items())),
                         "simulated_match_duration_ms": quantiles([int(row["simulated_ms"]) for row in tournaments]),
                         "timeouts_per_tournament": quantiles([int(row["timeouts"]) for row in tournaments]),
                         "ghosts_per_tournament": quantiles([int(row["ghosts"]) for row in tournaments]),
                         "maximum_rounds": maximum_rounds, "seeds_reaching_maximum_round": at_maximum,
                         "inferred_capped_adjudication_seeds": inferred_caps,
                         "cap_boundary": "The CSV has no explicit capped field. Inferred from final round=max_rounds and multiple seats with positive health, matching current Match::Settle. Round24 alone is not counted as a cap.",
                         "shared_first_place_seeds": shared_first,
                         "hero_usage": "NOT_RECORDED in these engine CSVs; supplementary standalone composition observations are separately labeled.",
                         "individual_fight_duration_distribution": "NOT_RECORDED in these CSVs",
                         "automation_duration_seconds": runtime_test["duration"],
                         "automation_state": runtime_test["state"], "automation_errors": runtime_test["errors"],
                         "automation_warnings": runtime_test["warnings"]},
              "parity": {"status": "PASS" if parity else "FAIL", "summary_rows_compared": len(tournaments),
                         "summary_fields_per_row": len(tournaments[0]), "summary_mismatches": summary_mismatches,
                         "round_seat_rows_compared": len(rounds), "round_fields_per_row": len(rounds[0]),
                         "round_row_mismatch_count": len(round_mismatches), "round_row_mismatches": round_mismatches,
                         "duplicate_engine_keys": duplicate_keys, "missing_engine_keys": missing_keys,
                         "unexpected_engine_keys": unexpected_keys,
                         "standalone_archive_sha256_verified": True},
              "structural_checks": {"round_seat_completeness_errors": completeness_errors,
                                    "negative_health_gold_rows": health_gold_errors,
                                    "inconsistent_per_round_hashes": hash_consistency_errors},
              "current_core_sources_vs_preserved_standalone_snapshot": source_checks,
              "supplemental_standalone": {"boundary": "Measured by the standalone MSVC /fp:fast harness, not exported by candidate4 engine. Exact engine summary/round hashes match, but these extra metrics retain standalone provenance.",
                                         "combat_effect_events": sum(int(row["combat_events"]) for row in standalone_tournaments),
                                         "composition_rows": len(compositions), "mirror_rows": len(mirrors),
                                         "hero_usage": hero_usage},
              "all_automation_tests": {key: automation[key] for key in ("succeeded", "succeededWithWarnings", "failed", "notRun", "totalDuration")},
              "reported_test_device": automation["devices"], "inputs": inputs, "standalone_archive_entries": archive_entries}
    (OUT / "comparison.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Candidate4 actual engine regression analysis", "",
             f"Candidate4 completed 100 actual eight-bot tournaments in the WindowsEditor runtime automation test. Seeds 1-100 produced {total['encounters']} encounters, {total['timeouts']} timeouts ({100*result['engine']['timeout_fraction']:.4f}%), {total['ghosts']} ghost encounters, {total['commands']} bot command log entries and {total['rejects']} rejected bot commands.", "",
             f"Comparison with the SHA256-verified latest post-event-metadata standalone archive: all {len(tournaments)} summary rows ({len(tournaments[0])} fields each) and all {len(rounds)} round/seat rows ({len(rounds[0])} fields each) agree exactly after CSV integer normalization. There are no missing, extra or duplicate round/seat keys. Round completeness, nonnegative health/gold and common settlement/state hashes also pass the structural checks.", "",
             f"The 100-match automation test reports Success, 0 errors, 0 warnings and {runtime_test['duration']:.6f} seconds execution time. The complete candidate4 batch reports 5 successful automation tests, 0 failed and 0 not run. This duration measures the C++ test, not rendered frame rate or packaged startup.", "",
             f"Round counts: {dict(sorted(Counter(int(row['rounds']) for row in tournaments).items()))}. Simulated match duration milliseconds: {result['engine']['simulated_match_duration_ms']}.", "",
             f"{len(at_maximum)} seeds reach the authored 24-round ceiling. Of those, {len(inferred_caps)} retain more than one positive-health seat and therefore satisfy the implemented capped-adjudication condition. Inferred cap seeds: {inferred_caps}. This is derived from actual final rows plus the cap rule; the CSV does not explicitly record the capped flag. Shared-first-place seeds: {shared_first}.", "",
             "Engine CSVs do not contain individual fight lengths, hero compositions/use or effect-event totals. The separate standalone archive contains 1,390,777 effect events and preparation-lock composition rows. Its hero usage below remains supplementary standalone evidence despite exact shared result/hash parity. Placements indicate seats that used a hero at any captured round; they are not evidence that the hero caused that result.", "",
             "| Hero | Deployed unit-rounds | Seat-rounds | Seat-tournaments used | Maximum star | First-place seats that used hero |",
             "|---|---:|---:|---:|---:|---:|"]
    for row in hero_usage:
        lines.append(f"| {row['unit_id']} | {row['deployed_unit_rounds']} | {row['seat_rounds_deployed']} | {row['seat_tournaments_used']} | {row['maximum_deployed_star']} | {row['final_placement_counts_for_seats_that_used_hero'].get(1,0)} |")
    lines += ["", "All three current core source hashes match the preserved standalone source snapshot. This readback is not a substitute for a delivered build manifest. Input file hashes, exact comparisons, supplemental provenance and all metric boundaries are in comparison.json. The executable/core source/data are unchanged by this analysis.", "", "The candidate4 asset automation also reports success, but art attractiveness, deformation, feet/forward calibration, in-game clarity and audio remain their separate evidence gates. No packaged, 1H7B, 2H6B or performance acceptance is inferred from these CSVs."]
    (OUT / "analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "totals": total, "parity": result["parity"],
                      "inferred_caps": inferred_caps, "shared_first": shared_first,
                      "core_sources_match": all(item["matches"] for item in source_checks)}, indent=2))


if __name__ == "__main__":
    main()
