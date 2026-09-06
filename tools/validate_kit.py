"""Validate authoring/schema consistency, NOT Blender/Unreal execution or game balance."""
from __future__ import annotations
import json,math,re,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def ability_errors(a):
 """Cross-field capability checks beyond the closed JSON object schema."""
 errors=[]
 def require(ok,label):
  if not ok:errors.append(label)
 if a is None:return errors
 effects=a['effects'];kinds=[e['effect'] for e in effects]
 require(len(effects)==1 or kinds==['damage','stun'],'supported ordered effects')
 require(len(effects)==1 or a['target_rule']=='current_enemy','composite enemy selector')
 require(a['cast_ms']>=50 and a['recovery_ms']>=50,'positive cast and recovery')
 require(a['cooldown_ms']>a['cast_ms']+a['recovery_ms'],'cooldown bounds')
 for e in effects:
  kind=e['effect'];values=e['magnitude_by_star']
  require(e['duration_ms']%50==0,'effect 50ms alignment')
  require((kind=='damage')==(e['damage_type'] in ('physical','magic','true')),'damage type agrees with effect')
  require(kind=='damage' or e['damage_type'] is None,'nondamage type null')
  require(kind not in ('dash','stun') or (values==[0,0,0] and e['magnitude_unit'] is None),'status has no hidden magnitude')
  require(kind not in ('damage','heal','shield') or (min(values)>0 and e['magnitude_unit']=='centipoints'),'positive packet centipoints')
  require(kind!='stat_modifier' or (e['stat']=='attack_rate' and e['magnitude_unit']=='basis_points' and (min(values)>0 or max(values)<0) and min(values)>-10000),'supported rate modifier')
  require(kind=='stat_modifier' or e['stat'] is None,'unrelated stat forbidden')
  require(kind not in ('stun','shield','stat_modifier') or e['duration_ms']>0,'timed effect has duration')
  require(kind in ('stun','shield','stat_modifier') or e['duration_ms']==0,'instant effect has no duration')
  require(kind!='dash' or a['max_dash_tiles']>0,'dash distance')
 require(a['target_rule']!='highest_attack_rate_enemy' or (kinds==['stat_modifier'] and max(effects[0]['magnitude_by_star'])<0),'enemy rate selector only debuffs')
 return errors

