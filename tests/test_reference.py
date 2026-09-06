from __future__ import annotations
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/reference'))
from rules_reference import *
CATALOG={u['id']:u for u in json.loads((ROOT/'data/units.json').read_text())['units']}
TRAITS=json.loads((ROOT/'data/traits.json').read_text())['traits']
A='wc_u_human_guardian';B='wc_u_elf_ranger';C='wc_u_dwarf_guardian'

class MathTests(unittest.TestCase):
 def test_physical(self):self.assertEqual(resolve_damage(12000,'physical',50,0),8000)
 def test_magic(self):self.assertEqual(resolve_damage(12000,'magic',0,20),10000)
 def test_true(self):self.assertEqual(resolve_damage(9000,'true',9999,9999),9000)
 def test_shield_overflow(self):self.assertEqual(absorb_damage(100000,3000,8000),(95000,0,3000,5000))
 def test_true_shield(self):self.assertEqual(absorb_damage(100000,4000,resolve_damage(9000,'true',99,99)),(95000,0,4000,5000))
 def test_damage_additive(self):self.assertEqual(resolve_damage(10000,'physical',25,0,2500),10000)
 def test_no_minimum_damage(self):self.assertEqual(resolve_damage(0,'physical',999,0),0)
 def test_negative_armor_rejected(self):
  with self.assertRaises(ValueError):resolve_damage(100,'physical',-1,0)
 def test_invalid_type_rejected(self):
  with self.assertRaises(ValueError):resolve_damage(100,'arcane',0,0)
 def test_half_up(self):self.assertEqual(rounded_ratio(1,2),1);self.assertEqual(rounded_ratio(4,3),1)
 def test_star_health(self):self.assertEqual(star_value(100000,2,2500),225000)
 def test_star_three(self):self.assertEqual(star_value(4800,3),15552)
 def test_invalid_star(self):
  with self.assertRaises(ValueError):star_value(100,4)
 def test_heal_cap(self):self.assertEqual(heal(95000,100000,10000),(100000,5000))
 def test_heal_no_revive(self):self.assertEqual(heal(0,100000,10000),(0,0))
 def test_shield_stronger(self):self.assertEqual(apply_shield(5000,100,6000,90,1),(6000,90))
 def test_shield_equal_later(self):self.assertEqual(apply_shield(5000,100,5000,120,1),(5000,120))
 def test_shield_equal_earlier(self):self.assertEqual(apply_shield(5000,100,5000,90,1),(5000,100))
 def test_shield_weaker(self):self.assertEqual(apply_shield(5000,100,4000,200,1),(5000,100))
 def test_shield_expiry_boundary(self):self.assertEqual(apply_shield(5000,100,3000,120,100),(3000,120))
 def test_rate_additive(self):self.assertEqual(interval_ticks(800,2500),20)
 def test_rate_quantization(self):self.assertEqual(interval_ticks(850),24)
 def test_rate_cap(self):self.assertEqual(interval_ticks(2000,10000),8)
 def test_timeout_fraction(self):self.assertEqual(battle_timeout_score([(50,100),(25,100)]),Fraction(3,4))
 def test_timeout_not_raw_health(self):self.assertGreater(battle_timeout_score([(50,100)]),battle_timeout_score([(100,1000)]))
 def test_timeout_invalid(self):
  with self.assertRaises(ValueError):battle_timeout_score([(11,10)])

