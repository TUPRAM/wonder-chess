"""Regenerate dossiers and model briefs from canonical JSON. Standard library only."""
from __future__ import annotations
import argparse,json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'reference'))
from rules_reference import star_value,interval_ticks
ROOT=Path(__file__).resolve().parents[1]
def points(cp):return f'{cp/100:,.2f}'.rstrip('0').rstrip('.')
def render(u):
 s=u['stats'];a=u['ability'];art=u['art'];t=u['tactics'];fps=u['animation_contract']['fps']
 effects=a['effects']
 magnitude=['{}: {}'.format(e['effect'], ' / '.join(f'{v/100:g}%' if e['magnitude_unit']=='basis_points' else points(v) if e['magnitude_unit']=='centipoints' else 'Not applicable' for v in e['magnitude_by_star'])) for e in effects]
 lines=[f'# {u["name"]} — {u["title"]}',f'**{u["race"].title()} · {u["unit_class"].title()} · {u["role"]} · {u["production_phase"].upper()}**',
 f'Stable identity: `{u["id"]}`. Cost: **{u["cost"]} gold**. Rarity label: **{u["rarity"]}**, separate from star level. Production and verification status is recorded separately in reports/implementation_state.json; this generated dossier does not certify an asset or build. All combat values are provisional prototype inputs.',
 f'Quick display name: **{u["display_name"]}**. Informational roles: {", ".join(x.title() for x in u["role_tags"])}. Role tags provide no additional synergy.',
 '## Character and world',u['biography'],f'Home region: `{u["region"]}`. Affiliation: `{u["faction"]}`. Neither supplies a hidden third synergy. Proper names are original proposed fiction, not trademark-clearance claims.',
 '## Appearance and art direction',f'Authored standing height: **{u["height_m"]} m**, excluding raised equipment. Rig family: `{u["rig_family"]}`. One logical tile at every star. All characters are adults, fully clothed and presented as non-graphic heroic fantasy.',]
 for key,title in [('silhouette','Silhouette and proportions'),('face','Face, hair and expression'),('costume','Costume construction'),('palette','Color palette'),('equipment','Equipment and magical focus'),('signature','Three low-resolution identifiers'),('materials','Materials and surface detail'),('back','Back and side-view constraints')]:lines += [f'### {title}',art[key]]
 lines+=['## Combat statistics — without traits or temporary effects','| Property | One star | Two stars | Three stars |','|---|---:|---:|---:|',f'| Health | {points(star_value(s["health_cp"],1))} | {points(star_value(s["health_cp"],2))} | {points(star_value(s["health_cp"],3))} |',f'| Basic attack damage | {points(star_value(s["attack_damage_cp"],1))} | {points(star_value(s["attack_damage_cp"],2))} | {points(star_value(s["attack_damage_cp"],3))} |']
 for name,value in [('Attack delivery',s['attack_delivery']),('Basic damage type',s['attack_damage_type']),('Nominal attacks/second',f'{s["attack_rate_milli"]/1000:.2f}'),('Effective attacks/second at 20 Hz',f'{20/interval_ticks(s["attack_rate_milli"]):.4f}'),('Range in tiles',s['attack_range_tiles']),('Physical armor',s['physical_armor']),('Magic resistance',s['magic_resistance']),('Movement tiles/second',f'{s["movement_rate_milli"]/1000:.2f}')]:lines += [f'| {name} | {value} | {value} | {value} |']
 lines += [f'Nominal basic-attack DPS at one star: **{s["attack_damage_cp"]/100*s["attack_rate_milli"]/1000:.2f}**, before mitigation, movement, stuns, skills, targeting downtime or timing quantization. Basic windup: {s["attack_windup_ms"]} ms; ordinary projectile travel: {s["projectile_travel_ms"]} ms. No hidden critical hits, evasion, lifesteal or mana.',
 '## One active skill',f'### {a["name"]}',f'**Player tooltip:** {a["tooltip_en"]}',f'**Indonesian draft:** {a["tooltip_id"]}',
 '| Contract field | Value |','|---|---|',f'| Stable ability ID | `{a["id"]}` |',f'| Effect / target selector | `{" then ".join(e["effect"] for e in effects)}` / `{a["target_rule"]}` |',f'| One / two / three star magnitude | {"; ".join(magnitude)} |',f'| Damage type | {"; ".join(e["damage_type"] or "Not damaging" for e in effects)} |',f'| First-cast delay / cooldown | {a["first_cast_ms"]/1000:g} s / {a["cooldown_ms"]/1000:g} s |',f'| Windup / recovery | {a["cast_ms"]/1000:g} s / {a["recovery_ms"]/1000:g} s |',f'| Effect duration | {"; ".join(str(e["duration_ms"]/1000)+" s" for e in effects)} |',f'| Skill reach / area radius | {a["range_tiles"]} / {a["radius_tiles"]} tiles |',f'| Can include self | {a["allow_self"]} |',f'| Max dash distance | {a["max_dash_tiles"]} tiles |',f'| Projectile travel | {a["travel_ms"]} ms |',f'| Affected stat | {"; ".join(e["stat"] or "Not applicable" for e in effects)} |',
 'Cooldown starts at successful cast commitment. An interrupted committed cast keeps its cooldown; an unavailable target leaves the ability ready and allows ordinary behavior. Area centers and area recipients are captured at release. Targeted projectiles keep their target ID but never retarget a defeated unit. Dash landing is reserved at commitment and validated before movement. See the rules contract for same-tick ordering, shield replacement and refresh semantics.',
 'Health and basic damage use 1.00/1.80/3.24 star multipliers. Only explicitly authored skill magnitudes vary with stars; stun duration, range, radius, dash distance, cooldown and model footprint do not grow. A status-only skill may deliberately have identical behavior across stars; its owner still gains health and basic damage.',
 '## Positioning and counterplay']
 for k,label in [('placement','Preferred formation'),('partner','Useful partners'),('counter','Counterplay'),('weakness','Practical weakness'),('contrast','Difference from the nearest alternative'),('test','Character-specific acceptance test')]:lines += [f'**{label}.** {t[k]}']
 lines+=['## Animation, effects and sound',art['animation'],f'**Skill effect:** {art["vfx"]}',f'**Sound:** {art["audio"]}',
 f'Author at {fps} FPS, as in-place animations with no locomotion-driven root translation. Required clips: Idle, Move, Attack, Active, Hit, Defeat, Victory. The active release marker is frame {round(a["cast_ms"]*fps/1000)} relative to animation start. Basic release marker is frame {round(s["attack_windup_ms"]*fps/1000)}. These are presentation alignment points, not sources of authoritative damage. Idle begins as a 2-second loop; movement as a 1-second cycle; hit as 0.4 seconds; defeat as 1 second; victory as 1.5 seconds. Adjust clip lengths during animation review without altering gameplay timing.',
 'A defeat uses a brief stagger, kneel or magical dissolve with no injury detail. Stars use UI pips, a subtle trim accent and a brief upgrade flourish; do not produce three separate bodies or enlarge the collision footprint.',
 '## Blender construction and Unreal handoff',
 f'Start from the `{u["rig_family"]}` base or a validated compatible family. Block silhouette before bevels; separate body, costume and equipment into named source collections. Build equipment as decorative fantasy game props, not real functional objects. Author model-space Z up and a consistent forward orientation, then prove conversion with the calibration fixture. Materials use one or two runtime slots and a shared atlas where it preserves identity.',
 f'Targets to profile: at most {u["art_budget"]["lod0_triangles_max"]:,} LOD0 triangles, {u["art_budget"]["texture_size_default"]}-pixel default maps, up to {u["art_budget"]["deform_bones_target_max"]} deforming bones and {u["art_budget"]["skin_influences_max"]} influences per vertex. Lower-detail targets begin near 50% and 25% triangles. These are budgets, not measured performance.',
 'Sockets: `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`. Inspect shoulder, elbow, hip and knee extremes. Use separate rig proportions where needed; matching bone names is not proof of animation compatibility. Selection uses a stable unit proxy, not detailed prop collision. Team affiliation uses base rings/icons in addition to color, never a complete costume recolor.',
 f'**Specific production risk:** {art["risk"]}',
 'Required source/export locations:']
 lines += [f'- {k}: `{v}`' for k,v in u['asset_paths'].items()]
 lines += ['Create separate animation exports and texture maps, a model-derived portrait, front/side/back/three-quarter views, a gameplay-camera screenshot, and an actual Unreal animation capture. Log source/export hashes, skeleton revision, tool versions and import preset. Deliberately change one costume detail, re-export and verify existing material, skeleton, animation and actor references survive.',
 '## Model-sheet generation brief',u['model_sheet_prompt'],
 '## Approval gates',
 'Silhouette passes at 96-pixel preview; costume agrees across all views; all seven clips reviewed; no required missing textures; no unexplained import scale compensation; effect matches declared reach and damage type; portrait agrees with the modeled hero; crowded-board test passes; source revision/reimport is demonstrated. A Python exit code alone does not approve the art.',
 'Canonical source: `data/units.json`. Regenerate this dossier with `python tools/build_documents.py` after data edits. Do not hand-edit a stat table and leave the JSON unchanged.']
 return '\n\n'.join(lines).replace('|\n\n|','|\n|')+'\n'

