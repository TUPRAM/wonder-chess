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
        self.assertEqual(len(runtime["heroes"]), 40)
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
        for hero in source["heroes"]:
            if hero["enabled"] and hero["cost"] == 5:
                hero["cost"] = 4
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
        original = source["heroes"][-1]
        candidate = copy.deepcopy(original)
        candidate["id"] = "wc_vn_future_dossier"
        if candidate["enabled"]:
            # A playable hero also needs its own ability identity and a place in the roster recipe.
            candidate["ability"]["id"] = "wc_vn_a_future_dossier"
            recipe = source["roster_recipe"]
            recipe["mana_heroes" if original["id"] in recipe["mana_heroes"] else "passive_heroes"].append(candidate["id"])
        source["heroes"].append(candidate)
        for trait in source["traits"]:
            if trait["id"] in (candidate["race"], candidate["unit_class"]):
                trait["members"].append(candidate["id"])
        CATALOG.validate(source)

    def test_traits_cannot_silently_enable_unimplemented_behaviors(self):
        # Every trait is executed now, so take one and strip its executed parts.
        source = copy.deepcopy(self.source)
        source["traits"][0].pop("runtime")
        source["traits"][0].pop("runtime_extra", None)
        with self.assertRaisesRegex(ValueError, "implemented stat bonus"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        source["traits"][0].pop("runtime_extra", None)
        source["traits"][0]["runtime"] = {"stat": "made_up_stat_bp", "scope": "members", "values": [2000, 4000]}
        with self.assertRaisesRegex(ValueError, "Unsupported trait stat"):
            CATALOG.validate(source)

    def test_roster_recipe_adds_mana_and_stat_traits_without_changing_the_control(self):
        outputs = CATALOG.artifacts(self.raw)
        runtime = json.loads(outputs["data/vnext/generated/runtime_catalog.json"])
        self.assertEqual({trait["id"] for trait in runtime["roster_recipe"]["traits"]},
                         {"human", "orc", "beastkin", "dragonkin", "tank", "fighter", "mage", "undead",
                          "dwarf", "priest", "engineer", "sniper", "elemental", "goblin",
                          "elf", "warlock", "demon", "assassin", "shaman", "summoner"})
        self.assertIn("WonderVNextRosterCatalog()", outputs["data/vnext/generated/WonderVNextCatalog.h"])
        source = copy.deepcopy(self.source)
        source["roster_recipe"]["mana_heroes"].append("wc_vn_shieldbearer")
        with self.assertRaises(ValueError):
            CATALOG.validate(source)

    def test_schema_and_generator_agree_on_ability_names(self):
        # The generator's tables are the one source; the schema must list exactly the same names.
        schema = json.loads((ROOT / "data/vnext/catalog.schema.json").read_text(encoding="utf-8"))
        ability = schema["properties"]["heroes"]["items"]["oneOf"][0]["properties"]["ability"]["properties"]
        for key, table in (("mechanic", CATALOG.MECHANICS), ("effect", CATALOG.EFFECTS),
                           ("selector", CATALOG.SELECTORS), ("damageType", CATALOG.DAMAGE_TYPES)):
            self.assertEqual(set(ability[key]["enum"]), set(table), key)
        self.assertEqual(set(ability["effects"]["items"]["properties"]["effect"]["enum"]), set(CATALOG.EFFECTS))

    def test_effect_chains_allow_up_to_four_generic_effects(self):
        stitcher = next(hero for hero in self.source["heroes"] if hero["id"] == "wc_vn_stitcher")
        self.assertEqual([part["effect"] for part in stitcher["ability"]["effects"]], ["heal", "shield"])
        header = CATALOG.artifacts(self.raw)["data/vnext/generated/WonderVNextCatalog.h"]
        self.assertIn("u.ability.effects.push_back({wc::Effect::Shield,wc::DamageType::Magic,4000,{11000,18000,29000},250});", header)
        source = copy.deepcopy(self.source)
        chain = next(hero for hero in source["heroes"] if hero["id"] == "wc_vn_stitcher")["ability"]["effects"]
        chain.extend(copy.deepcopy(chain) + copy.deepcopy(chain[:1]))
        with self.assertRaises(Exception):
            CATALOG.artifacts(json.dumps(source).encode("utf-8"))
        source = copy.deepcopy(self.source)
        next(hero for hero in source["heroes"] if hero["id"] == "wc_vn_stitcher")["ability"]["effects"][1]["delayMs"] = 275
        with self.assertRaisesRegex(ValueError, "Unquantized chained effect timing"):
            CATALOG.validate(source)

    def test_stat_modifiers_name_a_supported_stat(self):
        header = CATALOG.artifacts(self.raw)["data/vnext/generated/WonderVNextCatalog.h"]
        self.assertIn("{-2500,-3500,-5000},0,false,wc::Selector::CurrentEnemy,wc::ModifierStat::AttackDamage});", header)
        self.assertIn('t.id = "undead"; t.stat = "enemy_armor_reduction_flat";', header)
        source = copy.deepcopy(self.source)
        jinx = next(hero for hero in source["heroes"] if hero["id"] == "wc_vn_jinxer")["ability"]["effects"]
        jinx[0]["stat"] = "armor"
        with self.assertRaisesRegex(ValueError, "Only a stat modifier names a stat"):
            CATALOG.validate(source)

    def test_a_trait_may_have_several_parts(self):
        outputs = CATALOG.artifacts(self.raw)
        header = outputs["data/vnext/generated/WonderVNextCatalog.h"]
        self.assertIn('t.id = "sniper"; t.stat = "range_bonus_flat";', header)
        self.assertIn('t.id = "sniper"; t.stat = "basic_damage_bonus_bp";', header)
        source = copy.deepcopy(self.source)
        sniper = next(trait for trait in source["traits"] if trait["id"] == "sniper")
        sniper["runtime_extra"][0]["stat"] = sniper["runtime"]["stat"]
        with self.assertRaisesRegex(ValueError, "A trait names each stat once"):
            CATALOG.validate(source)

    def test_target_shapes_reach_the_runtime_and_need_the_standard_mechanic(self):
        header = CATALOG.artifacts(self.raw)["data/vnext/generated/WonderVNextCatalog.h"]
        heroes = {hero["id"]: hero for hero in self.source["heroes"]}
        for hero_id, selector in (("wc_vn_rifleman", "FarthestEnemy"), ("wc_vn_siege_master", "DensestEnemyArea"),
                                  ("wc_vn_forge_king", "RandomEnemyAreas"), ("wc_vn_longbow_scout", "EnemyLine"),
                                  ("wc_vn_flame_regent", "EnemyCone"), ("wc_vn_storm_spirit", "ChainFromCurrentEnemy"),
                                  ("wc_vn_bonechanter", "ChainFromCurrentEnemy"), ("wc_vn_dawn_oracle", "AllAllies")):
            self.assertEqual(CATALOG.SELECTORS[heroes[hero_id]["ability"]["selector"]], selector)
            self.assertIn(f"u.ability.selector = wc::Selector::{selector};", header)
        source = copy.deepcopy(self.source)
        ported = next(hero for hero in source["heroes"] if hero["enabled"] and hero["ability"]["mechanic"] != "standard")
        ported["ability"]["selector"] = "enemy_cone"
        with self.assertRaisesRegex(ValueError, "Standard selectors and effects need the standard mechanic"):
            CATALOG.validate(source)

    def test_statuses_carry_their_duration_per_star_and_the_hex_trait_its_own(self):
        header = CATALOG.artifacts(self.raw)["data/vnext/generated/WonderVNextCatalog.h"]
        self.assertIn("u.ability.effects.push_back({wc::Effect::Hex,wc::DamageType::Magic,2500,{2500,3500,5000}});", header)
        self.assertIn("{wc::Effect::Taunt,wc::DamageType::Physical,2000,{2000,2500,3000},0,true,wc::Selector::AdjacentEnemies});", header)
        self.assertIn("{wc::Effect::ManaDrain,wc::DamageType::Magic,0,{5000,7500,10000}});", header)
        self.assertIn('t.id = "shaman"; t.stat = "enemy_hex_count"; t.team = false; t.durationMs = 3000; t.tiers = {{2,1},{4,2}};', header)

        def hero(source, identity):
            return next(hero for hero in source["heroes"] if hero["id"] == identity)["ability"]

        source = copy.deepcopy(self.source)
        hero(source, "wc_vn_owl_seer")["durationMs"] = 3000
        with self.assertRaisesRegex(ValueError, "A status lasts its magnitude"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        hero(source, "wc_vn_void_wyrm")["effects"][1]["magnitude"][2] = 5025
        with self.assertRaisesRegex(ValueError, "A status lasts its magnitude"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        hero(source, "wc_vn_void_wyrm")["effects"][0]["magnitude"][2] = 10050
        with self.assertRaisesRegex(ValueError, "A mana drain removes at most a full bar"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        next(trait for trait in source["traits"] if trait["id"] == "undead")["runtime"]["durationMs"] = 3000
        with self.assertRaisesRegex(ValueError, "Only a hex trait carries a duration"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        del next(trait for trait in source["traits"] if trait["id"] == "shaman")["runtime"]["durationMs"]
        with self.assertRaisesRegex(ValueError, "Only a hex trait carries a duration"):
            CATALOG.validate(source)

    def test_a_blink_names_a_cell_and_a_guaranteed_critical_is_a_direct_hit(self):
        header = CATALOG.artifacts(self.raw)["data/vnext/generated/WonderVNextCatalog.h"]
        self.assertIn("{wc::Effect::Blink,wc::DamageType::Physical,0,{0,0,0},0,true,wc::Selector::CellBehindTarget});", header)
        self.assertIn("{wc::Effect::Damage,wc::DamageType::Physical,0,{15000,24000,38000},0,false,wc::Selector::FarthestEnemy,"
                      "wc::ModifierStat::AttackRate,0,false,true});", header)
        self.assertIn("{wc::Effect::Blink,wc::DamageType::Physical,0,{0,0,0},0,true,wc::Selector::CellThroughTarget});", header)
        self.assertIn('t.id = "assassin"; t.stat = "start_leap"; t.team = false; t.tiers = {{2,1},{4,1}};', header)

        def hero(source, identity):
            return next(hero for hero in source["heroes"] if hero["id"] == identity)["ability"]

        source = copy.deepcopy(self.source)
        del hero(source, "wc_vn_moonblade")["effects"][0]["selector"]
        with self.assertRaisesRegex(ValueError, "A blink names a cell selector"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        hero(source, "wc_vn_moonblade")["effects"][1]["selector"] = "cell_beside_target"
        with self.assertRaisesRegex(ValueError, "A blink names a cell selector"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        hero(source, "wc_vn_moonblade")["selector"] = "cell_behind_target"
        with self.assertRaisesRegex(ValueError, "A blink is a chained effect"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        hero(source, "wc_vn_shadow_fiend")["maxDash"] = 0
        with self.assertRaisesRegex(ValueError, "A blink names a cell selector"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        hero(source, "wc_vn_foxclaw")["effects"][2]["critical"] = True
        with self.assertRaisesRegex(ValueError, "Only a direct hit can be a guaranteed critical"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        next(trait for trait in source["traits"] if trait["id"] == "assassin")["runtime_extra"][0]["values"] = [1, 2]
        with self.assertRaisesRegex(ValueError, "Unsupported trait stat bonus"):
            CATALOG.validate(source)

    def test_summons_are_their_own_list_and_reach_the_runtime_after_the_monsters(self):
        outputs = CATALOG.artifacts(self.raw)
        header = outputs["data/vnext/generated/WonderVNextCatalog.h"]
        runtime = json.loads(outputs["data/vnext/generated/runtime_catalog.json"])
        monsters, summons = self.source["neutrals"], self.source["summons"]
        self.assertEqual([unit["id"] for unit in runtime["neutrals"]], [unit["id"] for unit in monsters + summons])
        wolf = len(monsters) + [unit["id"] for unit in summons].index("wc_vn_s_wolf")
        self.assertIn(f"u.ability.effects.back().summon = {wolf}; u.ability.effects.back().count = 2;", header)
        self.assertIn("{wc::Effect::Summon,wc::DamageType::Physical,0,{0,0,0},0,true,wc::Selector::FallenUnits});", header)
        self.assertIn(f'c.summonLimit = {self.source["summon_limit_per_side"]};', header)
        self.assertIn("u.inert = true;", header)
        self.assertIn('t.id = "summoner"; t.stat = "summon_power_bonus_bp";', header)
        for wave in self.source["waves"]:
            for slot in wave["slots"]:
                self.assertLess(slot["definition"], len(monsters))

        def hero(source, identity):
            return next(hero for hero in source["heroes"] if hero["id"] == identity)["ability"]

        source = copy.deepcopy(self.source)
        hero(source, "wc_vn_wolf_caller")["effects"][0]["summon"] = "wc_vn_n_seedpod"
        with self.assertRaisesRegex(ValueError, "A summon names a known unit"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        hero(source, "wc_vn_jinxer")["effects"][0]["count"] = 2
        with self.assertRaisesRegex(ValueError, "Only a summon names a unit to summon"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        hero(source, "wc_vn_necromancer")["selector"] = "fallen_units"
        with self.assertRaisesRegex(ValueError, "A summon is a chained effect"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        source["neutrals"][0]["id"] = source["summons"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate ID"):
            CATALOG.validate(source)

    def test_economy_rules_reach_the_runtime_and_are_bounded(self):
        header = CATALOG.artifacts(self.raw)["data/vnext/generated/WonderVNextCatalog.h"]
        for line in ("c.rules.preparationStages.push_back({1,5,25000});", "c.rules.preparationStages.push_back({6,20,30000});",
                     "c.rules.preparationStages.push_back({21,60,35000});", "c.rules.streakIncome.push_back({3,1});",
                     "c.rules.streakIncome.push_back({7,3});", "c.rules.autoDeploy = true;"):
            self.assertIn(line, header)
        source = copy.deepcopy(self.source)
        source["rules"]["preparationStages"][1]["start"] = 5
        with self.assertRaisesRegex(ValueError, "preparation stage start"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        source["rules"]["preparationStages"][0]["ms"] = 25025
        with self.assertRaisesRegex(ValueError, "Unquantized preparation stage"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        source["rules"]["streakIncome"][2]["gold"] = 2
        with self.assertRaisesRegex(ValueError, "streak gold"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        source["rules"]["autoDeploy"] = 1
        with self.assertRaisesRegex(ValueError, "Source schema"):
            CATALOG.validate(source)

    def test_the_guided_match_names_playable_heroes_reachable_offers_and_both_languages(self):
        header = CATALOG.artifacts(self.raw)["data/vnext/generated/WonderVNextCatalog.h"]
        self.assertIn("inline wc::Tutorial WonderVNextTutorial()", header)
        stages = self.source["tutorial"]["stages"]
        self.assertEqual([stage["id"] for stage in stages], ["field", "grow", "synergy", "position", "gold", "relic"])
        self.assertEqual(header.count("t.stages.push_back(s); }"), len(stages))
        self.assertEqual(header.count("s.steps.push_back(p); }"), sum(len(stage["steps"]) for stage in stages))

        def broken(change, message):
            source = copy.deepcopy(self.source)
            change(source["tutorial"]["stages"])
            with self.assertRaisesRegex(ValueError, message):
                CATALOG.validate(source)

        broken(lambda s: s[0]["bench"][0].update(hero="wc_vn_nobody"), "names a hero that is not playable")
        broken(lambda s: s[1]["shop"].__setitem__(0, "wc_vn_tide_caller"), "its level could never show")
        broken(lambda s: s[0]["steps"][0].update(text_id=" "), "English and Indonesian text")
        broken(lambda s: s[0]["steps"][0].update(highlight="WC.Nowhere"), "unknown highlight or order")
        broken(lambda s: s[0]["steps"][0]["allow"].append("cheat"), "unknown highlight or order")
        broken(lambda s: s[2]["steps"][0]["done"].update(value=3), "exactly the fields it needs")
        broken(lambda s: s[0]["board"].extend([{"hero": "wc_vn_hammerer", "star": 1, "column": 0, "row": 0}] * 2), "separate cells")
        broken(lambda s: s[0]["steps"].pop(), "ends by watching it")

    def test_repeating_effects_are_damage_or_healing_on_a_quantized_interval(self):
        header = CATALOG.artifacts(self.raw)["data/vnext/generated/WonderVNextCatalog.h"]
        self.assertIn("{3500,5500,9000},0,false,wc::Selector::AdjacentEnemies,wc::ModifierStat::AttackRate,1000,true});", header)
        source = copy.deepcopy(self.source)
        poison = next(hero for hero in source["heroes"] if hero["id"] == "wc_vn_dartblower")["ability"]["effects"]
        poison[0]["repeatMs"] = 1025
        with self.assertRaisesRegex(ValueError, "A repeating effect is damage or healing"):
            CATALOG.validate(source)
        source = copy.deepcopy(self.source)
        poison = next(hero for hero in source["heroes"] if hero["id"] == "wc_vn_dartblower")["ability"]["effects"]
        poison[1]["follow"] = True
        with self.assertRaisesRegex(ValueError, "Only a repeating effect follows its caster"):
            CATALOG.validate(source)

    def test_roster_recipe_gives_every_class_a_bot_role(self):
        outputs = CATALOG.artifacts(self.raw)
        header = outputs["data/vnext/generated/WonderVNextCatalog.h"]
        classes = [trait["id"] for trait in self.source["traits"] if trait["kind"] == "class"]
        for identity in classes:
            self.assertIn(f'c.classRoles.push_back({{"{identity}", wc::BotRole::', header)
        roles = {role["id"]: role for role in self.source["roster_recipe"]["class_roles"]}
        self.assertEqual((roles["tank"]["role"], roles["tank"]["row"]), ("frontline", 3))
        self.assertEqual(roles["sniper"]["row"], 0)
        source = copy.deepcopy(self.source)
        source["roster_recipe"]["class_roles"].pop()
        with self.assertRaisesRegex(ValueError, "Bot roles must name every class"):
            CATALOG.validate(source)

    def test_roster_recipe_tells_bots_what_each_cost_is_worth(self):
        worth = self.source["roster_recipe"]["bot_cost_value_bp"]
        self.assertEqual((len(worth), worth[0]), (5, 10000))
        self.assertEqual(worth, sorted(worth))
        header = CATALOG.artifacts(self.raw)["data/vnext/generated/WonderVNextCatalog.h"]
        self.assertIn("c.botCostValueBp = {" + ",".join(str(value) for value in worth) + "};", header)
        # Only the roster rule set carries the table; the control catalogue's bots keep the older valuation.
        self.assertEqual(header.count("botCostValueBp"), 1)
        source = copy.deepcopy(self.source)
        source["roster_recipe"]["bot_cost_value_bp"] = [10000, 9000, 12000, 13000, 14000]
        with self.assertRaisesRegex(ValueError, "Bot cost values name the five costs in rising order"):
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
