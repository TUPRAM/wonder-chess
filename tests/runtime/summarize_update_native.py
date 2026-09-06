"""Summarize a completed native run without promoting it to packaged evidence."""
import argparse
import collections
import csv
import hashlib
import json
import re
import statistics
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("run_directory", type=Path)
args = parser.parse_args()
root = args.run_directory.resolve()


def rows(name):
    with (root / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


process = json.loads((root / "process.json").read_text(encoding="utf-8-sig"))
if process["compile_exit"] or process["process_exit"]:
    raise SystemExit("Cannot summarize a failed process as accepted execution")
log = (root / "runtime-tests.log").read_text(encoding="utf-8-sig")
passed = re.search(r"PASS assertions=(\d+) data_digest=([0-9a-f]{64})", log)
if not passed:
    raise SystemExit("Missing final native assertion result")
tournaments = rows("tournaments.csv")
expected = process["requested_tournaments"]
if [int(row["seed"]) for row in tournaments] != list(range(1, expected + 1)):
    raise SystemExit("Tournament evidence has missing, duplicate or reordered seeds")
encounters = rows("encounter-outcomes.csv")
abilities = rows("ability-coverage.csv")
traits = rows("trait-coverage.csv")
compositions = rows("compositions.csv")
waves = {}
for row in encounters:
    if row["kind"] != "2":
        continue
    wave = waves.setdefault(row["round"], collections.Counter())
    wave["encounters"] += 1
    outcome = "wins" if row["winner"] == "0" else "losses" if row["winner"] == "1" else "draws"
    wave[outcome] += 1
    wave["timeouts"] += int(row["timeout"])


def extent(values):
    return [min(values), statistics.median(values), max(values)] if values else []


summary = {
    "status": "PASS_NATIVE_EXECUTION_ONLY",
    "content_digest": passed[2],
    "assertions": int(passed[1]),
    "tournaments": len(tournaments),
    "seed_range": [1, expected] if expected else [],
    "encounters": sum(int(row["encounters"]) for row in tournaments),
    "combat_events": sum(int(row["combat_events"]) for row in tournaments),
    "timeouts": sum(int(row["timeouts"]) for row in tournaments),
    "ghosts": sum(int(row["ghosts"]) for row in tournaments),
    "bot_rejects": sum(int(row["bot_rejects"]) for row in tournaments),
    "rounds_min_median_max": extent([int(row["rounds"]) for row in tournaments]),
    "simulated_seconds_min_median_max": extent([int(row["simulated_ms"]) / 1000 for row in tournaments]),
    "hero_definitions": sorted({row["definition"] for row in compositions}),
    "hero_skill_definitions": sorted({row["definition"] for row in abilities if row["definition"].startswith("wc_u_")}),
    "tier4_seen_in_normal_tournaments": sorted({row["trait"] for row in traits if int(row["count"]) >= 4}),
    "neutral_wave_outcomes": waves,
    "focused_test_boundary": "The executable also asserts all 24 skills at three stars, Neris/Finn/Oren revisions, all eleven eight-seat waves in an actual forced round-40 match, neutral failures/draws, reward application and restart. See the exact compiled harness hashes in process.json.",
    "limits": [
        "Native actual combat only; no Unreal rendering, packaged human play, LAN or frame times established.",
        "Simulated duration uses policy-ready preparation and is not measured human play duration.",
        "Random formation coverage is separate from the focused twelve-trait tier tests.",
    ],
    "evidence_sha256": {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in ("process.json", "runtime-tests.log", "tournaments.csv", "encounter-outcomes.csv", "ability-coverage.csv", "trait-coverage.csv", "compositions.csv")
    },
}
(root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: summary[key] for key in ("status", "tournaments", "encounters", "combat_events", "assertions", "bot_rejects")}, indent=2))
