"""Generate Unreal-shaped flat rows, a header candidate, and content hash.
No Unreal APIs are called. Actual compile/import/parity tests remain mandatory.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def encoded(x):return json.dumps(x,ensure_ascii=False,indent=2)+'\n'
def unit_row(u):
 s=u['stats']
 return {'Name':u['id'],'UnitId':u['id'],'DisplayName':u['name'],'RaceId':u['race'],'ClassId':u['unit_class'],'AbilityId':u['ability']['id'],'Cost':u['cost'],'HealthCp':s['health_cp'],'AttackDamageCp':s['attack_damage_cp'],'AttackRateMilli':s['attack_rate_milli'],'AttackRangeTiles':s['attack_range_tiles'],'PhysicalArmor':s['physical_armor'],'MagicResistance':s['magic_resistance'],'MovementRateMilli':s['movement_rate_milli'],'AttackDelivery':s['attack_delivery'],'AttackDamageType':s['attack_damage_type'],'AttackWindupMs':s['attack_windup_ms'],'ProjectileTravelMs':s['projectile_travel_ms'],'ProductionPhase':u['production_phase']}
def ability_row(a):
 return {'Name':a['id'],'AbilityId':a['id'],'DisplayName':a['name'],'EffectId':a['effect'],'TargetRule':a['target_rule'],'DamageType':a['damage_type'] or 'none','MagnitudeUnit':a['magnitude_unit'] or 'none','Magnitude1':a['magnitude_by_star'][0],'Magnitude2':a['magnitude_by_star'][1],'Magnitude3':a['magnitude_by_star'][2],'FirstCastMs':a['first_cast_ms'],'CooldownMs':a['cooldown_ms'],'CastMs':a['cast_ms'],'RecoveryMs':a['recovery_ms'],'DurationMs':a['duration_ms'],'RangeTiles':a['range_tiles'],'RadiusTiles':a['radius_tiles'],'MaxDashTiles':a['max_dash_tiles'],'TravelMs':a['travel_ms'],'StatId':a['stat'] or 'none','AllowSelf':a['allow_self'],'TooltipEn':a['tooltip_en'],'TooltipId':a['tooltip_id']}
def header(rows):
 out=['// GENERATED CANDIDATE: not Unreal-compiled by the kit. Verify in the installed engine.','#pragma once','#include "CoreMinimal.h"','#include "Engine/DataTable.h"','#include "WCDataRows.generated.h"','']
 for name,row in rows:
  out+=['USTRUCT(BlueprintType)',f'struct F{name} : public FTableRowBase','{','    GENERATED_BODY()']
  for key,value in row.items():
   if key=='Name':continue
   typ='bool' if isinstance(value,bool) else 'int64' if key in ('HealthCp','AttackDamageCp','Magnitude1','Magnitude2','Magnitude3') else 'int32' if isinstance(value,int) else 'FString' if key in ('DisplayName','TooltipEn','TooltipId') else 'FName'
   init='false' if typ=='bool' else '0' if typ in ('int64','int32') else 'TEXT("")' if typ=='FString' else 'NAME_None'
   out += ['    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")',f'    {typ} {key} = {init};']
  out+=['};','']
 return '\n'.join(out)+'\n'
def outputs():
 units=json.loads((ROOT/'data/units.json').read_text(encoding='utf-8'))['units'];rule=json.loads((ROOT/'data/rules.alpha.json').read_text(encoding='utf-8'))
 alpha=[u for u in units if u['id'] in rule['alpha_unit_ids']]
 out={}
 for suffix,selection in [('Alpha',alpha),('Design24',units)]:
  out[f'generated/unreal/DT_Units_{suffix}.json']=encoded([unit_row(u) for u in selection])
  out[f'generated/unreal/DT_Abilities_{suffix}.json']=encoded([ability_row(u['ability']) for u in selection])
 out['generated/unreal/WCDataRows.h']=header([('WCUnitRow',unit_row(units[0])),('WCAbilityRow',ability_row(units[0]['ability']))])
 digests={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'data').glob('*.json'))}
 out['generated/catalog_digest.json']=encoded({'schema_version':'3.0.0','source_sha256':digests,'combined_sha256':hashlib.sha256(json.dumps(digests,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'engine_import_status':'not_run'})
 return out

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();bad=[]
 out=outputs()
 for rel,text in out.items():
  p=ROOT/rel
  if args.check:
   if not p.exists() or p.read_text(encoding='utf-8')!=text:bad.append(rel)
  else:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
 if bad:raise SystemExit('Stale generated catalog: '+', '.join(bad))
 print(f'{len(out)} catalog artifacts '+('match canonical data' if args.check else 'written; Unreal compile/import NOT RUN'))
if __name__=='__main__':main()
