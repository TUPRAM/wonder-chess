"""Reconcile completed native diagnostic runs; never promote a balance candidate."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
from statistics import mean, median


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def summarize(directory: Path) -> dict:
    process = json.loads((directory / "process.json").read_text(encoding="utf-8-sig"))
    if not (process["compile_exit"] == 0 and process["test_exit"] == 0
            and process["source_stable"] is True and process["diagnostics"] is True):
        raise ValueError("A completed, source-stable diagnostic run is required")
    tournaments, encounters, traces, seats, recruitment = [rows(directory / name) for name in (
        "tournaments.csv", "encounters.csv", "mechanic_outcomes.csv", "seat_rounds.csv", "recruitment_by_level.csv")]
    seeds = {int(row["seed"]) for row in tournaments}
    expected = set(range(process["first_seed"], process["first_seed"] + process["requested_tournaments"]))
    if seeds != expected or len(tournaments) != len(expected):
        raise ValueError("Missing or duplicate tournament seeds")
    encounter_counts, timeout_counts = Counter(), Counter()
    keys = set()
    for row in encounters:
        key = tuple(row[k] for k in ("seed", "round", "index"))
        if key in keys or int(row["seed"]) not in seeds:
            raise ValueError("Unexpected or duplicate encounter")
        keys.add(key)
        encounter_counts[row["seed"]] += 1
        timeout_counts[row["seed"]] += int(row["timeout"])
    for row in tournaments:
        if (int(row["encounters"]) != encounter_counts[row["seed"]]
                or int(row["timeouts"]) != timeout_counts[row["seed"]]
                or int(row["command_rejects"]) != 0):
            raise ValueError("Encounter accounting or command rejection failed")
    trace_counts, pulse_totals = defaultdict(Counter), defaultdict(Counter)
    for row in traces:
        if tuple(row[k] for k in ("seed", "round", "index")) not in keys:
            raise ValueError("Mechanic trace has no encounter")
        trace_counts[row["hero"]][row["phase"] + "/" + row["reason"]] += int(row["count"])
        if row["phase"] == "impact":
            for field in ("recipients", "full_health_ally_pulses", "requested_cp", "resolved_cp"):
                pulse_totals[row["hero"]][field] += int(row[field])
    for hero, counts in trace_counts.items():
        cancelled = sum(value for key, value in counts.items() if key.startswith("cancelled/"))
        if counts["committed/ready"] != counts["released/ready"] + cancelled:
            raise ValueError("Incomplete commitment outcomes: " + hero)
    grove = "wc_vn_grandmother_root"
    if pulse_totals[grove]["resolved_cp"] != sum(int(row["effective_healing_cp"]) for row in encounters):
        raise ValueError("Grove diagnostics do not reconcile with encounter healing")
    for row in seats:
        if max(0, int(row["health_before"]) - int(row["damage"])) != int(row["health_after"]):
            raise ValueError("Captain damage does not reconcile")
    strata = {}
    for kind in ("pvp", "ghost", "neutral"):
        selected = [row for row in encounters if row["kind"] == kind]
        timeouts = sum(int(row["timeout"]) for row in selected)
        strata[kind] = {"encounters": len(selected), "timeouts": timeouts,
            "timeout_percent": 100 * timeouts / len(selected) if selected else None,
            "draws": sum(row["winner"] == "-1" for row in selected),
            "mean_deaths": mean(int(row["deaths"]) for row in selected) if selected else None,
            "timeout_screen": "INSUFFICIENT" if len(selected) < 100 else "PASS" if timeouts / len(selected) < .02 else "FAIL"}
    round_damage = []
    for low, high in ((1, 10), (11, 20), (21, 30), (31, 40), (41, 45)):
        selected = [row for row in seats if low <= int(row["round"]) <= high and row["kind"] != "neutral"]
        positive = [int(row["damage"]) for row in selected if int(row["damage"]) > 0]
        round_damage.append({"rounds": [low, high], "seat_rounds": len(selected),
            "damaged_seat_rounds": len(positive), "mean_positive_damage": mean(positive) if positive else None})
    access = defaultdict(Counter)
    for row in recruitment:
        key = row["hero"] + "/level_" + row["level"]
        for field in ("new_offer_slots", "affordable_at_first_observed_offer", "legal_buy_at_first_observed_offer",
                      "purchased_copies", "deployed_unit_rounds"):
            access[key][field] += int(row[field])
    capped_seeds = {row["seed"] for row in tournaments if row["capped"] == "1"}
    last_round = {row["seed"]: row["rounds"] for row in tournaments}
    remaining = [int(row["health_after"]) for row in seats if row["seed"] in capped_seeds
                 and row["round"] == last_round[row["seed"]] and int(row["health_after"]) > 0]
    files = ("process.json", "variant.json", "tournaments.csv", "encounters.csv", "mechanic_outcomes.csv",
             "seat_rounds.csv", "recruitment_by_level.csv", "recruitment.csv", "fixtures.csv")
    return {"directory": str(directory.resolve()), "variant": process["variant"], "seeds": sorted(seeds),
        "tournaments": len(tournaments), "caps": len(capped_seeds), "encounters": len(encounters),
        "timeouts": sum(timeout_counts.values()), "median_simulated_minutes": median(int(r["simulated_ms"]) for r in tournaments) / 60000,
        "strata": strata, "mechanic_outcomes": trace_counts, "impact_totals": pulse_totals,
        "round_damage": round_damage, "recruitment_by_observed_level": access,
        "captains_alive_at_cap": len(remaining), "median_health_at_cap": median(remaining) if remaining else None,
        "source_hashes": process["source_hashes"],
        "evidence_sha256": {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in files}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control", required=True, type=Path)
    parser.add_argument("--root75", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    control, experiment = summarize(args.control), summarize(args.root75)
    if control["variant"] != "control" or experiment["variant"] != "root75" or control["seeds"] != experiment["seeds"]:
        raise ValueError("Comparison needs the named arms on identical seeds")
    if control["source_hashes"] != experiment["source_hashes"]:
        raise ValueError("Comparison was not built from identical source inputs")
    result = {"schema": "wonder-vnext-mechanic-diagnostics-1", "status": "RECONCILED", "control": control,
        "root75": experiment, "balance_promotion": "NONE",
        "reserved_confirmation_seeds_used": bool(set(control["seeds"]) & set(range(900001, 900251))),
        "boundaries": ["Development seeds and automated bot policies; no human playtest or enjoyment evidence.",
            "Attempt means a cooldown-ready decision opportunity, not an independent encounter or unique creature.",
            "Full-health ally-pulses count geometric exclusions, not discarded healing packets or a quantified heal budget.",
            "Grove requested/resolved are summed selected-recipient centipoints; charge requested is base magnitude before momentum bonuses and resolved is actual health loss.",
            "Recruitment level is the level when the shop transition was observed; a bot may level between the offer and purchase observations.",
            "Root75 changes only in-memory pulse magnitude. Recruitment and later combat composition can respond to that change."]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"status": result["status"], "control_caps": control["caps"], "root75_caps": experiment["caps"],
                      "control_encounters": control["encounters"], "root75_encounters": experiment["encounters"],
                      "balance_promotion": "NONE", "output": str(args.output)}))


if __name__ == "__main__":
    main()
