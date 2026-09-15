"""Reconcile a preserved mana package against the unchanged native arm records."""
import csv
import hashlib
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[4]
evidence = Path(__file__).resolve().parent
revision = sys.argv[1]

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

result = {}
for arm in ("control", "mana100"):
    native = root / f"reports/vnext/milestones/b1-balance/mana-activation-{arm}-20260913T061630085Z"
    tournaments = {int(r["seed"]): r for r in rows(native / "tournaments.csv")}
    encounters = {(int(r["seed"]), int(r["round"]), int(r["index"])): r for r in rows(native / "encounters.csv")}
    batch = read(evidence / f"engine-{revision}-{arm}/regression.json")
    assert batch["complete"] and batch["failed"] == 0 and batch["attempted"] == batch["requested"] == 10
    assert {t["seed"] for t in batch["trials"]} == set(range(1, 11))
    count = rounds = 0
    for trial in batch["trials"]:
        expected = tournaments[trial["seed"]]
        assert trial["pass"] and not trial["error"] and trial["command_rejects"] == 0
        assert trial["capped"] == bool(int(expected["capped"]))
        for key in ("simulated_ms", "timeouts"):
            assert trial[key] == int(expected[key])
        assert len(trial["rounds"]) == int(expected["rounds"])
        trial_encounters = 0
        for round_record in trial["rounds"]:
            rounds += 1
            for index, actual in enumerate(round_record["encounters"]):
                wanted = encounters[(trial["seed"], round_record["round"], index)]
                assert actual["complete"] and actual["kind"] == wanted["kind"]
                for key in ("winner", "timeout", "ticks", "survivors_a", "survivors_b"):
                    assert int(actual[key]) == int(wanted[key]), (arm, trial["seed"], key)
                count += 1
                trial_encounters += 1
        assert trial_encounters == int(expected["encounters"])
    result[arm] = {"status": "PASS", "tournaments": 10, "rounds": rounds, "encounters": count,
                   "digest": batch["digest"], "comparison": "Every encounter kind, winner, timeout, ticks and survivors; tournament duration, cap and counts; no rejected commands. Does not compare full combat event streams or round state hashes."}
if revision == "r9":
    frozen = read(evidence / "build-source-r9.json")
    for filename, expected in frozen.items():
        assert hashlib.sha256((root / filename).read_bytes()).hexdigest() == expected, filename
    result["build_sources_unchanged"] = len(frozen)
destination = evidence / f"engine-native-reconciliation-{revision}.json"
destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
