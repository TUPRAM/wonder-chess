"""Reject falsely reconciled native/engine evidence using small isolated fixtures."""
import copy
import csv
import importlib.util
import json
import shutil
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("vnext_run_analysis", ROOT / "tools/vnext/analyze_runs.py")
ANALYZER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANALYZER)


class VNextRunAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.native = Path(self.temp.name) / "native"
        self.native.mkdir()
        self.engine_path = Path(self.temp.name) / "engine.json"
        self.summary = dict(profile="wonder_vnext", catalog_digest="a" * 64,
                            actual_combat_tournaments=2, encounters=4, timeouts=0,
                            relic_choices=2, relic_equips=2, command_rejects=0)
        self.process = dict(compile_exit=0, process_exit=0, requested_tournaments=2, source_stable=True)
        self.tournaments = [dict(seed=seed, rounds=2, simulated_ms=140000, preparation_ms=100000,
                                 combat_ms=30000, settlement_ms=10000, capped=0, encounters=2,
                                 timeouts=0, relic_choices=1, relic_equips=1, command_rejects=0)
                            for seed in (1, 2)]
        self.rounds, self.fights, trials = [], [], []
        for seed in (1, 2):
            engine_rounds = []
            for round_number in (1, 2):
                # State hashes exceed exact IEEE double range; engine preserves them as strings.
                pre = 9007199254740993 + seed * 100 + round_number * 10
                post = pre + 7
                self.rounds.append(dict(seed=seed, round=round_number, pre_hash=pre, post_hash=post))
                kind = ((seed - 1) * 2 + round_number - 1) % 3
                fight = dict(seed=seed, round=round_number, index=0, a=0, b=-1 if kind == 2 else 1, kind=kind, winner=0, ticks=300,
                             timeout=0, survivors_a=2, survivors_b=0)
                self.fights.append(fight)
                engine_fight = {key: value for key, value in fight.items() if key not in ("seed", "round", "index")}
                engine_fight["kind"] = ("pvp", "ghost", "neutral")[kind]
                engine_fight["complete"] = True
                engine_rounds.append(dict(round=round_number, pre_hash=str(pre), post_hash=str(post), encounters=[engine_fight]))
            trials.append(dict(seed=seed, simulated_ms=140000, command_rejects=0, unresolved_encounters=0,
                               **{"pass": True}, rounds=engine_rounds))
        self.engine = dict(digest="a" * 64, profile_id="wonder_vnext", complete=True, failed=False,
                           evidence_write_failed=False, requested=2, trials=trials,
                           executable_path="fixture/WonderChess.exe")

    def run_analysis(self, engine=True):
        for name, value in (("summary.json", self.summary), ("process.json", self.process)):
            (self.native / name).write_text(json.dumps(value), encoding="utf-8")
        for name, rows in (("tournaments.csv", self.tournaments), ("rounds.csv", self.rounds), ("encounters.csv", self.fights)):
            with (self.native / name).open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
        self.engine_path.write_text(json.dumps(self.engine), encoding="utf-8")
        return ANALYZER.analyze(self.native, self.engine_path if engine else None)

    def assert_rejected(self, result):
        self.assertFalse(result["technical_reconciliation_passed"], result)
        self.assertTrue(result["verification_errors"])

    def test_matching_records_preserve_large_hashes_and_separate_sample_targets(self):
        result = self.run_analysis()
        self.assertTrue(result["technical_reconciliation_passed"])
        self.assertEqual(result["engine_comparison"]["rounds"], 4)
        self.assertEqual(result["engine_comparison"]["encounters"], 4)
        self.assertEqual(len(result["inputs_sha256"]), 6)
        self.assertFalse(result["sample_targets"]["median_duration_35_to_45"])
        self.assertTrue(result["sample_targets"]["combat_timeout_below_two_percent"])

    def test_wrong_engine_digest_is_rejected(self):
        self.engine["digest"] = "b" * 64
        self.assert_rejected(self.run_analysis())

    def test_later_seed_batch_requires_exact_range_and_history(self):
        self.summary["first_seed"] = self.process["first_seed"] = 251
        for rows in (self.tournaments, self.rounds, self.fights):
            for row in rows:
                row["seed"] += 250
        result = self.run_analysis(engine=False)
        self.assertTrue(result["technical_reconciliation_passed"], result)
        self.assertEqual((result["first_seed"], result["last_seed"]), (251, 252))
        self.fights[-1]["seed"] = 253
        self.assert_rejected(self.run_analysis(engine=False))

    def test_batch_summary_cannot_change_process_seed_range(self):
        self.process["first_seed"] = 251
        self.assert_rejected(self.run_analysis(engine=False))

    def second_batch(self):
        self.process["source_hashes"] = {"simulation.cpp": "b" * 64}
        self.run_analysis(engine=False)
        second = self.native.parent / "second"
        shutil.copytree(self.native, second)
        for name in ("summary.json", "process.json"):
            path = second / name
            record = json.loads(path.read_text())
            record["first_seed"] = 3
            path.write_text(json.dumps(record))
        for name in ("tournaments.csv", "rounds.csv", "encounters.csv"):
            rows = ANALYZER.read_csv(second / name)
            for row in rows:
                row["seed"] += 2
            with (second / name).open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
        return second

    def test_batches_reconcile_unique_seeds_and_first_batch_engine_results(self):
        second = self.second_batch()
        result = ANALYZER.analyze_batches([self.native, second], self.engine_path)
        self.assertTrue(result["technical_reconciliation_passed"], result)
        self.assertEqual((result["native_tournaments"], result["native_encounters"]), (4, 8))
        self.assertEqual(result["engine_comparison"]["tournaments"], 2)

    def test_reusing_one_batch_cannot_inflate_total_tournaments(self):
        self.second_batch()
        self.assert_rejected(ANALYZER.analyze_batches([self.native, self.native]))

    def test_different_compiled_sources_cannot_be_aggregated(self):
        second = self.second_batch()
        path = second / "process.json"
        record = json.loads(path.read_text())
        record["source_hashes"]["simulation.cpp"] = "c" * 64
        path.write_text(json.dumps(record))
        self.assert_rejected(ANALYZER.analyze_batches([self.native, second]))

    def test_wrong_engine_profile_is_rejected(self):
        self.engine["profile_id"] = "alpha_24"
        self.assert_rejected(self.run_analysis())

    def test_wrong_or_missing_native_profile_is_rejected_without_engine(self):
        for profile in ("alpha_24", "unrecognized", None):
            with self.subTest(profile=profile):
                self.summary["profile"] = profile
                self.assert_rejected(self.run_analysis(engine=False))

    def test_summary_command_totals_must_match_tournament_rows(self):
        for field in ("relic_choices", "relic_equips", "command_rejects"):
            with self.subTest(field=field):
                original = self.summary[field]
                self.summary[field] = 999999
                result = self.run_analysis(engine=False)
                self.assert_rejected(result)
                self.assertEqual(result["native_relic_choices"], 2)
                self.assertEqual(result["native_relic_equips"], 2)
                self.summary[field] = original

    def test_negative_command_counters_cannot_cancel_in_the_total(self):
        self.tournaments[0]["relic_choices"] = -1
        self.tournaments[1]["relic_choices"] = 3
        self.assert_rejected(self.run_analysis(engine=False))

    def test_engine_encounter_kind_must_match_native_enum(self):
        self.engine["trials"][0]["rounds"][0]["encounters"][0]["kind"] = "neutral"
        self.assert_rejected(self.run_analysis())

    def test_unknown_native_kind_is_rejected_without_engine(self):
        for kind in (-1, 3, 99):
            with self.subTest(kind=kind):
                self.fights[0]["kind"] = kind
                self.assert_rejected(self.run_analysis(engine=False))

    def test_unknown_or_missing_engine_kind_is_not_mapped_to_a_default(self):
        fight = self.engine["trials"][0]["rounds"][0]["encounters"][0]
        for kind in ("other", 0, None):
            with self.subTest(kind=kind):
                fight["kind"] = kind
                self.assert_rejected(self.run_analysis())
        del fight["kind"]
        self.assert_rejected(self.run_analysis())

    def test_changed_logical_state_hash_is_rejected(self):
        self.engine["trials"][1]["rounds"][0]["post_hash"] = "9007199254740992"
        self.assert_rejected(self.run_analysis())

    def test_changed_winner_is_rejected_even_with_same_state_hash(self):
        self.engine["trials"][0]["rounds"][0]["encounters"][0]["winner"] = 1
        self.assert_rejected(self.run_analysis())

    def test_missing_native_seed_is_rejected(self):
        self.tournaments.pop()
        self.assert_rejected(self.run_analysis())

    def test_missing_engine_seed_is_rejected(self):
        self.engine["trials"].pop()
        self.assert_rejected(self.run_analysis())

    def test_duplicate_native_round_is_rejected(self):
        self.rounds.append(copy.deepcopy(self.rounds[0]))
        self.assert_rejected(self.run_analysis())

    def test_phase_total_mismatch_is_rejected(self):
        self.tournaments[0]["combat_ms"] += 50
        self.assert_rejected(self.run_analysis())

    def test_negative_phase_duration_cannot_cancel_against_another_phase(self):
        self.tournaments[0]["combat_ms"] = -1000
        self.tournaments[0]["preparation_ms"] = 131000
        self.assert_rejected(self.run_analysis())

    def test_unstable_native_source_is_rejected(self):
        self.process["source_stable"] = False
        self.assert_rejected(self.run_analysis())

    def test_incomplete_engine_fight_is_rejected(self):
        self.engine["trials"][0]["rounds"][1]["encounters"][0]["complete"] = False
        self.assert_rejected(self.run_analysis())

    def test_native_orphan_fight_cannot_hide_in_reconciled_totals(self):
        orphan = dict(self.fights[0], seed=99)
        self.fights.append(orphan)
        self.summary["encounters"] += 1
        self.assert_rejected(self.run_analysis(engine=False))

    def test_native_orphan_round_cannot_hide_in_reconciled_seed_totals(self):
        self.fights[-1]["round"] = 999
        self.assert_rejected(self.run_analysis(engine=False))

    def test_native_fight_indexes_must_start_at_zero_without_gaps(self):
        self.fights[-1]["index"] = 17
        self.assert_rejected(self.run_analysis(engine=False))

    def test_a_recorded_round_cannot_lose_all_encounters_even_if_totals_match(self):
        self.fights.pop()
        self.summary["encounters"] -= 1
        self.tournaments[-1]["encounters"] -= 1
        self.assert_rejected(self.run_analysis(engine=False))

    def test_zero_requested_engine_batch_is_not_comparison_evidence(self):
        self.engine["requested"] = 0
        self.engine["trials"] = []
        self.assert_rejected(self.run_analysis())


if __name__ == "__main__":
    unittest.main()
