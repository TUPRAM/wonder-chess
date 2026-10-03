"""Prepare immutable native-only reservation experiments and compare real evidence."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import re
from pathlib import Path
from statistics import median

from development_20260930_diagnostics import summarize

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp"
HELPER = ROOT / "tools/vnext/development_20260930_diagnostics.cpp"
OBSERVER = ROOT / "tools/vnext/development_20260930_cocoon_observer.h"
CONTRACT = ROOT / "tests/runtime/vnext_combat_tests.cpp"
ANCHOR = "            if (a.mechanic == AbilityMechanic::CocoonProjectile && u.cocoonExpiry > tick_) continue;"
PATCH = """            if (a.mechanic == AbilityMechanic::CocoonProjectile)
            {
                if (u.cocoonExpiry > tick_) continue;
                // Isolated development experiment: avoid duplicate allied webs.
                // Live windups release naturally on interruption/death; released
                // packets reserve until impact even if their source is defeated.
                bool reserved = false;
                for (const auto &other : units_)
                    if (Alive(other) && other.side == s.side && other.id != s.id &&
                        other.state == ActionState::CastWindup && other.target == i &&
                        other.ability.mechanic == AbilityMechanic::CocoonProjectile)
                        reserved = true;
                for (const auto &pending : packets_)
                    if (pending.mechanic == AbilityMechanic::CocoonProjectile &&
                        pending.target == i && units_[pending.source].side == s.side)
                        reserved = true;
                if (reserved) continue;
            }"""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError("Snapshot injection anchor changed or ambiguous: " + old[:80])
    return source.replace(old, new)


def prepare(directory: Path, variant: str) -> None:
    directory.mkdir(parents=True, exist_ok=False)
    snapshots = directory / "source"
    snapshots.mkdir()
    core = CORE.read_text(encoding="utf-8-sig")
    if variant == "cocoon_reservation":
        core = replace_once(core, ANCHOR, PATCH)
    helper = HELPER.read_text(encoding="utf-8-sig")
    preamble = ("#define WC_COCOON_RESERVATION_EXPERIMENT 1\n" if variant == "cocoon_reservation" else "")
    preamble += '#include "' + OBSERVER.as_posix() + '"\n'
    helper = preamble + helper
    helper = replace_once(helper, "    std::map<wc::Id, Activity> activity;",
        '    cocoonstudy::Observe(combat,catalog,"tournament",seed,round,index,"none",1,-1,-1);\n    std::map<wc::Id, Activity> activity;')
    helper = replace_once(helper, "            Outcome(out,c); out << '\\n';",
        '            cocoonstudy::Observe(c,catalog,"fixture",seed,0,cocoonstudy::fixtureIndex++,exposed?"exposed":"protected",enabled,mirror,star);\n            Outcome(out,c); out << \'\\n\';')
    helper = replace_once(helper, '        Require(catalog.Validate().empty(), "Current canonical runtime catalogue invalid");',
        '        Require(catalog.Validate().empty(), "Current canonical runtime catalogue invalid");\n        cocoonstudy::RunContracts(catalog);')
    (snapshots / "WonderSimulation.cpp").write_text(core, encoding="utf-8")
    (snapshots / "diagnostics.cpp").write_text(helper, encoding="utf-8")
    (snapshots / "canonical-WonderSimulation.cpp").write_bytes(CORE.read_bytes())
    (snapshots / "original-diagnostics.cpp").write_bytes(HELPER.read_bytes())
    (snapshots / "cocoon-observer.h").write_bytes(OBSERVER.read_bytes())
    (snapshots / "preserved-vnext_combat_tests.cpp").write_bytes(CONTRACT.read_bytes())
    identity = {"schema": "wonder-isolated-cocoon-reservation-1", "variant": variant,
        "canonical_core_sha256": digest(CORE), "original_helper_sha256": digest(HELPER),
        "observer_sha256": digest(OBSERVER), "preserved_contract_sha256": digest(CONTRACT),
        "isolated_core_sha256": digest(snapshots / "WonderSimulation.cpp"),
        "instrumented_helper_sha256": digest(snapshots / "diagnostics.cpp"),
        "recipe": "Exclude targets of live allied cocoon windups or released packets" if variant == "cocoon_reservation" else "Unmodified canonical mechanics with additional observation",
        "canonical_modified": False, "balance_promotion": "NONE", "human_pacing": "NOT_RUN"}
    (directory / "variant.json").write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(identity))


def records(directory: Path, name: str) -> list[dict[str, str]]:
    with (directory / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def distribution(values: list[int]) -> dict:
    return {"n": len(values), "minimum": min(values) if values else None,
        "median": median(values) if values else None, "maximum": max(values) if values else None}


def contract_summary(directory: Path) -> dict:
    result = json.loads((directory / "reservation_contracts.json").read_text())
    match = re.search(r"PASS vNext native combat: (\d+) assertions", (directory / "tests.log").read_text(encoding="utf-8-sig"))
    if not match or result["status"] != "PASS":
        raise ValueError("Missing actual successful preserved-contract log")
    printed = int(match.group(1))
    reported = result["preserved_native_assertions"]
    if reported < printed:
        raise ValueError("Contract counter inconsistency")
    if reported != printed:
        # Earlier immutable manifests captured the shared tick-check counter at
        # the end of new fixtures. Reconcile the preserved subtotal from its
        # actual printed result without overwriting original execution evidence.
        result["original_manifest_assertion_counter"] = reported
        result["focused_fixture_tick_assertions"] = reported - printed
        result["preserved_native_assertions"] = printed
        result["counter_note"] = "Original manifest included focused fixture ticks; preserved subtotal reconciled against the actual native-suite log."
    return result


def describe_intervals(directory: Path) -> dict:
    rows = records(directory, "cocoon_intervals.csv")
    result = {}
    for label, selected in (("single_silkmother_encounter", [r for r in rows if int(r["silkmothers_in_encounter"]) == 1]),
                            ("tournament_single_silkmother_encounter", [r for r in rows if r["context"] == "tournament" and int(r["silkmothers_in_encounter"]) == 1]),
                            ("one_silkmother_on_source_side", [r for r in rows if int(r["silkmothers_on_source_side"]) == 1]),
                            ("all", rows)):
        repeated = [r for r in selected if int(r["previous_same_target_end_tick"]) >= 0]
        result[label] = {"impacts": len(selected), "same_source_target_repeats": len(repeated),
            "observed_control_ms": distribution([int(r["observed_control_ms"]) for r in selected]),
            "same_target_uncontrolled_gap_ms": distribution([int(r["gap_ms"]) for r in repeated]),
            "source_basic_hits_in_gap": distribution([int(r["source_basic_hits_in_gap"]) for r in repeated]),
            "target_damage_during_control_cp": distribution([int(r["target_damage_during_cp"]) for r in selected]),
            "target_healing_during_control_cp": distribution([int(r["target_healing_during_cp"]) for r in selected])}
    fixture = [r for r in rows if r["context"] == "fixture"]
    for label in ("protected", "exposed"):
        selected = [r for r in fixture if r["layout"] == label]
        repeated = [r for r in selected if int(r["previous_same_target_end_tick"]) >= 0]
        result["fixture_" + label] = {"impacts": len(selected), "repeated_same_target": len(repeated),
            "control_ms": distribution([int(r["observed_control_ms"]) for r in selected]),
            "gap_ms": distribution([int(r["gap_ms"]) for r in repeated]),
            "source_basics_in_gap": distribution([int(r["source_basic_hits_in_gap"]) for r in repeated])}
    fixture_units = records(directory, "fixture_unit_activity.csv")
    pairs = defaultdict(dict)
    for r in fixture_units:
        if r["hero"] == "wc_vn_silkmother":
            pairs[tuple(r[k] for k in ("layout", "mirror", "star", "seed"))][r["skill_enabled"]] = r
    if len(pairs) != 48 or any(set(p) != {"0", "1"} for p in pairs.values()):
        raise ValueError("Incomplete fixture unit activity pairs")
    result["paired_silkmother_basic_opportunity"] = {}
    for layout in ("protected", "exposed"):
        selected = [p for k, p in pairs.items() if k[0] == layout]
        result["paired_silkmother_basic_opportunity"][layout] = {
            "on_minus_off_basic_hits": distribution([int(p["1"]["basic_hits"]) - int(p["0"]["basic_hits"]) for p in selected]),
            "on_minus_off_damage_cp": distribution([int(p["1"]["damage_cp"]) - int(p["0"]["damage_cp"]) for p in selected]),
            "skill_on_casts": distribution([int(p["1"]["casts_committed"]) for p in selected])}
    return result


def compare(baseline: Path, candidate: Path, output: Path) -> None:
    a, b = summarize(baseline), summarize(candidate)
    av = json.loads((baseline / "variant.json").read_text())
    bv = json.loads((candidate / "variant.json").read_text())
    if av["variant"] != "baseline" or bv["variant"] != "cocoon_reservation":
        raise ValueError("Named baseline/candidate pair required")
    for key in ("canonical_core_sha256", "original_helper_sha256", "observer_sha256", "preserved_contract_sha256"):
        if av[key] != bv[key]:
            raise ValueError("Comparison source mismatch: " + key)
    if a["development_seeds"] != b["development_seeds"] or a["identity"]["catalog_digest"] != b["identity"]["catalog_digest"]:
        raise ValueError("Candidate differs in input seeds or catalogue")
    paired = {}
    for filename, fields in (("tournaments.csv", ("seed",)), ("silkmother_formations.csv", ("fixture", "skill_enabled", "mirror", "star", "seed"))):
        left = {tuple(r[k] for k in fields): r for r in records(baseline, filename)}
        right = {tuple(r[k] for k in fields): r for r in records(candidate, filename)}
        if set(left) != set(right):
            raise ValueError("Missing paired outcomes")
        changed = sum(left[k] != right[k] for k in left)
        paired[filename] = {"pairs": len(left), "changed_rows": changed,
            "candidate_shorter": sum(int(right[k].get("ticks", right[k].get("simulated_ms", 0))) < int(left[k].get("ticks", left[k].get("simulated_ms", 0))) for k in left),
            "candidate_longer": sum(int(right[k].get("ticks", right[k].get("simulated_ms", 0))) > int(left[k].get("ticks", left[k].get("simulated_ms", 0))) for k in left)}
        if filename == "tournaments.csv":
            paired[filename]["cap_removed_seeds"] = [int(k[0]) for k in left if left[k]["capped"] == "1" and right[k]["capped"] == "0"]
            paired[filename]["new_cap_seeds"] = [int(k[0]) for k in left if left[k]["capped"] == "0" and right[k]["capped"] == "1"]
    result = {"schema": "wonder-cocoon-reservation-comparison-1", "status": "RECONCILED", "baseline": a, "candidate": b,
        "paired_outcomes": paired, "baseline_control_intervals": describe_intervals(baseline), "candidate_control_intervals": describe_intervals(candidate),
        "contracts": {"baseline": contract_summary(baseline), "candidate": contract_summary(candidate)},
        "balance_promotion": "NONE", "human_pacing": "NOT_RUN", "reserved_confirmation_seeds_used": False,
        "additional_evidence_sha256": {label: {name: digest(directory / name) for name in (
            "variant.json", "reservation_contracts.json", "cocoon_intervals.csv", "fixture_unit_activity.csv",
            "source/WonderSimulation.cpp", "source/diagnostics.cpp", "source/canonical-WonderSimulation.cpp",
            "source/original-diagnostics.cpp", "source/cocoon-observer.h", "source/preserved-vnext_combat_tests.cpp")}
            for label, directory in (("baseline", baseline), ("candidate", candidate))},
        "boundaries": ["Only an output-directory source copy changes target reservation; canonical runtime and catalogue remain untouched.",
            "Actual seeded bot outcomes are development evidence, not human pacing or accepted balance.",
            "Observed control intervals end at authored expiry, reconstructed target defeat or end-of-combat observation; they do not measure hypothetical prevented damage.",
            "A single-Silkmother skill-on/off contrast isolates skill activation but does not identify every mediation path through targeting, healing, interruption and deaths."]}
    with output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2); handle.write("\n")
    print(json.dumps({"status": "RECONCILED", "baseline_caps": a["caps"], "candidate_caps": b["caps"],
        "baseline_timeouts": a["strata"]["overall"]["timeouts"], "candidate_timeouts": b["strata"]["overall"]["timeouts"], "paired_outcomes": paired, "balance_promotion": "NONE"}))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    prep = sub.add_parser("prepare"); prep.add_argument("directory", type=Path); prep.add_argument("--variant", choices=("baseline", "cocoon_reservation"), required=True)
    comparison = sub.add_parser("compare"); comparison.add_argument("baseline", type=Path); comparison.add_argument("candidate", type=Path); comparison.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "prepare": prepare(args.directory, args.variant)
    else: compare(args.baseline, args.candidate, args.output)


if __name__ == "__main__": main()
