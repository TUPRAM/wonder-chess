"""Fail-closed evidence accounting, using tiny synthetic CSV fixtures."""
import csv
import json
from pathlib import Path
import tempfile
import unittest

from tools.vnext.summarize_mechanic_diagnostics import summarize


class MechanicDiagnosticEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="wc-diagnostic-evidence-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.process = {"compile_exit": 0, "test_exit": 0, "source_stable": True, "diagnostics": True,
                        "first_seed": 1, "requested_tournaments": 1, "variant": "control", "source_hashes": {}}
        self.write_process()
        self.csv("tournaments.csv", [{"seed": 1, "rounds": 1, "capped": 0, "encounters": 1,
                                     "timeouts": 0, "command_rejects": 0, "simulated_ms": 1000}])
        self.csv("encounters.csv", [{"seed": 1, "round": 1, "index": 0, "kind": "pvp", "timeout": 0,
                                   "winner": 0, "deaths": 1, "effective_healing_cp": 5}])
        self.trace_rows = [dict(seed=1, round=1, index=0, kind="pvp", hero="wc_vn_grandmother_root",
            phase=phase, reason=reason, count=1, recipients=recipients, full_health_ally_pulses=0,
            requested_cp=requested, resolved_cp=resolved) for phase, reason, recipients, requested, resolved in
            (("committed", "ready", 0, 0, 0), ("released", "ready", 0, 0, 0), ("impact", "resolved", 1, 8, 5))]
        self.csv("mechanic_outcomes.csv", self.trace_rows)
        self.csv("seat_rounds.csv", [dict(seed=1, round=1, kind="pvp_or_ghost", health_before=10, damage=2, health_after=8)])
        self.csv("recruitment_by_level.csv", [dict(hero="wc_vn_grandmother_root", level=3, new_offer_slots=1,
            affordable_at_first_observed_offer=1, legal_buy_at_first_observed_offer=1, purchased_copies=1, deployed_unit_rounds=1)])
        for name in ("variant.json", "recruitment.csv", "fixtures.csv"):
            (self.root / name).write_text("synthetic fixture\n", encoding="utf-8")

    def csv(self, name, entries):
        with (self.root / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(entries[0]))
            writer.writeheader()
            writer.writerows(entries)

    def write_process(self):
        (self.root / "process.json").write_text(json.dumps(self.process), encoding="utf-8")

    def test_small_and_absent_strata_never_pass_screen(self):
        result = summarize(self.root)
        self.assertEqual(result["strata"]["pvp"]["timeout_screen"], "INSUFFICIENT")
        self.assertEqual(result["strata"]["ghost"]["timeout_screen"], "INSUFFICIENT")
        self.assertIsNone(result["strata"]["ghost"]["timeout_percent"])

    def test_incomplete_or_unstable_run_rejected(self):
        for field, value in (("test_exit", 1), ("source_stable", False), ("diagnostics", False)):
            before = self.process[field]
            self.process[field] = value
            self.write_process()
            with self.assertRaises(ValueError): summarize(self.root)
            self.process[field] = before

    def test_missing_seed_rejected(self):
        self.process["requested_tournaments"] = 2
        self.write_process()
        with self.assertRaisesRegex(ValueError, "seeds"): summarize(self.root)

    def test_unclosed_commitment_rejected(self):
        self.csv("mechanic_outcomes.csv", [self.trace_rows[0], self.trace_rows[2]])
        with self.assertRaisesRegex(ValueError, "commitment"): summarize(self.root)

    def test_healing_total_mismatch_rejected(self):
        self.trace_rows[2]["resolved_cp"] = 6
        self.csv("mechanic_outcomes.csv", self.trace_rows)
        with self.assertRaisesRegex(ValueError, "healing"): summarize(self.root)

    def test_orphan_trace_rejected(self):
        self.trace_rows[0]["index"] = 9
        self.csv("mechanic_outcomes.csv", self.trace_rows)
        with self.assertRaisesRegex(ValueError, "no encounter"): summarize(self.root)

    def test_captain_damage_mismatch_rejected(self):
        self.csv("seat_rounds.csv", [dict(seed=1, round=1, kind="pvp_or_ghost", health_before=10, damage=2, health_after=9)])
        with self.assertRaisesRegex(ValueError, "Captain damage"): summarize(self.root)


if __name__ == "__main__":
    unittest.main()
