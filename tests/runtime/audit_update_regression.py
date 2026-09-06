"""Audit a retained 24-hero packaged regression against an explicit native run.

SourceData must be extracted from that package (UnrealPak -Extract with a
SourceData filter). Every extracted byte is bound to the retained packaging
provenance. Current workspace data and later native runs are never substituted.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path, algorithm="sha256"):
    state = hashlib.new(algorithm)
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            state.update(chunk)
    return state.hexdigest()


class Audit:
    def __init__(self):
        self.categories = defaultdict(lambda: {"passed": 0, "failed": 0})
        self.failures = []

    def check(self, category, condition, detail=None):
        self.categories[category]["passed" if condition else "failed"] += 1
        if not condition and len(self.failures) < 150:
            self.failures.append({"check": category, "detail": detail})

    @property
    def failed(self):
        return sum(value["failed"] for value in self.categories.values())


def indexed(audit, category, items, fields):
    result = {}
    for item in items:
        key = tuple(int(item[field]) for field in fields)
        audit.check(category, key not in result, key)
        result[key] = item
    return result


def integer_fields(item, fields):
    return tuple(int(item[field]) for field in fields)


def is_neutral(round_number, rules):
    config = rules["tournament"]
    return round_number > 0 and (round_number <= config["neutral_opening_rounds"]
                                 or round_number % config["neutral_every_rounds"] == 0)


def audit_payload(data, native, rules, waves, expected_tournaments=100, audit=None):
    """Pure semantic auditor; synthetic negative tests exercise this boundary."""
    audit = audit or Audit()
    ids = rules["alpha_unit_ids"]
    seat_count = rules["tournament"]["seats"]
    seats = set(range(seat_count))
    expected_seeds = set(range(1, expected_tournaments + 1))
    trials = data["trials"]
    seeds = [int(trial["seed"]) for trial in trials]
    audit.check("batch_complete", data.get("complete") is True and data.get("failed") == 0
                and not data.get("evidence_write_failed")
                and data.get("requested") == data.get("attempted") == len(trials) == expected_tournaments)
    audit.check("seed_set", set(seeds) == expected_seeds and len(seeds) == len(set(seeds)), seeds)
    audit.check("active_profile", len(ids) == len(set(ids)) == 24 and seat_count == 8
                and data["profile_id"] == rules["profile_id"] == "alpha_24")
    audit.check("version_parity", data["schema_version"] == rules["schema_version"]
                and data["balance_version"] == rules["balance_version"])
    audit.check("tick_parity", data["tick_ms"] == rules["simulation"]["tick_ms"])
    audit.check("native_catalog_parity", data["digest"] == native["summary"]["content_digest"])
    nt = indexed(audit, "native_summary_unique", native["tournaments"], ("seed",))
    nr = indexed(audit, "native_round_seat_unique", native["rounds"], ("seed", "round", "seat"))
    nf = defaultdict(list)
    for fight in native["fights"]:
        nf[(int(fight["seed"]), int(fight["round"]))].append(fight)
    nc = defaultdict(list)
    for unit in native["compositions"]:
        if int(unit["on_board"]):
            nc[(int(unit["seed"]), int(unit["round"]), int(unit["seat"]))].append(unit)
    decisions = Counter()
    for decision in native["decisions"]:
        seed = int(decision["seed"])
        decisions[seed] += 1
        audit.check("native_commands_legal", int(decision["accepted"]) == 1
                    and int(decision["gold_after"]) >= 0 and int(decision["seat"]) in seats
                    and seed in expected_seeds, (seed, decision["round"], decision["seat"]))
    audit.check("native_seed_set", {key[0] for key in nt} == expected_seeds)
    seen_rounds, seen_fight_rounds, seen_compositions = set(), set(), set()
    settlements, native_settlements = set(), set()
    totals = Counter()
    usage_totals = Counter()
    neutral_outcomes = defaultdict(Counter)
    wave_by_round = {int(wave["round"]): wave["id"] for wave in waves}
    audit.check("wave_schedule_complete", set(wave_by_round) == {
        number for number in range(1, rules["tournament"]["max_rounds"] + 1) if is_neutral(number, rules)})
    for trial in trials:
        seed = int(trial["seed"])
        audit.check("trial_execution", trial.get("pass") is True and not trial.get("error")
                    and trial.get("phase") == 3 and trial.get("unresolved_encounters") == 0
                    and trial.get("command_rejects") == 0 and not trial.get("rejected_commands")
                    and trial.get("invariant_checks", 0) > 0 and trial.get("steps", 0) > 0, seed)
        round_rows = trial["rounds"]
        round_numbers = [int(row["round"]) for row in round_rows]
        audit.check("rounds_contiguous", round_numbers == list(range(1, len(round_rows) + 1))
                    and 1 <= len(round_rows) <= rules["tournament"]["max_rounds"], seed)
        audit.check("cap_truthful", not trial["capped"] or len(round_rows) == rules["tournament"]["max_rounds"], seed)
        placements = indexed(audit, "placement_seat_unique", trial["placements"], ("seat",))
        audit.check("placement_seat_set", {key[0] for key in placements} == seats, seed)
        audit.check("placement_range", all(1 <= int(row["placement"]) <= seat_count
                                           and int(row["health"]) >= 0 for row in placements.values()), seed)
        locks = indexed(audit, "combat_lock_round_unique", trial["combat_lock_deployments"], ("round",))
        audit.check("combat_lock_round_set", {key[0] for key in locks} == set(round_numbers), seed)
        expected_summary = nt.get((seed,))
        audit.check("native_seed_present", expected_summary is not None, seed)
        if expected_summary is not None:
            for actual_key, native_key in (("commands", "bot_commands"), ("command_rejects", "bot_rejects"),
                                           ("fights", "encounters"), ("timeouts", "timeouts"),
                                           ("ghosts", "ghosts"), ("simulated_ms", "simulated_ms")):
                audit.check("native_tournament_parity", int(trial[actual_key]) == int(expected_summary[native_key]),
                            (seed, actual_key, trial[actual_key], expected_summary[native_key]))
            winners = sum(int(row["placement"]) == 1 for row in placements.values())
            audit.check("native_tournament_parity", len(round_rows) == int(expected_summary["rounds"])
                        and int(round_rows[-1]["post_hash"]) == int(expected_summary["final_hash"])
                        and winners == int(expected_summary["winner_seats"]), seed)
        audit.check("native_command_count", trial["commands"] == decisions[seed], seed)
        before = {seat: {"health": rules["tournament"]["starting_health"], "wins": 0, "placement": 0}
                  for seat in seats}
        usage = defaultdict(lambda: {"units": 0, "rounds": set(), "instances": set(), "max_star": 0})
        trial_counts = Counter()
        pvp_index = 0
        for round_row in round_rows:
            number = int(round_row["round"])
            neutral = is_neutral(number, rules)
            pvp_index += int(not neutral)
            settlement = int(round_row["settlement_id"])
            audit.check("settlement_once", 0 < settlement < 2 ** 64 and settlement not in settlements, (seed, number, settlement))
            settlements.add(settlement)
            native_ids = {int(nr[(seed, number, seat)]["settlement_id"]) for seat in seats if (seed, number, seat) in nr}
            audit.check("native_settlement_once", len(native_ids) == 1 and not native_ids.intersection(native_settlements)
                        and all(0 < value < 2 ** 64 for value in native_ids), (seed, number))
            native_settlements.update(native_ids)
            alive = {seat for seat in seats if before[seat]["health"] > 0}
            round_seats = indexed(audit, "round_seat_unique", round_row["seats"], ("seat",))
            audit.check("round_seat_set", {key[0] for key in round_seats} == seats, (seed, number))
            encounters = round_row["encounters"]
            native_fights = nf.get((seed, number), [])
            seen_fight_rounds.add((seed, number))
            actual_fights = Counter()
            responsible_seats = Counter()
            rewards = {}
            for encounter in encounters:
                a, b = int(encounter["a"]), int(encounter["b"])
                kind = 2 if encounter["neutral"] else 1 if encounter["ghost"] else 0
                winner = int(encounter["winner"])
                ticks = int(encounter["ticks"])
                actual_fights[(kind, encounter["waveId"], a, b, winner, ticks, int(encounter["timeout"]),
                               int(encounter["survivors_a"]), int(encounter["survivors_b"]))] += 1
                audit.check("fight_completed", encounter["complete"] is True and winner in (-1, 0, 1)
                            and ticks > 0 and encounter["simulated_ms"] == ticks * data["tick_ms"]
                            and encounter["simulated_ms"] <= rules["tournament"]["combat_timeout_ms"],
                            (seed, number, a, b))
                audit.check("fight_namespace", a in alive and encounter["kind"] == ("neutral" if kind == 2 else "ghost" if kind == 1 else "pvp")
                            and encounter["neutral"] == neutral and not (encounter["neutral"] and encounter["ghost"]),
                            (seed, number, a, b))
                responsible_seats[a] += 1
                if neutral:
                    wave_id = wave_by_round.get(number)
                    expected_sides = [{"seat": a, "waveId": ""}, {"seat": None, "waveId": wave_id}]
                    audit.check("neutral_typed_owner", b == -1 and encounter["sides"] == expected_sides
                                and encounter["waveId"] == wave_id, (seed, number, encounter))
                    reward = rules["economy"]["neutral_win_income"] if winner == 0 else 0
                    damage = 0 if winner == 0 or number <= rules["tournament"]["neutral_opening_rounds"] else rules["tournament"]["neutral_failure_damage"]
                    rewards[a] = reward
                    row = round_seats.get((a,))
                    audit.check("neutral_settlement", row is not None and row["wins"] == before[a]["wins"]
                                and row["damage"] == damage and row["health"] == max(0, before[a]["health"] - damage),
                                (seed, number, a))
                    neutral_outcomes[number]["encounters"] += 1
                    neutral_outcomes[number]["wins"] += int(winner == 0)
                    neutral_outcomes[number]["losses"] += int(winner == 1)
                    neutral_outcomes[number]["draws"] += int(winner == -1)
                    neutral_outcomes[number]["timeouts"] += int(encounter["timeout"])
                else:
                    audit.check("pvp_typed_owners", b in alive and a != b and encounter["waveId"] == ""
                                and encounter["sides"] == [{"seat": a, "waveId": ""}, {"seat": b, "waveId": ""}],
                                (seed, number, a, b))
                    if not encounter["ghost"]:
                        responsible_seats[b] += 1
                trial_counts["fights"] += 1
                trial_counts["timeouts"] += int(encounter["timeout"])
                trial_counts["ghosts"] += int(encounter["ghost"])
            audit.check("every_living_seat_one_fight", responsible_seats == Counter({seat: 1 for seat in alive}),
                        (seed, number, dict(responsible_seats), sorted(alive)))
            expected_fights = Counter((int(row["kind"]), row["wave_id"], *integer_fields(row, (
                "seat_a", "seat_b", "winner", "ticks", "timeout", "survivors_a", "survivors_b"))) for row in native_fights)
            audit.check("native_fight_parity", actual_fights == expected_fights,
                        {"seed": seed, "round": number, "packaged_only": list((actual_fights - expected_fights).elements())[:3],
                         "native_only": list((expected_fights - actual_fights).elements())[:3]})
            audit.check("native_fight_pvp_index", all(int(row["pvp_round_index"]) == pvp_index for row in native_fights), (seed, number))
            for row in round_seats.values():
                seat = int(row["seat"])
                key = (seed, number, seat)
                seen_rounds.add(key)
                expected = nr.get(key)
                audit.check("native_round_present", expected is not None, key)
                if expected is not None:
                    fields = ("health", "gold", "damage", "wins", "placement")
                    audit.check("native_round_seat_parity", integer_fields(row, fields) == integer_fields(expected, fields), key)
                    audit.check("native_logical_hash_parity", int(round_row["pre_hash"]) == int(expected["pre_hash"])
                                and int(round_row["post_hash"]) == int(expected["post_hash"]), key)
                    audit.check("native_round_schedule", int(expected["pvp_round_index"]) == pvp_index
                                and int(expected["neutral"]) == int(neutral), key)
                    if neutral and seat in alive:
                        audit.check("native_pending_neutral_reward", int(expected["pending_reward"]) == rewards.get(seat), key)
                audit.check("health_and_economy", 0 <= row["health"] <= before[seat]["health"]
                            and row["gold"] >= 0 and row["damage"] >= 0 and row["wins"] >= before[seat]["wins"], key)
                if seat not in alive:
                    audit.check("elimination_persistent", row["health"] == 0 and row["wins"] == before[seat]["wins"]
                                and row["placement"] == before[seat]["placement"], key)
            lock = locks.get((number,), {"seats": []})
            lock_seats = indexed(audit, "deployment_seat_unique", lock["seats"], ("seat",))
            audit.check("deployment_seat_set", {key[0] for key in lock_seats} == seats, (seed, number))
            owned_ids = set()
            for (seat,), lock_seat in lock_seats.items():
                key = (seed, number, seat)
                if lock_seat["units"]:
                    seen_compositions.add(key)
                audit.check("eliminated_deployment_empty", seat in alive or not lock_seat["units"], key)
                expected_units = nc.get(key, [])
                actual_units = Counter()
                occupied = set()
                for unit in lock_seat["units"]:
                    definition = int(unit["def"])
                    unit_id = int(unit["id"])
                    cell = (int(unit["col"]), int(unit["row"]))
                    valid_definition = 0 <= definition < len(ids)
                    audit.check("deployment_legal", valid_definition and unit["neutral"] is False and unit["board"] is True
                                and int(unit["star"]) in (1, 2, 3) and int(unit["bench"]) == -1
                                and 0 <= cell[0] < rules["board"]["columns"]
                                and 0 <= cell[1] < rules["board"]["deployment_rows_per_side"]
                                and cell not in occupied and unit_id > 0 and unit_id not in owned_ids,
                                (key, unit))
                    occupied.add(cell)
                    owned_ids.add(unit_id)
                    if not valid_definition:
                        continue
                    definition_id = ids[definition]
                    actual_units[(unit_id, definition_id, int(unit["star"]), *cell, int(unit["bench"]))] += 1
                    use = usage[(seat, definition_id)]
                    use["units"] += 1
                    use["rounds"].add(number)
                    use["instances"].add(unit_id)
                    use["max_star"] = max(use["max_star"], int(unit["star"]))
                    usage_totals[definition_id] += 1
                expected = Counter((int(unit["unit_id"]), unit["definition"], *integer_fields(unit, (
                    "star", "column", "row", "bench"))) for unit in expected_units)
                audit.check("native_deployment_parity", actual_units == expected, key)
                audit.check("native_deployment_capacity", not expected_units or len(lock_seat["units"]) <= int(expected_units[0]["level"]), key)
            before = {key[0]: row for key, row in round_seats.items()}
        for seat in seats:
            final = placements.get((seat,))
            audit.check("final_round_placement", final is not None and final["health"] == before[seat]["health"]
                        and final["placement"] == before[seat]["placement"], (seed, seat))
        hero_rows = trial["hero_use_by_seat"]
        seen_usage = set()
        for use in hero_rows:
            key = (int(use["seat"]), use["unit_id"])
            audit.check("hero_use_key", key not in seen_usage and key[0] in seats and key[1] in ids, (seed, key))
            seen_usage.add(key)
            observed = usage[key]
            expected = (observed["units"], len(observed["rounds"]), len(observed["instances"]), observed["max_star"])
            actual = integer_fields(use, ("deployed_unit_rounds", "rounds_deployed", "distinct_owned_instances", "maximum_deployed_star"))
            audit.check("hero_use_reconciled", actual == expected and int(use["final_placement"]) == placements[(key[0],)]["placement"],
                        (seed, key, actual, expected))
        audit.check("hero_use_complete_matrix", seen_usage == {(seat, hero) for seat in seats for hero in ids}, seed)
        for field in ("fights", "timeouts", "ghosts"):
            audit.check("fight_aggregate_reconciled", trial_counts[field] == trial[field], (seed, field))
            totals[field] += trial_counts[field]
        totals["commands"] += trial["commands"]
        totals["rounds"] += len(round_rows)
        totals["round_seat_rows"] += len(round_rows) * seat_count
    audit.check("native_round_set_complete", set(nr) == seen_rounds)
    audit.check("native_fight_round_set_complete", set(nf) == seen_fight_rounds)
    audit.check("native_deployment_set_complete", set(nc) == seen_compositions)
    audit.check("all24_heroes_deployed", set(usage_totals) == set(ids), dict(usage_totals))
    for field, native_field in (("fights", "encounters"), ("timeouts", "timeouts"), ("ghosts", "ghosts")):
        audit.check("native_summary_aggregate", totals[field] == native["summary"][native_field], field)
    return audit, {"totals": dict(totals), "hero_deployed_unit_rounds": dict(sorted(usage_totals.items())),
                   "neutral_outcomes": {str(k): dict(v) for k, v in sorted(neutral_outcomes.items())},
                   "simulated_seconds": describe([trial["simulated_ms"] / 1000 for trial in trials])}


def describe(values):
    ordered = sorted(values)
    return {"count": len(values), "min": ordered[0], "median": statistics.median(values),
            "mean": statistics.mean(values), "p95": ordered[int((len(ordered) - 1) * .95)], "max": ordered[-1]}


def validate_artifacts(audit, evidence, native_run, source_data, data, artifacts):
    """Bind historical bytes, avoiding current canonical data and staging paths."""
    def retain(path):
        path = Path(path).resolve()
        value = {"path": str(path), "bytes": path.stat().st_size, "sha256": digest(path)}
        artifacts[str(path)] = value
        return value["sha256"]

    launch_path, exit_path = evidence / "launch.json", evidence / "process-exit.json"
    launch, process_exit = load(launch_path), load(exit_path)
    provenance_path = Path(launch["provenance_path"])
    provenance = load(provenance_path)
    for path in (evidence / "regression.json", launch_path, exit_path):
        retain(path)
    audit.check("provenance_hash", retain(provenance_path) == launch["provenance_sha256"])
    audit.check("package_build_success", provenance["package_report"]["exit_code"] == 0
                and provenance["input_files_stable_during_capture"] is True and provenance["configuration"] == "Shipping")
    payload = [item for item in provenance["files"] if item["group"] == "packaged_payload"]
    audit.check("package_payload_present", bool(payload))
    package_root = Path(provenance["package_root"]).resolve()
    for item in payload:
        path = Path(item["path"]).resolve()
        audit.check("package_payload_scope", path.is_relative_to(package_root), str(path))
        audit.check("package_payload_unchanged", retain(path) == item["sha256"] and path.stat().st_size == item["bytes"], str(path))
    executable = Path(launch["executable"]).resolve()
    audit.check("executable_binding", retain(executable) == launch["executable_sha256"]
                and executable == Path(provenance["packaged_game_executable"]).resolve()
                and executable == Path(data["executable_path"]).resolve()
                and any(Path(item["path"]).resolve() == executable for item in payload))
    audit.check("actual_process_exit", process_exit["exit_code"] == 0
                and process_exit["process_id"] == launch["process_id"]
                and Path(process_exit["executable"]).resolve() == executable)
    audit.check("execution_timestamp_order", datetime.fromisoformat(process_exit["started_utc"])
                == datetime.fromisoformat(launch["utc"])
                <= datetime.fromisoformat(data["start_utc"])
                < datetime.fromisoformat(data["end_utc"])
                <= datetime.fromisoformat(process_exit["ended_utc"]))
    audit.check("package_capture_precedes_launch", datetime.fromisoformat(provenance["capture_start_utc"])
                <= datetime.fromisoformat(provenance["capture_end_utc"])
                < datetime.fromisoformat(launch["utc"]))
    audit.check("actual_headless_mode", "-nullrhi" in launch["arguments"] and "-nosound" in launch["arguments"]
                and f"-WCRegression={data['requested']}" in launch["arguments"])
    stage = load(source_data / "runtime_stage_manifest.json")
    stage_records = {item["workspace_relative_path"].split("/SourceData/", 1)[1]: item
                     for item in provenance["files"] if item["group"] == "staged_source_data"}
    audit.check("source_data_file_set", set(stage_records) == set(stage["files"]) | {"runtime_stage_manifest.json"})
    for relative, record in stage_records.items():
        path = (source_data / relative).resolve()
        audit.check("source_data_path_scope", path.is_relative_to(source_data), relative)
        actual = retain(path)
        audit.check("package_source_provenance", actual == record["sha256"] and path.stat().st_size == record["bytes"], relative)
        if relative in stage["files"]:
            declared = stage["files"][relative]
            audit.check("stage_data_binding", actual == declared["sha256"]
                        and path.stat().st_size == declared["bytes"] and digest(path, "sha1") == declared["sha1"], relative)
        if relative in data["input_files"]:
            observed = data["input_files"][relative]
            audit.check("runtime_observed_data_binding", observed.get("available") is True
                        and digest(path, "sha1") == observed["sha1_actual"] and path.stat().st_size == observed["bytes"]
                        and observed.get("staged_manifest_sha1_matches", True) is True, relative)
    catalog = load(source_data / "generated/catalog_digest.json")
    for relative, declared in catalog["source_sha256"].items():
        audit.check("catalog_source_binding", retain(source_data / Path(relative).name) == declared, relative)
    combined = hashlib.sha256(json.dumps(catalog["source_sha256"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    audit.check("catalog_digest_binding", combined == catalog["combined_sha256"] == stage["catalog_digest"]
                == provenance["catalog_digest"] == data["digest"])
    rules = load(source_data / "rules.alpha.json")
    audit.check("stage_profile_binding", stage["alpha_unit_ids"] == rules["alpha_unit_ids"]
                and stage["schema_version"] == rules["schema_version"] and stage["balance_version"] == rules["balance_version"])
    summary, process = load(native_run / "summary.json"), load(native_run / "process.json")
    for file, expected in summary["evidence_sha256"].items():
        audit.check("native_retained_evidence_hash", retain(native_run / file) == expected, file)
    audit.check("native_execution_success", process["compile_exit"] == process["process_exit"] == 0
                and summary["status"] == "PASS_NATIVE_EXECUTION_ONLY" and summary["assertions"] > 0
                and process["requested_tournaments"] == summary["tournaments"] == data["requested"])
    audit.check("native_executable_hash", retain(Path(process["executable"])) == process["executable_sha256"])
    fixture = native_run / "CatalogFixture.h"
    declared_fixture = next(value for key, value in process["source_hashes"].items() if Path(key).name == "CatalogFixture.h")
    audit.check("native_fixture_binding", retain(fixture) == declared_fixture and combined in fixture.read_text(encoding="utf-8"))
    for file in ("summary.json", "round-economy.csv", "bot-decisions.csv"):
        retain(native_run / file)
    required_observations = {"rules.alpha.json", "units.json", "traits.json", "bots.json", "world.json", "runtime_stage_manifest.json"}
    audit.check("runtime_input_observation_set", required_observations <= set(data["input_files"]))
    return rules, load(source_data / "neutrals.json")["waves"], summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence_directory", type=Path)
    parser.add_argument("--native-run", required=True, type=Path)
    parser.add_argument("--source-data", required=True, type=Path,
                        help="SourceData extracted from this immutable package, never current workspace staging")
    parser.add_argument("--output-directory", required=True, type=Path)
    parser.add_argument("--expected-tournaments", type=int, default=100)
    args = parser.parse_args()
    output = args.output_directory.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report_path = output / "regression-analysis.json"
    if report_path.exists():
        raise SystemExit("Refusing to overwrite an existing audit; use a fresh output directory.")
    audit, artifacts, metrics, data = Audit(), {}, {}, {}
    evidence, native_run, source_data = (path.resolve() for path in (
        args.evidence_directory, args.native_run, args.source_data))
    started = datetime.now(timezone.utc).isoformat()
    try:
        data = load(evidence / "regression.json")
        rules, waves, summary = validate_artifacts(audit, evidence, native_run, source_data, data, artifacts)
        native = {"summary": summary, "tournaments": rows(native_run / "tournaments.csv"),
                  "rounds": rows(native_run / "round-economy.csv"), "fights": rows(native_run / "encounter-outcomes.csv"),
                  "compositions": rows(native_run / "compositions.csv"), "decisions": rows(native_run / "bot-decisions.csv")}
        audit, metrics = audit_payload(data, native, rules, waves, args.expected_tournaments, audit)
        for artifact in list(artifacts.values()):
            path = Path(artifact["path"])
            audit.check("audit_inputs_stable", path.stat().st_size == artifact["bytes"] and digest(path) == artifact["sha256"], str(path))
    except (OSError, ValueError, TypeError, KeyError, IndexError, StopIteration) as error:
        audit.check("malformed_or_missing_evidence", False, f"{type(error).__name__}: {error}")
    report = {"schema": "wonder_chess_update_regression_audit_v1", "status": "PASS" if not audit.failed else "FAIL",
              "started_utc": started, "ended_utc": datetime.now(timezone.utc).isoformat(),
              "evidence_directory": str(evidence), "native_run": str(native_run), "package_source_data": str(source_data),
              "auditor_sha256": digest(Path(__file__)), "checks_passed": sum(value["passed"] for value in audit.categories.values()),
              "checks_failed": audit.failed, "categories": dict(sorted(audit.categories.items())),
              "failures_first150": audit.failures, "metrics": metrics, "artifacts": list(artifacts.values()),
              "limits": [
                  "Actual packaged -nullrhi -nosound 0H8B combat regression only; no rendering, listening, human input, two-machine LAN or frame-time acceptance.",
                  "Native and engine process namespaces intentionally produce different settlement IDs; IDs must be unique within the packaged run, while every logical pre/post hash is compared exactly.",
                  "Package SourceData is bound to captured packaging provenance and immutable payload hashes. Current workspace canonical data and current observed source files are not treated as compiled inputs.",
                  ("Early package lacks a direct runtime neutrals.json hash observation. Its neutral bytes are bound through package payload, captured stage manifest and native catalog; this is not a direct runtime file-read hash."
                   if "neutrals.json" not in data.get("input_files", {}) else "This package records a runtime neutrals.json hash observation; its bytes are checked against the captured SourceData."),
                  "Native round-economy.csv and bot-decisions.csv lack pre-existing summary digests; this audit hashes retained bytes and checks their consistency with hash-bound native summaries/fights/compositions and packaged outcomes.",
                  "Packaged legal-command evidence records aggregate counts and rejections; per-command decisions come from the retained native run, not a claimed packaged command trace.",
                  "Simulated duration and headless wall time are not human match duration or graphical performance measurements."]}
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [f"# Packaged 24-hero regression audit: {report['status']}", "",
             f"Passed checks: {report['checks_passed']}; failed checks: {report['checks_failed']}.", "",
             f"Packaged evidence: `{evidence}`", f"Native evidence: `{native_run}`", "",
             "This audit compares actual retained combat outcomes and exact historical package data. It does not establish visual or human acceptance.", "",
             "```json", json.dumps(metrics, indent=2), "```", "", *[f"- {limit}" for limit in report["limits"]]]
    (output / "HANDOFF.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "checks_passed", "checks_failed", "failures_first150", "metrics")}))
    return 0 if not audit.failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
