"""Reconcile two native B1 experiment arms; never promote canonical tuning."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def quantile(values: list[int], proportion: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    position = (len(values) - 1) * proportion
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def validate_fixture_inputs(rows: list[dict]) -> None:
    groups = defaultdict(dict)
    for row in rows:
        key = (row["fixture"], row["mirrored"], row["star"])
        groups[key].setdefault(row["formation"], []).append(row)
    if len(groups) != 24:
        raise ValueError("Expected four formation pairs at three stars and two orientations")
    for (fixture, _, _), forms in groups.items():
        if set(forms) != {"0", "1"} or len(forms["0"]) != len(forms["1"]):
            raise ValueError("Missing equal-army formation input")
        expected_field = "row" if fixture == "charge_approach" else "column"
        changes = []
        for left, right in zip(forms["0"], forms["1"]):
            for field in left.keys() - {"formation"}:
                if left[field] != right[field]:
                    changes.append(field)
        if changes != [expected_field]:
            raise ValueError(f"{fixture}: army or undeclared formation input changed: {changes}")


def summarize_encounters(rows: list[dict], required: bool) -> dict:
    n = len(rows)
    timed = sum(int(row["timeout"]) for row in rows)
    rate = timed / n if n else None
    durations = [int(row["ticks"]) * 50 for row in rows]
    sums = {
        field: sum(int(row[field]) for row in rows)
        for field in (
            "health_damage_cp", "effective_healing_cp", "logged_recipient_overheal_cp",
            "guard_prevented_cp", "deaths", "crag_instances", "charging_sources",
            "charge_movement_landings", "charge_damage_cp",
        )
    }
    decisive = [row for row in rows if int(row["winner"]) >= 0]
    winning_survivors = [int(row["survivors_a"] if int(row["winner"]) == 0 else row["survivors_b"]) for row in decisive]
    return {
        "encounters": n,
        "timeouts": timed,
        "timeout_rate": rate,
        "timeout_screen": "insufficient" if required and n < 100 else (
            "pass" if required and rate < 0.02 else "fail" if required else "reported_only"
        ),
        "duration_ms_p50": quantile(durations, 0.5),
        "duration_ms_p90": quantile(durations, 0.9),
        "duration_ms_p99": quantile(durations, 0.99),
        "first_death_within_2s_encounters": sum(0 <= int(row["first_death_tick"]) <= 40 for row in rows),
        "no_death_encounters": sum(int(row["first_death_tick"]) < 0 for row in rows),
        "draws": n - len(decisive),
        "mean_winning_survivors": statistics.mean(winning_survivors) if winning_survivors else None,
        "timeout_with_roots_encounters": sum(
            int(row["timeout"]) and int(row["roots_a"]) + int(row["roots_b"]) > 0 for row in rows
        ),
        "timeout_with_three_or_more_same_hero_on_one_side": sum(
            int(row["timeout"]) and max(int(row["max_duplicates_a"]), int(row["max_duplicates_b"])) >= 3
            for row in rows
        ),
        **sums,
    }


def arm(path: Path, expected_variant: str) -> dict:
    process = read_json(path / "process.json")
    identity = read_json(path / "variant.json")
    if process.get("compile_exit") != 0 or process.get("test_exit") != 0 or process.get("source_stable") is not True:
        raise ValueError(f"{path}: incomplete, failed, or source-drift run")
    if identity["variant"] != expected_variant:
        raise ValueError(f"{path}: expected {expected_variant}")
    tournaments = read_rows(path / "tournaments.csv")
    if not tournaments:
        raise ValueError(f"{path}: comparison requires at least one completed tournament")
    encounters = read_rows(path / "encounters.csv")
    recruitment = read_rows(path / "recruitment.csv")
    fixtures = read_rows(path / "fixtures.csv")
    validate_fixture_inputs(read_rows(path / "fixture_inputs.csv"))
    charge_actions = read_rows(path / "fixture_charge_actions.csv")
    seeds = sorted(int(row["seed"]) for row in tournaments)
    expected = list(range(identity["first_seed"], identity["first_seed"] + identity["tournaments"]))
    if seeds != expected:
        raise ValueError(f"{path}: missing, duplicated, or extra tournament seed")
    by_seed = defaultdict(list)
    for row in encounters:
        by_seed[int(row["seed"])].append(row)
    for row in tournaments:
        cohort = by_seed[int(row["seed"])]
        if len(cohort) != int(row["encounters"]) or sum(int(item["timeout"]) for item in cohort) != int(row["timeouts"]):
            raise ValueError(f"{path}: encounter/tournament totals disagree")
        if int(row["command_rejects"]) != 0:
            raise ValueError(f"{path}: rejected bot command")
    usage = defaultdict(lambda: defaultdict(int))
    for row in recruitment:
        for field in sorted(row.keys() - {"variant", "seed", "hero"}):
            usage[row["hero"]][field] += int(row[field])
    total_deployed = sum(value["deployed_unit_rounds"] for value in usage.values())
    for hero in usage.values():
        hero["deployment_share"] = hero["deployed_unit_rounds"] / total_deployed if total_deployed else 0
        hero["purchase_per_exposed_slot"] = hero["purchased_copies"] / hero["new_offer_slots"] if hero["new_offer_slots"] else None
    fixture_groups = defaultdict(list)
    for row in fixtures:
        fixture_groups[(row["fixture"], row["formation"], row["star"])].append(row)
    fixture_summary = []
    for (fixture, formation, star), cohort in sorted(fixture_groups.items()):
        # Side swapping puts the experimentally placed army on side 1 for mirrored fixtures.
        placed_wins = sum(int(row["winner"]) == int(row["mirrored"]) for row in cohort)
        fixture_summary.append({
            "fixture": fixture, "formation": int(formation), "star": int(star),
            "placed_army_wins": placed_wins,
            **summarize_encounters(cohort, False),
        })
    phases = {
        field: statistics.median(int(row[field]) for row in tournaments)
        for field in ("simulated_ms", "preparation_ms", "combat_ms", "settlement_ms")
    } if tournaments else {}
    charge_formations = []
    for fixture in ("charge_approach", "charge_own_screen"):
        for formation in (0, 1):
            # Native constructor packs fixture OwnedUnit.id below bit 20; actor 1 is the declared Cragstoat.
            cohort = [row for row in charge_actions if row["fixture"] == fixture
                      and int(row["formation"]) == formation and int(row["source"]) % (1 << 20) == 1]
            resolved = [row for row in cohort if row["outcome"] == "resolved_charge_event"]
            encounters_with_release = {(row["mirrored"], row["star"], row["seed"]) for row in resolved}
            charge_formations.append({
                "fixture": fixture, "formation": formation, "actor_owned_id": 1,
                "encounters": sum(row["fixture"] == fixture and int(row["formation"]) == formation for row in fixtures),
                "actor_commitments": len(cohort), "actor_resolved_charge_actions": len(resolved),
                "actor_encounters_with_resolved_charge": len(encounters_with_release),
                "actor_commitments_without_resolved_event": len(cohort) - len(resolved),
            })
    return {
        "path": str(path.resolve()), "identity": identity,
        "source_hashes": process["source_hashes"], "executable_sha256": process["executable_sha256"],
        "seed_ids": seeds, "tournaments": len(tournaments),
        "round_caps": sum(int(row["capped"]) for row in tournaments),
        "median_phase_ms": phases,
        "strata": {
            kind: summarize_encounters([row for row in encounters if kind == "overall" or row["kind"] == kind], kind != "neutral")
            for kind in ("overall", "pvp", "ghost", "neutral")
        },
        "recruitment": dict(usage), "fixed_army_fixtures": fixture_summary,
        "cragstoat_placement": charge_formations,
        "raw_evidence_sha256": {
            name: hashlib.sha256((path / name).read_bytes()).hexdigest()
            for name in ("encounters.csv", "tournaments.csv", "recruitment.csv", "fixtures.csv", "fixture_inputs.csv", "fixture_charge_actions.csv")
        },
    }


def analyze(control_path: Path, candidate_path: Path) -> dict:
    control, candidate = arm(control_path, "control"), arm(candidate_path, "root75")
    if control["seed_ids"] != candidate["seed_ids"] or control["source_hashes"] != candidate["source_hashes"]:
        raise ValueError("Comparison needs identical source inputs and paired seed intervals")
    if control["identity"]["origin_catalog_digest"] != candidate["identity"]["origin_catalog_digest"]:
        raise ValueError("Comparison origins differ")
    if control["raw_evidence_sha256"]["fixture_inputs.csv"] != candidate["raw_evidence_sha256"]["fixture_inputs.csv"]:
        raise ValueError("Controlled fixture armies differ across tuning variants")
    screens = [candidate["strata"][kind]["timeout_screen"] for kind in ("overall", "pvp", "ghost")]
    return {
        "schema": "wonder_vnext.b1_balance_comparison.1",
        "control": control, "root75": candidate,
        "candidate_numeric_screen": "fail" if "fail" in screens else "insufficient" if "insufficient" in screens else "pass",
        "promotion": "not_promoted",
        "limitations": [
            "Unchanged provisional bot code revalues the changed healing magnitude; tournament changes include recruitment and matchup drift.",
            "Encounter counts within tournaments are clustered; no independence or population inference is claimed.",
            "Healing overheal includes requested minus resolved at logged injured recipients only. Full-health recipients and cancelled tethered pulses emit no heal event; unlogged healing opportunity is unavailable.",
            "Charge movement landings exclude zero-distance successful charges. Charging sources require a resolved charge damage event. Fixture commitments without resolved events cannot distinguish interruption, changed target, illegal landing, or no remaining recipient with this telemetry.",
            "Two-second first-death and duplicate-composition summaries are descriptive investigation aids, not adopted acceptance criteria.",
            "Mirrored side swaps probe orientation sensitivity; stochastic initiative and tie-breaking do not guarantee equal winner rates in a small fixture set.",
            "Bot-ready simulated tournament timing does not measure human match pacing. Human comprehension, sustain utility and enjoyment remain untested.",
        ],
    }


def markdown(result: dict) -> str:
    lines = [
        "# B1 controlled balance experiment", "",
        f"Native execution completed for {result['control']['tournaments']} paired seed IDs per arm. "
        f"The Root75 candidate's provisional numeric screen is **{result['candidate_numeric_screen'].upper()}**. "
        "Canonical tuning is unchanged and no human acceptance is claimed.", "",
        "| Arm / stratum | Encounters | Timeouts | Rate | Median / p90 seconds | Screen |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for name in ("control", "root75"):
        for kind, row in result[name]["strata"].items():
            rate = f"{row['timeout_rate']:.3%}" if row["timeout_rate"] is not None else "n/a"
            median = f"{row['duration_ms_p50']/1000:.2f}" if row["duration_ms_p50"] is not None else "n/a"
            p90 = f"{row['duration_ms_p90']/1000:.2f}" if row["duration_ms_p90"] is not None else "n/a"
            lines.append(f"| {name} / {kind} | {row['encounters']:,} | {row['timeouts']:,} | "
                         f"{rate} | {median} / {p90} | {row['timeout_screen']} |")
    lines += ["", f"Round caps: **{result['control']['round_caps']}/{result['control']['tournaments']} control** and "
              f"**{result['root75']['round_caps']}/{result['root75']['tournaments']} Root75**. "
              "These are separate from combat timeouts; a shorter fight does not guarantee a resolved tournament.", "",
              "The only experimental tuning edit is `HalfUp(base_pulse * 7500 / 10000)` on Grandmother Root's three star magnitudes, "
              "in an in-memory copy of the generated canonical catalog. Timing, geometry, stars, relic evaluation, basic damage, "
              "bot policy and timeout adjudication remain the source control. Exact source/executable/evidence hashes are in the companion JSON.", "",
              "## Recruitment and deployed composition", "",
              "| Hero | Control / candidate purchases | Control / candidate deployment share |",
              "|---|---:|---:|"]
    for hero, values in result["control"]["recruitment"].items():
        other = result["root75"]["recruitment"][hero]
        lines.append(f"| {hero} | {values['purchased_copies']:,} / {other['purchased_copies']:,} | "
                     f"{values['deployment_share']:.2%} / {other['deployment_share']:.2%} |")
    lines += ["", "New offer slots, affordability and legal buy feasibility at first observed offer are logged. "
              "Actual buys inferred from consumed shop slots reconcile against accepted authoritative bot buy replies for every tournament. "
              "Deployment is counted once per live-seat combat lock; ghost copies do not inflate ownership. "
              "Star levels represent 1/3/9 acquired copies for investment and deployment-copy totals.", "",
              "## Fixed-army and charge evidence", "",
              "Four formation pairs are run at all three star levels, four fixed seeds and both side orientations (192 encounters per arm). "
              "Both formations preserve the literal armies and equal represented-copy investment; each pair changes one declared cell component. "
              "Every encounter is replayed and compared event by event. `fixture_inputs.csv` stores inputs; `fixtures.csv` stores complete results; "
              "`fixture_charge_actions.csv` stores every observed Cragstoat commitment and its resolved-event classification. "
              "The JSON preserves each formation/star cohort without treating a placement as a guaranteed improvement.", "",
              "| Arm / formation | Actor commits | Resolved charges | Encounters with actor charge |",
              "|---|---:|---:|---:|"]
    for name in ("control", "root75"):
        for row in result[name]["cragstoat_placement"]:
            lines.append(f"| {name} / {row['fixture']} {row['formation']} | {row['actor_commitments']} | "
                         f"{row['actor_resolved_charge_actions']} | {row['actor_encounters_with_resolved_charge']}/{row['encounters']} |")
    lines += ["", "In `charge_approach`, formation 0 starts the same Cragstoat in row 3 and formation 1 in row 0, "
              "providing room to approach. In `charge_own_screen`, both start Cragstoat in row 0; formation 1 moves Bellback "
              "from column 1 to column 3. A screen need not prevent every later charge because units continue moving. "
              "These actor-specific counts exclude the opponent's Cragstoat and include all star levels and mirrored orientations.", "",
              "## Scope and unresolved evidence", ""]
    lines.extend(f"- {item}" for item in result["limitations"])
    lines += ["", "The unused confirmation set remains reserved until a candidate is eligible for confirmation. "
              "A failed numerical screen does not justify consuming holdout seeds or approving weaker positional sustain. "
              "Required next work is to investigate the failed strata and round-cap mechanism, test practical early pressure, "
              "instrument charge rejection reasons, and run the separate normal-speed external-player study.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.control, args.candidate)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(markdown(result), encoding="utf-8")
    print(json.dumps({"numeric_screen": result["candidate_numeric_screen"], "paired_seeds": result["control"]["tournaments"], "promotion": result["promotion"]}))


if __name__ == "__main__":
    main()
