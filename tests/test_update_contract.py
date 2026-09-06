"""Authoring and arithmetic regression fixtures; no claim of engine execution."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'reference'))
from rules_reference import (active_traits, income, is_neutral_round, player_damage,
                             scaled_neutral_definition, settle_supplied_results,
                             wave_for_round)

spec = importlib.util.spec_from_file_location('validate_kit', ROOT / 'tools' / 'validate_kit.py')
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


UNITS = load('data/units.json')
CATALOG = {u['id']: u for u in UNITS['units']}
RULES = load('data/rules.alpha.json')
TRAITS = load('data/traits.json')['traits']
NEUTRALS = load('data/neutrals.json')


class UpdateSchemaTests(unittest.TestCase):
    def test_all_selected_heroes_and_short_names_are_unique(self):
        self.assertEqual(set(RULES['alpha_unit_ids']), set(CATALOG))
        self.assertEqual(len(RULES['alpha_unit_ids']), 24)
        self.assertEqual(len({u['display_name'].casefold() for u in CATALOG.values()}), 24)
        self.assertTrue(all(u['display_name'] == u['name'].split()[0] for u in CATALOG.values()))

    def test_old_schema_and_old_primary_effect_are_rejected(self):
        validator = Draft202012Validator(load('data/schemas/units.schema.json'))
        old_version = copy.deepcopy(UNITS)
        old_version['schema_version'] = '3.0.0'
        self.assertFalse(validator.is_valid(old_version))
        duplicate_authority = copy.deepcopy(UNITS)
        duplicate_authority['units'][0]['ability']['effect'] = 'shield'
        self.assertFalse(validator.is_valid(duplicate_authority))

    def test_unknown_role_inventory_and_third_trait_are_rejected(self):
        validator = Draft202012Validator(load('data/schemas/units.schema.json'))
        for field, value in [('role_tags', ['invented']), ('inventory', []), ('origin_bonus', 'third_trait')]:
            malformed = copy.deepcopy(UNITS)
            malformed['units'][0][field] = value
            self.assertFalse(validator.is_valid(malformed), field)

    def test_policy_aliases_and_unbounded_timings_are_rejected(self):
        validator = Draft202012Validator(load('data/schemas/units.schema.json'))
        for key, value in [('interrupt_policy','cancel_before_release_keep_cooldown'),
                           ('no_target_policy','remain_ready_continue_basic'),
                           ('effect_snapshot','release'),('cast_ms',2**40),
                           ('range_tiles',9),('recovery_ms',0)]:
            malformed = copy.deepcopy(UNITS)
            malformed['units'][0]['ability'][key] = value
            self.assertFalse(validator.is_valid(malformed), key)

    def test_ordered_effects_are_bounded_and_supported(self):
        neris = copy.deepcopy(CATALOG['wc_u_elf_mage']['ability'])
        self.assertEqual(validation.ability_errors(neris), [])
        neris['effects'].reverse()
        self.assertIn('supported ordered effects', validation.ability_errors(neris))
        malformed = copy.deepcopy(UNITS)
        malformed['units'][0]['ability']['effects'] *= 3
        self.assertFalse(Draft202012Validator(load('data/schemas/units.schema.json')).is_valid(malformed))

    def test_neris_damage_and_control_are_separate_explicit_values(self):
        ability = CATALOG['wc_u_elf_mage']['ability']
        damage, stun = ability['effects']
        self.assertEqual(damage['magnitude_by_star'], [6000, 10800, 19440])
        self.assertEqual((damage['effect'], damage['damage_type'], damage['duration_ms']), ('damage', 'magic', 0))
        self.assertEqual((stun['effect'], stun['duration_ms'], stun['magnitude_by_star']), ('stun', 1250, [0, 0, 0]))
        self.assertEqual([ability[k] for k in ('range_tiles','radius_tiles','cast_ms','travel_ms','recovery_ms','first_cast_ms','cooldown_ms')], [4,0,400,200,300,3500,9500])

    def test_finn_enemy_selector_cannot_be_attached_to_positive_buff(self):
        finn = copy.deepcopy(CATALOG['wc_u_halfling_ranger']['ability'])
        self.assertEqual(finn['target_rule'], 'highest_attack_rate_enemy')
        self.assertEqual(validation.ability_errors(finn), [])
        finn['effects'][0]['magnitude_by_star'] = [2000, 2500, 3000]
        self.assertIn('enemy rate selector only debuffs', validation.ability_errors(finn))

    def test_neutral_and_hero_combat_shapes_cannot_drift(self):
        heroes = load('data/schemas/units.schema.json')['properties']['units']['items']['properties']
        creatures = load('data/schemas/neutrals.schema.json')['properties']['creatures']['items']['properties']
        self.assertEqual(heroes['ability'], creatures['ability']['anyOf'][0])
        self.assertEqual(heroes['stats'], creatures['stats'])

    def test_every_trait_four_replaces_two_and_ignores_duplicate_stars(self):
        for trait in TRAITS:
            members = [u['id'] for u in CATALOG.values() if trait['id'] in (u['race'], u['unit_class'])]
            self.assertEqual(len(members), 4)
            for count in range(5):
                active = active_traits(members[:count] * 3, CATALOG, [trait])
                expected = {} if count < 2 else {trait['id']: trait['tiers'][1 if count == 4 else 0]['value']}
                self.assertEqual(active, expected, (trait['id'], count))


class NeutralAuthoringTests(unittest.TestCase):
    def test_current_authored_waves_are_complete_and_valid(self):
        self.assertEqual(validation.neutral_errors(NEUTRALS, RULES), [])
        self.assertTrue(Draft202012Validator(load('data/schemas/neutrals.schema.json')).is_valid(NEUTRALS))

    def test_basic_only_creature_has_explicit_null_skill(self):
        creatures = {c['id']: c for c in NEUTRALS['creatures']}
        self.assertIsNone(creatures['wc_n_sprout']['ability'])
        self.assertIsNone(creatures['wc_n_thorn']['ability'])
        self.assertNotIn('Active', creatures['wc_n_sprout']['animation_contract']['required_clips'])

    def test_missing_duplicate_unknown_and_overlapping_waves_reject(self):
        bad = copy.deepcopy(NEUTRALS)
        bad['waves'].pop()
        self.assertIn('complete exact neutral schedule', validation.neutral_errors(bad, RULES))
        bad = copy.deepcopy(NEUTRALS)
        bad['waves'].append(copy.deepcopy(bad['waves'][0]))
        self.assertIn('unique wave IDs and rounds', validation.neutral_errors(bad, RULES))
        bad = copy.deepcopy(NEUTRALS)
        bad['waves'][0]['slots'][0]['creature_id'] = 'wc_n_absent'
        self.assertTrue(any('existing creature wc_n_absent' in e for e in validation.neutral_errors(bad, RULES)))
        bad = copy.deepcopy(NEUTRALS)
        bad['waves'][0]['slots'][1] = copy.deepcopy(bad['waves'][0]['slots'][0])
        self.assertTrue(any('bounded distinct slots' in e for e in validation.neutral_errors(bad, RULES)))

    def test_invalid_cells_and_unsafe_products_reject(self):
        bad = copy.deepcopy(NEUTRALS)
        bad['waves'][0]['slots'][0]['row'] = 4
        self.assertTrue(any('legal local cells' in e for e in validation.neutral_errors(bad, RULES)))
        bad = copy.deepcopy(NEUTRALS)
        bad['waves'][0]['hp_scale_bp'] = 2**63
        self.assertTrue(any('safe scaled stat' in e for e in validation.neutral_errors(bad, RULES)))

    def test_independent_scaled_copies_never_mutate_canonical(self):
        creature = next(c for c in NEUTRALS['creatures'] if c['id'] == 'wc_n_stoneback')
        original = copy.deepcopy(creature)
        wave = {'hp_scale_bp': 12000, 'damage_scale_bp': 11000}
        a = scaled_neutral_definition(creature, wave)
        b = scaled_neutral_definition(creature, wave)
        self.assertEqual(a['stats']['health_cp'], 84000)
        self.assertEqual(a['stats']['attack_damage_cp'], 4620)
        self.assertEqual(a['ability']['effects'][0]['magnitude_by_star'], [21600]*3)
        a['stats']['health_cp'] = 0
        self.assertEqual(b['stats']['health_cp'], 84000)
        self.assertEqual(creature, original)

    def test_damage_scales_once_while_timing_armor_and_speed_stay_fixed(self):
        creature = next(c for c in NEUTRALS['creatures'] if c['id'] == 'wc_n_warden')
        scaled = scaled_neutral_definition(creature, {'hp_scale_bp': 23000, 'damage_scale_bp': 17000})
        self.assertEqual(scaled['stats']['health_cp'], 322000)
        self.assertEqual(scaled['ability']['effects'][0]['magnitude_by_star'], [22100]*3)
        for key in ('physical_armor','magic_resistance','attack_rate_milli','movement_rate_milli'):
            self.assertEqual(scaled['stats'][key], creature['stats'][key])
        for key in ('cast_ms','cooldown_ms','range_tiles','travel_ms'):
            self.assertEqual(scaled['ability'][key], creature['ability'][key])

    def test_fractional_scale_rounds_half_up_once(self):
        creature = copy.deepcopy(NEUTRALS['creatures'][0])
        creature['stats']['health_cp'] = 3
        self.assertEqual(scaled_neutral_definition(creature, {'hp_scale_bp':15000,'damage_scale_bp':10000})['stats']['health_cp'], 5)


class NeutralScheduleAndSettlementTests(unittest.TestCase):
    def test_schedule_boundaries_and_cap_distribution(self):
        expected = {1,2,3,5,10,15,20,25,30,35,40}
        self.assertEqual({r for r in range(1,41) if is_neutral_round(r)}, expected)
        self.assertEqual(sum(not is_neutral_round(r) for r in range(1,41)), 29)
        self.assertFalse(is_neutral_round(41))
        self.assertTrue(is_neutral_round(45))
        for r in (0,-1):
            with self.assertRaises(ValueError): is_neutral_round(r)
        for opening, every in ((-1,5),(3,0)):
            with self.assertRaises(ValueError): is_neutral_round(1,opening,every)

    def test_missing_future_wave_is_not_invented(self):
        with self.assertRaises(ValueError): wave_for_round(45, NEUTRALS['waves'])
        with self.assertRaises(ValueError): wave_for_round(0, NEUTRALS['waves'])

    def test_neutral_income_replaces_pvp_bonus_and_finished_pays_nothing(self):
        self.assertEqual(income(30, True, neutral=True), 10)
        self.assertEqual(income(30, False, neutral=True), 8)
        self.assertEqual(income(30, True, neutral=False), 9)
        self.assertEqual(income(30, True, False, neutral=True), 0)

    def test_opening_failure_is_real_failure_without_captain_damage(self):
        outcomes = {0:('loss',2), 1:('draw',0), 2:('win',0)}
        for round_no in (1,2,3):
            result = settle_supplied_results({0:60,1:60,2:60}, {0:1,1:2,2:3}, outcomes, round_no, encounter_kind='neutral')
            self.assertEqual(result['health'], {0:60,1:60,2:60})
            self.assertEqual(result['wins'], {0:1,1:2,2:3})
            self.assertEqual(result['pending_victory_income'], {0:0,1:0,2:2})

    def test_late_neutral_loss_ignores_survivor_count(self):
        result = settle_supplied_results({0:60,1:60}, {}, {0:('loss',6),1:('loss',1)}, 5, encounter_kind='neutral')
        self.assertEqual(result['health'], {0:58,1:58})
        self.assertEqual(result['wins'], {0:0,1:0})

    def test_round_six_uses_second_pvp_stage_not_calendar_index(self):
        result = settle_supplied_results({0:60,1:60}, {}, {0:('loss',3),1:('win',0)}, 6, pvp_index=2)
        self.assertEqual(result['health'][0], 55)
        self.assertEqual(player_damage(7,3), 7)

    def test_round_forty_neutral_settles_before_cap_without_next_income(self):
        result = settle_supplied_results({0:50,1:50}, {0:3,1:2}, {0:('loss',6),1:('win',0)}, 40, encounter_kind='neutral')
        self.assertTrue(result['finished'])
        self.assertEqual(result['new_placements'], {1:1,0:2})
        self.assertEqual(result['health'], {0:48,1:50})
        self.assertEqual(result['pending_victory_income'], {0:0,1:0})
        self.assertEqual(result['wins'], {0:3,1:2})

    def test_simultaneous_neutral_elimination_preserves_pvp_ties(self):
        result = settle_supplied_results({0:2,1:2}, {0:3,1:3}, {0:('loss',1),1:('draw',0)}, 5, encounter_kind='neutral')
        self.assertEqual(result['active'], [])
        self.assertEqual(result['new_placements'], {0:1,1:1})
        self.assertTrue(result['finished'])
        self.assertEqual(result['pending_victory_income'], {0:0,1:0})

    def test_invalid_kind_calendar_round_and_missing_result_reject(self):
        for kwargs in ({'encounter_kind':'neutral'}, {'encounter_kind':'monster'}):
            with self.assertRaises(ValueError): settle_supplied_results({0:60,1:60},{},{0:('win',0),1:('win',0)},4,**kwargs)
        with self.assertRaises(ValueError): settle_supplied_results({0:60,1:60},{},{0:('win',0)},5,encounter_kind='neutral')


if __name__ == '__main__':
    unittest.main()