class EconomyTests(unittest.TestCase):
 def test_interest(self):self.assertEqual(income(29,False),7);self.assertEqual(income(30,True),9)
 def test_no_income_finished(self):self.assertEqual(income(30,True,False),0)
 def test_stage_boundaries(self):self.assertEqual(player_damage(6,3),5);self.assertEqual(player_damage(7,3),7);self.assertEqual(player_damage(13,3),9)
 def test_draw_not_loss(self):self.assertEqual(player_damage(24,6,True),2)
 def test_xp_overflow(self):self.assertEqual(advance_xp(3,0,20),(5,8))
 def test_xp_cap(self):self.assertEqual(advance_xp(3,0,24),(6,0));self.assertEqual(advance_xp(6,0,100),(6,0))
 def test_purchase(self):
  s=EconomyState(10,shop=[A,None,None,None,None]);n=purchase(s,0,'one',CATALOG)
  self.assertEqual(n.gold,9);self.assertIsNone(n.shop[0]);self.assertEqual(s.gold,10)
 def test_insufficient_preserves(self):
  s=EconomyState(0,shop=[A]*5);old=copy.deepcopy(s)
  with self.assertRaises(ValueError):purchase(s,0,'one',CATALOG)
  self.assertEqual(s,old)
 def test_phase_lock(self):
  s=EconomyState(10,shop=[A]*5,phase='Combat')
  with self.assertRaises(ValueError):purchase(s,0,'one',CATALOG)
 def test_idempotent(self):
  n=purchase(EconomyState(10,shop=[A]*5),0,'one',CATALOG)
  self.assertEqual(purchase(n,0,'one',CATALOG),n)
 def test_replayed_id_wrong_payload(self):
  n=purchase(EconomyState(10,shop=[A]*5),0,'one',CATALOG)
  with self.assertRaises(ValueError):purchase(n,1,'one',CATALOG)
 def test_full_bench_failure_preserves(self):
  s=EconomyState(10,[OwnedUnit(i+1,B,3,'bench',i) for i in range(8)],[A]*5,9);old=copy.deepcopy(s)
  with self.assertRaises(ValueError):purchase(s,0,'one',CATALOG)
  self.assertEqual(s,old)
 def test_full_bench_merge(self):
  us=[OwnedUnit(1,A,1,'bench',0),OwnedUnit(2,A,1,'bench',1)]+[OwnedUnit(i+1,B,3,'bench',i) for i in range(2,8)]
  n=purchase(EconomyState(10,us,[A]*5,9),0,'one',CATALOG)
  self.assertEqual(len(n.units),7);self.assertEqual(next(u for u in n.units if u.definition_id==A).star,2)
 def test_deployed_survivor(self):
  us=[OwnedUnit(5,A,1,'board',27),OwnedUnit(2,A,1,'bench',0)]
  n=purchase(EconomyState(10,us,[A]*5,6),0,'one',CATALOG)
  self.assertEqual([(u.instance_id,u.star,u.location,u.slot) for u in n.units],[(5,2,'board',27)])
 def test_cascade_conserves_copies(self):
  us=[OwnedUnit(1,A,2,'bench',0),OwnedUnit(2,A,2,'bench',1),OwnedUnit(3,A,1,'bench',2),OwnedUnit(4,A,1,'bench',3)]
  n=purchase(EconomyState(10,us,[A]*5,5),0,'one',CATALOG)
  self.assertEqual(len(n.units),1);self.assertEqual(n.units[0].star,3);self.assertEqual(n.units[0].copies(),9)
 def test_no_four_star(self):
  us=[OwnedUnit(1,A,3,'bench',0),OwnedUnit(2,A,3,'bench',1)]
  n=purchase(EconomyState(10,us,[A]*5,3),0,'one',CATALOG)
  self.assertEqual(sorted(u.star for u in n.units),[1,3,3])

class TraitAndGridTests(unittest.TestCase):
 def test_duplicate_does_not_activate(self):self.assertEqual(active_traits([A,A],CATALOG,TRAITS),{})
 def test_matching_race_class(self):
  out=active_traits([A,C,'wc_u_human_priest'],CATALOG,TRAITS)
  self.assertEqual(out,{'human':1000,'guardian':15})
 def test_four_tier_replaces(self):
  ids=[u['id'] for u in CATALOG.values() if u['race']=='human']
  self.assertEqual(active_traits(ids,CATALOG,TRAITS,(2,4))['human'],2000)
 def test_legacy_v3_threshold_fixture_ignores_four(self):
  ids=[u['id'] for u in CATALOG.values() if u['race']=='human']
  self.assertEqual(active_traits(ids,CATALOG,TRAITS,(2,))['human'],1000)
 def test_retreat_valid(self):
  origin=(3,3);target=(3,4);d=retreat_destination(origin,target,{origin,target},set())
  self.assertIsNotNone(d);self.assertGreater(max(abs(d[0]-3),abs(d[1]-4)),1)
 def test_retreat_fully_blocked(self):self.assertIsNone(retreat_destination((3,3),(3,4),{(x,y) for x in range(8) for y in range(8)},set()))
 def test_retreat_reservations(self):
  occupied={(3,3),(3,4)};d1=retreat_destination((3,3),(3,4),occupied,set());d2=retreat_destination((3,3),(3,4),occupied,{d1})
  self.assertNotEqual(d1,d2)