def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
 units=json.loads((ROOT/'data/units.json').read_text(encoding='utf-8'))['units']
 outputs={}
 for u in units:outputs[f'docs/heroes/{u["id"]}.md']=render(u)
 index=['# Wonder Chess — Complete Character Bible v3','All 24 heroes are fully described. All 24 are selected by the adopted playable profile. Selection is an implementation obligation, not proof of finished assets or a verified game. Numbers are prototype values, not validated balance.','## Master roster','| Hero | Race | Class | Cost | Phase | Active skill |','|---|---|---|---:|---|---|']
 for u in units:index += [f'| {u["name"]} | {u["race"]} | {u["unit_class"]} | {u["cost"]} | {u["production_phase"]} | {u["ability"]["name"]} |']
 index += ['\n---\n'+outputs[f'docs/heroes/{u["id"]}.md'] for u in units]
 outputs['docs/CHARACTER_BIBLE_24.md']='\n'.join(index)+'\n'
 outputs['docs/ALPHA_24_ASSET_BRIEFS.md']='# Wonder Chess — Twenty-four Alpha Hero Asset Briefs\n\nUse the per-hero art, animation and numerical contracts below alongside BLENDER_PRODUCTION.md. No model or render is included in this document.\n\n'+'\n---\n'.join(render(u) for u in units if u['production_phase']=='alpha')
 outputs['docs/ALPHA_12_ASSET_BRIEFS.md']='# Wonder Chess — prior twelve-hero anthology\n\nThe adopted update uses [ALPHA_24_ASSET_BRIEFS.md](ALPHA_24_ASSET_BRIEFS.md). This retained path preserves historical links; it is not a second active roster. Prior source revisions retain the original twelve-hero document.\n'
 world=json.loads((ROOT/'data/world.json').read_text(encoding='utf-8'))
 world_lines=['# '+world['name']+' — Wonder Chess World Brief',world['pitch'],'## Why captains compete',world['tournament_explanation'],'## The threat',world['antagonist']]
 for region in world['regions']:
  world_lines += ['## '+region['name'],'Location: '+region['location']+'. Neighbors: '+', '.join(region['neighbors'])+'.', 'Settlement: '+region['capital']+'. Landmark: '+region['landmark']+'.', 'Everyday life: '+region['everyday_place']+'.', 'Visual identity: '+region['look'],'Culture: '+region['culture'],'What is at stake: '+region['stake']]
  associated=[u['name'] for u in units if u['region']==region['id']]
  world_lines += ['Associated heroes: '+', '.join(associated)+'.']
 world_lines += ['## Mortal organizations']
 for faction in world['factions']:world_lines += ['**'+faction['name']+'** — '+faction['purpose']]
 world_lines += ['This is original proposed fiction, not existing historical or geographical information. The alpha depicts one courtyard; it does not require building all regions as game levels. World names and future website copy must remain consistent with data/world.json.']
 outputs['docs/WORLD_BIBLE.md']='\n\n'.join(world_lines)+'\n'
 bad=[]
 for rel,txt in outputs.items():
  path=ROOT/rel
  if args.check:
   if not path.exists() or path.read_text(encoding='utf-8')!=txt:bad.append(rel)
  else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(txt,encoding='utf-8')
 if bad:raise SystemExit('Stale generated documents: '+', '.join(bad))
 print(f'{len(outputs)} generated documents '+('match canonical data' if args.check else 'written'))
if __name__=='__main__':main()
