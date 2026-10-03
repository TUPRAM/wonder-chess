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

    def test_mana_experiment_is_opt_in_and_bound_to_runtime(self):
        outputs = CATALOG.artifacts(self.raw)
        runtime = json.loads(outputs["data/vnext/generated/runtime_catalog.json"])
        self.assertEqual(runtime["experiments"], self.source["experiments"])
        self.assertTrue(all("mana" not in hero["ability"] for hero in runtime["heroes"]))
        self.assertIn("WonderVNextManaCatalog()", outputs["data/vnext/generated/WonderVNextCatalog.h"])
        for field, value in (("maximum", 0), ("starting", 10001), ("damageWindowMs", 1), ("damageWindowCap", 1)):
            source = copy.deepcopy(self.source)
            source["experiments"]["mana100_v1"][field] = value
            with self.assertRaises(ValueError):
                CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        source["experiments"]["mana100_v1"]["heroes"][0] = "wc_vn_grove_druid"
        with self.assertRaisesRegex(ValueError, "control heroes"):
            CATALOG.validate(source)

    def test_mana20_changes_only_basic_hit_gain(self):
        first = self.source["experiments"]["mana100_v1"]
        second = self.source["experiments"]["mana100_hit20_v1"]
        self.assertEqual(second, dict(first, basicAttackGain=2000))
        outputs = CATALOG.artifacts(self.raw)
        self.assertIn("WonderVNextMana20Catalog()", outputs["data/vnext/generated/WonderVNextCatalog.h"])
        for key, value in (("starting", 1000), ("damageEventCap", 1000), ("damageGainAtFullHealth", 9000), ("basicAttackGain", 1500)):
            source = copy.deepcopy(self.source)
            source["experiments"]["mana100_hit20_v1"][key] = value
            with self.assertRaisesRegex(ValueError, "only basicAttackGain"):
                CATALOG.validate(source)

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
        self.assertEqual(len(self.source["heroes"]), 40)
        self.assertEqual(len(runtime["heroes"]), 14)
        for trait in self.source["traits"]:
            self.assertEqual((len(trait["members"]), trait["thresholds"]), (4, [2, 4]), trait["id"])
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
        inactive = next(i for i, trait in enumerate(self.source["traits"]) if not trait["runtime_enabled"])
        source = copy.deepcopy(self.source)
        source["traits"][inactive]["runtime_enabled"] = True
        with self.assertRaisesRegex(ValueError, "implemented stat bonus"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        source["traits"][inactive].update(runtime_enabled=True,
                                          runtime={"stat": "evasion_bp", "scope": "members", "values": [2000, 4000]})
        with self.assertRaisesRegex(ValueError, "Unsupported trait stat"):
            CATALOG.validate(source)

    def test_roster_recipe_adds_mana_and_stat_traits_without_changing_the_control(self):
        outputs = CATALOG.artifacts(self.raw)
        runtime = json.loads(outputs["data/vnext/generated/runtime_catalog.json"])
        self.assertEqual({trait["id"] for trait in runtime["roster_recipe"]["traits"]},
                         {"human", "orc", "beastkin", "dragonkin", "tank", "fighter", "mage"})
        self.assertIn("WonderVNextRosterCatalog()", outputs["data/vnext/generated/WonderVNextCatalog.h"])
        source = copy.deepcopy(self.source)
        source["roster_recipe"]["mana_heroes"].append("wc_vn_shieldbearer")
        with self.assertRaises(ValueError):
            CATALOG.validate(source)

    def test_relics_require_multiple_compatibilities_and_tradeoffs(self):
        self.assertEqual(len(self.source["relics"]), 12)
        self.assertTrue(all(relic["compatible_mechanics"] == [] for relic in self.source["relics"]))
        source = copy.deepcopy(self.source)
        source["relics"][0]["compatible_mechanics"] = ["screened_strike"]
        with self.assertRaises(ValueError):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        source["relics"][0]["modifiers"]["skillPowerBp"] = 0
        with self.assertRaisesRegex(ValueError, "requires a benefit"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        source["relics"][0]["modifiers"]["radiusDelta"] = 1
        with self.assertRaisesRegex(ValueError, "may not reshape"):
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
