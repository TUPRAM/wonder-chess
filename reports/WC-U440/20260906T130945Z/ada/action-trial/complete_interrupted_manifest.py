"""Complete observed metadata failure only after exact staged-file verification."""
import hashlib, json, sys
from pathlib import Path
import bpy

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
UID = 'wc_u_human_guardian'
SOURCE = ROOT/f'art-source/heroes/{UID}/{UID}.blend'
EXPORT = ROOT/f'exports/heroes/{UID}'
sys.path.insert(0, str(ROOT/'tools/blender'))
from refine_update_ada import invariants, mesh_geometry_digest, action_curve_digest

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

before = json.loads((OUT/'before-export-manifest.json').read_text())
trial = json.loads((OUT/'result.json').read_text())
assert json.loads((EXPORT/'export_manifest.json').read_text()) == before
assert sha(SOURCE.with_name(UID+'_revision7.blend')) == before['source_sha256']
assert sha(SOURCE) == sha(SOURCE.with_name(UID+'_revision8.blend'))
changed = [f'AN_{UID}_{record["clip"]}.fbx' for record in trial['changed_clips']]
unchanged = [name for name in before['files'] if name not in changed]
for name in changed: assert sha(EXPORT/name) == sha(OUT/'normalized-export'/name)
for name in unchanged: assert sha(EXPORT/name) == before['files'][name]
bpy.ops.wm.open_mainfile(filepath=str(SOURCE.with_name(UID+'_revision7.blend')))
old_rest = invariants(bpy.data.objects['Armature'])['rest_skeleton_sha256']
old_geometry = mesh_geometry_digest()
old_actions = {name: action_curve_digest(bpy.data.actions[f'AN_{UID}_{name}'])
               for name in trial['unchanged_clips']}
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
assert mesh_geometry_digest() == old_geometry
assert invariants(bpy.data.objects['Armature'])['rest_skeleton_sha256'] == old_rest
for name, expected in old_actions.items():
    assert action_curve_digest(bpy.data.actions[f'AN_{UID}_{name}']) == expected
manifest = before.copy()
manifest.update(source_revision=8, animation_revision=8, source_sha256=sha(SOURCE),
    status='update24_motion_refined_exported_pending_Unreal_reimport_and_visual_acceptance',
    animation_update_script_sha256=sha(OUT/'prepare_actions.py'),
    animation_update_export_script_sha256=sha(ROOT/'tools/blender/refine_update_ada.py'),
    animation_update_evidence=OUT.relative_to(ROOT).as_posix())
for record in trial['changed_clips']:
    spec = manifest['clips'][record['clip']]
    assert spec['frames'] == record['frames'] and spec['release_frame'] == record['release_frame']
    spec['support_hand_bake_samples'] = len(range(spec['frames'][0], spec['frames'][1]+1, 3))
    spec['maximum_support_reach_clamp_m'] = record['max_reach_clamp_m']
    spec['sampled_width_m'] = record['max_width_m']
    spec['minimum_eye_above_shield_m'] = record['minimum_eye_above_shield_m']
manifest['files'] = {name: sha(EXPORT/name) for name in before['files']}
(OUT/'normalized-export/export_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
(EXPORT/'export_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
report = {'status':'ACTION_EXPORT_PASS_UNREAL_REIMPORT_PENDING',
    'source':str(SOURCE), 'source_revision':8, 'geometry_revision':7, 'animation_revision':8,
    'source_sha256':sha(SOURCE), 'manifest_sha256':sha(EXPORT/'export_manifest.json'),
    'changed_exports':changed, 'unchanged_exports':unchanged,
    'rest_skeleton_sha256':old_rest, 'geometry_sha256':old_geometry,
    'unchanged_action_sha256':old_actions, 'timings_preserved':True,
    'Unreal_import_tested':False,
    'corrected_failure':'Relative output path rejected by relative_to after copying source/clips; exact staged hashes and preserved revision7 validated before completing manifest. Exporter now resolves output and validates metadata before promotion.'}
(OUT/'export-result.json').write_text(json.dumps(report, indent=2)+'\n')
print('WC_ADA_ACTION_REVISION8_RECOVERY_PASS '+json.dumps(report), flush=True)
