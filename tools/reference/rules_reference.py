"""Executable contract fixtures, NOT an Unreal game or combat simulator.
All numeric APIs use integer centipoints, basis points, milliseconds or milli-rates.
Pairing/settlement consume supplied outcomes; they do not fabricate combat results.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import combinations
from typing import Iterable, Mapping, Sequence
import copy
import hashlib
import json


def rounded_ratio(n: int, d: int) -> int:
    if n < 0 or d <= 0:
        raise ValueError('rounding expects nonnegative numerator and positive denominator')
    return (2*n+d)//(2*d)


def star_value(base: int, star: int, bonus_bp: int = 0) -> int:
    if star not in (1,2,3) or base < 0 or bonus_bp < -10000:
        raise ValueError('invalid star stat')
    return rounded_ratio(base*(10000,18000,32400)[star-1]*(10000+bonus_bp),10000**2)


def resolve_damage(raw_cp: int, damage_type: str, armor: int, resistance: int,
                   bonus_bp: int = 0) -> int:
    if raw_cp < 0 or armor < 0 or resistance < 0 or bonus_bp < -10000:
        raise ValueError('invalid damage inputs')
    if damage_type not in ('physical','magic','true'):
        raise ValueError('unknown damage type')
    defense={'physical':armor,'magic':resistance,'true':0}[damage_type]
    return rounded_ratio(raw_cp*(10000+bonus_bp)*100,10000*(100+defense))


def absorb_damage(health: int, shield: int, damage: int) -> tuple[int,int,int,int]:
    if min(health,shield,damage) < 0:
        raise ValueError('negative amount')
    absorbed=min(shield,damage)
    lost=min(health,damage-absorbed)
    return health-lost,shield-absorbed,absorbed,lost


def heal(health: int, maximum: int, amount: int) -> tuple[int,int]:
    if health < 0 or maximum <= 0 or health > maximum or amount < 0:
        raise ValueError('invalid healing inputs')
    if health==0:
        return 0,0  # no revival
    effective=min(amount,maximum-health)
    return health+effective,effective


def apply_shield(remaining: int, expiry_tick: int, amount: int,
                 incoming_expiry: int, now_tick: int) -> tuple[int,int]:
    if min(remaining,amount,expiry_tick,incoming_expiry,now_tick)<0:
        raise ValueError('negative shield inputs')
    if expiry_tick<=now_tick:
        remaining,expiry_tick=0,0
    if incoming_expiry<=now_tick or amount==0:
        return remaining,expiry_tick
    if amount>remaining:
        return amount,incoming_expiry
    if amount==remaining:
        return remaining,max(expiry_tick,incoming_expiry)
    return remaining,expiry_tick


def interval_ticks(rate_milli: int, additive_bp: int=0, tick_ms: int=50) -> int:
    if rate_milli<=0 or tick_ms<=0 or additive_bp<=-10000:
        raise ValueError('invalid rate')
    rate=max(250,min(2500,rounded_ratio(rate_milli*(10000+additive_bp),10000)))
    return (1000000+rate*tick_ms-1)//(rate*tick_ms)


def battle_timeout_score(units: Iterable[tuple[int,int]]) -> Fraction:
    score=Fraction(0)
    for health,maximum in units:
        if maximum<=0 or health<0 or health>maximum:
            raise ValueError('invalid health fraction')
        score+=Fraction(health,maximum)
    return score


def trait_counts(unit_ids: Iterable[str], catalog: Mapping[str,dict]) -> dict[str,int]:
    c=Counter()
    for uid in set(unit_ids):
        u=catalog[uid];c[u['race']]+=1;c[u['unit_class']]+=1
    return dict(c)


def active_traits(unit_ids: Iterable[str], catalog: Mapping[str,dict],
                  traits: Sequence[dict], thresholds: tuple[int,...]=(2,4)) -> dict[str,int]:
    c=trait_counts(unit_ids,catalog);result={}
    for t in traits:
        eligible=[x for x in t['tiers'] if x['count'] in thresholds and c.get(t['id'],0)>=x['count']]
        if eligible:
            result[t['id']]=max(eligible,key=lambda x:x['count'])['value']
    return result


def income(lock_gold: int, won: bool, continues: bool=True, *, neutral: bool=False) -> int:
    if lock_gold<0:
        raise ValueError('negative gold')
    return 5+(2 if neutral else 1)*int(won)+min(3,lock_gold//10) if continues else 0


def player_damage(round_no: int, enemy_survivors: int, draw: bool=False) -> int:
    """PvP-index stage fixture; calendar rounds must not be passed after neutrals."""
    if not 1<=round_no<=40 or not 0<=enemy_survivors<=6:
        raise ValueError('invalid result')
    return 2 if draw else (2 if round_no<=6 else 4 if round_no<=12 else 6)+enemy_survivors


def is_neutral_round(round_no: int, opening_rounds: int=3, every: int=5) -> bool:
    if round_no<1 or opening_rounds<0 or every<1:
        raise ValueError('invalid round schedule')
    return round_no<=opening_rounds or round_no%every==0


def wave_for_round(round_no: int, waves: Sequence[dict]) -> dict:
    """Explicit lookup never fabricates a wave for a later unconfigured profile."""
    if round_no<1:raise ValueError('invalid round')
    found=[wave for wave in waves if wave['round']==round_no]
    if len(found)!=1:raise ValueError('exactly one authored wave is required')
    return found[0]


def scaled_neutral_definition(creature: dict, wave: dict) -> dict:
    """Pure authoring fixture: isolated copy, wave factors once, no star growth."""
    hp_factor=wave['hp_scale_bp'];damage_factor=wave['damage_scale_bp']
    if hp_factor<=0 or damage_factor<=0:raise ValueError('nonpositive wave scale')
    result=copy.deepcopy(creature);stats=result['stats']
    stats['health_cp']=rounded_ratio(stats['health_cp']*hp_factor,10000)
    stats['attack_damage_cp']=rounded_ratio(stats['attack_damage_cp']*damage_factor,10000)
    if result['ability']:
        for effect in result['ability']['effects']:
            factor=hp_factor if effect['effect']=='shield' else damage_factor if effect['effect']=='damage' else 10000
            effect['magnitude_by_star']=[rounded_ratio(value*factor,10000) if value>=0 else -rounded_ratio(-value*factor,10000) for value in effect['magnitude_by_star']]
    return result


def advance_xp(level: int, xp: int, added: int) -> tuple[int,int]:
    if not 3<=level<=6 or xp<0 or added<0:
        raise ValueError('invalid progression')
    if level==6:return 6,0
    xp+=added
    while level<6 and xp>={3:4,4:8,5:12}[level]:
        xp-={3:4,4:8,5:12}[level];level+=1
    return level,0 if level==6 else xp


@dataclass
class OwnedUnit:
    instance_id:int
    definition_id:str
    star:int=1
    location:str='bench'  # bench, board or pending (transaction-local only)
    slot:int=0
    def copies(self)->int:return 3**(self.star-1)

@dataclass
class EconomyState:
    gold:int
    units:list[OwnedUnit]=field(default_factory=list)
    shop:list[str|None]=field(default_factory=lambda:[None]*5)
    next_instance_id:int=1
    phase:str='Preparation'
    successful_commands:dict[str,dict]=field(default_factory=dict)


def _survivor_key(u:OwnedUnit)->tuple[int,int,int]:
    return (0,u.instance_id,0) if u.location=='board' else (1,u.slot,u.instance_id) if u.location=='bench' else (2,u.instance_id,0)


def purchase(state:EconomyState,shop_slot:int,command_id:str,catalog:Mapping[str,dict])->EconomyState:
    """Returns a new state; validation failure leaves the caller's state untouched.
    Command replay is idempotent only for matching arguments. This small fixture is
    not the full production command envelope, which also validates authenticated seats.
    """
    payload={'kind':'buy','slot':shop_slot}
    if not command_id:raise ValueError('empty command id')
    if command_id in state.successful_commands:
        if state.successful_commands[command_id]!=payload:raise ValueError('command id reused with different payload')
        return copy.deepcopy(state)
    if state.phase!='Preparation':raise ValueError('phase locked')
    if not 0<=shop_slot<len(state.shop):raise ValueError('bad shop slot')
    uid=state.shop[shop_slot]
    if uid is None or uid not in catalog:raise ValueError('empty or unknown offer')
    cost=catalog[uid]['cost']
    if state.gold<cost:raise ValueError('insufficient funds')
    s=copy.deepcopy(state);s.gold-=cost;s.shop[shop_slot]=None
    used={u.slot for u in s.units if u.location=='bench'}
    free=next((i for i in range(8) if i not in used),None)
    new=OwnedUnit(s.next_instance_id,uid,1,'bench' if free is not None else 'pending',free or 0)
    s.next_instance_id+=1;s.units.append(new)
    for star in (1,2):
        # Multiple groups are supported but merges are bounded by roster capacity.
        while True:
            candidates=sorted([u for u in s.units if u.definition_id==uid and u.star==star],key=_survivor_key)
            if len(candidates)<3:break
            chosen=candidates[:3];keep=chosen[0];keep.star+=1
            remove={u.instance_id for u in chosen[1:]}
            s.units=[u for u in s.units if u.instance_id not in remove]
    pending=[u for u in s.units if u.location=='pending']
    used={u.slot for u in s.units if u.location=='bench'}
    for u in pending:
        free=next((i for i in range(8) if i not in used),None)
        if free is None:raise ValueError('bench full without legal merge')
        u.location='bench';u.slot=free;used.add(free)
    if len(used)>8:raise ValueError('bench capacity')
    s.successful_commands[command_id]=payload
    return s


def all_matchings(seats:tuple[int,...]):
    if not seats:
        yield ()
        return
    a=seats[0]
    for i in range(1,len(seats)):
        b=seats[i];remaining=seats[1:i]+seats[i+1:]
        for rest in all_matchings(remaining):yield ((a,b),)+rest


def _digest(seed:int,round_no:int,value)->int:
    # Portable reference tie-break, explicitly not Python's randomized hash().
    raw=json.dumps([seed,round_no,value],separators=(',',':')).encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8],'big')


def pair_round(active:Sequence[int],round_no:int,seed:int,
               pair_counts:Mapping[tuple[int,int],int]|None=None,
               last_pairs:Iterable[tuple[int,int]]=(),
               ghost_counts:Mapping[int,int]|None=None,
               previous_ghost:int|None=None)->dict:
    seats=tuple(sorted(active))
    if len(set(seats))!=len(seats) or len(seats)>8 or len(seats)<2:
        raise ValueError('pairing requires 2..8 unique seats')
    counts=pair_counts or {};last={tuple(sorted(p)) for p in last_pairs};gc=ghost_counts or {}
    ghost=None
    if len(seats)%2:
        recipient=min(seats,key=lambda s:(gc.get(s,0),s==previous_ghost,_digest(seed,round_no,['ghost',s])))
        rest=tuple(s for s in seats if s!=recipient)
        donor=min(rest,key=lambda s:(tuple(sorted((recipient,s))) in last,counts.get(tuple(sorted((recipient,s))),0),_digest(seed,round_no,['donor',recipient,s])))
        ghost={'recipient':recipient,'donor':donor}
        seats=rest
    candidates=list(all_matchings(seats))
    def score(pairs):
        normalized=tuple(sorted(tuple(sorted(p)) for p in pairs))
        return (sum(p in last for p in normalized),sum(counts.get(p,0) for p in normalized),_digest(seed,round_no,normalized))
    pairs=min(candidates,key=score)
    return {'round':round_no,'pairs':[list(p) for p in pairs],'ghost':ghost}


def health_effect_seats(plan:dict)->list[int]:
    seats=[s for pair in plan['pairs'] for s in pair]
    if plan['ghost']:seats.append(plan['ghost']['recipient'])
    return seats


def rank_groups(items:Mapping[int,tuple],start_place:int=1)->dict[int,int]:
    """Competition ranks, descending tuple: e.g. 1,1,3, never player-ID tiebreaks."""
    keys=sorted(set(items.values()),reverse=True);out={};place=start_place
    for key in keys:
        group=[s for s,v in items.items() if v==key]
        for s in group:out[s]=place
        place+=len(group)
    return out


def settle_supplied_results(health:Mapping[int,int],wins:Mapping[int,int],outcomes:Mapping[int,tuple[str,int]],round_no:int,
                            *,encounter_kind:str='pvp',pvp_index:int|None=None,max_rounds:int=40)->dict:
    """One independently supplied result per real active seat. Ghost donor's second
    appearance is deliberately absent. No combat or full tournament is simulated.
    The default PvP kind keeps direct old-profile fixture calls explicit; the
    production tournament owns schedule resolution and duplicate-settlement guards.
    """
    if set(health)!=set(outcomes) or any(h<=0 for h in health.values()):
        raise ValueError('one result required per living real seat')
    if not 1<=round_no<=max_rounds or max_rounds>40 or encounter_kind not in ('pvp','neutral'):
        raise ValueError('invalid settlement round or kind')
    if encounter_kind=='neutral' and not is_neutral_round(round_no):
        raise ValueError('neutral result outside configured schedule')
    raw={};new_wins=dict(wins)
    for s,hp in health.items():
        outcome,survivors=outcomes[s]
        if outcome not in ('win','loss','draw') or not 0<=survivors<=6:raise ValueError('bad outcome')
        delta=0 if outcome=='win' else (0 if round_no<=3 else 2) if encounter_kind=='neutral' else player_damage(pvp_index or round_no,survivors,outcome=='draw')
        raw[s]=hp-delta
        new_wins[s]=new_wins.get(s,0)+int(outcome=='win' and encounter_kind=='pvp')
    alive=[s for s,hp in raw.items() if hp>0];dead=[s for s in raw if s not in alive]
    placements=rank_groups({s:(raw[s],new_wins[s]) for s in dead},len(alive)+1)
    finished=len(alive)<=1 or round_no==max_rounds
    if finished:
        placements.update(rank_groups({s:(raw[s],new_wins[s]) for s in alive},1))
    pending={s:(2 if encounter_kind=='neutral' else 1) if s in alive and not finished and outcomes[s][0]=='win' else 0 for s in health}
    return {'health':{s:max(0,h) for s,h in raw.items()},'raw_health':raw,'wins':new_wins,'new_placements':placements,'active':alive,'finished':finished,'pending_victory_income':pending}


def retreat_destination(origin:tuple[int,int],target:tuple[int,int],occupied:set[tuple[int,int]],
                        reserved:set[tuple[int,int]],max_dash:int=2,attack_range:int=4)->tuple[int,int]|None:
    """Pure destination selector fixture; does not animate or execute a dash."""
    def distance(a,b):return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
    if any(not 0<=v<8 for p in (origin,target) for v in p) or max_dash<1:
        raise ValueError('invalid grid input')
    candidates=[]
    for x in range(8):
        for y in range(8):
            cell=(x,y);sep=distance(cell,target);step=distance(cell,origin)
            if cell not in occupied|reserved and 0<step<=max_dash and distance(origin,target)<sep<=attack_range:
                candidates.append(cell)
    return min(candidates,key=lambda c:(-distance(c,target),distance(c,origin),c[0],c[1])) if candidates else None
