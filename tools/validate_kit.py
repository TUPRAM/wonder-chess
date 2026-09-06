"""Validate authoring/schema consistency, NOT Blender/Unreal execution or game balance."""
from __future__ import annotations
import json,math,re,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def main():
 errors=[];checks=[]
 def check(condition,label):
  checks.append(label)
  if not condition:errors.append(label)
 try:
  from jsonschema import Draft202012Validator
 except ImportError:
  raise SystemExit('Missing jsonschema. Install requirements-tools.txt in a project-local environment; schema validation was NOT RUN.')
 for name in ['units','rules.alpha','traits','world','bots','asset_manifest']:
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
 check(len(set(rules['alpha_unit_ids']))==len(alpha)==12,'12 valid distinct alpha IDs')
 check(Counter(u['race'] for u in alpha)==Counter(dict.fromkeys(['human','elf','dwarf','orc'],3)),'alpha four races x three')
 check(Counter(u['unit_class'] for u in alpha)==Counter(dict.fromkeys(['guardian','warrior','ranger','rogue','mage','priest'],2)),'alpha six classes x two')
 check({u['id'] for u in alpha}=={u['id'] for u in units if u['production_phase']=='alpha'},'phase/profile agreement')
 check(rules['active_trait_thresholds']==[2],'only two-unit alpha thresholds')
 check({u['ability']['effect'] for u in alpha}=={'damage','heal','shield','stun','dash','stat_modifier'},'six effect types covered')
 check(len(traits)==12 and len({t['id'] for t in traits})==12,'12 unique traits')
 activecounts=Counter(u['race'] for u in alpha)+Counter(u['unit_class'] for u in alpha)
 for t in traits:
  check([x['count'] for x in t['tiers']]==[2,4],f'trait tiers:{t["id"]}')
  check(not t['alpha_enabled'] or activecounts[t['id']]>=2,f'alpha trait reachable:{t["id"]}')
 for level,weights in rules['economy']['shop_weights_by_level'].items():
  check(sum(weights.values())==10000,f'shop weights:{level}')
  check(all(any(u['cost']==int(tier) for u in alpha) for tier,w in weights.items() if w),f'nonempty shop tiers:{level}')
 regions={r['id']:r for r in world['regions']};factions={f['id'] for f in world['factions']}
 for r in regions.values():
  check(all(n in regions and r['id'] in regions[n]['neighbors'] for n in r['neighbors']),f'map reciprocity:{r["id"]}')
 for u in units:
  uid=u['id'];s=u['stats'];a=u['ability']
  check(u['region'] in regions and u['faction'] in factions,f'world references:{uid}')
  check(all(isinstance(a[k],int) and a[k]%50==0 for k in ['first_cast_ms','cooldown_ms','cast_ms','recovery_ms','duration_ms','travel_ms']),f'50ms skill alignment:{uid}')
  check(a['cooldown_ms']>a['cast_ms']+a['recovery_ms'],f'cooldown bounds:{uid}')
  check(s['attack_windup_ms']+50<=400,f'max-speed recovery:{uid}')
  check(a['effect']=='damage' or a['damage_type'] is None,f'nondamage type null:{uid}')
  check(a['effect']!='damage' or a['damage_type'] in ['physical','magic','true'],f'damage enum:{uid}')
  check(a['effect'] not in ['dash','stun'] or a['magnitude_by_star']==[0,0,0],f'status magnitude:{uid}')
  check(a['effect']!='dash' or a['max_dash_tiles']>0,f'dash distance:{uid}')
  check(s['attack_damage_type']!='true' or u['production_phase']=='expansion',f'true basic restriction:{uid}')
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
 result={'check_count':len(checks),'passed':len(checks)-sum(1 for x in checks if x in errors),'errors':errors,'scope':'specification_and_data_only','game_build_tested':False,'blender_executed':False}
 if '--write-report' in sys.argv:(ROOT/'reports/data_validation.json').write_text(json.dumps(result,indent=2)+'\n')
 if errors:
  print('\n'.join(errors));raise SystemExit(1)
 print(f'PASS: {len(checks)} specification/data checks. No game or Blender execution is implied.')
if __name__=='__main__':main()
