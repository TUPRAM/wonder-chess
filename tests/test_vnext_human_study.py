"""Synthetic, temporary measurement-tool fixtures; not human participant evidence."""
import csv
import json
from pathlib import Path
import tempfile
import unittest

from tools.vnext import human_study as study


class HumanStudyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tables = {name: [] for name in study.HEADERS}
        raw = self.root / "synthetic-test-only.txt"
        raw.write_text("SYNTHETIC UNIT TEST ONLY. No human participated.\n", encoding="utf-8")
        self.reference = raw.name
        self.reference_hash = study.digest(raw)

    def write(self):
        for name, fields in study.HEADERS.items():
            with (self.root / name).open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fields)
                writer.writeheader()
                writer.writerows(self.tables[name])

    def build(self, stage="B1", count=5):
        explanation_tasks = study.B1_TASKS if stage == "B1" else study.B2_EXPLANATIONS
        for task in explanation_tasks:
            self.tables["scenarios.csv"].append({"scenario_id": "TEST_" + task, "task_id": task, "kind": "unfamiliar", "seed": "41001", "fixture_ref": self.reference, "fixture_sha256": self.reference_hash, "answer_key_ref": self.reference, "answer_key_sha256": self.reference_hash})
        self.write()
        protocol = {"format": "wc-human-study-1", "study": stage, "registered_utc": "2026-09-12T09:00:00Z", "registered_by": "R001", "source_commit": "a" * 40, "package_sha256": "b" * 64, "content_digest": "c" * 64, "scenario_registry_sha256": study.digest(self.root / "scenarios.csv"), "primary_participants": 5, "b1_primary_tasks": study.PRIMARY}
        (self.root / "protocol.json").write_text(json.dumps(protocol), encoding="utf-8")
        protocol_hash = study.digest(self.root / "protocol.json")
        for index in range(1, count + 1):
            pid, sid = f"P{index:03}", f"S{index:03}"
            self.tables["participants.csv"].append({"participant_id": pid, "external": "yes", "consented": "yes", "adult_eligible": "yes", "genre_experience": "newcomer" if index % 2 else "experienced"})
            self.tables["sessions.csv"].append({"session_id": sid, "participant_id": pid, "study": stage, "cohort_slot": str(index), "session_order": "1", "prior_wonder_sessions": "0", "started_utc": "2026-09-12T10:00:00Z", "ended_utc": "2026-09-12T11:00:00Z", "package_sha256": "b" * 64, "content_digest": "c" * 64, "protocol_sha256": protocol_hash, "observer_id": "R001", "hardware_id": "H001", "normal_speed": "yes", "completed": "yes", "withdrawn": "no"})
            tasks = study.B1_TASKS + ("B1_F07",) if stage == "B1" else study.B2_TASKS + study.B2_EXPLANATIONS
            for task in tasks:
                explain = task in explanation_tasks
                self.tables["observations.csv"].append({"session_id": sid, "task_id": task, "scenario_id": "TEST_" + task if explain else "", "attempt": "1", "assistance": "none", "outcome": "pass", "explanation_score": "2" if explain else "", "revision_useful": "yes" if stage == "B1" and explain else "not_assessed", "pre_recap": "yes" if explain else "no", "unfamiliar": "yes" if explain else "no", "elapsed_seconds": "40", "evidence_ref": self.reference, "evidence_sha256": self.reference_hash})
        self.write()

    def summary(self):
        self.write()
        return study.summarize(self.root)

    def find(self, sid, task):
        return next(row for row in self.tables["observations.csv"] if row["session_id"] == sid and row["task_id"] == task and row["attempt"] == "1")

    def test_empty_records_never_supply_human_evidence(self):
        self.build(count=0)
        result = self.summary()
        self.assertEqual(result["criterion"], "INCOMPLETE")
        self.assertEqual(result["primary_distinct_participants"], 0)
        self.assertEqual(result["acceptance"], "HUMAN_REVIEW_REQUIRED")
        self.assertEqual(result["standard_duration_median_seconds"], None)

    def test_b1_primary_pass_never_issues_acceptance(self):
        self.build()
        result = self.summary()
        self.assertEqual(result["criterion"], "MET")
        self.assertEqual(result["primary_distinct_participants"], 5)
        self.assertEqual(result["acceptance"], "HUMAN_REVIEW_REQUIRED")
        self.assertEqual(result["full_standard_tournament_observations"], 0)

    def test_assisted_retry_does_not_repair_first_attempt(self):
        self.build()
        for sid, task in (("S001", "B1_F01"), ("S002", "B1_F02")):
            row = self.find(sid, task)
            row["assistance"] = "strategy"
            retry = dict(row, attempt="2", assistance="none")
            self.tables["observations.csv"].append(retry)
        result = self.summary()
        self.assertEqual(result["criterion"], "NOT_MET")
        self.assertEqual(result["retry_attempts_excluded_from_primary"], 2)
        self.assertFalse(result["participant_primary_result"]["P001"]["met"])
        self.assertEqual(result["tasks"]["B1_F01"]["assisted_first_attempts"], 1)

    def test_missing_task_or_small_sample_is_incomplete(self):
        self.build(count=4)
        self.assertEqual(self.summary()["criterion"], "INCOMPLETE")
        self.tables["observations.csv"].remove(self.find("S001", "B1_F01"))
        result = self.summary()
        self.assertIn({"participant_id": "P001", "task_id": "B1_F01"}, result["missing_first_opportunities"])

    def test_same_person_cannot_fill_two_slots(self):
        self.build()
        self.tables["sessions.csv"][1]["participant_id"] = "P001"
        with self.assertRaisesRegex(study.StudyError, "multiple cohort slots"):
            self.summary()

    def test_repeated_sessions_are_not_additional_people(self):
        self.build(count=1)
        extra = dict(self.tables["sessions.csv"][0], session_id="S002", session_order="2", prior_wonder_sessions="1", started_utc="2026-09-13T10:00:00Z", ended_utc="2026-09-13T11:00:00Z")
        self.tables["sessions.csv"].append(extra)
        result = self.summary()
        self.assertEqual(result["primary_distinct_participants"], 1)
        self.assertEqual(result["observed_distinct_people"], 1)
        self.assertEqual(result["criterion"], "INCOMPLETE")

    def test_b2_per_task_and_two_of_three_explanations(self):
        self.build("B2")
        self.find("S001", "B2_EXPLAIN_1")["explanation_score"] = "1"
        self.find("S002", "B2_EXPLAIN_2")["explanation_score"] = "1"
        self.assertEqual(self.summary()["criterion"], "MET")
        self.find("S001", "B2_SCOUT_RETURN")["assistance"] = "controls"
        self.find("S002", "B2_SCOUT_RETURN")["assistance"] = "controls"
        result = self.summary()
        self.assertEqual(result["criterion"], "NOT_MET")
        self.assertEqual(result["tasks"]["B2_SCOUT_RETURN"]["independent_successes"], 3)

    def test_b2_returning_participant_is_not_first_use(self):
        self.build("B2")
        self.tables["sessions.csv"][0]["prior_wonder_sessions"] = "1"
        with self.assertRaisesRegex(study.StudyError, "returning Wonder Chess"):
            self.summary()

    def test_recap_or_known_answer_cannot_count_as_independent_explanation(self):
        self.build()
        self.find("S001", "B1_F01")["pre_recap"] = "no"
        self.find("S002", "B1_F02")["pre_recap"] = "no"
        self.assertEqual(self.summary()["criterion"], "NOT_MET")

    def test_mixed_or_changed_frozen_evidence_is_rejected(self):
        self.build()
        self.tables["sessions.csv"][0]["package_sha256"] = "d" * 64
        with self.assertRaisesRegex(study.StudyError, "mixed package"):
            self.summary()
        self.tables["sessions.csv"][0]["package_sha256"] = "b" * 64
        self.tables["scenarios.csv"][0]["seed"] = "999"
        with self.assertRaisesRegex(study.StudyError, "registry changed"):
            self.summary()

    def test_missing_or_modified_raw_record_rejected(self):
        self.build()
        (self.root / self.reference).write_text("Changed after scoring", encoding="utf-8")
        with self.assertRaisesRegex(study.StudyError, "hash mismatch"):
            self.summary()

    def test_malformed_protocol_rejected_with_actionable_error(self):
        self.build()
        (self.root / "protocol.json").write_text("[]", encoding="utf-8")
        with self.assertRaisesRegex(study.StudyError, "JSON object"):
            self.summary()

    def test_extra_csv_columns_and_external_raw_paths_rejected(self):
        self.build()
        row = self.find("S001", "B1_F01")
        row["evidence_ref"] = "../unrelated.txt"
        with self.assertRaisesRegex(study.StudyError, "inside the local study"):
            self.summary()
        self.write()
        path = self.root / "participants.csv"
        path.write_text(path.read_text().replace("participant_id,", "name,participant_id,", 1), encoding="utf-8")
        with self.assertRaisesRegex(study.StudyError, "header must exactly match"):
            study.summarize(self.root)

    def test_consent_and_external_eligibility(self):
        self.build()
        self.tables["participants.csv"][0]["consented"] = "no"
        with self.assertRaisesRegex(study.StudyError, "consent"):
            self.summary()
        self.tables["participants.csv"][0]["consented"] = "yes"
        self.tables["participants.csv"][0]["external"] = "no"
        with self.assertRaisesRegex(study.StudyError, "owner/developer"):
            self.summary()

    def duration(self, index, **changes):
        return {"session_id": f"S{index:03}", "observation_id": f"D{index:03}", "match_id": f"M{index:03}", "started_utc": "2026-09-12T10:05:00Z", "ended_utc": "2026-09-12T10:45:00Z", "end_kind": "final_winner", "complete_from_start": "yes", "normal_speed": "yes", "accelerated_after_elimination": "no", "interrupted": "no", "active_preparation_seconds": "1200", "waiting_seconds": "200", "combat_seconds": "800", "recap_seconds": "200", "pause_seconds": "0", "other_seconds": "0", "voluntary_replay": "not_offered", "loss_present": "yes", "evidence_ref": self.reference, "evidence_sha256": self.reference_hash, **changes}

    def test_actual_duration_and_elimination_are_separate(self):
        self.build("B2")
        self.tables["durations.csv"] = [self.duration(index) for index in range(1, 6)]
        result = self.summary()
        self.assertEqual(result["full_standard_tournament_observations"], 5)
        self.assertEqual(result["standard_duration_median_seconds"], 2400)
        self.assertEqual(result["pacing_criterion"], "MET")
        self.tables["durations.csv"][0]["end_kind"] = "player_eliminated"
        self.tables["durations.csv"][1]["accelerated_after_elimination"] = "yes"
        result = self.summary()
        self.assertEqual(result["full_standard_tournament_observations"], 3)
        self.assertEqual(result["pacing_criterion"], "INCOMPLETE")
        self.assertEqual(len(result["duration_observations"]), 5)

    def test_duration_components_and_unique_matches(self):
        self.build("B2")
        self.tables["durations.csv"] = [self.duration(1, combat_seconds="900")]
        with self.assertRaisesRegex(study.StudyError, "do not reconcile"):
            self.summary()
        self.tables["durations.csv"] = [self.duration(1), self.duration(2, match_id="M001")]
        with self.assertRaisesRegex(study.StudyError, "same complete match"):
            self.summary()


if __name__ == "__main__":
    unittest.main()
