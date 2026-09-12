"""One-time AS1 Ada intake. Reads canonical definitions, never existing Ada geometry."""
from pathlib import Path
import hashlib
import json
import shutil
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[5]
WORK = ROOT / 'art-source/asset-studio/wc_u_human_guardian'
KIT = ROOT / 'production/asset-studio'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, data):
    target = WORK / path
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

unit = next(x for x in json.loads((ROOT/'data/units.json').read_text(encoding='utf-8'))['units'] if x['id']=='wc_u_human_guardian')
sources = ['data/units.json', 'data/rules.alpha.json', 'docs/MASTER_IMPLEMENTATION_v3.md',
           'docs/updates/2026-09-auto-chess-inspired/MASTER_UPDATE.md', 'docs/BLENDER_PRODUCTION.md',
           'game/Source/WonderChessRuntime/Private/WCBoardPresenter.cpp']
write('stages/brief/canonical_snapshot_r001.json', {
    'captured_utc':datetime.now(timezone.utc).isoformat(), 'unit':unit,
    'source_hashes':{p:sha(ROOT/p) for p in sources},
    'note':'Read-only authoring contract snapshot. Existing asset paths are provenance only; no old mesh, rig, material, texture or animation loaded.',
    'camera':{'source_kind':'current C++ source, not newly executed gameplay', 'normal_board':{
        'projection':'orthographic', 'position_cm':[2450,0,2800], 'rotation_pitch_yaw_roll':[-50,180,0],
        'ortho_width_cm':4300, 'axis_constraint':'MaintainXFOV'},
        'art_review_override':{'position_cm':[2400,0,3100], 'rotation_pitch_yaw_roll':[-52,180,0], 'ortho_width_cm':2300},
        'tile_pitch_cm':200, 'test_resolutions':[[1920,1080],[1280,720]], 'portrait_identity_px':96}
})

copied=[]
for src in sorted((KIT/'examples/ada/reference_inputs').glob('*.png')):
    dest=WORK/'inputs'/src.name
    with dest.open('xb') as stream: stream.write(src.read_bytes())
    copied.append({'path':dest.relative_to(WORK).as_posix(), 'sha256':sha(dest),
        'origin':src.relative_to(ROOT).as_posix(), 'role':'rejected_example_only' if 'rejected' in src.name else 'aesthetic_master_not_geometry'})
shutil.copytree(KIT/'examples/ada/crops', WORK/'inputs/crops')
write('inputs/provenance_r001.json', {'inputs':copied,
    'geometry_source':'new original source to be authored after reference approval', 'old_ada_geometry_reused':False,
    'rights_scope':'User supplied these references for this private project task; no independent copyright clearance claimed.',
    'allowed_generation':'Built-in image generation of task-specific reference candidates, authorized by the requested AS1 pipeline.',
    'external_upload_policy':'No third-party uploads, external API jobs, purchases or public publishing authorized.',
    'crop_note':'11 bundled native crops preserved byte-for-byte; no added detail, no certified orthographic views.'})

parts=[]
def part(pid,parent,kind,symmetry,treatment,policy,refs,dimensions,risk):
    parts.append(dict(id=pid,parent=parent,type=kind,symmetry=symmetry,treatment=treatment,runtime_policy=policy,
        reference_ids=refs,dimensional_relationship=dimensions,risks=risk,owner='Codex root Ada AS1 lane',
        authoring_source='new original editable geometry; existing Ada source prohibited'))
part('body','root','organic','bilateral across local X=0','connected torso and limbs with joint loops','skinned',['construction_turnaround'], '1.82 m floor to crown; one logical tile',['shoulder and hip volume'])
for pid,parent,refs,risk in [('head_surface','neck',['face-primary'],['lid/socket fit','jaw/profile likeness']),('neck','body',['face-primary','torso-layering'],['collar clearance'])]:
    part(pid,parent,'organic','bilateral base; expression deliberate','connected polygon surface with controlled facial planes','skinned',refs,'Adult stylized proportions anchored to supplied face',risk)
for side in ['l','r']:
    for limb,parent in [('arm','body'),('hand','arm_'+side),('leg','body'),('foot','leg_'+side)]:
        part(limb+'_'+side,parent,'organic','bilateral foundation; no forced pose symmetry','deliberate polygon loops','skinned',['construction_turnaround','hands_contact'], 'joint positions fit 1.82 m body; hand fits separate grip',['joint collapse','contact'])
part('hair_main','head_surface','hair','asymmetric swept masses','original mesh clumps','rigid to head',['face-primary','hair-back'],'follows skull; no helmet-like sphere',['hairline likeness'])
part('hair_braid','hair_main','hair','single central braid','interwoven tapered clumps','accessory bones only if tested',['hair-back'],'ends at upper back; clear of collar',['shoulder intersection'])
for pid,parent,refs,shape in [('quilted_coat','body',['torso-layering'],'ivory padded underlayer ending above knee'),('collar_inner','neck',['face-primary'],'ivory padded upright collar'),('collar_outer','neck',['torso-layering'],'short navy inner facing'),('tabard_front','body',['front-panel-candidate'],'navy above-knee pointed front panel'),('tabard_back','body',['back-panel-candidate'],'navy split rear panel with above-knee hem'),('trousers','body',['boot-knee-context'],'brown fitted trousers')]:
    part(pid,parent,'costume','bilateral base','tailored shell and broad folds','skinned; no cloth simulation',refs,shape,['layer clearance','fold deformation'])
