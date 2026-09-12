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
}
EFFECTS = {"damage": "Damage", "heal": "Heal", "shield": "Shield"}
SELECTORS = {"self": "Self", "current_enemy": "CurrentEnemy", "adjacent_allies": "AdjacentAllies",
             "farthest_enemy_adjacent": "FarthestEnemyAdjacent"}
DAMAGE_TYPES = {"physical": "Physical", "magic": "Magic", "true": "True"}
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
    rules = source["rules"]
    for key, expected in {"columns": 8, "rows": 8, "deploymentRows": 4, "benchCapacity": 10,
                          "startingLevel": 3, "maximumLevel": 10, "shopSlots": 5, "tickMs": 50,
                          "seatCount": 8, "maximumRelics": 3}.items():
        integer(rules[key], key, expected, expected)
    if source["shop_pool"] != "independent_with_replacement":
        raise ValueError("Independent shops required")
    if rules["relicRounds"] != [3, 15, 25] or source["relic_policy"]["draft_rounds"] != [3, 15, 25]:
        raise ValueError("Relic draft rounds must remain 3, 15, 25")
    for key, value in rules.items():
        if isinstance(value, (list, dict)):
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
            if ability["damageType"] not in DAMAGE_TYPES:
                raise ValueError("Unsupported damage type")
            if len(ability["magnitude"]) != 3:
                raise ValueError("Three authored star magnitudes required")
            for magnitude in ability["magnitude"]:
                integer(magnitude, "ability magnitude", 0, rules["maxRawDamage"])
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
            if trait["runtime_enabled"]:
                raise ValueError("Behavioral traits require an implementation before activation")
    unique(source["relics"], "relics")
    for relic in source["relics"]:
        mechanics = relic["compatible_mechanics"]
        if len(set(mechanics)) < 2 or any(mechanic not in MECHANICS for mechanic in mechanics):
            raise ValueError("Relic requires at least two implemented compatible mechanics")
        params = relic["modifiers"]
        if set(params) != {"magnitudeBp", "rangeDelta", "radiusDelta", "durationBp", "castBp", "cooldownBp"}:
            raise ValueError("Unknown or missing relic transform")
        for key, value in params.items():
            integer(value, "relic." + key, -2 if key.endswith("Delta") else 5000,
                    2 if key.endswith("Delta") else 15000 if key == "magnitudeBp" else 20000)
        benefit = params["magnitudeBp"] > 10000 or params["rangeDelta"] > 0 or params["radiusDelta"] > 0 or params["castBp"] < 10000 or params["cooldownBp"] < 10000
        drawback = params["magnitudeBp"] < 10000 or params["rangeDelta"] < 0 or params["radiusDelta"] < 0 or params["castBp"] > 10000 or params["cooldownBp"] > 10000
        if not benefit or not drawback:
            raise ValueError("Every relic requires a benefit and a tradeoff")
    unique(source["neutrals"], "neutrals")
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
    unique(source["bots"], "bots")
    if len(source["bots"]) != 7:
        raise ValueError("Seven bot personas required")
    if set(source["locales"]["en"]) != set(source["locales"]["id"]):
        raise ValueError("Locale key mismatch")


def literal(value):
    return json.dumps(value, ensure_ascii=True) if isinstance(value, str) else str(value).lower()


def native_header(runtime, runtime_sha1):
    lines = ["// Generated by tools/vnext/catalog.py. Edit data/vnext/catalog.json only.", "#pragma once",
             '#include "Simulation/WonderSimulation.h"', "namespace wcvnext {",
             f'inline constexpr const char* RuntimeSha1 = "{runtime_sha1}";',
             f'inline constexpr const char* SourceSha256 = "{runtime["source_sha256"]}";',
             "inline wc::Catalog WonderVNextCatalog() { wc::Catalog c;",
             'c.profileId = "wonder_vnext";', 'c.schemaVersion = "wonder_vnext.catalog.1";',
             f'c.balanceVersion = {literal(runtime["balance_version"])};', "c.contentDigest = SourceSha256;"]

    def assign(prefix, values, excluded=()):
        for key, value in values.items():
            if key in excluded:
                continue
            if isinstance(value, list):
                lines.append(f"{prefix}.{key} = {{{','.join(literal(item) for item in value)}}};")
            else:
                lines.append(f"{prefix}.{key} = {literal(value)};")

    rules = runtime["rules"]
    assign("c.rules", rules, ("lossStages", "shopWeights", "xpToNext"))
    for stage in rules["lossStages"]:
        lines.append(f'c.rules.lossStages.push_back({{{stage["start"]},{stage["end"]},{stage["damage"]}}});')
    for level, xp in rules["xpToNext"].items():
        lines.append(f"c.rules.xpToNext[{level}] = {xp};")
    for level, weights in rules["shopWeights"].items():
        lines.append(f'c.rules.shopWeights[{level}] = {{{",".join(map(str, weights))}}};')
    for collection in ("heroes", "neutrals"):
        for hero in runtime[collection]:
            lines.append("{ wc::UnitDef u;")
            assign("u", {"id": hero["id"], "name": hero["name"], "displayName": hero["display_name"]})
            if collection == "heroes":
                assign("u", {"race": hero["race"], "unitClass": hero["unit_class"], "cost": hero["cost"], "roleTags": hero["role_tags"]})
            assign("u", hero["stats"], ("damageType",))
            lines.append(f'u.damageType = wc::DamageType::{DAMAGE_TYPES[hero["stats"]["damageType"]]};')
            ability = hero["ability"]
            if ability is None:
                lines.append("u.ability.enabled = false;")
            else:
                assign("u.ability", ability, ("effect", "selector", "damageType", "mechanic", "tooltip_en", "tooltip_id"))
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
    lines.extend(["return c; }", "} // namespace wcvnext", ""])
    return "\n".join(lines)


def artifacts(source_bytes):
    source = json.loads(source_bytes)
    validate(source)
    digest = hashlib.sha256(source_bytes).hexdigest()
    runtime = {key: source[key] for key in ("schema_version", "profile_id", "balance_version", "rules", "bots", "neutrals", "waves", "world", "locales")}
    runtime.update(source_sha256=digest, heroes=[hero for hero in source["heroes"] if hero["enabled"]],
                   relics=[relic for relic in source["relics"] if relic["runtime_enabled"]], traits=[],
                   status="gameplay_laboratory_not_release")
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
            dossiers.extend(["Authored future design. No executable ability, stats, model, or runtime acceptance.", ""])
    coverage = {"source_sha256": digest, "authored_heroes": len(source["heroes"]), "enabled_lab_heroes": len(runtime["heroes"]),
                "authored_traits": len(source["traits"]), "runtime_traits": 0, "runtime_relics": len(runtime["relics"]),
                "body_families": sorted({hero["body_family"] for hero in source["heroes"]}),
                "archetypes": sorted({hero["archetype"] for hero in source["heroes"]}),
                "trait_gaps": [{"id": t["id"], "authored_members": len(t["members"]), "thresholds": t["thresholds"]} for t in source["traits"]],
                "balance_status": "not_verified", "human_acceptance": "not_run"}
    relic_lines = ["# Generated relic catalogue", "", "Source: `data/vnext/catalog.json`. Laboratory tuning; balance and human acceptance are not established.", "",
                   "Draft after rounds 3, 15 and 25; three offers; three equipped per team; one per hero. Surviving players receive the choice regardless of neutral victory.", ""]
    for relic in source["relics"]:
        relic_lines.extend([f'## {relic["name"]}', "", relic["description"], "",
                            "Compatible: " + ", ".join(relic["compatible_mechanics"]) + ".", "",
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
