"""Synthetic analyzer tests only. These never count as Unreal execution evidence."""

import json
import tempfile
import unittest
from pathlib import Path

from audit_session_transitions import disconnect, restart


def write_session(directory, pid, seat, namespace=1, **overrides):
    directory.mkdir(parents=True, exist_ok=True)
    value = {"process_id": pid, "seat": seat, "match_namespace": namespace,
             "authority_process": seat == 0, "network_mode": 2 if seat == 0 else 3,
             "complete": False, "aborted": False, "process_exit_requested": False,
             "elapsed_wall_seconds": 120, **overrides}
    prefix = f"match-{namespace}-seat-{seat}-pid-{pid}"
    path = directory / (prefix + "-session.json")
    path.write_text(json.dumps(value), encoding="utf-8")
    (directory / "session.json").write_text(json.dumps(value), encoding="utf-8")
    public = {"phase": 0, "round": 1, "matchNamespace": namespace,
              "seats": [{"id": i, "human": i < 2} for i in range(8)]}
    row = {"public": public, "owner_private": {"seat": seat, "revision": namespace << 32}}
    (directory / (prefix + "-snapshots.jsonl")).write_text(json.dumps(row) + "\n", encoding="utf-8")
    return path


class TransitionReaderTests(unittest.TestCase):
    def test_client_loss_requires_preserved_resources_and_actual_exit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            before = {"seat": 1, "human": True, "takeover": False, "gold": 20, "sequence": 8, "roster": [1, 3]}
            after = {**before, "human": False, "takeover": True}
            transition = {"departed_seat": 1, "status": "PASS", "before": before, "after": after,
                          "elapsed_wall_seconds": 60}
            host = write_session(root / "host", 100, 0, authority_takeover_transitions=[transition])
            client = write_session(root / "client", 101, 1, process_exit_requested=True)
            self.assertEqual(disconnect(host, client, "client-loss")["status"], "PASS")
            after["gold"] = 25
            host = write_session(root / "host", 100, 0, authority_takeover_transitions=[transition])
            self.assertEqual(disconnect(host, client, "client-loss")["status"], "FAIL")
            transition["status"] = "INCONCLUSIVE"
            host = write_session(root / "host", 100, 0, authority_takeover_transitions=[transition])
            self.assertEqual(disconnect(host, client, "client-loss")["status"], "INCOMPLETE")

    def test_host_loss_follows_client_through_menu_travel(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            host = write_session(root / "host", 100, 0, process_exit_requested=True)
            write_session(root / "client", 101, 1)
            client = write_session(root / "client", 101, -1, namespace=0, authority_process=True,
                                   network_mode=0, host_disconnected=True, aborted=True,
                                   network_error="Host disconnected", network_error_detail="ConnectionLost")
            self.assertEqual(disconnect(host, client, "host-loss")["status"], "PASS")
            client = write_session(root / "client", 101, -1, namespace=0, authority_process=True,
                                   network_mode=0, host_disconnected=False, aborted=True)
            self.assertEqual(disconnect(host, client, "host-loss")["status"], "FAIL")

    def test_restart_requires_real_old_request_rejection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = write_session(root, 100, 0, complete=True, restart_requested_from_this_match=True)
            second = write_session(root, 100, 0, namespace=2, complete=True,
                                   prior_match_namespace=1, restart_requested_from_this_match=False,
                                   command_probes=[{"name": "previous_match_request_rejected", "status": "PASS"}])
            self.assertEqual(restart(first, second)["status"], "PASS")
            second = write_session(root, 100, 0, namespace=2, complete=True,
                                   prior_match_namespace=1, restart_requested_from_this_match=False)
            self.assertEqual(restart(first, second)["status"], "INCOMPLETE")

    def test_two_restarts_require_each_real_transition_and_final_stop(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = write_session(root, 100, 0, complete=True, restart_requested_from_this_match=True)
            second = write_session(root, 100, 0, namespace=2, complete=True,
                                   prior_match_namespace=1, restart_requested_from_this_match=True,
                                   command_probes=[{"name": "previous_match_request_rejected", "status": "PASS"}])
            third = write_session(root, 100, 0, namespace=3, complete=True,
                                  prior_match_namespace=2, restart_requested_from_this_match=False,
                                  command_probes=[{"name": "previous_match_request_rejected", "status": "PASS"}])
            self.assertEqual(restart(first, second, second_will_restart=True)["status"], "PASS")
            self.assertEqual(restart(second, third)["status"], "PASS")
            self.assertEqual(restart(first, second)["status"], "FAIL")
            self.assertEqual(restart(first, third)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