for pid,shape in [('breastplate','central sternum ridge and chest planes'),('backplate','fitted rear shell clear of braid')]:
    part(pid,'body','hard_surface','bilateral shell','controlled shell thickness and bevel','rigid regions with tested waist articulation',['torso-layering','back-panel-candidate'],shape,['armor bending','layer intersections'])
for side in ['l','r']:
    for name,parent,shape in [('pauldron','arm_'+side,'three overlapping shaped plates'),('bracer','arm_'+side,'forearm shell with wrist opening'),('glove','hand_'+side,'brown fitted leather five-finger glove'),('knee_guard','leg_'+side,'separate shaped knee shell'),('greave','leg_'+side,'shin shell over leather boot'),('boot','foot_'+side,'thick flat sole and strapped upper')]:
        part(name+'_'+side,parent,'costume' if name in ('glove','boot') else 'hard_surface','paired source; final side-specific clearance', 'purpose-built polygon shells', 'skinned soft parts; rigid armor attachment to be pose-tested',['construction_turnaround','boot-knee-context','torso-layering'],shape,['rigid bending','attachment contact'])
for pid,parent,shape in [('belt','body','one brown waist strap with square buckle'),('belt_buckle','belt','simple square fitting')]:
    part(pid,parent,'costume','local centered','polygon strip or solid fitting','waist-following',['front-panel-candidate'],shape,['tabard attachment'])
for pid,parent,shape in [('shield_shell','hand_l','convex navy rounded-kite shell'),('shield_rim','shield_shell','steel perimeter rim with bevel'),('shield_sun_crest','shield_shell','one shallow gold disk and broad rays'),('shield_grip','shield_shell','leather-wrapped grip in left palm'),('shield_forearm_straps','shield_shell','two brown leather loops on reverse')]:
    part(pid,parent,'equipment','local shield centerline','purpose-built solid/shell','weapon_l rigid attachment candidate',['shield-detail','shield_construction'],'shield below eyes at rest; '+shape,['grip and forearm contact','neighbor occlusion'])
for pid,parent,shape in [('sword_blade','sword_grip','short broad steel blade with center ridge and bevel'),('sword_guard','sword_grip','compact curved crossguard'),('sword_grip','hand_r','leather-wrapped grip sized to closed hand'),('sword_pommel','sword_grip','compact terminal cap')]:
    part(pid,parent,'equipment','local blade axes','purpose-built polygon solid','weapon_r rigid attachment candidate',['sword-detail','hands_contact'],shape,['swing clearance','finger contact'])
write('stages/brief/part_inventory_r001.json',{'asset_id':unit['id'],'status':'reference_candidate_not_approved','parts':parts,
    'axes':{'forward':'+Y','up':'+Z','anatomical_right':'-X','anatomical_left':'+X'},
    'symmetry_plane':'local X=0, explicit origin or mirror object; apply only to paired foundations',
    'source_start':'empty source scene, no old Ada assets appended or imported'})

manifest=json.loads((WORK/'asset.json').read_text())
manifest.update(design_revision='ada_as1_scratch_r001',contract={
    'scope':'art_only_no_gameplay_changes','source_forward':'+Y','source_up':'+Z','authoring_unit':'meter',
    'height_m':unit['height_m'],'gameplay_id':unit['id'],'rig_family_interface':unit['rig_family'],
    'max_candidates_per_stage':2,'max_external_spend':0,'geometry_start':'empty original source; no current Ada reuse',
    'logical_tile_footprint':1,'equipment_handedness':{'shield':'anatomical_left','sword':'anatomical_right'},
    'required_clips':unit['animation_contract']['required_clips'],'sockets':unit['animation_contract']['socket_names'],
    'fps':60,'root_motion':False,'budget':unit['art_budget'],
    'reference_choices':'stages/references/construction_decisions_r001.md',
    'canonical_snapshot':'stages/brief/canonical_snapshot_r001.json',
    'runtime_timing_authority':'data/units.json; copied snapshot is evidence, never independent gameplay authority'},
    rights={'status':'user_supplied_for_private_task_no_independent_clearance', 'external_upload_authorized':False,
       'built_in_reference_generation_authorized':True,'third_party_jobs_authorized':False,'public_publishing_authorized':False},
    notes=['Reference, modeled forms, and final in-game release require actual owner approval.',
      'Illustrated gold trim, braid, tabard, and hidden construction are proposed art amendments pending reference approval; canonical data remains unchanged.',
      'All geometry, rig, textures, and motion will be created from scratch; existing runtime contracts are retained.',
      'The bust is an early method checkpoint and cannot pass the full-hero forms gate.'])
(WORK/'asset.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'workspace':str(WORK),'parts':len(parts),'old_geometry_loaded':False,'source':'new intake only'},indent=2))
