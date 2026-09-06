"""Summarize the executed native alpha-trait fixtures without promoting them to UE execution."""
from collections import Counter
from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "reports/WC-310/runtime/trait-native"
BUILD = BASE / "build"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def bind(path):
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}


def main():
    summary, process = load(BUILD / "summary.json"), load(BUILD / "process.json")
    cases = list(csv.DictReader((BUILD / "trait-cases.csv").open(encoding="utf-8-sig")))
    events = list(csv.DictReader((BUILD / "trait-events.csv").open(encoding="utf-8-sig")))
    traits = [t for t in load(ROOT / "data/traits.json")["traits"] if t["alpha_enabled"]]
    coverage = {t["id"]: [row for row in cases if row["case"].startswith(t["id"] + "_") and any(word in row["case"] for word in
                ("two_distinct_matching_only", "duplicate_stars_do_not_count", "bench_excluded", "duplicate_recipient_gets_bonus_once", "opponent_types_do_not_enable_friendly", "four_instances_do_not_unlock_expansion_tier"))] for t in traits}
    checks = {
        "compile_exit0": process["compile_exit"] == 0,
        "actual_native_process_exit0": process["process_exit"] == 0,
        "all_reported_cases_pass": all(row["status"] == "PASS" for row in cases) and summary["failed"] == 0,
        "reported_case_count_reconciles": summary["cases"] == len(cases),
        "reported_assertions_reconcile": summary["assertions"] == sum(int(row["assertions"]) for row in cases),
        "all_ten_active_traits_have_twelve_boundary_groups": len(coverage) == 10 and all(len(rows) == 12 for rows in coverage.values()),
        "actual_damage_and_support_impacts_recorded": all(str(effect) in {row["effect"] for row in events} for effect in (0, 1, 2, 5)),
    }
    inputs = [BUILD / name for name in ("summary.json", "process.json", "trait-cases.csv", "trait-events.csv", "compile.log", "run.log", "trait_combat_tests.exe")]
    inputs += [ROOT / name for name in ("tests/runtime/trait_combat_tests.cpp", "tests/runtime/run_trait_combat.ps1", "tests/runtime/build/CatalogFixture.h",
                "tests/runtime/generate_catalog_fixture.py", "game/Source/WonderChessRuntime/Public/Simulation/WonderSimulation.h",
                "game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp", "data/traits.json", "data/units.json", "data/rules.alpha.json", "generated/catalog_digest.json")]
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "utc": datetime.now(timezone.utc).isoformat(),
              "native_results": summary, "process": process, "audit_checks": checks,
              "trait_groups": {key: len(rows) for key, rows in coverage.items()}, "impact_rows": len(events),
              "impact_rows_by_effect": dict(Counter(row["effect"] for row in events)),
              "boundary": "Compiled native MSVC executable invokes the actual production wc::Combat implementation. It is focused RULE-02 fixture evidence, not a new packaged/Unreal run, rendered effect review or balance acceptance. Snapshot groups isolate one parsed canonical trait at a time while preserving authored hero identities and values; overlap groups use the full catalog. Damage/support groups keep canonical trait identities/values but use explicitly controlled timing, damage, range, defense and ability selectors to expose source/recipient errors.",
              "scope": "Ten active alpha traits, threshold two only; snapshot recipient statistics at all three stars; distinct deployed types; duplicates across stars; bench exclusion; opposing-side separation; matching recipients; repeated recipients receive one bonus; four instances do not enable the disabled expansion tier. Star-one controlled actual impacts check Orc, Warrior, Ranger, Mage and Priest bonus categories, additive overlapping bonuses, no receiver-side support reapplication, no Orc/Mage support amplification and no Priest amplification of negative modifiers. Paired Elf/Rogue/combined traces check exact basic release intervals and repeated unchanged authored ability cooldown/release intervals.",
              "not_tested": ["Expansion threshold-four profiles or disabled halfling/dragonkin traits", "Live Unreal animation/audio/visual trait feedback", "All possible formations or a solved balance metagame"],
              "cases": cases, "inputs": [bind(path) for path in inputs]}
    (BASE / "validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Executed native alpha-trait matrix", "", f"**{result['status']}**: {summary['cases']} groups, {summary['failed']} failed, {summary['assertions']} assertions, {summary['combat_constructions']} actual Combat constructions.", "", result["boundary"], "", result["scope"], "",
             f"MSVC compile exit {process['compile_exit']}; native process exit {process['process_exit']}. Started {process['started_utc']}, ended {process['ended_utc']}. The report binds the test executable, exact production core, fixture generator/header, canonical source and all raw evidence with SHA256.", "",
             "Each of the ten active traits has twelve boundary groups. Actual damage/support impact rows are retained separately in build/trait-events.csv; these controlled inputs are clearly distinguished from the canonical formation matrix in the earlier targeted-native report.", "",
             "Expansion thresholds/traits, rendered trait presentation, and complete balance coverage were not tested by this fixture suite."]
    (BASE / "validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "native_results": summary, "audit_checks": checks, "impact_rows": len(events)}, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
