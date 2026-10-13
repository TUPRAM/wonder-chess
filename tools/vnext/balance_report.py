"""Summarise a native tournament run for balance work.

Input: a run directory written by tests/runtime/run_vnext_tournament.ps1 (tournaments.csv,
seats.csv, boards.csv, traits.csv, settlements.csv, waves.csv, placements.csv).
Output: report.json and REPORT.md in --output.

Bot tournaments only. Nothing here is human evidence or balance acceptance.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET_MINUTES = (35, 45)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def mean(values) -> float | None:
    values = list(values)
    return round(statistics.fmean(values), 3) if values else None


def preparation_ms(rules: dict, round_number: int) -> int:
    if round_number == 1:
        return rules["firstPreparationMs"]
    for stage in rules.get("preparationStages", []):
        if stage["start"] <= round_number <= stage["end"]:
            return stage["ms"]
    return rules["preparationMs"]


def analyse(run: Path, catalog: dict) -> dict:
    rules = catalog["rules"]
    heroes = {hero["id"]: hero for hero in catalog["heroes"] if hero["enabled"]}
    tournaments = rows(run / "tournaments.csv")
    placements = {(r["seed"], r["seat"]): r for r in rows(run / "placements.csv")}
    seats = rows(run / "seats.csv")
    boards = rows(run / "boards.csv")
    traits = rows(run / "traits.csv")
    waves = rows(run / "waves.csv")

    # Match length. The ceiling adds the full configured preparation time for every round,
    # as if a player used all of it; bots finish preparing in seconds.
    lengths = []
    for match in tournaments:
        played = int(match["rounds"])
        fixed = int(match["combat_ms"]) + int(match["settlement_ms"])
        ceiling = fixed + sum(preparation_ms(rules, number) for number in range(1, played + 1))
        lengths.append({"rounds": played, "simulated_min": int(match["simulated_ms"]) / 60000,
                        "combat_min": int(match["combat_ms"]) / 60000, "ceiling_min": ceiling / 60000})
    encounters = sum(int(m["encounters"]) for m in tournaments)
    timeouts = sum(int(m["timeouts"]) for m in tournaments)
    ceilings = [x["ceiling_min"] for x in lengths]
    match_summary = {
        "matches": len(tournaments),
        "median_rounds": statistics.median(x["rounds"] for x in lengths),
        "rounds_p10_p90": [sorted(x["rounds"] for x in lengths)[int(len(lengths) * q)] for q in (0.1, 0.9)],
        "median_simulated_minutes": round(statistics.median(x["simulated_min"] for x in lengths), 1),
        "median_combat_minutes": round(statistics.median(x["combat_min"] for x in lengths), 1),
        "median_player_time_ceiling_minutes": round(statistics.median(ceilings), 1),
        "share_ceiling_in_target": round(sum(TARGET_MINUTES[0] <= c <= TARGET_MINUTES[1] for c in ceilings) / len(ceilings), 3),
        "timeout_rate": round(timeouts / encounters, 4),
        "capped_matches": sum(int(m["capped"]) for m in tournaments),
    }

    # Final board per seat: the last preparation the seat locked.
    last_round: dict[tuple[str, str], int] = {}
    for r in seats:
        key = (r["seed"], r["seat"])
        last_round[key] = max(last_round.get(key, 0), int(r["round"]))
    seat_rounds = len(seats)
    seat_count = len(last_round)

    slots_by_hero: dict[str, int] = defaultdict(int)
    final_seats_by_hero: dict[str, set] = defaultdict(set)
    stars_by_hero: dict[str, list[int]] = defaultdict(list)
    for r in boards:
        slots_by_hero[r["hero"]] += 1
        key = (r["seed"], r["seat"])
        if int(r["round"]) == last_round[key]:
            final_seats_by_hero[r["hero"]].add(key)
            stars_by_hero[r["hero"]].append(int(r["star"]))
    slots_by_cost: dict[int, list[int]] = defaultdict(list)
    for hero_id, hero in heroes.items():
        slots_by_cost[hero["cost"]].append(slots_by_hero.get(hero_id, 0))
    hero_table = []
    for hero_id, hero in heroes.items():
        cost_mean = statistics.fmean(slots_by_cost[hero["cost"]]) or 1
        finals = final_seats_by_hero.get(hero_id, set())
        hero_table.append({
            "hero": hero["name"], "id": hero_id, "cost": hero["cost"], "class": hero["unit_class"], "race": hero["race"],
            "board_slots": slots_by_hero.get(hero_id, 0),
            "pick_vs_cost_mean": round(slots_by_hero.get(hero_id, 0) / cost_mean, 2),
            "final_board_share": round(len(finals) / seat_count, 3),
            "placement_on_final_board": mean(int(placements[k]["placement"]) for k in finals),
            "final_board_samples": len(finals),
            "mean_final_star": mean(stars_by_hero.get(hero_id, [])),
        })
    hero_table.sort(key=lambda h: (h["cost"], h["hero"]))

    trait_final: dict[str, dict[int, set]] = defaultdict(lambda: defaultdict(set))
    trait_rounds: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for r in traits:
        tier = int(r["tier"])
        trait_rounds[r["trait"]][tier] += 1
        key = (r["seed"], r["seat"])
        if int(r["round"]) == last_round[key]:
            trait_final[r["trait"]][tier].add(key)
    trait_table = []
    for trait in catalog["traits"]:
        if not trait["runtime_enabled"]:
            continue
        final, by_round = trait_final[trait["id"]], trait_rounds[trait["id"]]
        active = final[1] | final[2]
        trait_table.append({
            "trait": trait["name"], "kind": trait["kind"],
            "seat_round_share_tier1": round(by_round[1] / seat_rounds, 3),
            "seat_round_share_tier2": round(by_round[2] / seat_rounds, 3),
            "final_board_share_active": round(len(active) / seat_count, 3),
            "placement_tier1": mean(int(placements[k]["placement"]) for k in final[1]),
            "placement_tier2": mean(int(placements[k]["placement"]) for k in final[2]),
            "samples_tier1": len(final[1]), "samples_tier2": len(final[2]),
        })

    wave_table = []
    by_wave: dict[int, list[dict]] = defaultdict(list)
    for r in waves:
        by_wave[int(r["round"])].append(r)
    for round_number in sorted(by_wave):
        group = by_wave[round_number]
        wave_table.append({
            "round": round_number, "wave": group[0]["wave"], "fights": len(group),
            "clear_rate": round(sum(r["result"] == "won" for r in group) / len(group), 3),
            "draw_rate": round(sum(r["result"] == "draw" for r in group) / len(group), 3),
            "timeout_rate": round(sum(int(r["timeout"]) for r in group) / len(group), 3),
            "median_seconds": round(statistics.median(int(r["ticks"]) for r in group) * rules["tickMs"] / 1000, 1),
        })

    economy = []
    by_round: dict[int, list[dict]] = defaultdict(list)
    for r in seats:
        by_round[int(r["round"])].append(r)
    for round_number in sorted(by_round):
        if round_number not in (1, 3, 5) and round_number % 5:
            continue
        group = by_round[round_number]
        economy.append({
            "round": round_number, "seats": len(group),
            "median_gold": statistics.median(int(r["gold"]) for r in group),
            "median_level": statistics.median(int(r["level"]) for r in group),
            "median_deployed": statistics.median(int(r["deployed"]) for r in group),
            "median_board_cost": statistics.median(int(r["board_cost"]) for r in group),
        })

    bots: dict[str, list[int]] = defaultdict(list)
    for r in placements.values():
        bots[r["bot"]].append(int(r["placement"]))
    bot_table = [{"bot": bot, "seats": len(values), "mean_placement": mean(values)} for bot, values in sorted(bots.items())]

    summary = json.loads((run / "summary.json").read_text(encoding="utf-8")) if (run / "summary.json").exists() else {}
    return {"run": run.name, "balance_version": summary.get("balance_version", catalog["balance_version"]),
            "catalog_digest": summary.get("catalog_digest"), "boundary": "bot tournaments only; not human or balance acceptance",
            "match": match_summary, "heroes": hero_table, "traits": trait_table, "waves": wave_table,
            "economy": economy, "bots": bot_table}


def table(headers: list[str], body: list[list]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines += ["| " + " | ".join("-" if cell is None else str(cell) for cell in row) + " |" for row in body]
    return lines + [""]


def markdown(report: dict, baseline: dict | None) -> str:
    m = report["match"]
    lines = [f"# Balance run: {report['run']}", "",
             f"Balance version `{report['balance_version']}`. {m['matches']} bot tournaments. "
             "Bot play only; not human evidence and not balance acceptance.", "", "## Match", ""]
    keys = [("Median rounds", "median_rounds"), ("Rounds, 10th-90th percentile", "rounds_p10_p90"),
            ("Median simulated minutes (bots)", "median_simulated_minutes"), ("Median fight minutes", "median_combat_minutes"),
            ("Median player-time ceiling, minutes", "median_player_time_ceiling_minutes"),
            ("Share of matches with ceiling in 35-45 min", "share_ceiling_in_target"),
            ("Fights ending by timeout", "timeout_rate"), ("Matches hitting the round cap", "capped_matches")]
    if baseline:
        lines += table(["Measure", "This run", "Baseline"], [[label, m[key], baseline["match"].get(key)] for label, key in keys])
    else:
        lines += table(["Measure", "Value"], [[label, m[key]] for label, key in keys])
    base_heroes = {h["id"]: h for h in baseline["heroes"]} if baseline else {}
    lines += ["## Heroes", "", "Placement is the mean final placement of seats that ended with the hero on the board (4.5 is neutral, lower is better).", ""]
    lines += table(["Cost", "Hero", "Class", "Pick vs cost mean", "Final boards", "Placement", "Samples"] + (["Placement, baseline"] if baseline else []),
                   [[h["cost"], h["hero"], h["class"], h["pick_vs_cost_mean"], h["final_board_share"], h["placement_on_final_board"],
                     h["final_board_samples"]] + ([base_heroes.get(h["id"], {}).get("placement_on_final_board")] if baseline else [])
                    for h in report["heroes"]])
    lines += ["## Traits", ""]
    lines += table(["Trait", "Kind", "Seat-rounds at 2", "Seat-rounds at 4", "Final boards active", "Placement at 2", "Placement at 4"],
                   [[t["trait"], t["kind"], t["seat_round_share_tier1"], t["seat_round_share_tier2"], t["final_board_share_active"],
                     t["placement_tier1"], t["placement_tier2"]] for t in report["traits"]])
    lines += ["## Monster waves", ""]
    lines += table(["Round", "Wave", "Fights", "Cleared", "Draw", "Timeout", "Median seconds"],
                   [[w["round"], w["wave"], w["fights"], w["clear_rate"], w["draw_rate"], w["timeout_rate"], w["median_seconds"]]
                    for w in report["waves"]])
    lines += ["## Economy at lock", ""]
    lines += table(["Round", "Seats alive", "Median gold", "Median level", "Median deployed", "Median board cost"],
                   [[e["round"], e["seats"], e["median_gold"], e["median_level"], e["median_deployed"], e["median_board_cost"]]
                    for e in report["economy"]])
    lines += ["## Bot profiles", ""]
    lines += table(["Bot", "Seats", "Mean placement"], [[b["bot"], b["seats"], b["mean_placement"]] for b in report["bots"]])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, help="report.json of an earlier run to show beside this one")
    parser.add_argument("--catalog", type=Path, default=ROOT / "data/vnext/catalog.json")
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    report = analyse(args.run, catalog)
    baseline = json.loads(args.baseline.read_text(encoding="utf-8")) if args.baseline else None
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    (args.output / "REPORT.md").write_text(markdown(report, baseline), encoding="utf-8")
    print(json.dumps(report["match"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
