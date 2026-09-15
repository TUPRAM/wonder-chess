"""Validate locally recorded B1/B2 human evidence without issuing acceptance.

CSV templates contain no participants. Tests use temporary synthetic fixtures only.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import statistics
import sys


HEADERS = {
    "participants.csv": ["participant_id", "external", "consented", "adult_eligible", "genre_experience"],
    "sessions.csv": ["session_id", "participant_id", "study", "cohort_slot", "session_order", "prior_wonder_sessions", "started_utc", "ended_utc", "package_sha256", "content_digest", "protocol_sha256", "observer_id", "hardware_id", "normal_speed", "completed", "withdrawn"],
    "observations.csv": ["session_id", "task_id", "scenario_id", "attempt", "assistance", "outcome", "explanation_score", "revision_useful", "pre_recap", "unfamiliar", "elapsed_seconds", "evidence_ref", "evidence_sha256"],
    "scenarios.csv": ["scenario_id", "task_id", "kind", "seed", "fixture_ref", "fixture_sha256", "answer_key_ref", "answer_key_sha256"],
    "durations.csv": ["session_id", "observation_id", "match_id", "started_utc", "ended_utc", "end_kind", "complete_from_start", "normal_speed", "accelerated_after_elimination", "interrupted", "active_preparation_seconds", "waiting_seconds", "combat_seconds", "recap_seconds", "pause_seconds", "other_seconds", "voluntary_replay", "loss_present", "evidence_ref", "evidence_sha256"],
}
B1_TASKS = tuple(f"B1_F{i:02}" for i in range(1, 7))
B2_TASKS = ("B2_BUY_UPGRADE", "B2_DEPLOY_FACE", "B2_SCOUT_RETURN", "B2_ADAPT", "B2_RELIC", "B2_LOSS", "B2_FINISH", "B2_RESTART", "B2_RESUME")
B2_EXPLANATIONS = tuple(f"B2_EXPLAIN_{i}" for i in range(1, 4))
PRIMARY = {"1": ["B1_F01", "B1_F04"], "2": ["B1_F02", "B1_F05"], "3": ["B1_F03", "B1_F06"], "4": ["B1_F04", "B1_F01"], "5": ["B1_F05", "B1_F02"]}
YES_NO = {"yes", "no"}


class StudyError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise StudyError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integer(value: str, low: int, high: int, label: str) -> int:
    require(bool(re.fullmatch(r"[0-9]+", value)), f"{label}: expected integer")
    number = int(value)
    require(low <= number <= high, f"{label}: outside {low}..{high}")
    return number


def seconds(value: str, label: str) -> float:
    require(bool(re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", value)), f"{label}: expected nonnegative seconds")
    result = float(value)
    require(result <= 604800, f"{label}: exceeds one week")
    return result


def utc(value: str, label: str) -> datetime:
    require(isinstance(value, str), f"{label}: expected ISO UTC text")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise StudyError(f"{label}: invalid ISO UTC time") from error
    require(result.tzinfo is not None and result.utcoffset() == timezone.utc.utcoffset(result), f"{label}: UTC offset required")
    return result


def local_id(value: str, prefix: str, label: str) -> None:
    require(isinstance(value, str) and bool(re.fullmatch(prefix + r"[0-9]{3,6}", value)), f"{label}: use anonymous local {prefix}### IDs")


def sha(value: str, label: str) -> None:
    require(isinstance(value, str) and bool(re.fullmatch(r"[a-f0-9]{64}", value)), f"{label}: expected lowercase SHA-256")


def evidence(root: Path, reference: str, expected: str, label: str) -> None:
    path = Path(reference)
    require(reference and not path.is_absolute() and ":" not in reference and ".." not in path.parts,
            f"{label}: evidence must use a relative path inside the local study directory")
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root.resolve()) and resolved.is_file(), f"{label}: missing or external evidence file")
    sha(expected, label)
    require(digest(resolved) == expected, f"{label}: evidence hash mismatch")


def read_tables(root: Path) -> dict[str, list[dict[str, str]]]:
    tables = {}
    for filename, fields in HEADERS.items():
        try:
            with (root / filename).open(encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                require(reader.fieldnames == fields, f"{filename}: header must exactly match the study schema")
                rows = list(reader)
        except OSError as error:
            raise StudyError(f"{filename}: {error}") from error
        require(len(rows) <= 10000, f"{filename}: too many rows")
        for index, row in enumerate(rows, 2):
            require(None not in row and all(value is not None and "\x00" not in value for value in row.values()),
                    f"{filename}:{index}: malformed CSV row")
        tables[filename] = rows
    return tables


def summarize(root: Path) -> dict:
    tables = read_tables(root)
    try:
        protocol = json.loads((root / "protocol.json").read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as error:
        raise StudyError(f"protocol.json: {error}") from error
    require(isinstance(protocol, dict), "Protocol must be a JSON object")
    require(protocol.get("format") == "wc-human-study-1", "Unsupported study protocol")
    study = protocol.get("study")
    require(isinstance(study, str) and study in {"B1", "B2"}, "Only the preregistered B1 and B2 rubrics are implemented")
    registered = utc(protocol.get("registered_utc", ""), "Protocol registration")
    local_id(protocol.get("registered_by", ""), "R", "Protocol registrar")
    require(protocol.get("primary_participants") == 5, "The preregistered primary cohort has five distinct people")
    require(protocol.get("b1_primary_tasks") == PRIMARY, "B1 primary task allocation changed; register a separate protocol version")
    require(isinstance(protocol.get("source_commit"), str) and bool(re.fullmatch(r"[a-f0-9]{40}", protocol["source_commit"])), "Record the exact source commit")
    for key in ("package_sha256", "content_digest"):
        sha(protocol.get(key, ""), key)
    sha(protocol.get("scenario_registry_sha256", ""), "Scenario registry")
    require(digest(root / "scenarios.csv") == protocol["scenario_registry_sha256"], "Frozen scenario/answer-key registry changed after registration")
    protocol_hash = digest(root / "protocol.json")

    people = {}
    for person in tables["participants.csv"]:
        pid = person["participant_id"]
        local_id(pid, "P", "Participant")
        require(pid not in people, f"Duplicate participant {pid}; sessions are not new people")
        require(person["external"] in YES_NO and person["consented"] in YES_NO and person["adult_eligible"] in YES_NO, f"{pid}: invalid consent/external/eligibility flag")
        require(person["genre_experience"] in {"newcomer", "experienced"}, f"{pid}: record genre experience separately")
        people[pid] = person

    sessions, slots, participant_slots = {}, {}, {}
    for session in tables["sessions.csv"]:
        sid, pid = session["session_id"], session["participant_id"]
        local_id(sid, "S", "Session")
        require(sid not in sessions and pid in people, f"{sid}: duplicate session or unknown participant")
        require(people[pid]["consented"] == "yes", f"{sid}: sessions require recorded voluntary consent")
        require(people[pid]["adult_eligible"] == "yes", f"{sid}: this protocol enrolls adults only")
        require(session["study"] == study, f"{sid}: mixed studies cannot be pooled")
        for flag in ("normal_speed", "completed", "withdrawn"):
            require(session[flag] in YES_NO, f"{sid}: invalid {flag}")
        require(session["withdrawn"] == "no", f"{sid}: remove withdrawn participant's observations before analysis and disclose attrition")
        local_id(session["observer_id"], "R", "Observer")
        local_id(session["hardware_id"], "H", "Hardware")
        for key in ("package_sha256", "content_digest"):
            require(session[key] == protocol[key], f"{sid}: mixed {key} cannot be pooled")
        require(session["protocol_sha256"] == protocol_hash, f"{sid}: protocol changed or was not frozen before collection")
        session["_start"] = utc(session["started_utc"], sid)
        session["_end"] = utc(session["ended_utc"], sid)
        require(registered <= session["_start"] < session["_end"], f"{sid}: registration must precede the recorded session")
        session["_order"] = integer(session["session_order"], 1, 999, sid)
        session["_prior"] = integer(session["prior_wonder_sessions"], 0, 100000, sid)
        slot = integer(session["cohort_slot"], 0, 5, sid)
        if slot:
            require(people[pid]["external"] == "yes", f"{pid}: owner/developer sessions cannot fill external cohort slots")
            require(slot not in slots or slots[slot] == pid, "A primary slot cannot be reassigned after observing results")
            require(pid not in participant_slots or participant_slots[pid] == slot, "One person cannot fill multiple cohort slots")
            slots[slot], participant_slots[pid] = pid, slot
        sessions[sid] = session

    for pid in people:
        ordered = sorted((s for s in sessions.values() if s["participant_id"] == pid), key=lambda s: s["_start"])
        for index, session in enumerate(ordered):
            require(session["_order"] == index + 1, f"{pid}: session order must start at one and stay contiguous")
            if index:
                require(ordered[index - 1]["_end"] <= session["_start"] and session["_prior"] > ordered[index - 1]["_prior"],
                        f"{pid}: repeat sessions cannot be labeled fresh first use or overlap")
        if ordered and study == "B2" and pid in participant_slots:
            require(ordered[0]["_prior"] == 0, f"{pid}: returning Wonder Chess users cannot enter B2 first-use cohort")

    scenarios = {}
    allowed_tasks = set(B1_TASKS + ("B1_F07",) if study == "B1" else B2_TASKS + B2_EXPLANATIONS + ("B2_SPECTATE",))
    for scenario in tables["scenarios.csv"]:
        key = scenario["scenario_id"]
        require(bool(re.fullmatch(r"[A-Z0-9_-]{1,48}", key)) and key not in scenarios, "Invalid/duplicate scenario identity")
        require(scenario["task_id"] in allowed_tasks and scenario["kind"] in {"unfamiliar", "demonstration"}, f"{key}: invalid task/kind")
        integer(scenario["seed"], 1, 2147483647, key)
        evidence(root, scenario["fixture_ref"], scenario["fixture_sha256"], key)
        evidence(root, scenario["answer_key_ref"], scenario["answer_key_sha256"], key)
        scenarios[key] = scenario

    observations, first = {}, {}
    for row in tables["observations.csv"]:
        sid, task = row["session_id"], row["task_id"]
        require(sid in sessions and task in allowed_tasks, "Observation references an unknown session/task")
        session = sessions[sid]
        pid = session["participant_id"]
        attempt = integer(row["attempt"], 1, 999, f"{pid}/{task}")
        key = (pid, task, attempt)
        require(key not in observations, "Duplicate participant/task/attempt; later sessions are not new first attempts")
        require(row["assistance"] in {"none", "controls", "clarification", "strategy", "takeover"}, "Invalid assistance code")
        require(row["outcome"] in {"pass", "fail", "not_run"}, "Invalid task outcome")
        require(row["revision_useful"] in {"yes", "no", "not_assessed"}, "Invalid revision result")
        require(row["pre_recap"] in YES_NO and row["unfamiliar"] in YES_NO, "Invalid explanation timing/familiarity flag")
        seconds(row["elapsed_seconds"], "Task duration")
        explanation = task in B1_TASKS or task in B2_EXPLANATIONS
        if row["outcome"] != "not_run":
            evidence(root, row["evidence_ref"], row["evidence_sha256"], f"{pid}/{task}")
            if explanation:
                require(row["scenario_id"] in scenarios, f"{pid}/{task}: missing frozen scenario and answer key")
                scenario = scenarios[row["scenario_id"]]
                require(scenario["task_id"] == task, "Scenario answer key belongs to another task")
                require(row["unfamiliar"] == ("yes" if scenario["kind"] == "unfamiliar" else "no"), "Scenario familiarity conflicts with registered input")
                integer(row["explanation_score"], 0, 2, "Explanation score")
        row["_session"] = session
        row["_independent"] = row["outcome"] == "pass" and row["assistance"] == "none" and session["normal_speed"] == "yes"
        if explanation:
            row["_independent"] = row["_independent"] and row["explanation_score"] == "2" and row["pre_recap"] == "yes" and row["unfamiliar"] == "yes"
            if study == "B1":
                row["_independent"] = row["_independent"] and row["revision_useful"] == "yes"
        observations[key] = row
        if attempt == 1 and session["cohort_slot"] != "0":
            first[(pid, task)] = row
    for pid, task, _ in observations:
        attempts = sorted(a for p, t, a in observations if p == pid and t == task)
        require(attempts == list(range(1, len(attempts) + 1)), f"{pid}/{task}: attempts must start at one and stay contiguous")
        dates = [observations[(pid, task, a)]["_session"]["_start"] for a in attempts]
        require(dates == sorted(dates), f"{pid}/{task}: later attempt cannot precede the first session")

    duration_rows, duration_ids, match_ids = [], set(), set()
    component_keys = ("active_preparation_seconds", "waiting_seconds", "combat_seconds", "recap_seconds", "pause_seconds", "other_seconds")
    for row in tables["durations.csv"]:
        require(row["session_id"] in sessions, "Duration references unknown session")
        local_id(row["observation_id"], "D", "Duration")
        local_id(row["match_id"], "M", "Match")
        require(row["observation_id"] not in duration_ids, "Duplicate duration observation")
        duration_ids.add(row["observation_id"])
        require(row["end_kind"] in {"final_winner", "player_eliminated", "exit", "abort"}, "Invalid duration endpoint")
        for flag in ("complete_from_start", "normal_speed", "accelerated_after_elimination", "interrupted", "loss_present"):
            require(row[flag] in YES_NO, f"Invalid duration flag {flag}")
        require(row["voluntary_replay"] in {"yes", "no", "not_offered"}, "Invalid voluntary replay result")
        session = sessions[row["session_id"]]
        start, end = utc(row["started_utc"], "Duration start"), utc(row["ended_utc"], "Duration end")
        require(session["_start"] <= start < end <= session["_end"], "Duration must be contained within its observation session")
        wall = (end - start).total_seconds()
        components = {key: seconds(row[key], key) for key in component_keys}
        require(abs(sum(components.values()) - wall) <= 2, "Duration components do not reconcile to elapsed wall time")
        evidence(root, row["evidence_ref"], row["evidence_sha256"], row["observation_id"])
        full = row["end_kind"] == "final_winner" and row["complete_from_start"] == "yes" and row["normal_speed"] == "yes" and session["normal_speed"] == "yes" and row["accelerated_after_elimination"] == "no" and row["interrupted"] == "no" and people[session["participant_id"]]["external"] == "yes"
        if full:
            require(row["match_id"] not in match_ids, "The same complete match cannot count twice")
            match_ids.add(row["match_id"])
        duration_rows.append({"match_id": row["match_id"], "participant_id": session["participant_id"], "end_kind": row["end_kind"], "full_standard": full, "wall_seconds": wall, "standard_seconds": wall - components["pause_seconds"], "components": components, "voluntary_replay": row["voluntary_replay"], "loss_present": row["loss_present"]})

    primary_people = [slots[slot] for slot in sorted(slots)]
    required_tasks = B1_TASKS + ("B1_F07",) if study == "B1" else B2_TASKS + B2_EXPLANATIONS
    missing = [(pid, task) for pid in primary_people for task in required_tasks if (pid, task) not in first or first[(pid, task)]["outcome"] == "not_run"]
    task_results = {}
    for task in required_tasks:
        rows = [first[(pid, task)] for pid in primary_people if (pid, task) in first]
        task_results[task] = {"independent_successes": sum(row["_independent"] for row in rows), "primary_participants": len(primary_people), "assisted_first_attempts": sum(row["assistance"] != "none" and row["outcome"] != "not_run" for row in rows), "not_run_or_missing": sum((pid, task) in missing for pid in primary_people), "per_participant": {pid: bool(first.get((pid, task), {}).get("_independent", False)) for pid in primary_people}}
    participant_pass = {}
    for pid in primary_people:
        tasks = PRIMARY[str(participant_slots[pid])] if study == "B1" else B2_EXPLANATIONS
        count = sum(bool(first.get((pid, task), {}).get("_independent", False)) for task in tasks)
        participant_pass[pid] = {"successes": count, "required": 2, "opportunities": len(tasks), "met": count >= 2}
    sample_complete = len(primary_people) == 5 and not missing
    sessions_complete = all(s["completed"] == "yes" for s in sessions.values() if s["cohort_slot"] != "0")
    groups = {kind: [pid for pid in primary_people if people[pid]["genre_experience"] == kind] for kind in ("newcomer", "experienced")}
    sample_complete = sample_complete and sessions_complete and all(groups.values())
    primary_met = sum(row["met"] for row in participant_pass.values()) >= 4
    if study == "B2":
        primary_met = primary_met and all(task_results[task]["independent_successes"] >= 4 for task in B2_TASKS)
    criterion = "INCOMPLETE" if not sample_complete else "MET" if primary_met else "NOT_MET"
    full = [row for row in duration_rows if row["full_standard"]]
    times = [row["standard_seconds"] for row in full]
    median = statistics.median(times) if times else None
    pacing = "INCOMPLETE" if len(times) < 5 else "MET" if 35 * 60 <= median <= 45 * 60 else "NOT_MET"
    spectating = any(task == "B2_SPECTATE" and attempt == 1 and row["outcome"] == "pass" and people[pid]["external"] == "yes" for (pid, task, attempt), row in observations.items())
    return {"format": "wc-human-study-summary-1", "study": study, "criterion": criterion,
            "acceptance": "HUMAN_REVIEW_REQUIRED", "source_commit": protocol["source_commit"], "package_sha256": protocol["package_sha256"], "content_digest": protocol["content_digest"], "protocol_sha256": protocol_hash,
            "primary_distinct_participants": len(primary_people), "observed_distinct_people": len({s["participant_id"] for s in sessions.values()}),
            "supplementary_people": len({s["participant_id"] for s in sessions.values()} - set(primary_people)),
            "experience_groups": groups, "tasks": task_results, "participant_primary_result": participant_pass,
            "missing_first_opportunities": [{"participant_id": pid, "task_id": task} for pid, task in missing],
            "retry_attempts_excluded_from_primary": sum(attempt > 1 for _, _, attempt in observations),
            "systematic_mechanic_review_flags": [task for task in B1_TASKS if task in task_results and task_results[task]["independent_successes"] < 4],
            "full_standard_tournament_observations": len(full), "duration_distinct_people": len({row["participant_id"] for row in full}),
            "standard_duration_median_seconds": median, "standard_duration_range_seconds": [min(times), max(times)] if times else None,
            "pacing_criterion": pacing, "spectating_journey_observed": spectating, "duration_observations": duration_rows,
            "boundaries": ["Scores are observer judgments tied to hashed evidence, not machine-certified understanding", "Attempts, mirrors and repeated sessions are not additional participants", "A numerical criterion never grants gameplay, art or release acceptance", "Full-match pacing excludes early elimination, interrupted sessions and accelerated endings", "Voluntary replay differs from scheduled return and does not establish retention"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--check-template", action="store_true", help="Check empty CSV headers only; supplies no human evidence")
    parser.add_argument("--output", type=Path, help="Write a new summary file; never overwrite existing evidence")
    args = parser.parse_args()
    try:
        if args.check_template:
            tables = read_tables(args.directory)
            require(all(not rows for rows in tables.values()), "Template check requires empty tables; use normal analysis for records")
            result = {"status": "TEMPLATE_ONLY", "human_evidence": "NOT_RUN", "participants": 0}
            code = 0
        else:
            result = summarize(args.directory)
            code = {"MET": 0, "NOT_MET": 1, "INCOMPLETE": 3}[result["criterion"]]
        serialized = json.dumps(result, indent=2) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as file:
                file.write(serialized)
        print(serialized, end="")
        return code
    except (StudyError, OSError) as error:
        print(json.dumps({"status": "INVALID", "acceptance": "NOT_ESTABLISHED", "error": str(error)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
