import json, copy, re
from pathlib import Path
R=Path.cwd()
def read(p): return json.loads((R/p).read_text(encoding='utf-8'))
def write(p,x): (R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
version='3.1.0'; balance='alpha_24_v0.4.0'
# The versioned migration replaces effect fields, never creates two authorities.
units=read('data/units.json'); units.update(schema_version=version,balance_version=balance)
effect_keys=['effect','damage_type','magnitude_unit','magnitude_by_star','stat','duration_ms']
brief=(R/'docs/updates/2026-09-auto-chess-inspired/HERO_UPGRADE_BRIEFS.md').read_text(encoding='utf-8')
short_skills={m.group(1):m.group(2) for m in re.finditer(r'\*\*Stable ID:\*\* `([^`]+)`(?:(?!\*\*Stable ID:).)*?\*\*Proposed display skill:\*\* \*\*([^*]+)\*\*',brief,re.S)}
roles={'Defender':'tank','Melee damage':'melee','Ranged damage':'ranged','Spell damage':'caster','Disruption':'control','Support':'support'}
for u in units['units']:
 u['display_name']=u['name'].split()[0];u['role_tags']=[roles[u['role']]];u['production_phase']='alpha'
 if u['display_name'] in ('Mira','Orla'):u['role_tags']=['healer']
 if u['display_name']=='Neris':u['role_tags']=['control']
 a=u['ability'];a['effects']=[{k:a.pop(k) for k in effect_keys}]
 if u['id'] in short_skills:a['name']=short_skills[u['id']]
 if u['display_name']=='Neris':
  a['effects'].insert(0,{'effect':'damage','damage_type':'magic','magnitude_unit':'centipoints','magnitude_by_star':[6000,10800,19440],'stat':None,'duration_ms':0})
  a['tooltip_en']='Deal 60 / 108 / 194.4 magic damage to the current enemy, then stun it for 1.25 seconds if it survives. Mage bonuses affect damage only.'
  a['tooltip_id']='Berikan 60 / 108 / 194,4 kerusakan sihir kepada musuh saat ini, lalu buatnya tertegun selama 1,25 detik jika bertahan. Bonus Mage hanya meningkatkan kerusakan.'
 if u['display_name']=='Finn':
  a['target_rule']='highest_attack_rate_enemy'
  a['tooltip_en']='Reduce the basic attack rate of the in-range enemy with the highest current attack rate. Ties prefer the nearer enemy, then stable identity. Movement and skill cooldowns are unchanged.'
  a['tooltip_id']='Kurangi laju serangan dasar musuh dalam jangkauan dengan laju serangan tertinggi saat ini. Jika sama, pilih yang terdekat, lalu identitas tetap. Gerakan dan jeda skill tidak berubah.'
 if u['display_name']=='Oren':
  a['tooltip_en']='Shield the lowest-health eligible ally in range, including self. Skip an ally whose existing shield would reject the ward; remain ready when no ally can benefit.'
  a['tooltip_id']='Lindungi sekutu yang memenuhi syarat dengan persentase kesehatan terendah dalam jangkauan, termasuk diri sendiri. Lewati perisai yang akan menolak perlindungan ini; tetap siap jika tidak ada penerima yang mendapat manfaat.'
write('data/units.json',units)
rules=read('data/rules.alpha.json');rules.update(schema_version=version,balance_version=balance,profile_id='alpha_24',future_profile='future_changes_require_versioned_profile',active_trait_thresholds=[2,4],alpha_unit_ids=[u['id'] for u in units['units']])
rules['tournament'].update(max_rounds=40,neutral_opening_rounds=3,neutral_every_rounds=5,neutral_opening_failure_damage=0,neutral_failure_damage=2)
rules['tournament']['loss_base_by_stage'][-1]['end']=40
rules['economy']['neutral_win_income']=2
rules['network']['protocol_version']=4
write('data/rules.alpha.json',rules)
for name in ['traits','world','bots','asset_manifest']:
 data=read(f'data/{name}.json');data['schema_version']=version
 if name=='traits':
  for t in data['traits']:t['alpha_enabled']=True
 if name=='asset_manifest':
  for entry in data['entries']:entry['phase']='alpha'
 write(f'data/{name}.json',data)
# Add explicit localized shared labels, preserving existing locale keys.
labels={'menu.heroes':('Heroes','Hero'),'role.tank':('Tank','Pelindung'),'role.melee':('Melee','Jarak dekat'),'role.ranged':('Ranged','Jarak jauh'),'role.caster':('Caster','Penyihir'),'role.support':('Support','Pendukung'),'role.healer':('Healer','Penyembuh'),'role.control':('Control','Pengendali'),'match.neutral':('Monster round','Ronde monster'),'match.neutral_reward':('+{gold} gold at next preparation','+{gold} emas pada persiapan berikutnya'),'gallery.skill':('Skill','Skill'),'gallery.tactics':('Tactics','Taktik'),'gallery.story':('Story','Kisah'),'gallery.appearance':('Gear & Appearance','Perlengkapan & Penampilan'),'gallery.search':('Search heroes','Cari hero'),'gallery.empty':('No heroes match these filters.','Tidak ada hero yang sesuai dengan filter ini.'),'gallery.clear':('Clear filters','Hapus filter')}
for lang,i in [('en',0),('id',1)]:
 data=read(f'data/locales/{lang}.json')
 for k,v in labels.items():data[k]=v[i]
 for u in units['units']:data['hero.'+u['id']+'.name']=u['display_name']
 for trait in read('data/traits.json')['traits']:data['trait.'+trait['id']+'.name']=trait['id'].title()
 write(f'data/locales/{lang}.json',data)
# Closed schemas migrate in step with source; no legacy field survives validation.
for path in (R/'data/schemas').glob('*.schema.json'):
 schema=read(str(path.relative_to(R)))
 if 'schema_version' in schema.get('properties',{}):schema['properties']['schema_version']={'const':version}
 write(str(path.relative_to(R)),schema)
schema=read('data/schemas/units.schema.json');u=schema['properties']['units']['items'];u['properties']['display_name']={'type':'string','minLength':1,'maxLength':24};u['properties']['role_tags']={'type':'array','minItems':1,'maxItems':2,'uniqueItems':True,'items':{'enum':['tank','melee','ranged','caster','support','healer','control']}};u['required']+=['display_name','role_tags'];u['properties']['production_phase']={'const':'alpha'}
a=u['properties']['ability'];effect={'type':'object','properties':{k:a['properties'].pop(k) for k in effect_keys},'required':effect_keys,'additionalProperties':False}
effect['properties']['stat']={'enum':[None,'attack_rate_bonus_bp']};effect['properties']['magnitude_unit']={'enum':[None,'basis_points','centipoints']}
effect['properties']['magnitude_by_star']['items'].update(minimum=-10000,maximum=10000000)
for k in effect_keys:a['required'].remove(k)
a['properties']['effects']={'type':'array','minItems':1,'maxItems':2,'items':effect};a['required'].append('effects');a['properties']['target_rule']['enum'].append('highest_attack_rate_enemy')
a['properties']['max_targets'].update(minimum=1,maximum=12)
u['properties']['stats']['properties']['movement_rate_milli'].update(minimum=1,maximum=10000)
u['properties']['stats']['properties']['attack_damage_cp']['maximum']=10000000
u['properties']['stats']['properties']['physical_armor']['maximum']=10000;u['properties']['stats']['properties']['magic_resistance']['maximum']=10000
schema['title']='Wonder Chess 24 playable heroes schema 3.1';write('data/schemas/units.schema.json',schema)
schema=read('data/schemas/rules.alpha.schema.json')
for k,v in [('neutral_opening_rounds',{'type':'integer','minimum':0,'maximum':40}),('neutral_every_rounds',{'type':'integer','minimum':1,'maximum':40}),('neutral_opening_failure_damage',{'type':'integer','minimum':0,'maximum':60}),('neutral_failure_damage',{'type':'integer','minimum':0,'maximum':60})]:schema['properties']['tournament']['properties'][k]=v;schema['properties']['tournament']['required'].append(k)
schema['properties']['economy']['properties']['neutral_win_income']={'type':'integer','minimum':0,'maximum':100};schema['properties']['economy']['required'].append('neutral_win_income')
schema['properties']['network']['properties']['protocol_version']={'const':4};schema['properties']['network']['required'].append('protocol_version')
schema['properties']['alpha_unit_ids'].update(minItems=24,maxItems=24,uniqueItems=True);schema['properties']['active_trait_thresholds']={'const':[2,4]};schema['properties']['tournament']['properties']['max_rounds'].update(minimum=1,maximum=40)
write('data/schemas/rules.alpha.schema.json',schema)
# Seven creatures and eleven explicit formations. Scale once; skills have no hero-star growth.
raw=[('sprout','Sprout',220,18,'physical',700,1,5,5,1000,250,0),('thorn','Thorn',260,24,'physical',750,3,5,5,900,300,200),('wisp','Wisp',320,22,'magic',650,3,0,15,1000,300,200),('stoneback','Stoneback',700,42,'physical',600,1,25,5,750,350,0),('prowler','Prowler',480,34,'physical',1000,1,10,5,1200,250,0),('sentinel','Sentinel',850,46,'physical',650,1,20,15,800,350,0),('warden','Warden',1400,60,'magic',650,3,20,25,800,350,250)]
# name, selector, effect, magnitude, duration, range, radius, maxdash, maxTargets, damageType, first, cooldown, cast, recovery, travel
skills={'wisp':('Spark','current_enemy','damage',6500,0,3,0,0,1,'magic',3000,8000,350,300,200),'stoneback':('Shell','self','shield',18000,2500,0,0,0,1,None,2000,9000,350,350,0),'prowler':('Bound','farthest_enemy_adjacent','dash',0,0,8,0,4,1,None,2500,10000,350,350,0),'sentinel':('Bell shock','adjacent_enemies','stun',0,750,1,1,0,8,None,3500,10000,450,350,0),'warden':('Beacon burst','current_enemy_area','damage',13000,0,4,1,0,12,'magic',4000,9000,600,400,250)}
creatures=[]
for slug,name,hp,dmg,dtype,rate,rng,armor,mr,movement,windup,travel in raw:
 uid='wc_n_'+slug;ability=None
 if slug in skills:
  sn,sel,eff,mag,duration,reach,radius,dash,targets,damage,first,cd,cast,recovery,st=skills[slug]
  ability={'id':'wc_a_neutral_'+slug,'name':sn,'tooltip_en':sn+': '+eff+' using the declared target and timing.','tooltip_id':sn+': '+eff+' sesuai sasaran dan waktu yang ditetapkan.','target_rule':sel,'first_cast_ms':first,'cooldown_ms':cd,'cast_ms':cast,'radius_tiles':radius,'range_tiles':reach,'allow_self':sel=='self','recovery_ms':recovery,'max_targets':targets,'max_dash_tiles':dash,'travel_ms':st,'interrupt_policy':'cancel_before_release_keep_cooldown','no_target_policy':'remain_ready_continue_basic','effect_snapshot':'release','delivery':'projectile' if st else 'instant','effects':[{'effect':eff,'damage_type':damage,'magnitude_unit':'centipoints' if eff in ('damage','shield') else None,'magnitude_by_star':[mag]*3,'stat':None,'duration_ms':duration}]}
 creatures.append({'id':uid,'display_name':name,'footprint_cells':1,'stats':{'health_cp':hp*100,'attack_damage_cp':dmg*100,'attack_rate_milli':rate,'attack_range_tiles':rng,'physical_armor':armor,'magic_resistance':mr,'movement_rate_milli':movement,'attack_delivery':'melee' if rng==1 else 'ranged','attack_damage_type':dtype,'attack_windup_ms':windup,'projectile_travel_ms':travel},'ability':ability,'asset_paths':{'blender':f'art-source/neutrals/{uid}/{uid}.blend','mesh_fbx':f'exports/neutrals/{uid}/SK_{uid}.fbx','unreal_folder':f'/Game/WonderChess/Neutrals/{uid}','portrait':f'exports/neutrals/{uid}/portrait.png'},'animation_contract':{'required_clips':['Idle','Move','Attack','Hit','Defeat']+(['Active'] if ability else []),'fps':30,'in_place':True,'root_motion':False}})
raw_waves=[(1,'Garden stirrings',10000,10000,[('sprout',3,3),('sprout',4,3)]),(2,'Thorn watch',10000,10000,[('sprout',3,3),('thorn',4,1)]),(3,'Lantern sparks',10000,10000,[('sprout',2,3),('sprout',5,3),('wisp',3,1)]),(5,'Stone shell',10000,10000,[('stoneback',3,3),('thorn',2,1),('thorn',5,1)]),(10,'Prowler path',12000,11000,[('stoneback',3,3),('prowler',1,2),('prowler',6,2),('wisp',3,0)]),(15,'Bell ward',14000,12000,[('sentinel',3,3),('stoneback',4,3),('thorn',1,1),('thorn',6,1)]),(20,'Broken beacon',15000,13000,[('warden',3,1),('stoneback',2,3),('stoneback',5,3)]),(25,'Garden siege',17000,14000,[('sentinel',3,3),('stoneback',4,3),('prowler',1,2),('prowler',6,2),('wisp',2,0)]),(30,'Twin ward',19000,15000,[('sentinel',2,3),('sentinel',5,3),('thorn',1,1),('thorn',6,1),('wisp',3,0)]),(35,'Beacon breach',21000,16000,[('warden',3,1),('sentinel',2,3),('stoneback',5,3),('prowler',1,2),('prowler',6,2)]),(40,'Final ward',23000,17000,[('warden',3,0),('sentinel',2,3),('sentinel',5,3),('prowler',1,2),('prowler',6,2),('wisp',4,1)])]
waves=[{'id':f'wc_wave_{round_:02d}','round':round_,'display_name':name,'hp_scale_bp':hp,'damage_scale_bp':dmg,'reward_policy':'neutral_standard','slots':[{'creature_id':'wc_n_'+slug,'column':col,'row':row} for slug,col,row in slots]} for round_,name,hp,dmg,slots in raw_waves]
write('data/neutrals.json',{'schema_version':version,'balance_version':balance,'creatures':creatures,'waves':waves})
# Embed shared closed authoring shapes to keep standalone offline schema validation.
def obj(props):return {'type':'object','properties':props,'required':list(props),'additionalProperties':False}
def arr(items,lo,hi):return {'type':'array','items':items,'minItems':lo,'maxItems':hi}
def integer(lo,hi):return {'type':'integer','minimum':lo,'maximum':hi}
text={'type':'string','minLength':1}
creature=obj({'id':{'type':'string','pattern':'^wc_n_[a-z]+$'},'display_name':text,'footprint_cells':{'const':1},'stats':copy.deepcopy(u['properties']['stats']),'ability':{'anyOf':[copy.deepcopy(a),{'type':'null'}]},'asset_paths':copy.deepcopy(u['properties']['asset_paths']),'animation_contract':obj({'required_clips':arr({'enum':['Idle','Move','Attack','Hit','Defeat','Active']},5,6),'fps':{'const':30},'in_place':{'const':True},'root_motion':{'const':False}})})
wave=obj({'id':{'type':'string','pattern':'^wc_wave_[0-9]{2}$'},'round':integer(1,40),'display_name':text,'hp_scale_bp':integer(1,100000),'damage_scale_bp':integer(1,100000),'reward_policy':{'const':'neutral_standard'},'slots':arr(obj({'creature_id':{'type':'string','pattern':'^wc_n_[a-z]+$'},'column':integer(0,7),'row':integer(0,3)}),1,6)})
neutral_schema=obj({'schema_version':{'const':version},'balance_version':text,'creatures':arr(creature,7,7),'waves':arr(wave,11,11)});neutral_schema['$schema']='https://json-schema.org/draft/2020-12/schema';neutral_schema['title']='Wonder Chess original neutral creatures and waves 3.1';write('data/schemas/neutrals.schema.json',neutral_schema)
print('Migrated 24 hero definitions, 12 traits, protocol 4, 7 neutral archetypes and 11 waves.')
