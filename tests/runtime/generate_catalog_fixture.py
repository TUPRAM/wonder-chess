"""Emit the standalone C++ harness input from the current canonical JSON.

The emitted header is a build artifact, never an independently maintained balance file.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "build"
OUT.mkdir(exist_ok=True)
rules = json.loads((ROOT / "data/rules.alpha.json").read_text(encoding="utf-8"))
units = json.loads((ROOT / "data/units.json").read_text(encoding="utf-8"))["units"]
traits = json.loads((ROOT / "data/traits.json").read_text(encoding="utf-8"))["traits"]
bots = json.loads((ROOT / "data/bots.json").read_text(encoding="utf-8"))["bots"]
lines = ['#pragma once', '#include "Simulation/WonderSimulation.h"', 'inline wc::Catalog FixtureCatalog() { wc::Catalog c;']


def string(value):
    return json.dumps(value, ensure_ascii=True)


def assign(prefix, values, mapping):
    for source, destination in mapping.items():
        value = values[source]
        lines.append(f"{prefix}.{destination} = {string(value) if isinstance(value, str) else str(value).lower()};")


lines.extend([f'c.schemaVersion = {string(rules["schema_version"])};', f'c.balanceVersion = {string(rules["balance_version"])};'])
digest = hashlib.sha256()
for name in ("rules.alpha.json", "units.json", "traits.json", "bots.json"):
    digest.update((ROOT / "data" / name).read_bytes())
catalog_digest = json.loads((ROOT / "generated/catalog_digest.json").read_text(encoding="utf-8"))["combined_sha256"]
lines.append(f'c.contentDigest = "{catalog_digest}";')
assign("c.rules", rules["board"], {"columns": "columns", "rows": "rows", "deployment_rows_per_side": "deploymentRows", "tile_size_cm": "tileSizeCm"})
assign("c.rules", rules["simulation"], {"tick_ms": "tickMs", "min_attack_rate_milli": "minAttackRate", "max_attack_rate_milli": "maxAttackRate", "max_health_cp": "maxHealth", "max_armor": "maxArmor", "max_raw_damage_cp": "maxRawDamage"})
lines.append('c.rules.starMultiplierBp = {' + ','.join(map(str, rules["simulation"]["star_multiplier_bp"])) + '};')
assign("c.rules", rules["tournament"], {"seats": "seatCount", "starting_health": "startingHealth", "max_rounds": "maxRounds", "first_preparation_ms": "firstPreparationMs", "preparation_ms": "preparationMs", "combat_timeout_ms": "combatTimeoutMs", "settlement_ms": "settlementMs", "draw_damage": "drawDamage"})
for stage in rules["tournament"]["loss_base_by_stage"]:
    lines.append(f'c.rules.lossStages.push_back({{{stage["start"]},{stage["end"]},{stage["damage"]}}});')
assign("c.rules", rules["economy"], {"starting_gold": "startingGold", "bench_capacity": "benchCapacity", "shop_slots": "shopSlots", "reroll_cost": "rerollCost", "base_income": "baseIncome", "win_income": "winIncome", "interest_divisor": "interestDivisor", "interest_cap": "interestCap", "starting_level": "startingLevel", "maximum_level": "maximumLevel", "buy_xp_gold": "buyXpGold", "buy_xp_amount": "buyXpAmount", "passive_xp": "passiveXp"})
for level, xp in rules["economy"]["xp_to_next"].items():
    lines.append(f"c.rules.xpToNext[{level}] = {xp};")
for level, weights in rules["economy"]["shop_weights_by_level"].items():
    lines.append(f"c.rules.shopWeights[{level}] = {{{','.join(map(str, weights.values()))}}};")
assign("c.rules", rules["network"], {"bot_public_observation_ms": "botObservationMs", "bot_final_reposition_cutoff_ms": "botRepositionCutoffMs"})
effect_names = dict(damage="Damage", heal="Heal", shield="Shield", stun="Stun", dash="Dash", stat_modifier="StatModifier")
selector_names = dict(self="Self", current_enemy="CurrentEnemy", adjacent_enemies="AdjacentEnemies", adjacent_allies="AdjacentAllies", lowest_health_ally="LowestHealthAlly", current_enemy_area="CurrentEnemyArea", retreat_from_current_enemy="RetreatFromCurrentEnemy", current_enemy_adjacent="CurrentEnemyAdjacent", farthest_enemy_adjacent="FarthestEnemyAdjacent")
for identifier in rules["alpha_unit_ids"]:
    unit = next(unit for unit in units if unit["id"] == identifier)
    lines.append("{ wc::UnitDef u;")
    assign("u", unit, {"id": "id", "name": "name", "race": "race", "unit_class": "unitClass", "cost": "cost"})
    assign("u", unit["stats"], {"health_cp": "health", "attack_damage_cp": "attackDamage", "attack_rate_milli": "attackRate", "attack_range_tiles": "range", "physical_armor": "armor", "magic_resistance": "resistance", "movement_rate_milli": "movementRate", "attack_windup_ms": "attackWindupMs", "projectile_travel_ms": "projectileTravelMs"})
    lines.append(f'u.damageType = wc::DamageType::{unit["stats"]["attack_damage_type"].title()};')
    ability = unit["ability"]
    assign("u.ability", ability, {"id": "id", "name": "name", "first_cast_ms": "firstCastMs", "cooldown_ms": "cooldownMs", "cast_ms": "castMs", "recovery_ms": "recoveryMs", "duration_ms": "durationMs", "travel_ms": "travelMs", "radius_tiles": "radius", "range_tiles": "range", "max_targets": "maxTargets", "max_dash_tiles": "maxDash", "allow_self": "allowSelf"})
    lines.append(f'u.ability.effect = wc::Effect::{effect_names[ability["effect"]]};')
    lines.append(f'u.ability.selector = wc::Selector::{selector_names[ability["target_rule"]]};')
    if ability["damage_type"]:
        lines.append(f'u.ability.damageType = wc::DamageType::{ability["damage_type"].title()};')
    lines.append('u.ability.magnitude = {' + ','.join(map(str, ability["magnitude_by_star"])) + '};')
    lines.append('c.units.push_back(u); }')
for trait in traits:
    if trait["alpha_enabled"]:
        tier = next(tier for tier in trait["tiers"] if tier["count"] == 2)
        lines.append(f'c.traits.push_back({{{string(trait["id"])},{string(trait["stat"])},2,{tier["value"]}}});')
for bot in bots:
    lines.append("{ wc::BotDef b;")
    assign("b", bot, {"id": "id", "label": "label", "decision_interval_ms": "decisionIntervalMs", "public_observation_ms": "observationMs", "max_commands_per_preparation": "maxCommands", "max_paid_rerolls_per_preparation": "maxRerolls", "noise_bp": "noiseBp"})
    assign("b", bot["weights"], {key: key for key in bot["weights"]})
    lines.append("c.bots.push_back(b); }")
lines.append("return c; }")
(OUT / "CatalogFixture.h").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Generated exact fixture: catalog={catalog_digest}; four-runtime-inputs={digest.hexdigest()}")