class PairAndSettlementTests(unittest.TestCase):
 def test_matchings_count_eight(self):self.assertEqual(len(list(all_matchings(tuple(range(8))))),105)
 def test_all_seat_counts_many_seeds(self):
  # Structural pairing trials, NOT actual combat matches.
  for n in range(2,9):
   for seed in range(100):
    p=pair_round(list(range(n)),1,seed)
    self.assertEqual(sorted(health_effect_seats(p)),list(range(n)))
    self.assertTrue(all(a!=b for a,b in p['pairs']))
    if p['ghost']:self.assertNotEqual(p['ghost']['recipient'],p['ghost']['donor'])
 def test_pair_reproducible(self):self.assertEqual(pair_round(range(8),3,42),pair_round(list(reversed(range(8))),3,42))
 def test_immediate_repeat_avoided(self):
  a=pair_round(range(8),1,42);b=pair_round(range(8),2,42,last_pairs=a['pairs'])
  self.assertFalse({tuple(p) for p in a['pairs']} & {tuple(p) for p in b['pairs']})
 def test_low_ghost_count_priority(self):
  p=pair_round(range(5),5,42,ghost_counts={0:0,1:2,2:2,3:2,4:2})
  self.assertEqual(p['ghost']['recipient'],0)
 def test_donor_not_double_settled(self):
  p=pair_round(range(7),1,3);seats=health_effect_seats(p)
  self.assertEqual(seats.count(p['ghost']['donor']),1);self.assertEqual(seats.count(p['ghost']['recipient']),1)
 def test_one_seat_requires_end_path(self):
  with self.assertRaises(ValueError):pair_round([0],1,1)
 def test_duplicate_seat_rejected(self):
  with self.assertRaises(ValueError):pair_round([0,0],1,1)
 def test_shared_rank(self):self.assertEqual(rank_groups({0:(5,2),1:(5,2),2:(4,9)}),{0:1,1:1,2:3})
 def test_zero_survivors(self):
  s=settle_supplied_results({0:2,1:2},{0:0,1:0},{0:('draw',0),1:('draw',0)},1)
  self.assertTrue(s['finished']);self.assertEqual(s['active'],[]);self.assertEqual(s['new_placements'],{0:1,1:1})
 def test_elimination_order(self):
  s=settle_supplied_results({0:1,1:2,2:20,3:20},{},{0:('loss',2),1:('loss',2),2:('win',0),3:('win',0)},1)
  self.assertEqual(s['new_placements'],{1:3,0:4});self.assertFalse(s['finished'])
 def test_legacy_v3_cap_shared_first(self):
  s=settle_supplied_results({0:50,1:50},{0:2,1:2},{0:('draw',0),1:('draw',0)},24,max_rounds=24)
  self.assertTrue(s['finished']);self.assertEqual(s['new_placements'],{0:1,1:1})
 def test_missing_outcome_rejected(self):
  with self.assertRaises(ValueError):settle_supplied_results({0:50,1:50},{},{0:('win',0)},1)

if __name__=='__main__':unittest.main()

class FormationFixtureTests(unittest.TestCase):
    def test_authored_formations_have_legal_cells_and_exact_traits(self):
        import json
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        units = {u['id']:u for u in json.loads((root/'data/units.json').read_text())['units']}
        examples = json.loads((root/'tests/fixtures/example_formations.json').read_text())
        self.assertEqual(len(examples), 4)
        for example in examples:
            self.assertEqual(len(example['formation']), 6)
            self.assertEqual(len({tuple(s['cell']) for s in example['formation']}), 6)
            counts = {}
            for slot in example['formation']:
                unit = units[slot['unit_id']]
                self.assertEqual(unit['production_phase'], 'alpha')
                self.assertTrue(0 <= slot['cell'][0] < 8 and 0 <= slot['cell'][1] < 4)
                self.assertEqual(slot['star'], 1)
                for label in (unit['race'], unit['unit_class']):
                    counts[label] = counts.get(label, 0) + 1
            self.assertEqual(sorted(k for k,v in counts.items() if v >= 2), example['active_traits'])
