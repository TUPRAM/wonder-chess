"""Reconcile actual current-candidate native evidence without promoting balance."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
from statistics import median


def rows(directory: Path, name: str) -> list[dict[str, str]]:
    with (directory / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def summarize(directory: Path) -> dict:
    process = json.loads((directory / "process.json").read_text(encoding="utf-8-sig"))
    identity = json.loads((directory / "identity.json").read_text(encoding="utf-8-sig"))
    if process["compile_exit"] != 0 or process["test_exit"] != 0 or process["source_stable"] is not True:
        raise ValueError("Completed source-stable native execution required")
    tournaments = rows(directory, "tournaments.csv")
    encounters = rows(directory, "encounters.csv")
    units = rows(directory, "unit_activity.csv")
    traces = rows(directory, "mechanic_outcomes.csv")
    fixtures = rows(directory, "silkmother_formations.csv")
    expected = set(range(process["first_seed"], process["first_seed"] + process["requested_tournaments"]))
    if len(tournaments) != len(expected) or {int(r["seed"]) for r in tournaments} != expected:
        raise ValueError("Incomplete or duplicate tournament interval")
    if expected.intersection(range(900001, 900251)):
        raise ValueError("Reserved confirmation seeds must remain untouched")
    keys = {tuple(r[k] for k in ("seed", "round", "index")): r for r in encounters}
    if len(keys) != len(encounters):
        raise ValueError("Duplicate encounter identity")
    per_seed = Counter(r["seed"] for r in encounters)
    timeout_seed = Counter(r["seed"] for r in encounters if int(r["timeout"]))
    for row in tournaments:
        if int(row["encounters"]) != per_seed[row["seed"]] or int(row["timeouts"]) != timeout_seed[row["seed"]]:
            raise ValueError("Tournament encounter accounting mismatch")
        if int(row["command_rejects"]) or sum(int(row[k]) for k in ("preparation_ms", "combat_ms", "settlement_ms")) != int(row["simulated_ms"]):
            raise ValueError("Bot command or phase accounting failed")
    unit_totals = defaultdict(Counter)
    exposure = defaultdict(set)
    hero_totals = defaultdict(Counter)
    for row in units:
        key = tuple(row[k] for k in ("seed", "round", "index"))
        if key not in keys:
            raise ValueError("Unit activity without an encounter")
        exposure[row["hero"]].add(key)
        for field in ("damage_cp", "healing_cp", "cocoon_impacts"):
            unit_totals[key][field] += int(row[field])
        h = hero_totals[row["hero"]]
        h["unit_opportunities"] += 1
        h["survivors"] += int(int(row["final_health_cp"]) > 0)
        for field in ("damage_cp", "healing_cp", "basic_hits", "skill_damage_hits", "cocoon_impacts", "casts_committed", "last_5s_damage_cp", "last_5s_healing_cp"):
            h[field] += int(row[field])
    for key, row in keys.items():
        for unit_field, encounter_field in (("damage_cp", "damage_cp"), ("healing_cp", "effective_healing_cp"), ("cocoon_impacts", "cocoon_impacts")):
            if unit_totals[key][unit_field] != int(row[encounter_field]):
                raise ValueError("Unit/encounter event accounting mismatch")
    mechanic = defaultdict(Counter)
    for row in traces:
        if tuple(row[k] for k in ("seed", "round", "index")) not in keys:
            raise ValueError("Mechanic trace without an encounter")
        mechanic[row["hero"]][row["phase"] + "/" + row["reason"]] += int(row["count"])
    for hero, counts in mechanic.items():
        cancellations = sum(v for k, v in counts.items() if k.startswith("cancelled/"))
        if counts["committed/ready"] != counts["released/ready"] + cancellations:
            raise ValueError("Unreconciled mechanic commitments: " + hero)
    strata = {}
    for kind in ("overall", "pvp", "ghost", "neutral"):
        subset = [r for r in encounters if kind == "overall" or r["kind"] == kind]
        timeouts = sum(int(r["timeout"]) for r in subset)
        strata[kind] = {"encounters": len(subset), "timeouts": timeouts,
            "timeout_percent": 100 * timeouts / len(subset) if subset else None,
            "below_2_percent_screen": "INSUFFICIENT" if len(subset) < 100 else "PASS" if timeouts / len(subset) < .02 else "FAIL",
            "median_combat_seconds": median(int(r["ticks"]) * .05 for r in subset) if subset else None,
            "timeout_no_damage_last_5s": sum(int(r["timeout"]) and int(r["last_5s_damage_cp"]) == 0 for r in subset),
            "timeout_healing_at_least_damage_last_5s": sum(int(r["timeout"]) and int(r["last_5s_healing_cp"]) >= int(r["last_5s_damage_cp"]) for r in subset)}
    for hero, selected in exposure.items():
        hero_totals[hero]["encounter_exposure"] = len(selected)
        hero_totals[hero]["timeout_encounter_exposure"] = sum(int(keys[k]["timeout"]) for k in selected)
    pair_fields = ("fixture", "mirror", "star", "seed")
    pairs = defaultdict(dict)
    for row in fixtures:
        key = tuple(row[k] for k in pair_fields)
        if row["skill_enabled"] in pairs[key]:
            raise ValueError("Duplicate formation-control fixture")
        pairs[key][row["skill_enabled"]] = row
    if len(fixtures) != 96 or len(pairs) != 48 or any(set(p) != {"0", "1"} for p in pairs.values()):
        raise ValueError("Incomplete Silkmother formation/control matrix")
    comparison = defaultdict(Counter)
    for key, pair in pairs.items():
        off, on = pair["0"], pair["1"]
        if int(off["cocoon_impacts"]):
            raise ValueError("Skill-off control fabricated a cocoon")
        c = comparison[key[0]]
        c["pairs"] += 1
        c["on_delivered_control"] += int(int(on["cocoon_impacts"]) > 0)
        c["on_shorter"] += int(int(on["ticks"]) < int(off["ticks"]))
        c["on_longer"] += int(int(on["ticks"]) > int(off["ticks"]))
        c["winner_changes"] += int(on["winner"] != off["winner"])
        c["on_timeouts"] += int(on["timeout"])
        c["off_timeouts"] += int(off["timeout"])
    evidence_files = ("identity.json", "process.json", "tournaments.csv", "encounters.csv", "unit_activity.csv", "mechanic_outcomes.csv", "silkmother_formations.csv", "tests.log", "compile.log")
    return {"schema": "wonder-development-20260930-gameplay-1", "status": "RECONCILED", "identity": identity,
        "development_seeds": sorted(expected), "reserved_confirmation_seeds_used": False,
        "tournaments": len(tournaments), "caps": sum(int(r["capped"]) for r in tournaments),
        "median_simulated_minutes": median(int(r["simulated_ms"]) for r in tournaments) / 60000,
        "strata": strata, "hero_activity": hero_totals, "mechanic_outcomes": mechanic, "silkmother_fixture_comparison": comparison,
        "human_pacing": "NOT_RUN", "balance_promotion": "NONE", "human_or_release_acceptance": "NOT_ESTABLISHED",
        "boundaries": ["Actual native bot tournaments on the current unmodified canonical catalogue; diagnostic copies match authoritative events and final state.",
            "Simulated bot duration is not a normal-speed human 35–45-minute observation.",
            "Silkmother skill-off runs are isolated fixture controls, not a proposed gameplay balance profile.",
            "Hero timeout exposure is observational and confounded by allies, stars, opponents, economy and round; it does not establish causation.",
            "Cocoon duration is summed applied event duration, not summed damage or an independently measured effective prevented-damage value.",
            "Last-five-second damage and healing are authoritative event totals; they identify investigation candidates without proving a design correction."],
        "source_hashes": process["source_hashes"],
        "evidence_sha256": {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in evidence_files}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(args.directory)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"status": result["status"], "tournaments": result["tournaments"], "caps": result["caps"],
        "strata": result["strata"], "human_pacing": "NOT_RUN", "balance_promotion": "NONE"}))


if __name__ == "__main__":
    main()
