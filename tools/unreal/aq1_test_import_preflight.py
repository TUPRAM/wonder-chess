"""Run with ordinary Python; these tests do not execute Unreal or certify imports."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("aq1_import", Path(__file__).with_name("aq1_import_candidate.py"))
aq1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aq1)


class CandidatePreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "art-source/heroes" / aq1.UID / "candidates/AQ1/Ada.blend"
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(b"TEST_ONLY_NOT_A_BLEND")
        self.export = self.source.parent / "exports"
        self.export.mkdir()
        data = self.root / "data/units.json"
        data.parent.mkdir()
        data.write_text('{"units": []}', encoding="utf-8")
        self.names = [f"SK_{aq1.UID}.fbx"] + [f"AN_{aq1.UID}_{clip}.fbx" for clip in aq1.CLIPS]
        self.names += [f"T_{aq1.UID}_{kind}.png" for kind in ("BaseColor", "ORM", "Normal")]
        for name in self.names:
            (self.export / name).write_bytes(b"TEST_ONLY_NOT_AN_ASSET")
        self.manifest = {
            "unit_id": aq1.UID, "source_sha256": aq1.digest(self.source),
            "units_source_sha256": aq1.digest(data), "fps": 60,
            "clips": {name: {"frames": [1, 61]} for name in aq1.CLIPS},
            "files": {name: aq1.digest(self.export / name) for name in self.names},
        }
        self.persist()
        self.env = {
            "WC_AQ1_SOURCE_BLEND": str(self.source), "WC_AQ1_EXPORT": str(self.export),
            "WC_AQ1_REPORT": str(self.root / "reports/aq1/import.json"),
            "WC_AQ1_REVISION": "Ada_r01", "WC_AQ1_NORMAL_GREEN": "flip",
        }

    def persist(self):
        (self.export / "export_manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def test_valid_manifest_only_passes_preflight(self):
        self.assertEqual(aq1.preflight(self.root, self.env)[2], "Ada_r01")

    def test_rejects_canonical_source(self):
        self.env["WC_AQ1_SOURCE_BLEND"] = str(self.root / "art-source/heroes" / aq1.UID / "Ada.blend")
        with self.assertRaisesRegex(ValueError, "ownership"):
            aq1.preflight(self.root, self.env)

    def test_rejects_canonical_exports(self):
        self.env["WC_AQ1_EXPORT"] = str(self.root / "exports/heroes" / aq1.UID)
        with self.assertRaisesRegex(ValueError, "Canonical exports"):
            aq1.preflight(self.root, self.env)

    def test_rejects_destination_traversal(self):
        self.env["WC_AQ1_REVISION"] = "../../Heroes"
        with self.assertRaisesRegex(ValueError, "identifier"):
            aq1.preflight(self.root, self.env)

    def test_rejects_changed_mesh(self):
        (self.export / self.names[0]).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "changed frozen"):
            aq1.preflight(self.root, self.env)

    def test_rejects_changed_candidate_source(self):
        self.source.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "source identity/hash"):
            aq1.preflight(self.root, self.env)

    def test_rejects_stale_canonical_stats_provenance(self):
        (self.root / "data/units.json").write_text('{"units": [1]}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "current canonical units"):
            aq1.preflight(self.root, self.env)

    def test_rejects_incomplete_clip_set(self):
        self.manifest["clips"].pop("Hit")
        self.persist()
        with self.assertRaisesRegex(ValueError, "seven named clips"):
            aq1.preflight(self.root, self.env)

    def test_requires_explicit_green_channel_choice(self):
        self.env["WC_AQ1_NORMAL_GREEN"] = "automatic"
        with self.assertRaisesRegex(ValueError, "green-channel"):
            aq1.preflight(self.root, self.env)

    def test_refuses_to_overwrite_evidence(self):
        path = Path(self.env["WC_AQ1_REPORT"])
        path.parent.mkdir(parents=True)
        path.write_text('{}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "fresh"):
            aq1.preflight(self.root, self.env)

    def test_protects_other_candidate_revision_and_production(self):
        content = self.root / "game/Content"
        paths = ("WonderChess/Heroes/Ada.uasset", "WonderChess/Candidates/AQ1/Ada_r00/Ada.uasset",
                 "WonderChess/Candidates/AQ1/Ada_r01/Ada.uasset")
        for relative in paths:
            path = content / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"TEST")
        hashes = aq1.protected_hashes(self.root, "Ada_r01")
        self.assertEqual(set(hashes), set(paths[:2]))
        (content / paths[0]).write_bytes(b"changed")
        self.assertEqual(aq1.changed(hashes, aq1.protected_hashes(self.root, "Ada_r01"))["modified"], [paths[0]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