def neutral_errors(neutrals,rules):
 """Validate authored content; this function does not execute neutral combat."""
 errors=[]
 def require(ok,label):
  if not ok:errors.append(label)
 creatures=neutrals['creatures'];byid={c['id']:c for c in creatures};waves=neutrals['waves'];t=rules['tournament']
 require(len(creatures)==len(byid)==7,'seven unique neutral creatures')
 require(not set(byid)&set(rules['alpha_unit_ids']),'neutral identities excluded from shop')
 reachable={r for r in range(1,t['max_rounds']+1) if r<=t['neutral_opening_rounds'] or r%t['neutral_every_rounds']==0}
 require(len(waves)==len({w['id'] for w in waves})==len({w['round'] for w in waves}),'unique wave IDs and rounds')
 require({w['round'] for w in waves}==reachable,'complete exact neutral schedule')
 for c in creatures:
  a=c['ability'];s=c['stats'];uid=c['id']
  errors.extend(uid+': '+err for err in ability_errors(a))
  require(c['footprint_cells']==1 and 'race' not in c and 'unit_class' not in c,uid+': one-cell trait-free creature')
  require(s['attack_windup_ms']%50==0 and s['projectile_travel_ms']%50==0,uid+': basic tick alignment')
  require(s['attack_windup_ms']+50<=400,uid+': max-speed basic recovery')
  if a:
   require(all(e['magnitude_by_star']==[e['magnitude_by_star'][0]]*3 for e in a['effects']),uid+': no neutral hero-star growth')
  clips=['Idle','Move','Attack','Hit','Defeat']+(['Active'] if a else [])
  require(c['animation_contract']['required_clips']==clips,uid+': required clips agree with active presence')
 for w in waves:
  wid=w['id'];slots=w['slots'];cells=[(s['column'],s['row']) for s in slots]
  require(1<=len(slots)<=6 and len(cells)==len(set(cells)),wid+': bounded distinct slots')
  require(all(0<=x<8 and 0<=y<4 for x,y in cells),wid+': legal local cells')
  for slot in slots:
   cid=slot['creature_id'];require(cid in byid,wid+': existing creature '+cid)
   if cid not in byid:continue
   c=byid[cid];s=c['stats']
   for value,factor,limit in [(s['health_cp'],w['hp_scale_bp'],rules['simulation']['max_health_cp']),(s['attack_damage_cp'],w['damage_scale_bp'],rules['simulation']['max_raw_damage_cp'])]:
    require(value*factor<2**63 and (value*factor+5000)//10000<=limit,wid+': safe scaled stat')
   if c['ability']:
    for e in c['ability']['effects']:
     if e['effect'] in ('damage','shield'):
      factor=w['hp_scale_bp'] if e['effect']=='shield' else w['damage_scale_bp'];limit=rules['simulation']['max_health_cp'] if e['effect']=='shield' else rules['simulation']['max_raw_damage_cp']
      require(e['magnitude_by_star'][0]*factor<2**63 and (e['magnitude_by_star'][0]*factor+5000)//10000<=limit,wid+': safe scaled skill')
 return errors
def main():
 errors=[];checks=[]
 def check(condition,label):
  checks.append(label)
  if not condition:errors.append(label)
 try:
  from jsonschema import Draft202012Validator
 except ImportError:
  raise SystemExit('Missing jsonschema. Install requirements-tools.txt in a project-local environment; schema validation was NOT RUN.')
 for name in ['units','rules.alpha','traits','world','bots','asset_manifest','neutrals']:
  schema=load(f'data/schemas/{name}.schema.json');data=load(f'data/{name}.json')
  Draft202012Validator.check_schema(schema)
  err=list(Draft202012Validator(schema).iter_errors(data))
  check(not err,f'schema:{name}')
  for e in err:errors.append(f'{name}:{list(e.path)}: {e.message}')
 data=load('data/units.json');units=data['units'];rules=load('data/rules.alpha.json');traits=load('data/traits.json')['traits'];world=load('data/world.json')
 byid={u['id']:u for u in units};alpha=[byid[x] for x in rules['alpha_unit_ids'] if x in byid]
 check(len(units)==len(byid)==24,'24 unique units');check(len({u['slug'] for u in units})==24,'unique slugs');check(len({u['ability']['id'] for u in units})==24,'unique skills')
 check(Counter(u['race'] for u in units)==Counter(dict.fromkeys(['human','elf','dwarf','orc','halfling','dragonkin'],4)),'six races x four')
 check(Counter(u['unit_class'] for u in units)==Counter(dict.fromkeys(['guardian','warrior','ranger','rogue','mage','priest'],4)),'six classes x four')
 check(len(set(rules['alpha_unit_ids']))==len(alpha)==24,'24 valid distinct alpha IDs')
 check(Counter(u['race'] for u in alpha)==Counter(dict.fromkeys(['human','elf','dwarf','orc','halfling','dragonkin'],4)),'alpha six races x four')
 check(Counter(u['unit_class'] for u in alpha)==Counter(dict.fromkeys(['guardian','warrior','ranger','rogue','mage','priest'],4)),'alpha six classes x four')
 check({u['id'] for u in alpha}=={u['id'] for u in units if u['production_phase']=='alpha'},'phase/profile agreement')
 check(rules['active_trait_thresholds']==[2,4],'two and four-unit alpha thresholds')
 check({e['effect'] for u in alpha for e in u['ability']['effects']}=={'damage','heal','shield','stun','dash','stat_modifier'},'six effect types covered')
 check(len({u['display_name'].casefold() for u in alpha})==24,'unique short hero names')
 check(all(u['display_name']==u['name'].split()[0] for u in alpha),'short names retain authored identity')
 check(data['balance_version']==rules['balance_version']==load('data/neutrals.json')['balance_version'],'shared balance version')
 check(len(traits)==12 and len({t['id'] for t in traits})==12,'12 unique traits')
 activecounts=Counter(u['race'] for u in alpha)+Counter(u['unit_class'] for u in alpha)
 for t in traits:
  check([x['count'] for x in t['tiers']]==[2,4],f'trait tiers:{t["id"]}')
  check(t['alpha_enabled'] and activecounts[t['id']]>=4,f'alpha trait tier four reachable:{t["id"]}')
 for level,weights in rules['economy']['shop_weights_by_level'].items():
  check(sum(weights.values())==10000,f'shop weights:{level}')
  check(all(any(u['cost']==int(tier) for u in alpha) for tier,w in weights.items() if w),f'nonempty shop tiers:{level}')
 regions={r['id']:r for r in world['regions']};factions={f['id'] for f in world['factions']}
 for r in regions.values():
  check(all(n in regions and r['id'] in regions[n]['neighbors'] for n in r['neighbors']),f'map reciprocity:{r["id"]}')
 for u in units:
  uid=u['id'];s=u['stats'];a=u['ability']
  check(u['region'] in regions and u['faction'] in factions,f'world references:{uid}')
  check(all(isinstance(a[k],int) and a[k]%50==0 for k in ['first_cast_ms','cooldown_ms','cast_ms','recovery_ms','travel_ms']),f'50ms skill alignment:{uid}')
  check(a['cooldown_ms']>a['cast_ms']+a['recovery_ms'],f'cooldown bounds:{uid}')
  check(s['attack_windup_ms']+50<=400,f'max-speed recovery:{uid}')
  skill_errors=ability_errors(a);check(not skill_errors,f'supported skill contract:{uid}')
  errors.extend(uid+': '+err for err in skill_errors)
  check((ROOT/f'docs/heroes/{uid}.md').is_file(),f'dossier exists:{uid}')
  check(len(u['animation_contract']['required_clips'])==7,f'seven clips:{uid}')
  check(all('..' not in path for path in u['asset_paths'].values()),f'asset path safety:{uid}')
  check(len(u['biography'].split())>=40 and all(len(x)>25 for x in u['tactics'].values()),f'authored dossier content:{uid}')
  check(not re.search(r'\b(TODO|TBD|lorem ipsum|repeat similarly)\b',json.dumps(u),re.I),f'no incomplete hero placeholders:{uid}')
 en=load('data/locales/en.json');id_=load('data/locales/id.json')
 check(en.keys()==id_.keys(),'core locale key parity')
 for k in en:check(set(re.findall(r'\{([^}]+)\}',en[k]))==set(re.findall(r'\{([^}]+)\}',id_[k])),f'locale variables:{k}')
 check(len(load('data/bots.json')['bots'])==7,'seven bot personas')
 manifest=load('data/asset_manifest.json')['entries'];check({a['unit_id'] for a in manifest}==set(byid),'asset manifest coverage')
 neutral_issues=neutral_errors(load('data/neutrals.json'),rules);check(not neutral_issues,'neutral definitions, waves and scaling')
 errors.extend(neutral_issues)
 result={'check_count':len(checks),'passed':len(checks)-sum(1 for x in checks if x in errors),'errors':errors,'scope':'specification_and_data_only','game_build_tested':False,'blender_executed':False}
 if '--write-report' in sys.argv:(ROOT/'reports/data_validation.json').write_text(json.dumps(result,indent=2)+'\n')
 if errors:
  print('\n'.join(errors));raise SystemExit(1)
 print(f'PASS: {len(checks)} specification/data checks. No game or Blender execution is implied.')
if __name__=='__main__':main()
