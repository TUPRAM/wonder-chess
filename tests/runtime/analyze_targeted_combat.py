"""Summarize actual native outputs; never synthesize a combat outcome."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/WC-310/runtime/targeted-native"
BUILD = REPORT / "build"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rows(name):
    with (BUILD / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    execution = read_json(BUILD / "execution.json")
    process = read_json(BUILD / "process.json")
    edge_cases = rows("edge-cases.csv")
    fights = rows("formation-combats.csv")
    formations = rows("formations.csv")
    assert execution["status"] == "PASS" and execution["failures"] == 0
    assert process["compile_exit"] == process["process_exit"] == 0
    assert all(row["status"] == "PASS" for row in edge_cases)
    assert len(fights) == 720
    assert all(row["observed_replay_exact"] == "1" for row in fights)
    assert digest(ROOT / "game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp") == process["core_sha256"]
    assert digest(ROOT / "tests/runtime/targeted_combat_tests.cpp") == process["source_sha256"]
    totals = defaultdict(Counter)
    oriented = {}
    for row in fights:
        a, b, swapped = row["formation_a"], row["formation_b"], int(row["swapped"])
        winner = int(row["winner"])
        left, right = (b, a) if swapped else (a, b)
        for side, name in enumerate((left, right)):
            totals[name]["seat_appearances"] += 1
            totals[name]["draws" if winner == -1 else "wins" if winner == side else "losses"] += 1
            totals[name]["timeout_appearances"] += int(row["timeout"])
        oriented[(a, b, int(row["star"]), int(row["seed"]), swapped)] = row
    mirror_rows = []
    for key, original in oriented.items():
        a, b, star, seed, swapped = key
        if swapped or a == b:
            continue
        reversed_row = oriented[(a, b, star, seed, 1)]
        original_outcome = int(original["winner"])
        reversed_outcome = int(reversed_row["winner"])
        mapped = -1 if reversed_outcome == -1 else 1 - reversed_outcome
        mirror_rows.append({"formation_a": a, "formation_b": b, "star": star, "seed": seed,
                            "original_winner_relative_to_a": original_outcome,
                            "swapped_winner_relative_to_a": mapped,
                            "outcome_changed": original_outcome != mapped,
                            "original_ticks": int(original["ticks"]), "swapped_ticks": int(reversed_row["ticks"])})
    with (REPORT / "mirror-comparisons.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=mirror_rows[0].keys())
        writer.writeheader()
        writer.writerows(mirror_rows)
    filenames = ["execution.json", "process.json", "edge-cases.csv", "edge-events.csv", "edge-positions.csv",
                 "formations.csv", "formation-combats.csv", "compile.log", "run.log", "targeted_combat_tests.exe"]
    bindings = [{"path": str(BUILD / name), "sha256": digest(BUILD / name), "bytes": (BUILD / name).stat().st_size} for name in filenames]
    source_names = ["tests/runtime/targeted_combat_tests.cpp", "tests/runtime/run_targeted_combat.ps1",
                    "tests/runtime/analyze_targeted_combat.py", "tests/runtime/generate_catalog_fixture.py",
                    "tests/runtime/build/CatalogFixture.h", "game/Source/WonderChessRuntime/Public/Simulation/WonderSimulation.h",
                    "game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp",
                    "data/rules.alpha.json", "data/units.json", "data/traits.json", "data/bots.json", "generated/catalog_digest.json"]
    bindings += [{"path": str(ROOT / name), "sha256": digest(ROOT / name), "bytes": (ROOT / name).stat().st_size} for name in source_names]
    result = {"status": "PASS", "generated_utc": datetime.now(timezone.utc).isoformat(), "execution": execution,
              "process": process, "edge_cases": edge_cases[:-1], "formation_case": edge_cases[-1],
              "formation_scenarios": len(fights), "distinct_formation_inputs": 600,
              "observed_replays": len(fights), "actual_matrix_combat_executions": len(fights) * 2,
              "edge_combat_executions_including_bounded_seed_search": execution["combat_executions"] - len(fights) * 2,
              "formation_timeouts": sum(int(row["timeout"]) for row in fights),
              "formation_events": sum(int(row["events"]) for row in fights),
              "combat_ticks_min": min(int(row["ticks"]) for row in fights),
              "combat_ticks_max": max(int(row["ticks"]) for row in fights),
              "cross_formation_mirror_pairs": len(mirror_rows),
              "cross_formation_mirror_outcome_changes": sum(row["outcome_changed"] for row in mirror_rows),
              "star_scenario_counts": dict(Counter(row["star"] for row in fights)),
              "base_cost_per_formation": 10, "acquisition_cost_per_star": {"1": 10, "2": 30, "3": 90},
              "formation_definitions": formations, "formation_seat_results": dict(totals),
              "boundaries": [
                  "These are native MSVC executions of current authoritative Combat, not Unreal Automation or packaged network tests.",
                  "Controlled edge fixtures copy the canonical catalog in memory, remove trait bonuses, set deterministic health/damage/range/timing and effect routing, and do not modify canonical files or production code.",
                  "The matrix uses unchanged canonical unit stats, abilities, traits, and rules. All five formations have six heroes and base cost10; all seats use the same star in each scenario. Shield-heavy uses two Ada Brightshield instances and sustain two Mira Dawnwell instances, each below the automatic three-copy same-star merge threshold.",
                  "The720 matrix rows comprise480 cross-formation oriented scenarios plus240 same-formation rows. Same-formation swapped rows repeat120 identical inputs, leaving600 distinct initial-input scenarios.",
                  "Observation replay reads simulation state and events at each tick; it does not test rendering, networking or user-interface observation. Compared fields are exactly those in Signature().",
                  "Read-only replay checks and all invariant assertions dominate the assertion count; assertion volume is not a quality or performance score.",
                  "Mirror outcomes can change because a seed determines initiative in side insertion order and board route tie-breaking is absolute. The report records these differences without declaring them necessarily defects or balanced outcomes.",
                  "This is a bounded formation sample, not an exhaustive strategy search or proof of solved balance. Frame-time and audio/visual acceptance are outside this harness.",
                  "Empty battles, released projectile after source defeat, expiry-tick shield ordering, and tournament frame-hitch recaps were executed in the separate existing runtime suite; they were not rerun in this new executable."
              ], "files": bindings}
    (REPORT / "validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    md = ["# Actual native combat boundary and formation checks", "",
          f"PASS: {execution['cases']} groups, zero failed, {execution['combat_executions']:,} actual combat constructions/executions. MSVC compile and process exits were both0; compiler194435226 and `/std:c++20 /O2 /fp:fast /W4` were used. The pure C++ core source SHA256 is `{process['core_sha256']}`.", "",
          f"The matrix completed720 scenarios plus720 observed replays, with {result['formation_timeouts']} supported timeouts and {result['formation_events']:,} events in the720 primary rows. All720 compared replay signatures matched; no checked occupancy, reservation, identity, health or shield invariant failed.", "",
          "The five formations use six canonical alpha heroes, cost10 at one star,30 at two stars and90 at three stars. Shield-heavy deploys two Ada Brightshield instances and sustain deploys two Mira Dawnwell instances; each same-star duplicate pair is legal below the three-copy merge threshold. Each matchup has equal star and equal acquisition cost. Eight seeds, three star levels, both seat orientations, and self-matchups were executed. Full row data and exact deployment coordinates are preserved in the build CSV files.", "",
          f"Across {len(mirror_rows)} cross-formation mirror pairs, {result['cross_formation_mirror_outcome_changes']} changed their winner relative to formation A. This is observed position/initiative sensitivity, not a claim that the metagame is solved.", "",
          "| Formation | Seat appearances | Wins | Losses | Draws | Timeout appearances |",
          "|---|---:|---:|---:|---:|---:|"]
    for name, row in totals.items():
        md.append(f"| {name} | {row['seat_appearances']} | {row['wins']} | {row['losses']} | {row['draws']} | {row['timeout_appearances']} |")
    md += ["", "The targeted checks actually delivered delayed shield packets to existing shields: stronger replaced amount/expiry/source, equal later refreshed, weaker and equal earlier left amount/expiry/source untouched. Physical mitigation before shield absorption, true-damage overflow/overkill, effective heal cap, defeated-target exclusion, each independent orthogonal corner blocker, a physically empty reserved orthogonal blocker, destination contention, origin retention, movement/dash interruption, an enclosed corner, dash zero damage, and maximum-expiry stun refresh all passed.", "",
           "## Evidence boundaries", ""]
    md += ["- " + boundary for boundary in result["boundaries"]]
    md += ["", "Rerun from the workspace with `./tests/runtime/run_targeted_combat.ps1`, then `python tests/runtime/analyze_targeted_combat.py`, using the current PowerShell execution policy. This overwrites this harness's build outputs; preserve an earlier evidence bundle before a future source change. `validation.json` binds all current source, canonical input, executable and raw evidence files."]
    (REPORT / "validation.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "formation_scenarios", "observed_replays", "formation_timeouts", "cross_formation_mirror_pairs", "cross_formation_mirror_outcome_changes")}, indent=2))


if __name__ == "__main__":
    main()
