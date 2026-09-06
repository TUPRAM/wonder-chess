"""Tests the evidence reader only; synthetic exports never count as game evidence."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("audit", Path(__file__).with_name("audit_network_evidence.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class EvidenceReaderTests(unittest.TestCase):
    def test_retained_recap_does_not_claim_current_seat_health(self):
        recap = {"round": 1, "damage": [3, 0], "encounters": [{"winner": 1}]}
        rows = [{"public": {"round": round_number, "recap": recap,
                            "seats": [{"id": 0, "health": health, "wins": 0, "place": 0}]}}
                for round_number, health in [(2, 27), (3, 23)]]
        self.assertEqual(len(MODULE.sets_by(rows, "settlement")[1]), 1)

    def test_known_consistent_exports_and_detected_divergence(self):
        with tempfile.TemporaryDirectory(prefix="wc-audit-fixture-") as directory:
            root = Path(directory)
            paths = []
            names = ["out_of_order_sequence_rejected", "original_idempotent_lock_request",
                     "duplicate_request_applies_once", "changed_payload_same_request_rejected"]
            for seat in range(2):
                path = root / str(seat)
                path.mkdir()
                session_path = path / "session.json"
                pid = 100 + seat
                public = {"phase": 1, "round": 1, "matchNamespace": 1,
                          "seats": [{"id": i, "human": i < 2, "health": 30,
                                     "wins": 0, "place": 0} for i in range(8)],
                          "pairs": [{"a": 0, "b": 1, "ghost": False}],
                          "encounters": [{"a": 0, "b": 1, "ghost": False, "tick": 10, "units": []}],
                          "recap": {"round": 1}}
                session = {"match_namespace": 1, "process_id": pid, "seat": seat,
                           "network_mode": 2 + seat, "authority_process": seat == 0,
                           "received_state_privacy_violations": [], "round": 1,
                           "command_probes": [{"name": name, "status": "PASS"} for name in names],
                           "actual_accepted_replies": 3, "actual_rejected_replies": 2,
                           "complete": True, "aborted": False, "public_snapshot": json.dumps(public)}
                session_path.write_text(json.dumps(session), encoding="utf-8")
                row = {"public": public, "owner_private": {"seat": seat, "revision": 1 << 32}}
                snapshot_path = path / f"match-1-seat-{seat}-pid-{pid}-snapshots.jsonl"
                snapshot_path.write_text(json.dumps(row) + "\n", encoding="utf-8")
                paths.append(session_path)
            result = MODULE.audit(*paths, require_complete=True)
            self.assertEqual(result["status"], "PASS", result)
            first = MODULE.load(paths[0])
            first["extended_authority_checks"] = True
            paths[0].write_text(json.dumps(first), encoding="utf-8")
            missing_extended = MODULE.audit(*paths, require_complete=True)
            self.assertEqual(missing_extended["status"], "INCOMPLETE")
            required = {c["check"] for c in missing_extended["checks"] if c["status"] == "NOT_RUN"}
            self.assertIn("process_0_foreign_unit_sale_rejected", required)
            self.assertIn("process_0_combat_phase_buy_rejected", required)
            self.assertIn("process_0_stale_revision_rejected", required)
            second = MODULE.load(paths[1])
            second["process_id"] = 100
            second["complete"] = False
            second["received_state_privacy_violations"] = ["public.seats[0].gold"]
            paths[1].write_text(json.dumps(second), encoding="utf-8")
            result = MODULE.audit(*paths, require_complete=True)
            self.assertEqual(result["status"], "FAIL")
            failures = {c["check"] for c in result["checks"] if c["status"] == "FAIL"}
            self.assertIn("distinct_processes", failures)
            self.assertIn("process_1_received_state_privacy", failures)
            self.assertIn("process_1_complete_tournament", failures)
            missing = {c["check"] for c in result["checks"] if c["status"] == "NOT_RUN"}
            self.assertIn("combat_public_state_agreement", missing)


if __name__ == "__main__":
    unittest.main()
