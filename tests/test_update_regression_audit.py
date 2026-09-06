"""Synthetic analyzer fault injections; these do not count as game tournaments."""

from copy import deepcopy
import importlib.util
from pathlib import Path
from contextlib import redirect_stdout
import io
import json
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("update_regression_audit", Path(__file__).parent / "runtime/audit_update_regression.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture():
    ids = [f"synthetic_hero_{index}" for index in range(24)]
    rules = {"schema_version": "3.1.0", "balance_version": "synthetic", "profile_id": "alpha_24", "alpha_unit_ids": ids,
             "tournament": {"seats": 8, "max_rounds": 1, "starting_health": 60, "neutral_opening_rounds": 3,
                            "neutral_every_rounds": 5, "neutral_failure_damage": 2, "combat_timeout_ms": 40000},
             "simulation": {"tick_ms": 50}, "economy": {"neutral_win_income": 2},
             "board": {"columns": 8, "deployment_rows_per_side": 4}}
    wave = {"round": 1, "id": "synthetic_wave"}
    settlements, fights, locks, use, compositions, native_fights, native_rounds = [], [], [], [], [], [], []
    for seat in range(8):
        result = {"seat": seat, "health": 60, "gold": 10, "damage": 0, "wins": 0, "placement": 1}
        settlements.append(result)
        native_rounds.append({**result, "seed": 1, "round": 1, "pre_hash": "10", "post_hash": "20",
                              "settlement_id": "999", "neutral": 1, "pvp_round_index": 0, "pending_reward": 2})
        fights.append({"a": seat, "b": -1, "ghost": False, "neutral": True, "kind": "neutral", "waveId": wave["id"],
                       "sides": [{"seat": seat, "waveId": ""}, {"seat": None, "waveId": wave["id"]}],
                       "winner": 0, "ticks": 1, "timeout": False, "complete": True, "simulated_ms": 50,
                       "survivors_a": 3, "survivors_b": 0})
        native_fights.append({"seed": 1, "round": 1, "pvp_round_index": 0, "kind": 2, "wave_id": wave["id"],
                              "seat_a": seat, "seat_b": -1, "winner": 0, "ticks": 1, "timeout": 0,
                              "survivors_a": 3, "survivors_b": 0})
        units = []
        for index in range(3):
            definition = seat * 3 + index
            units.append({"id": definition + 1, "def": definition, "neutral": False, "star": 1,
                          "board": True, "col": index, "row": 1, "bench": -1})
            compositions.append({"seed": 1, "round": 1, "seat": seat, "unit_id": definition + 1,
                                 "definition": ids[definition], "star": 1, "on_board": 1,
                                 "column": index, "row": 1, "bench": -1, "level": 3})
        locks.append({"seat": seat, "units": units})
        for hero, hero_id in enumerate(ids):
            count = int(hero // 3 == seat)
            use.append({"seat": seat, "unit_id": hero_id, "final_placement": 1,
                        "deployed_unit_rounds": count, "rounds_deployed": count,
                        "distinct_owned_instances": count, "maximum_deployed_star": count})
    trial = {"seed": 1, "phase": 3, "pass": True, "error": "", "capped": True, "unresolved_encounters": 0,
             "command_rejects": 0, "rejected_commands": [], "steps": 1, "invariant_checks": 1,
             "commands": 8, "fights": 8, "timeouts": 0, "ghosts": 0, "simulated_ms": 50,
             "placements": [{"seat": seat, "placement": 1, "health": 60} for seat in range(8)],
             "rounds": [{"round": 1, "settlement_id": "123456", "pre_hash": "10", "post_hash": "20",
                         "encounters": fights, "seats": settlements}],
             "combat_lock_deployments": [{"round": 1, "seats": locks}], "hero_use_by_seat": use}
    data = {"complete": True, "failed": 0, "evidence_write_failed": False, "requested": 1, "attempted": 1,
            "trials": [trial], "profile_id": "alpha_24", "schema_version": "3.1.0", "balance_version": "synthetic",
            "tick_ms": 50, "digest": "synthetic-digest"}
    native = {"summary": {"content_digest": data["digest"], "encounters": 8, "timeouts": 0, "ghosts": 0},
              "tournaments": [{"seed": 1, "rounds": 1, "simulated_ms": 50, "final_hash": "20", "winner_seats": 8,
                               "encounters": 8, "timeouts": 0, "ghosts": 0, "bot_commands": 8, "bot_rejects": 0}],
              "rounds": native_rounds, "fights": native_fights, "compositions": compositions,
              "decisions": [{"seed": 1, "round": 1, "seat": seat, "accepted": 1, "gold_after": 10} for seat in range(8)]}
    return data, native, rules, [wave]


class UpdateRegressionAuditTests(unittest.TestCase):
    def setUp(self):
        self.data, self.native, self.rules, self.waves = fixture()

    def audit(self):
        return MODULE.audit_payload(self.data, self.native, self.rules, self.waves, 1)[0]

    def fails(self, category):
        result = self.audit()
        self.assertGreater(result.categories[category]["failed"], 0, result.failures)

    def test_matching_rows_allow_different_process_settlement_ids(self):
        result = self.audit()
        self.assertEqual(result.failed, 0, result.failures)

    def test_neutral_owner_must_be_null_not_a_player(self):
        self.data["trials"][0]["rounds"][0]["encounters"][0]["sides"][1]["seat"] = 0
        self.fails("neutral_typed_owner")

    def test_neutral_wave_identity_cannot_change(self):
        self.data["trials"][0]["rounds"][0]["encounters"][0]["waveId"] = "different_wave"
        self.fails("neutral_typed_owner")

    def test_wrong_fight_winner_is_detected(self):
        self.native["fights"][0]["winner"] = 1
        self.fails("native_fight_parity")

    def test_wrong_fight_duration_is_detected(self):
        self.native["fights"][0]["ticks"] = 2
        self.fails("native_fight_parity")

    def test_duplicate_round_and_settlement_are_rejected(self):
        self.data["trials"][0]["rounds"].append(deepcopy(self.data["trials"][0]["rounds"][0]))
        self.fails("settlement_once")
        self.fails("rounds_contiguous")

    def test_missing_native_round_seat_fails(self):
        self.native["rounds"].pop()
        self.fails("native_round_present")

    def test_duplicate_native_row_cannot_hide_by_dict_overwrite(self):
        self.native["rounds"].append(deepcopy(self.native["rounds"][0]))
        self.fails("native_round_seat_unique")

    def test_native_settlement_must_be_atomic_across_seats(self):
        self.native["rounds"][0]["settlement_id"] = "1000"
        self.fails("native_settlement_once")

    def test_logical_hashes_are_compared_despite_process_namespace_exception(self):
        self.native["rounds"][0]["post_hash"] = "21"
        self.fails("native_logical_hash_parity")

    def test_other_balance_native_run_is_rejected(self):
        self.native["summary"]["content_digest"] = "later-balance-digest"
        self.fails("native_catalog_parity")

    def test_deployment_definition_mutation_is_detected(self):
        self.data["trials"][0]["combat_lock_deployments"][0]["seats"][0]["units"][0]["def"] = 1
        self.fails("native_deployment_parity")

    def test_out_of_range_definition_fails_without_indexing_error(self):
        self.data["trials"][0]["combat_lock_deployments"][0]["seats"][0]["units"][0]["def"] = 999
        self.fails("deployment_legal")

    def test_occupied_deployment_cell_is_illegal(self):
        self.data["trials"][0]["combat_lock_deployments"][0]["seats"][0]["units"][1]["col"] = 0
        self.fails("deployment_legal")

    def test_fabricated_hero_use_is_detected(self):
        self.data["trials"][0]["hero_use_by_seat"][0]["deployed_unit_rounds"] = 99
        self.fails("hero_use_reconciled")

    def test_missing_hero_use_row_is_detected(self):
        self.data["trials"][0]["hero_use_by_seat"].pop()
        self.fails("hero_use_complete_matrix")

    def test_missing_neutral_opponent_fails_isolation(self):
        self.data["trials"][0]["rounds"][0]["encounters"].pop()
        self.fails("every_living_seat_one_fight")

    def test_neutral_reward_and_wins_cannot_be_fabricated(self):
        self.native["rounds"][0]["pending_reward"] = 3
        self.fails("native_pending_neutral_reward")
        self.data["trials"][0]["rounds"][0]["seats"][0]["wins"] = 1
        self.fails("neutral_settlement")

    def test_command_rejection_is_not_hidden_by_success_flag(self):
        self.native["decisions"][0]["accepted"] = 0
        self.fails("native_commands_legal")
        self.data["trials"][0]["command_rejects"] = 1
        self.fails("trial_execution")

    def test_neutral_round_must_not_advance_pvp_index(self):
        self.native["rounds"][0]["pvp_round_index"] = 1
        self.fails("native_round_schedule")

    def test_empty_deployment_rows_remain_explicit(self):
        self.data["trials"][0]["combat_lock_deployments"][0]["seats"][0]["units"] = []
        self.native["compositions"] = [unit for unit in self.native["compositions"] if unit["seat"] != 0]
        result = self.audit()
        self.assertEqual(result.categories["deployment_seat_set"]["failed"], 0)
        self.assertEqual(result.categories["native_deployment_set_complete"]["failed"], 0)
        self.assertEqual(result.categories["native_deployment_parity"]["failed"], 0)
        self.assertGreater(result.categories["hero_use_reconciled"]["failed"], 0)

    def test_eliminated_seat_cannot_retain_combat_deployment(self):
        trial = self.data["trials"][0]
        trial["rounds"].append(deepcopy(trial["rounds"][0]))
        trial["rounds"][0]["seats"][0]["health"] = 0
        trial["rounds"][1]["round"] = 2
        lock = deepcopy(trial["combat_lock_deployments"][0])
        lock["round"] = 2
        trial["combat_lock_deployments"].append(lock)
        self.fails("eliminated_deployment_empty")

    def test_missing_report_writes_failure_without_crashing_or_passing(self):
        with tempfile.TemporaryDirectory(prefix="wc-update-audit-test-") as temporary:
            root = Path(temporary)
            command = ["audit_update_regression.py", str(root / "absent"), "--native-run", str(root / "native"),
                       "--source-data", str(root / "source"), "--output-directory", str(root / "out")]
            with patch("sys.argv", command), redirect_stdout(io.StringIO()):
                self.assertEqual(MODULE.main(), 1)
            report = json.loads((root / "out/regression-analysis.json").read_text())
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["categories"]["malformed_or_missing_evidence"]["failed"], 1)


if __name__ == "__main__":
    unittest.main()
