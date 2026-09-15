"""Tiny filesystem fixtures exercise manifest failures; these are not Unreal build tests."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.vnext import verify_milestone_package as package_manifest


class MilestonePackageIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="wc-package-identity-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.package = self.root / "package"
        authored = b'{"profile_id":"wonder_vnext","fixture":true}\n'
        source_sha = hashlib.sha256(authored).hexdigest()
        runtime = json.dumps({"profile_id": "wonder_vnext", "balance_version": "fixture-only",
                              "source_sha256": source_sha}).encode()
        runtime_sha1 = hashlib.sha1(runtime).hexdigest()
        header = ('constexpr auto SourceSha256 = "' + source_sha + '";\n'
                  'constexpr auto RuntimeSha1 = "' + runtime_sha1 + '";\n').encode()
        actual = b"fixture-executable\0" + source_sha.encode() + b"\0" + runtime_sha1.encode()
        files = {
            "data/vnext/catalog.json": authored,
            package_manifest.GENERATED_RUNTIME: runtime,
            "data/vnext/generated/WonderVNextCatalog.h": header,
            package_manifest.HEADER: header,
            package_manifest.SOURCE_RUNTIME: runtime,
            "game/WonderChess.uproject": b"{}",
            "tools/vnext/catalog.py": b"# fixture",
            "tools/unreal/package_game.ps1": b"# fixture",
            "game/Source/WonderChessRuntime/Private/Simulation.cpp": b"// fixture",
            "game/Config/DefaultGame.ini": b"[Fixture]\nValue=1\n",
            "game/Binaries/Win64/WonderChess.exe": actual,
        }
        for name, content in files.items():
            self.write(self.source, name, content)
        for name, content in {
            "WonderChess.exe": b"fixture-bootstrap",
            "WonderChess/Binaries/Win64/WonderChess.exe": actual,
            "WonderChess/Content/Paks/fixture.ucas": b"fixture-container-not-real-ucas",
            package_manifest.RUNTIME: runtime,
            "Engine/Binaries/ThirdParty/example.dll": b"fixture-dependency",
        }.items():
            self.write(self.package, name, content)
        self.manifest = package_manifest.capture(self.source, self.package)

    @staticmethod
    def write(root, name, content):
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    def verify(self):
        return package_manifest.verify(self.manifest, self.source, self.package)

    def test_exact_round_trip_and_only_runtime_saved_changes_are_ignored(self):
        self.assertEqual("PASS", self.verify()["status"])
        for name in ("Saved/Logs/session.log", "WonderChess/Saved/SaveGames/slot.json", "Engine/Saved/Logs/engine.log"):
            self.write(self.package, name, b"runtime change")
        self.assertEqual("PASS", self.verify()["status"])
        self.write(self.package, "Logs/outside-saved.log", b"unrecorded package content")
        with self.assertRaisesRegex(ValueError, "membership changed"):
            self.verify()

    def test_changed_executables_containers_dependencies_and_source_are_rejected(self):
        mutations = (
            (self.package, "WonderChess.exe"),
            (self.package, "WonderChess/Binaries/Win64/WonderChess.exe"),
            (self.package, "WonderChess/Content/Paks/fixture.ucas"),
            (self.package, "Engine/Binaries/ThirdParty/example.dll"),
            (self.source, "game/Config/DefaultGame.ini"),
            (self.source, "game/Source/WonderChessRuntime/Private/Simulation.cpp"),
        )
        for root, relative in mutations:
            with self.subTest(file=relative):
                target = root / relative
                original = target.read_bytes()
                target.write_bytes(original + b"tampered")
                with self.assertRaisesRegex(ValueError, "bytes differ"):
                    self.verify()
                target.write_bytes(original)

    def test_missing_container_and_unexpected_compiled_source_are_rejected(self):
        target = self.package / "WonderChess/Content/Paks/fixture.ucas"
        original = target.read_bytes()
        target.unlink()
        with self.assertRaisesRegex(ValueError, "cooked containers"):
            self.verify()
        target.write_bytes(original)
        self.write(self.source, "game/Source/WonderChessRuntime/Private/Uncaptured.cpp", b"// unseen")
        with self.assertRaisesRegex(ValueError, "membership changed"):
            self.verify()

    def test_capture_rejects_wrong_runtime_even_when_it_is_valid_json(self):
        wrong = json.loads((self.package / package_manifest.RUNTIME).read_bytes())
        wrong["balance_version"] = "other-version"
        self.write(self.package, package_manifest.RUNTIME, json.dumps(wrong).encode())
        with self.assertRaisesRegex(ValueError, "Packaged runtime catalogue differs"):
            package_manifest.capture(self.source, self.package)
        with self.assertRaisesRegex(ValueError, "bytes differ"):
            self.verify()

    def test_capture_rejects_stale_binary_and_generated_header(self):
        binary = "WonderChess/Binaries/Win64/WonderChess.exe"
        original = (self.package / binary).read_bytes()
        self.write(self.package, binary, b"old-build")
        with self.assertRaisesRegex(ValueError, "differs from the current compiled"):
            package_manifest.capture(self.source, self.package)
        self.write(self.package, binary, original)
        self.write(self.source, package_manifest.HEADER, b"// stale header")
        with self.assertRaisesRegex(ValueError, "headers differ"):
            package_manifest.capture(self.source, self.package)

    def test_capture_rejects_matching_binaries_without_compiled_catalogue_markers(self):
        self.write(self.package, "WonderChess/Binaries/Win64/WonderChess.exe", b"other-build")
        self.write(self.source, "game/Binaries/Win64/WonderChess.exe", b"other-build")
        with self.assertRaisesRegex(ValueError, "lacks the expected compiled"):
            package_manifest.capture(self.source, self.package)

    def test_capture_rejects_a_binary_outside_the_bootstrap_launch_path(self):
        original = self.package / "WonderChess/Binaries/Win64/WonderChess.exe"
        self.write(self.package, "WonderChess/Binaries/Win64/wrong-directory/WonderChess.exe", original.read_bytes())
        original.unlink()
        with self.assertRaisesRegex(ValueError, "exactly one actual game binary"):
            package_manifest.capture(self.source, self.package)

    def test_loose_sidecar_cannot_hide_a_stale_packed_runtime(self):
        self.write(self.package, "WonderChess/Content/Paks/fixture.pak", b"fixture-pak")
        correct = (self.package / package_manifest.RUNTIME).read_bytes()

        def extract(command, **kwargs):
            self.write(Path(command[3]), "WonderChess/VNextData/runtime_catalog.json", b'{"stale":true}')
            return subprocess.CompletedProcess(command, 0, stdout=b"fixture extraction")

        with patch.object(package_manifest.subprocess, "run", side_effect=extract):
            with self.assertRaisesRegex(ValueError, "Loose and packed runtime catalogues differ"):
                package_manifest.capture(self.source, self.package, Path(package_manifest.__file__))
        self.assertEqual(correct, (self.package / package_manifest.RUNTIME).read_bytes())

    def test_malformed_traversal_duplicate_and_broadened_exclusion_manifests_reject(self):
        with self.assertRaises(ValueError):
            package_manifest.verify([])
        for mutation in ("traversal", "duplicate", "exclusions"):
            with self.subTest(mutation=mutation):
                altered = copy.deepcopy(self.manifest)
                if mutation == "traversal":
                    altered["package_files"][0]["path"] = "../outside"
                elif mutation == "duplicate":
                    altered["package_files"].append(altered["package_files"][0])
                else:
                    altered["ignored_runtime_prefixes"].append("engine/")
                with self.assertRaises(ValueError):
                    package_manifest.verify(altered, self.source, self.package)

    def test_cli_writes_fresh_manifest_verifies_and_reports_corruption(self):
        target = self.root / "evidence" / "package.json"
        command = [sys.executable, str(Path(package_manifest.__file__).resolve())]
        capture_args = ["capture", "--manifest", str(target), "--source-root", str(self.source),
                        "--package-root", str(self.package)]
        result = subprocess.run(command + capture_args, capture_output=True, text=True, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        original = target.read_bytes()
        duplicate = subprocess.run(command + capture_args, capture_output=True, text=True, check=False)
        self.assertEqual(1, duplicate.returncode)
        self.assertEqual("FAIL", json.loads(duplicate.stdout)["status"])
        self.assertEqual(original, target.read_bytes())
        for name in ("game/Source/self-invalidating-manifest.json", "GAME/SOURCE/self-invalidating-manifest.json"):
            invalid_target = self.source / name
            invalid_args = list(capture_args)
            invalid_args[2] = str(invalid_target)
            invalid = subprocess.run(command + invalid_args, capture_output=True, text=True, check=False)
            self.assertEqual(1, invalid.returncode)
            self.assertIn("own captured source inventory", json.loads(invalid.stdout)["error"])
            self.assertFalse(invalid_target.exists())
        verify_args = ["verify", "--manifest", str(target)]
        good = subprocess.run(command + verify_args, capture_output=True, text=True, check=False)
        self.assertEqual(0, good.returncode, good.stdout + good.stderr)
        self.assertEqual("PASS", json.loads(good.stdout)["status"])
        self.write(self.package, "WonderChess.exe", b"corrupt bootstrap")
        bad = subprocess.run(command + verify_args, capture_output=True, text=True, check=False)
        self.assertEqual(1, bad.returncode)
        self.assertEqual("FAIL", json.loads(bad.stdout)["status"])


if __name__ == "__main__":
    unittest.main()
