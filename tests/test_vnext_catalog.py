"""Successor source contract and generated/native/staged identity checks."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("vnext_catalog", ROOT / "tools/vnext/catalog.py")
CATALOG = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CATALOG)


class VNextCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = CATALOG.SOURCE.read_bytes()
        cls.source = json.loads(cls.raw)

    def test_canonical_catalog_validates(self):
        CATALOG.validate(self.source)

    def test_generated_native_runtime_and_dossiers_are_current(self):
        for path, expected in CATALOG.artifacts(self.raw).items():
            self.assertEqual((ROOT / path).read_bytes(), expected.encode("utf-8"), path)

    def test_runtime_digest_binds_exact_staged_bytes(self):
        outputs = CATALOG.artifacts(self.raw)
        runtime = outputs["data/vnext/generated/runtime_catalog.json"].encode("utf-8")
        header = outputs["data/vnext/generated/WonderVNextCatalog.h"]
        self.assertIn(hashlib.sha1(runtime).hexdigest(), header)
        self.assertIn(hashlib.sha256(self.raw).hexdigest(), header)
        staged = ROOT / "game/Content/WonderChess/VNextData/runtime_catalog.json"
        self.assertEqual(staged.read_bytes(), runtime)

    def test_unimplemented_candidates_are_not_executable(self):
        outputs = CATALOG.artifacts(self.raw)
        runtime = json.loads(outputs["data/vnext/generated/runtime_catalog.json"])
        self.assertEqual(len(self.source["heroes"]), 14)
        self.assertEqual(len(runtime["heroes"]), 6)
        self.assertEqual(runtime["traits"], [])
        self.assertEqual({h["cost"] for h in runtime["heroes"]}, {1, 2, 3, 4, 5})
        for hero in self.source["heroes"]:
            if not hero["enabled"]:
                self.assertNotIn(hero["id"], [h["id"] for h in runtime["heroes"]])
                self.assertNotIn("ability", hero)

    def test_unknown_mechanic_fails_before_generation(self):
        source = copy.deepcopy(self.source)
        source["heroes"][0]["ability"]["mechanic"] = "recursive_spell_copy"
        with self.assertRaises(ValueError):
            CATALOG.validate(source)

    def test_bad_shop_weights_and_unavailable_tier_rejected(self):
        source = copy.deepcopy(self.source)
        source["rules"]["shopWeights"]["3"] = [70, 25, 0, 0, 0]
        with self.assertRaisesRegex(ValueError, "sum to 100"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        source["heroes"][5]["cost"] = 4
        with self.assertRaisesRegex(ValueError, "has no hero"):
            CATALOG.validate(source)

    def test_numeric_type_and_quantization_are_strict(self):
        for value in (True, 8.0, "8"):
            source = copy.deepcopy(self.source)
            source["rules"]["columns"] = value
            with self.assertRaises(ValueError):
                CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        source["heroes"][0]["ability"]["castMs"] = 351
        with self.assertRaisesRegex(ValueError, "Unquantized"):
            CATALOG.validate(source)

    def test_schema_rejects_typos_instead_of_ignoring_tuning(self):
        source = copy.deepcopy(self.source)
        source["heroes"][0]["ability"]["guard_reduction"] = 9000
        with self.assertRaisesRegex(ValueError, "Source schema"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        source["rules"]["preperationMs"] = 1
        with self.assertRaisesRegex(ValueError, "Source schema"):
            CATALOG.validate(source)

    def test_roster_growth_has_no_fixed_cardinality_gate(self):
        source = copy.deepcopy(self.source)
        candidate = copy.deepcopy(source["heroes"][-1])
        candidate["id"] = "wc_vn_future_dossier"
        source["heroes"].append(candidate)
        for trait in source["traits"]:
            if trait["id"] in (candidate["race"], candidate["unit_class"]):
                trait["members"].append(candidate["id"])
        CATALOG.validate(source)

    def test_traits_cannot_silently_enable_unimplemented_behaviors(self):
        source = copy.deepcopy(self.source)
        source["traits"][0]["runtime_enabled"] = True
        with self.assertRaisesRegex(ValueError, "require an implementation"):
            CATALOG.validate(source)

    def test_relics_require_multiple_compatibilities_and_tradeoffs(self):
        self.assertEqual(len(self.source["relics"]), 12)
        source = copy.deepcopy(self.source)
        source["relics"][0]["compatible_mechanics"] = ["screened_strike"]
        with self.assertRaises(ValueError):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        source["relics"][0]["modifiers"]["castBp"] = 10000
        with self.assertRaisesRegex(ValueError, "benefit and a tradeoff"):
            CATALOG.validate(source)

    def test_neutral_schedule_and_occupancy_are_total(self):
        source = copy.deepcopy(self.source)
        source["waves"].pop()
        with self.assertRaisesRegex(ValueError, "neutral rounds"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        source["waves"][0]["slots"].append(copy.deepcopy(source["waves"][0]["slots"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate neutral cell"):
            CATALOG.validate(source)


if __name__ == "__main__":
    unittest.main()
