"""Validate and compile the isolated successor catalog; never rewrite legacy inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/vnext/catalog.json"
MECHANICS = {
    "directional_guard": "DirectionalGuard", "momentum_charge": "MomentumCharge",
    "stationary_grove": "StationaryGrove", "screened_strike": "ScreenedStrike",
    "crossing_beams": "CrossingBeams", "tidal_push": "TidalPush",
    "cocoon_projectile": "CocoonProjectile", "standard": "Standard",
}
EFFECTS = {"damage": "Damage", "heal": "Heal", "shield": "Shield", "stun": "Stun", "stat_modifier": "StatModifier",
           "hex": "Hex", "silence": "Silence", "taunt": "Taunt", "mana_drain": "ManaDrain", "blink": "Blink", "summon": "Summon"}
# A status carries its duration in milliseconds at each star as its magnitude.
STATUS_EFFECTS = ("hex", "silence", "taunt")
SELECTORS = {"self": "Self", "current_enemy": "CurrentEnemy", "adjacent_allies": "AdjacentAllies",
             "farthest_enemy_adjacent": "FarthestEnemyAdjacent", "adjacent_enemies": "AdjacentEnemies",
             "lowest_health_ally": "LowestHealthAlly", "current_enemy_area": "CurrentEnemyArea",
             "farthest_enemy": "FarthestEnemy", "lowest_health_enemy": "LowestHealthEnemy", "all_allies": "AllAllies", "densest_enemy_area": "DensestEnemyArea",
             "random_enemy_areas": "RandomEnemyAreas", "enemy_line": "EnemyLine", "enemy_cone": "EnemyCone", "chain_from_current_enemy": "ChainFromCurrentEnemy",
             "cell_beside_target": "CellBesideTarget", "cell_behind_target": "CellBehindTarget", "cell_through_target": "CellThroughTarget", "fallen_units": "FallenUnits"}
# Where a blink lands, relative to the ability's target. Only a blink effect may name one.
CELL_SELECTORS = ("cell_beside_target", "cell_behind_target", "cell_through_target")
DAMAGE_TYPES = {"physical": "Physical", "magic": "Magic", "true": "True"}
MODIFIER_STATS = {"attack_rate": "AttackRate", "attack_damage": "AttackDamage", "armor": "Armor", "resistance": "Resistance",
                  "damage_dealt": "DamageDealt", "damage_taken": "DamageTaken", "movement": "Movement", "reflect": "Reflect"}
TRAIT_STATS = {"summon_power_bonus_bp", "start_leap", "enemy_hex_count", "max_health_bonus_bp", "attack_rate_bonus_bp", "physical_armor_flat", "magic_resistance_flat",
               "all_damage_bonus_bp", "basic_damage_bonus_bp", "ability_damage_bonus_bp", "support_power_bonus_bp",
               "movement_bonus_bp", "starting_mana_flat", "enemy_armor_reduction_flat", "start_shield_health_bp",
               "health_regen_bp", "mana_per_second_flat", "range_bonus_flat", "ability_damage_taken_reduction_bp",
               "win_gold_flat", "evasion_bp", "crit_chance_bp", "lifesteal_bp", "bonus_true_damage_bp"}
RELIC_STATS = ("healthBp", "attackDamageBp", "attackRateBp", "skillPowerBp", "allDamageBp", "armorFlat",
               "resistanceFlat")
MANA_HEROES = ["wc_vn_hookjaw", "wc_vn_prism_scholar", "wc_vn_tide_caller"]
# Cast abilities spend mana; guard, charge and grove stay passive triggers.
MANA_MECHANICS = {"screened_strike", "crossing_beams", "tidal_push", "cocoon_projectile", "standard"}
DOSSIER_KEYS = {"form", "decision", "positioning", "allies", "counterplay", "recognition"}


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def integer(value, name, low=0, high=100000000):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name}: expected integer within {low}..{high}")


def unique(records, name):
    ids = [item["id"] for item in records]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{name}: duplicate ID")


def validate(source):
    """Fail before generating partial or silently simplified runtime content."""
    schema = json.loads((ROOT / "data/vnext/catalog.schema.json").read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(source), key=lambda error: str(error.json_path))
    if errors:
        failure = errors[0]
        raise ValueError(f"Source schema at {failure.json_path}: invalid {failure.validator} contract")
    if source["schema_version"] != "wonder_vnext.catalog.1" or source["profile_id"] != "wonder_vnext":
        raise ValueError("Unsupported successor schema/profile")
    if source["roster_cap"] is not None:
        raise ValueError("The successor roster has no predetermined cap")
    for experiment in source.get("experiments", {}).values():
        if experiment["heroes"] != MANA_HEROES:
            raise ValueError("Mana experiment must preserve the three control heroes")
        if not all(any(h["id"] == identity and h["enabled"] for h in source["heroes"]) for identity in experiment["heroes"]):
            raise ValueError("Mana experiment requires executable heroes")
        if not (experiment["maximum"] == 10000 and 0 <= experiment["starting"] <= 10000 and
                0 < experiment["basicAttackGain"] <= 10000 and
                0 < experiment["damageEventCap"] <= experiment["damageWindowCap"] <= 10000 and
                50 <= experiment["damageWindowMs"] <= 10000 and experiment["damageWindowMs"] % 50 == 0):
            raise ValueError("Invalid mana experiment bounds")
    experiments = source.get("experiments", {})
    if "mana100_hit20_v1" in experiments:
        baseline = experiments["mana100_v1"]
        expected = dict(baseline, basicAttackGain=2000)
        if baseline["basicAttackGain"] != 1000 or baseline["starting"] != 0 or experiments["mana100_hit20_v1"] != expected:
            raise ValueError("The mana20 comparison may change only basicAttackGain from 1000 to 2000")
    rules = source["rules"]
    for key, expected in {"columns": 8, "rows": 8, "deploymentRows": 4, "benchCapacity": 10,
                          "startingLevel": 3, "maximumLevel": 10, "shopSlots": 5, "tickMs": 50,
                          "seatCount": 8, "maximumRelics": 3}.items():
        integer(rules[key], key, expected, expected)
    if source["shop_pool"] != "independent_with_replacement":
        raise ValueError("Independent shops required")
    # Owner, 2026-10-04: relics come with the boss rounds only.
    boss_rounds = list(range(10, rules["maxRounds"] + 1, 10))
    if rules["relicRounds"] != boss_rounds or source["relic_policy"]["draft_rounds"] != boss_rounds:
        raise ValueError("Relic drafts follow the boss rounds: every tenth round")
    if type(rules["autoDeploy"]) is not bool:
        raise ValueError("autoDeploy is true or false")
    covered = 0
    for stage in rules["preparationStages"]:
        integer(stage["start"], "preparation stage start", covered + 1, rules["maxRounds"])
        integer(stage["end"], "preparation stage end", stage["start"], rules["maxRounds"])
        integer(stage["ms"], "preparation stage time", 5000, 600000)
        if stage["ms"] % rules["tickMs"]:
            raise ValueError("Unquantized preparation stage")
        covered = stage["end"]
    length, gold = 1, 0
    for step in rules["streakIncome"]:
        integer(step["length"], "streak length", length + 1, rules["maxRounds"])
        integer(step["gold"], "streak gold", gold + 1, 100)
        length, gold = step["length"], step["gold"]
    for key, value in rules.items():
        if isinstance(value, (list, dict)) or key == "autoDeploy":
            continue
        integer(value, f"rules.{key}")
        if key.endswith("Ms") and value % rules["tickMs"]:
            raise ValueError(f"Unquantized rule timing: {key}")
    if set(rules["shopWeights"]) != {str(level) for level in range(3, 11)}:
        raise ValueError("Missing shop level")
    if set(rules["xpToNext"]) != {str(level) for level in range(3, 10)}:
        raise ValueError("Missing XP progression")
    for level, xp in rules["xpToNext"].items():
        integer(xp, f"XP level {level}", 1)
    unique(source["heroes"], "heroes")
    active = [hero for hero in source["heroes"] if hero["enabled"]]
    if not active:
        raise ValueError("No executable heroes")
    available_costs = {hero["cost"] for hero in active}
    for level, weights in rules["shopWeights"].items():
        if len(weights) != 5 or sum(weights) != 10000:
            raise ValueError(f"Five shop tiers must sum to 10000 basis points at level {level}")
        for tier, weight in enumerate(weights, 1):
            integer(weight, f"shop.{level}.{tier}", 0, 10000)
            if weight and tier not in available_costs:
                raise ValueError(f"Enabled shop tier {tier} has no hero")
    for hero in source["heroes"]:
        if not hero["id"].startswith("wc_vn_"):
            raise ValueError("Successor IDs cannot reuse legacy identities")
        if type(hero["enabled"]) is not bool:
            raise ValueError("Enabled flag must be boolean")
        integer(hero["cost"], hero["id"] + ".cost", 1, 5)
        if set(hero["dossier"]) != DOSSIER_KEYS or not all(hero["dossier"].values()):
            raise ValueError("Incomplete hero decision dossier")
        if hero["enabled"]:
            ability = hero["ability"]
            if ability["mechanic"] not in MECHANICS:
                raise ValueError("Unsupported mechanic cannot enter the executable roster")
            if ability["effect"] not in EFFECTS or ability["selector"] not in SELECTORS:
                raise ValueError("Unsupported effect or selector")
            if ability["selector"] in CELL_SELECTORS or (ability["effect"] == "blink" and "effects" not in ability):
                raise ValueError("A blink is a chained effect with its own cell selector")
            if ability["selector"] == "fallen_units" or (ability["effect"] == "summon" and "effects" not in ability):
                raise ValueError("A summon is a chained effect; only it may choose fallen units")
            if ability["damageType"] not in DAMAGE_TYPES:
                raise ValueError("Unsupported damage type")
            if len(ability["magnitude"]) != 3:
                raise ValueError("Three authored star magnitudes required")
            for magnitude in ability["magnitude"]:
                integer(magnitude, "ability magnitude", 0, rules["maxRawDamage"])
            for part in ability.get("effects", [ability]):
                if part["effect"] in STATUS_EFFECTS and (part["durationMs"] != part["magnitude"][0] or any(
                        not rules["tickMs"] <= ms <= 10000 or ms % rules["tickMs"] for ms in part["magnitude"])):
                    raise ValueError("A status lasts its magnitude in milliseconds at each star")
                if part["effect"] == "mana_drain" and (part["durationMs"] or max(part["magnitude"]) > 10000):
                    raise ValueError("A mana drain removes at most a full bar and has no duration")
            if "effects" in ability:
                parts = ability["effects"]
                if ability["mechanic"] != "standard" or not 1 <= len(parts) <= 4:
                    raise ValueError("Effect chains need the standard mechanic and one to four effects")
                for part in parts:
                    if part["effect"] not in EFFECTS or part["damageType"] not in DAMAGE_TYPES or len(part["magnitude"]) != 3:
                        raise ValueError("Unsupported chained effect")
                    if part["effect"] == "stun" and part["magnitude"] != [0, 0, 0]:
                        raise ValueError("A chained stun carries no magnitude")
                    if part.get("selector", ability["selector"]) not in SELECTORS:
                        raise ValueError("Unsupported chained selector")
                    blink = part["effect"] == "blink"
                    if blink != (part.get("selector") in CELL_SELECTORS) or (blink and (
                            part["magnitude"] != [0, 0, 0] or part["durationMs"] or part.get("delayMs") or
                            (part["selector"] == "cell_through_target" and not 1 <= ability["maxDash"] <= 8))):
                        raise ValueError("A blink names a cell selector and carries nothing else")
                    if part.get("critical") and (part["effect"] != "damage" or part.get("repeatMs")):
                        raise ValueError("Only a direct hit can be a guaranteed critical")
                    summon = part["effect"] == "summon"
                    if summon != ("summon" in part) or ("count" in part and not summon) or (
                            part.get("selector") == "fallen_units" and not summon):
                        raise ValueError("Only a summon names a unit to summon, a count or fallen units")
                    if summon and (part["summon"] not in {unit["id"] for unit in source.get("summons", [])} or
                                   part["magnitude"] != [0, 0, 0] or part.get("delayMs") or
                                   part.get("selector", "fallen_units") != "fallen_units"):
                        raise ValueError("A summon names a known unit and a count, and nothing else")
                    if "stat" in part and (part["effect"] != "stat_modifier" or part["stat"] not in MODIFIER_STATS):
                        raise ValueError("Only a stat modifier names a stat, from the supported list")
                    repeat = part.get("repeatMs", 0)
                    if repeat and (part["effect"] not in ("damage", "heal") or repeat % rules["tickMs"] or
                                   part["durationMs"] < repeat or part["durationMs"] // repeat > 32):
                        raise ValueError("A repeating effect is damage or healing on a quantized interval within its duration")
                    if part.get("follow") and not repeat:
                        raise ValueError("Only a repeating effect follows its caster")
                    delay = part.get("delayMs", 0)
                    if part["durationMs"] % rules["tickMs"] or delay % rules["tickMs"] or not 0 <= delay <= 10000:
                        raise ValueError("Unquantized chained effect timing")
                    for magnitude in part["magnitude"]:
                        integer(magnitude, "chained magnitude", -10000 if part["effect"] == "stat_modifier" else 0, rules["maxRawDamage"])
            if ability["mechanic"] != "standard" and (ability["effect"] in ("stat_modifier", "mana_drain") + STATUS_EFFECTS or ability["selector"] in
                                                      ("adjacent_enemies", "lowest_health_ally", "current_enemy_area", "farthest_enemy", "lowest_health_enemy", "all_allies",
                                                       "densest_enemy_area", "random_enemy_areas", "enemy_line", "enemy_cone",
                                                       "chain_from_current_enemy")):
                raise ValueError("Standard selectors and effects need the standard mechanic")
            for key, value in ability.items():
                if isinstance(value, int) and not isinstance(value, bool):
                    integer(value, "ability." + key)
                    if key.endswith("Ms") and value % rules["tickMs"]:
                        raise ValueError(f"Unquantized ability timing: {key}")
            for key in ("cooldownMs", "castMs"):
                integer(ability[key], key, rules["tickMs"])
            integer(ability["maxTargets"], "maxTargets", 1, 48)
            if ability["mechanic"] == "directional_guard":
                integer(ability["guardReductionBp"], "guard reduction", 1, 9000)
                integer(ability["radius"], "guard radius", 1, 8)
            if ability["mechanic"] == "stationary_grove":
                integer(ability["pulseMs"], "grove pulse", 50)
                integer(ability["durationMs"], "grove duration", ability["pulseMs"], ability["pulseMs"] * 32)
            if ability["mechanic"] == "cocoon_projectile":
                if (ability["effect"] != "stun" or ability["magnitude"] != [0, 0, 0] or
                        ability["maxTargets"] != 1 or ability["radius"] != 0 or
                        ability["selector"] != "current_enemy"):
                    raise ValueError("Cocoon must be one damage-free enemy trap")
                integer(ability["durationMs"], "cocoon duration", 50, 10000)
                integer(ability["travelMs"], "cocoon projectile travel", 50, 10000)
            for key, value in hero["stats"].items():
                if key != "damageType":
                    integer(value, "stats." + key)
            integer(hero["stats"]["health"], "health", 1, rules["maxHealth"])
        elif "ability" in hero or "stats" in hero:
            raise ValueError("Unimplemented heroes must not carry executable stand-in abilities or stats")
    unique(source["traits"], "traits")
    for kind in ("race", "class"):
        records = [trait for trait in source["traits"] if trait["kind"] == kind]
        if len(records) < 9:
            raise ValueError(f"Missing initial {kind} families")
        ids = {trait["id"] for trait in records}
        key = "race" if kind == "race" else "unit_class"
        for hero in source["heroes"]:
            if hero[key] not in ids:
                raise ValueError("Unknown hero trait membership")
        for trait in records:
            expected = [hero["id"] for hero in source["heroes"] if hero[key] == trait["id"]]
            if trait["members"] != expected:
                raise ValueError("Trait membership drift")
            if trait["thresholds"] != sorted(set(trait["thresholds"])):
                raise ValueError("Trait thresholds must be distinct and ascending")
            runtime = trait.get("runtime")
            if trait["runtime_enabled"] != (runtime is not None):
                raise ValueError("Traits require an implemented stat bonus before activation")
            parts = ([runtime] if runtime else []) + trait.get("runtime_extra", [])
            if trait.get("runtime_extra") and not runtime:
                raise ValueError("Extra trait parts need a first part")
            if len({part["stat"] for part in parts}) != len(parts):
                raise ValueError("A trait names each stat once")
            for part in parts:
                if (part["stat"] not in TRAIT_STATS or len(part["values"]) != len(trait["thresholds"]) or
                        part["values"] != ([1] * len(part["values"]) if part["stat"] == "start_leap" else sorted(set(part["values"])))):
                    raise ValueError("Unsupported trait stat bonus")
                if ("durationMs" in part) != (part["stat"] == "enemy_hex_count") or part.get("durationMs", 0) % rules["tickMs"]:
                    raise ValueError("Only a hex trait carries a duration, in whole ticks")
    recipe = source.get("roster_recipe")
    if recipe:
        enabled = {hero["id"]: hero["ability"]["mechanic"] for hero in active}
        if recipe["mana"] not in source.get("experiments", {}):
            raise ValueError("Roster recipe needs its mana rules")
        if (set(recipe["mana_heroes"]) | set(recipe["passive_heroes"]) != set(enabled) or
                set(recipe["mana_heroes"]) & set(recipe["passive_heroes"])):
            raise ValueError("Roster recipe must classify every executable hero once")
        for identity, mechanic in enabled.items():
            if (identity in recipe["mana_heroes"]) != (mechanic in MANA_MECHANICS):
                raise ValueError("Cast abilities use mana; passive triggers do not")
        classes = [trait["id"] for trait in source["traits"] if trait["kind"] == "class"]
        if sorted(role["id"] for role in recipe["class_roles"]) != sorted(classes):
            raise ValueError("Bot roles must name every class exactly once")
    unique(source["relics"], "relics")
    for relic in source["relics"]:
        mechanics = relic["compatible_mechanics"]
        # An empty list fits every hero; a mechanic-bound relic still needs two real mechanics.
        if mechanics and (len(set(mechanics)) < 2 or
                          any(mechanic not in MECHANICS or mechanic == "standard" for mechanic in mechanics)):
            raise ValueError("Relic requires at least two implemented compatible mechanics")
        params = relic["modifiers"]
        transforms = {"magnitudeBp", "rangeDelta", "radiusDelta", "durationBp", "castBp", "cooldownBp"}
        if set(params) != transforms | set(RELIC_STATS):
            raise ValueError("Unknown or missing relic transform")
        for key in transforms:
            integer(params[key], "relic." + key, -2 if key.endswith("Delta") else 5000,
                    2 if key.endswith("Delta") else 15000 if key == "magnitudeBp" else 20000)
        for key in RELIC_STATS:
            integer(params[key], "relic." + key, 0, 100 if key.endswith("Flat") else 5000)
        benefit = (params["magnitudeBp"] > 10000 or params["rangeDelta"] > 0 or params["radiusDelta"] > 0 or
                   params["castBp"] < 10000 or params["cooldownBp"] < 10000 or any(params[key] for key in RELIC_STATS))
        if not benefit:
            raise ValueError("Every relic requires a benefit")
        if not mechanics and (params["rangeDelta"] or params["radiusDelta"] or params["magnitudeBp"] != 10000 or
                              params["durationBp"] != 10000):
            raise ValueError("A relic that fits every hero may not reshape abilities")
    unique(source["neutrals"], "neutrals")
    unique(source["neutrals"] + source.get("summons", []), "neutrals and summons")
    integer(source["summon_limit_per_side"], "summon limit", 0, 8)
    unique(source["waves"], "waves")
    expected_rounds = set(range(1, rules["neutralOpeningRounds"] + 1)) | set(range(5, rules["maxRounds"] + 1, 5))
    if {wave["round"] for wave in source["waves"]} != expected_rounds:
        raise ValueError("Missing or unexpected neutral rounds")
    for wave in source["waves"]:
        occupied = set()
        for slot in wave["slots"]:
            integer(slot["definition"], "neutral definition", 0, len(source["neutrals"]) - 1)
            integer(slot["column"], "neutral column", 0, 7)
            integer(slot["row"], "neutral row", 0, 3)
            cell = (slot["column"], slot["row"])
            if cell in occupied:
                raise ValueError("Duplicate neutral cell")
            occupied.add(cell)
    validate_tutorial(source)
    unique(source["bots"], "bots")
    if len(source["bots"]) != 7:
        raise ValueError("Seven bot personas required")
    if set(source["locales"]["en"]) != set(source["locales"]["id"]):
        raise ValueError("Locale key mismatch")


# The guided first match: what may complete a step and which fields that needs, the orders a step may allow,
# and the screen controls a step may point at.
TUTORIAL_DONE = {"deployed_at_least": "value", "ready": None, "fight_over": None, "shop_open": None, "trait_focus": "trait", "owns": "hero", "star_at_least": "hero+value", "row_at_least": "hero+value", "row_at_most": "hero+value", "level_at_least": "value", "gold_at_least": "value", "shop_locked": None, "relic_owned": "value", "relic_equipped": None, "trait_at_least": "trait+value"}
TUTORIAL_ORDERS = {"buy": "Buy", "sell": "Sell", "reroll": "Reroll", "lock": "ToggleLock", "buy_xp": "BuyXp", "move": "Move",
                   "ready": "Ready", "choose_relic": "ChooseRelic", "equip_relic": "EquipRelic", "facing": "SetFacing"}
TUTORIAL_TAGS = ("", "WC.OpenShop", "WC.Sell", "WC.Ready", "WC.BuyXp", "WC.Lock", "WC.Reroll", "WC.Bench", "WC.Board",
                 "WC.Synergies", "WC.Relics", "WC.Gold", "WC.Chart")


def validate_tutorial(source):
    tutorial = source.get("tutorial")
    if tutorial is None:
        return
    rules = source["rules"]
    heroes = {hero["id"]: hero for hero in source["heroes"] if hero["enabled"]}
    traits = {trait["id"] for trait in source["traits"]}
    unique(tutorial["stages"], "tutorial stages")
    for stage in tutorial["stages"]:
        name = "tutorial stage " + stage["id"]
        integer(stage["round"], name + " round", 1, rules["maxRounds"])
        integer(stage["level"], name + " level", rules["startingLevel"], rules["maximumLevel"])
        integer(stage["gold"], name + " gold", 0, 100)
        integer(stage["streak"], name + " streak", -rules["maxRounds"], rules["maxRounds"])
        if len(stage["board"]) > stage["level"] or len(stage["bench"]) > rules["benchCapacity"] or len(stage["shop"]) > rules["shopSlots"]:
            raise ValueError(name + ": more heroes than the level, bench or shop holds")
        for side in ("board", "opponent"):
            cells = [(unit["column"], unit["row"]) for unit in stage[side]]
            if len(set(cells)) != len(cells) or any(not (0 <= c < rules["columns"] and 0 <= r < rules["deploymentRows"]) for c, r in cells):
                raise ValueError(name + ": heroes must stand on separate cells of their own half")
        for unit in stage["board"] + stage["bench"] + stage["opponent"]:
            if unit["hero"] not in heroes:
                raise ValueError(name + ": names a hero that is not playable")
            integer(unit["star"], name + " star", 1, 3)
        for offer in stage["shop"]:
            if offer not in heroes or rules["shopWeights"][str(stage["level"])][heroes[offer]["cost"] - 1] == 0:
                raise ValueError(name + ": the shop offers a hero its level could never show")
        neutral = stage["round"] <= rules["neutralOpeningRounds"] or stage["round"] % rules["neutralEvery"] == 0
        if stage["fight"] and not neutral and not stage["opponent"]:
            raise ValueError(name + ": a player fight needs an opponent board")
        if not stage["steps"]:
            raise ValueError(name + ": needs at least one step")
        for step in stage["steps"]:
            if not step["text_en"].strip() or not step["text_id"].strip():
                raise ValueError(name + ": every step needs English and Indonesian text")
            done = step["done"]
            needs = TUTORIAL_DONE.get(done["type"], "?")
            if needs == "?":
                raise ValueError(name + ": unknown step condition")
            wanted = set((needs or "").split("+")) - {""}
            if set(done) - {"type"} != wanted:
                raise ValueError(name + ": a step condition carries exactly the fields it needs")
            if "hero" in done and done["hero"] not in heroes or "trait" in done and done["trait"] not in traits:
                raise ValueError(name + ": a step condition names an unknown hero or trait")
            if "value" in done:
                integer(done["value"], name + " condition value", 0, 100)
            if step.get("highlight", "") not in TUTORIAL_TAGS or any(order not in TUTORIAL_ORDERS for order in step["allow"]):
                raise ValueError(name + ": unknown highlight or order")
        if stage["fight"] != (stage["steps"][-1]["done"]["type"] == "fight_over"):
            raise ValueError(name + ": a stage with a fight ends by watching it, and only such a stage does")


def literal(value):
    return json.dumps(value, ensure_ascii=True) if isinstance(value, str) else str(value).lower()


def native_header(runtime, runtime_sha1):
    lines = ["// Generated by tools/vnext/catalog.py. Edit data/vnext/catalog.json only.", "#pragma once",
             '#include "Simulation/WonderSimulation.h"', "namespace wcvnext {",
             f'inline constexpr const char* RuntimeSha1 = "{runtime_sha1}";',
             f'inline constexpr const char* SourceSha256 = "{runtime["source_sha256"]}";',
             "inline wc::Catalog WonderVNextCatalog() { wc::Catalog c;",
             'c.profileId = "wonder_vnext";', 'c.schemaVersion = "wonder_vnext.catalog.1";',
             f'c.balanceVersion = {literal(runtime["balance_version"])};', "c.contentDigest = SourceSha256;",
             f'c.ownedTeamRelicOffers = {literal(runtime["relic_policy"]["offer_policy"] == "one_owned_compatible_if_available")};']

    def assign(prefix, values, excluded=()):
        for key, value in values.items():
            if key in excluded:
                continue
            if isinstance(value, list):
                lines.append(f"{prefix}.{key} = {{{','.join(literal(item) for item in value)}}};")
            else:
                lines.append(f"{prefix}.{key} = {literal(value)};")

    rules = runtime["rules"]
    assign("c.rules", rules, ("lossStages", "shopWeights", "xpToNext", "preparationStages", "streakIncome"))
    for stage in rules["preparationStages"]:
        lines.append(f'c.rules.preparationStages.push_back({{{stage["start"]},{stage["end"]},{stage["ms"]}}});')
    for step in rules["streakIncome"]:
        lines.append(f'c.rules.streakIncome.push_back({{{step["length"]},{step["gold"]}}});')
    for stage in rules["lossStages"]:
        lines.append(f'c.rules.lossStages.push_back({{{stage["start"]},{stage["end"]},{stage["damage"]}}});')
    for level, xp in rules["xpToNext"].items():
        lines.append(f"c.rules.xpToNext[{level}] = {xp};")
    for level, weights in rules["shopWeights"].items():
        lines.append(f'c.rules.shopWeights[{level}] = {{{",".join(map(str, weights))}}};')
    neutral_ids = [unit["id"] for unit in runtime["neutrals"]]
    lines.append(f'c.summonLimit = {runtime["summon_limit_per_side"]};')
    for collection in ("heroes", "neutrals"):
        for hero in runtime[collection]:
            lines.append("{ wc::UnitDef u;")
            assign("u", {"id": hero["id"], "name": hero["name"], "displayName": hero["display_name"]})
            if collection == "heroes":
                assign("u", {"race": hero["race"], "unitClass": hero["unit_class"], "cost": hero["cost"], "roleTags": hero["role_tags"]})
            assign("u", hero["stats"], ("damageType",))
            if hero.get("inert"):
                lines.append("u.inert = true;")
            lines.append(f'u.damageType = wc::DamageType::{DAMAGE_TYPES[hero["stats"]["damageType"]]};')
            ability = hero["ability"]
            if ability is None:
                lines.append("u.ability.enabled = false;")
            else:
                assign("u.ability", ability, ("effect", "selector", "damageType", "mechanic", "tooltip_en", "tooltip_id", "effects"))
                # The shared evaluator and combat read standard abilities through their effect list.
                single = [{key: ability[key] for key in ("effect", "damageType", "durationMs", "magnitude")}]
                for part in ability.get("effects", single if ability["mechanic"] == "standard" else ()):
                    own = "selector" in part
                    repeating = (f',{part.get("repeatMs", 0)},{literal(part.get("follow", False))}' + (",true" if part.get("critical") else "")
                                 if part.get("repeatMs") or part.get("critical") else "")
                    chain = (f',{part.get("delayMs", 0)},{literal(own)},wc::Selector::{SELECTORS[part.get("selector", ability["selector"])]}'
                             f',wc::ModifierStat::{MODIFIER_STATS[part.get("stat", "attack_rate")]}{repeating}' if "stat" in part or repeating
                             else f',{part.get("delayMs", 0)},true,wc::Selector::{SELECTORS[part["selector"]]}' if own
                             else f',{part["delayMs"]}' if part.get("delayMs") else "")
                    lines.append(f'u.ability.effects.push_back({{wc::Effect::{EFFECTS[part["effect"]]},'
                                 f'wc::DamageType::{DAMAGE_TYPES[part["damageType"]]},{part["durationMs"]},'
                                 f'{{{",".join(map(str, part["magnitude"]))}}}{chain}}});')
                    if part["effect"] == "summon":
                        lines.append(f'u.ability.effects.back().summon = {neutral_ids.index(part["summon"])}; '
                                     f'u.ability.effects.back().count = {part.get("count", 1)};')
                for key, enum, values in (("effect", "Effect", EFFECTS), ("selector", "Selector", SELECTORS),
                                           ("damageType", "DamageType", DAMAGE_TYPES), ("mechanic", "AbilityMechanic", MECHANICS)):
                    lines.append(f"u.ability.{key} = wc::{enum}::{values[ability[key]]};")
            lines.append("c." + ("units" if collection == "heroes" else "neutrals") + ".push_back(u); }")
    for wave in runtime["waves"]:
        lines.append("{ wc::NeutralWave w;")
        assign("w", wave, ("slots", "teaching_status", "boss_mechanics"))
        for slot in wave["slots"]:
            lines.append(f'w.slots.push_back({{{slot["definition"]},{{{slot["column"]},{slot["row"]}}}}});')
        lines.append("c.waves.push_back(w); }")
    for bot in runtime["bots"]:
        lines.append("{ wc::BotDef b;")
        assign("b", bot, ("honesty",))
        lines.append("c.bots.push_back(b); }")
    for relic in runtime["relics"]:
        lines.append("{ wc::RelicDef r;")
        assign("r", {key: relic[key] for key in ("id", "name", "description")})
        assign("r", relic["modifiers"])
        for mechanic in relic["compatible_mechanics"]:
            lines.append(f"r.compatibleMechanics.push_back(wc::AbilityMechanic::{MECHANICS[mechanic]});")
        lines.append("c.relics.push_back(r); }")
    lines.append("return c; }")
    for key, function in (("mana100_v1", "WonderVNextManaCatalog"), ("mana100_hit20_v1", "WonderVNextMana20Catalog")):
        experiment = runtime.get("experiments", {}).get(key)
        if not experiment:
            continue
        experiment_digest = hashlib.sha256((runtime["source_sha256"] + ":" + key).encode()).hexdigest()
        lines.extend([f"inline wc::Catalog {function}() {{ auto c = WonderVNextCatalog();",
                      f'c.contentDigest = "{experiment_digest}";',
                      f'c.balanceVersion += "+{key}";'])
        for identity in experiment["heroes"]:
            lines.append(f'for (auto &u : c.units) if (u.id == {literal(identity)}) {{')
            assign("u.ability.mana", experiment, ("status", "heroes", "relicTiming"))
            lines.append("}")
        lines.extend(["return c; }"])
    if runtime.get("combat_clarity"):
        recipe = runtime["combat_clarity"]
        lines.append("inline wc::Catalog WonderVNextCombatClarityCatalog(bool mobileRecovery = true) { auto c = WonderVNextMana20Catalog();")
        for mobile, suffix in ((True, "combat_clarity_v1"), (False, "nearest_target_v1")):
            digest = hashlib.sha256((runtime["source_sha256"] + ":" + suffix).encode()).hexdigest()
            lines.extend([("if (mobileRecovery) {" if mobile else "else {"),
                          f'c.contentDigest = "{digest}"; c.balanceVersion += "+{suffix}"; }}'])
        lines.append(f'c.rules.nearestReachableTarget = {literal(recipe["nearestReachableTarget"])};')
        lines.append(f'c.rules.mobileAttackRecovery = mobileRecovery && {literal(recipe["mobileAttackRecovery"])};')
        lines.append("return c; }")
    recipe = runtime.get("roster_recipe")
    if recipe:
        digest = hashlib.sha256((runtime["source_sha256"] + ":" + recipe["id"]).encode()).hexdigest()
        lines.extend(["inline wc::Catalog WonderVNextRosterCatalog() { auto c = WonderVNextCatalog();",
                      f'c.contentDigest = "{digest}";', f'c.balanceVersion += "+{recipe["id"]}";'])
        for identity in recipe["mana_heroes"]:
            lines.append(f'for (auto &u : c.units) if (u.id == {literal(identity)}) {{')
            assign("u.ability.mana", runtime["experiments"][recipe["mana"]], ("status", "heroes", "relicTiming"))
            lines.append("}")
        for rule in ("nearestReachableTarget", "directMovement", "chargeReturns"):
            lines.append(f'c.rules.{rule} = {literal(recipe["combat_rules"][rule])};')
        for trait in recipe["traits"]:
            tiers = ",".join(f"{{{count},{value}}}" for count, value in zip(trait["thresholds"], trait["values"]))
            lines.append(f'{{ wc::TraitDef t; t.id = {literal(trait["id"])}; t.stat = {literal(trait["stat"])}; '
                         f't.team = {literal(trait["scope"] == "team")}; '
                         + (f't.durationMs = {trait["durationMs"]}; ' if "durationMs" in trait else "")
                         + f't.tiers = {{{tiers}}}; c.traits.push_back(t); }}')
        lines.append(f'c.botSpendsSurplus = {literal(recipe["bot_spends_surplus"])};')
        for role in recipe["class_roles"]:
            lines.append(f'c.classRoles.push_back({{{literal(role["id"])}, wc::BotRole::{role["role"].capitalize()}, '
                         f'{role["row"]}, {literal(role["flank"])}}});')
        lines.append("return c; }")
    tutorial = runtime.get("tutorial")
    if tutorial:
        index = {hero["id"]: position for position, hero in enumerate(runtime["heroes"])}
        lines.append("inline wc::Tutorial WonderVNextTutorial() { wc::Tutorial t;")
        for stage in tutorial["stages"]:
            lines.append("{ wc::GuidedStage s;")
            lines.append(f's.id = {literal(stage["id"])}; s.titleEn = {literal(stage["title_en"])}; s.titleId = {literal(stage["title_id"])};')
            lines.append(f's.round = {stage["round"]}; s.gold = {stage["gold"]}; s.level = {stage["level"]}; s.streak = {stage["streak"]}; '
                         f's.fight = {literal(stage["fight"])}; s.relicDraft = {literal(stage["relic_draft"])};')
            for side in ("board", "opponent"):
                for unit in stage[side]:
                    lines.append(f's.{side}.push_back({{{index[unit["hero"]]},{unit["star"]},{{{unit["column"]},{unit["row"]}}}}});')
            for unit in stage["bench"]:
                lines.append(f's.bench.push_back({{{index[unit["hero"]]},{unit["star"]},{{-1,-1}}}});')
            lines.append("s.shop = {" + ",".join(str(index[offer]) for offer in stage["shop"]) + "};")
            for step in stage["steps"]:
                done = step["done"]
                orders = ",".join("wc::CommandType::" + TUTORIAL_ORDERS[order] for order in step["allow"])
                lines.append(f'{{ wc::GuidedStep p; p.textEn = {literal(step["text_en"])}; p.textId = {literal(step["text_id"])}; '
                             f'p.highlight = {literal(step.get("highlight", ""))}; p.done = {literal(done["type"])}; '
                             f'p.trait = {literal(done.get("trait", ""))}; p.definition = {index[done["hero"]] if "hero" in done else -1}; '
                             f'p.value = {done.get("value", 0)}; p.allow = {{{orders}}}; s.steps.push_back(p); }}')
            lines.append("t.stages.push_back(s); }")
        lines.append("return t; }")
    lines.extend(["} // namespace wcvnext", ""])
    return "\n".join(lines)


def artifacts(source_bytes):
    source = json.loads(source_bytes)
    validate(source)
    digest = hashlib.sha256(source_bytes).hexdigest()
    runtime = {key: source[key] for key in ("schema_version", "profile_id", "balance_version", "rules", "relic_policy", "bots", "neutrals", "waves", "world", "locales")}
    # Summoned units share the native neutral list, after the wave monsters.
    runtime["neutrals"] = source["neutrals"] + source.get("summons", [])
    runtime["summon_limit_per_side"] = source["summon_limit_per_side"]
    runtime["experiments"] = source.get("experiments", {})
    if source.get("tutorial"):
        runtime["tutorial"] = source["tutorial"]
    runtime["combat_clarity"] = source.get("combat_clarity", {})
    runtime.update(source_sha256=digest, heroes=[hero for hero in source["heroes"] if hero["enabled"]],
                   relics=[relic for relic in source["relics"] if relic["runtime_enabled"]], traits=[],
                   status="gameplay_laboratory_not_release")
    if source.get("roster_recipe"):
        runtime["roster_recipe"] = dict(source["roster_recipe"], traits=[
            dict(part, id=trait["id"], kind=trait["kind"], name=trait["name"],
                 thresholds=trait["thresholds"], behavior=trait["behavior"])
            for trait in source["traits"] if trait["runtime_enabled"]
            for part in [trait["runtime"]] + trait.get("runtime_extra", [])])
    runtime_text = encoded(runtime)
    header = native_header(runtime, hashlib.sha1(runtime_text.encode("utf-8")).hexdigest())
    dossiers = ["# Generated successor hero dossiers", "", "Source: `data/vnext/catalog.json`. Numeric data below is provisional and unbalanced.", ""]
    for hero in source["heroes"]:
        dossiers.extend([f'## {hero["name"]}', "", f'`{hero["id"]}` | {hero["race"]} / {hero["unit_class"]} | cost {hero["cost"]} | {hero["production_status"]}', ""])
        for key, value in hero["dossier"].items():
            dossiers.extend([f"**{key.title()}:** {value}", ""])
        if hero["enabled"]:
            dossiers.extend([f'Ability: **{hero["ability"]["name"]}** (`{hero["ability"]["mechanic"]}`); art: `{hero["art_status"]}`.', ""])
        else:
            dossiers.extend([f'Planned ability: **{hero["planned_ability"]["name"]}** — {hero["planned_ability"]["behavior"]}', "",
                             "Authored future design. No executable ability, stats, model, or runtime acceptance.", ""])
    coverage = {"source_sha256": digest, "authored_heroes": len(source["heroes"]), "enabled_lab_heroes": len(runtime["heroes"]),
                "authored_traits": len(source["traits"]), "runtime_traits": 0,
                "roster_recipe_traits": sum(trait["runtime_enabled"] for trait in source["traits"]), "runtime_relics": len(runtime["relics"]),
                "body_families": sorted({hero["body_family"] for hero in source["heroes"]}),
                "archetypes": sorted({hero["archetype"] for hero in source["heroes"]}),
                "trait_gaps": [{"id": t["id"], "authored_members": len(t["members"]), "thresholds": t["thresholds"]} for t in source["traits"]],
                "balance_status": "not_verified", "human_acceptance": "not_run"}
    relic_lines = ["# Generated relic catalogue", "", "Source: `data/vnext/catalog.json`. Untuned; balance and human acceptance are not established.", "",
                   "Draft after each boss round (10, 20, 30, 40, 50, 60); three offers; three equipped per team; one per hero. Surviving players receive the choice regardless of neutral victory.", ""]
    for relic in source["relics"]:
        relic_lines.extend([f'## {relic["name"]}', "", relic["description"], "",
                            "Fits: " + (", ".join(relic["compatible_mechanics"]) or "every hero") + ".", "",
                            "Canonical transforms: `" + json.dumps(relic["modifiers"], sort_keys=True) + "`.", ""])
    return {"data/vnext/generated/runtime_catalog.json": runtime_text,
            "data/vnext/generated/WonderVNextCatalog.h": header,
            "game/Source/WonderChessRuntime/Public/VNext/WonderVNextCatalog.generated.h": header,
            "docs/vnext/generated/hero_dossiers.md": "\n".join(dossiers),
            "docs/vnext/generated/relic_catalogue.md": "\n".join(relic_lines),
            "docs/vnext/generated/coverage.json": encoded(coverage)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--stage", action="store_true", help="Stage only the successor runtime JSON into the game")
    args = parser.parse_args()
    outputs = artifacts(SOURCE.read_bytes())
    if args.stage:
        outputs["game/Content/WonderChess/VNextData/runtime_catalog.json"] = outputs["data/vnext/generated/runtime_catalog.json"]
    stale = []
    for relative, content in outputs.items():
        path = ROOT / relative
        if args.check:
            if not path.exists() or path.read_bytes() != content.encode("utf-8"):
                stale.append(relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content.encode("utf-8"))
    if stale:
        raise SystemExit("Stale successor outputs: " + ", ".join(stale))
    print(f"{len(outputs)} successor artifacts {'match canonical source' if args.check else 'written'}; art, balance and release acceptance not established")


if __name__ == "__main__":
    main()
