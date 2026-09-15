"""Verify actual Git checkout preserves the successor's source and runtime identity."""
import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("vnext_checkout_catalog", ROOT / "tools/vnext/catalog.py")
CATALOG = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CATALOG)
GIT = shutil.which("git")


@unittest.skipUnless(GIT, "Git is required for checkout identity verification")
class VNextCheckoutIdentityTests(unittest.TestCase):
    def test_checkout_identity_under_each_autocrlf_policy(self):
        source = CATALOG.SOURCE.read_bytes()
        outputs = CATALOG.artifacts(source)
        snapshots = {
            ".gitattributes": (ROOT / ".gitattributes").read_bytes(),
            "data/vnext/catalog.json": source,
            **{name: (ROOT / name).read_bytes() for name in outputs},
        }
        staged_name = "game/Content/WonderChess/VNextData/runtime_catalog.json"
        snapshots[staged_name] = (ROOT / staged_name).read_bytes()
        self.assertEqual(snapshots[staged_name], outputs["data/vnext/generated/runtime_catalog.json"].encode("utf-8"))
        for name, generated in outputs.items():
            self.assertEqual(snapshots[name], generated.encode("utf-8"), name)

        for policy in ("true", "false", "input"):
            with self.subTest(core_autocrlf=policy), tempfile.TemporaryDirectory(prefix="wc-checkout-") as temporary:
                checkout = Path(temporary)
                environment = dict(os.environ)
                environment.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
                # An inherited external Git directory/index must never redirect fixture commands.
                for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
                    environment.pop(name, None)

                def git(*arguments):
                    result = subprocess.run(
                        [GIT, "-c", f"core.autocrlf={policy}", "-c", "core.safecrlf=false", *arguments],
                        cwd=checkout,
                        env=environment,
                        check=False,
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    return result.stdout

                git("init", "--quiet", "--template=")
                for name, content in snapshots.items():
                    destination = checkout / name
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(content)
                git("add", "--", *snapshots)
                # Force real smudge/checkout conversion from the temporary Git index.
                for name in snapshots:
                    (checkout / name).unlink()
                git("checkout-index", "--all", "--force")

                restored_source = (checkout / "data/vnext/catalog.json").read_bytes()
                self.assertEqual(restored_source, source, "Source digest must survive a real checkout")
                restored_outputs = CATALOG.artifacts(restored_source)
                self.assertEqual(restored_outputs, outputs)
                for name in (*outputs, staged_name):
                    self.assertEqual((checkout / name).read_bytes(), snapshots[name], name)
                runtime = (checkout / staged_name).read_bytes()
                header = (checkout / "game/Source/WonderChessRuntime/Public/VNext/WonderVNextCatalog.generated.h").read_text(encoding="utf-8")
                self.assertIn(hashlib.sha256(restored_source).hexdigest(), header)
                self.assertIn(hashlib.sha1(runtime).hexdigest(), header)


if __name__ == "__main__":
    unittest.main()
