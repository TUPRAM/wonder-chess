"""Correct the measured Kesh Move floor contact without touching his other actions."""
import argparse
import json
from pathlib import Path
import shutil
import sys

import bpy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/blender'))
from refine_update_ada import action_curve_digest, invariants, sha, use_clip

parser = argparse.ArgumentParser()
parser.add_argument('--candidate-dir', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
previous, out = args.candidate_dir.resolve(), args.output.resolve()
out.mkdir(exist_ok=False)
for name in ('before-source.blend', 'before-export-manifest.json', 'after-front.png',
             'after-side.png', 'after-back.png', 'after-three-quarter.png'):
    shutil.copy2(previous / name, out / name)
refined = json.loads((previous / 'refinement.json').read_text())
uid = refined['unit_id']
assert uid == 'wc_u_orc_rogue'
assert sha(Path(refined['candidate'])) == refined['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=refined['candidate'])
arm = bpy.data.objects['Armature']
mesh = bpy.data.objects['SK_' + uid]
before = invariants(arm)
unchanged = {action.name: action_curve_digest(action) for action in bpy.data.actions
             if action.name != f'AN_{uid}_Move'}
manifest = json.loads((out / 'before-export-manifest.json').read_text())
start, end = manifest['clips']['Move']['frames']
samples = []
for frame in range(start, end + 1):
    use_clip(arm, 'Move', frame, unit_id=uid)
    evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
    geometry = evaluated.to_mesh()
    try:
        minimum = min((evaluated.matrix_world @ vertex.co).z for vertex in geometry.vertices)
    finally:
        evaluated.to_mesh_clear()
    samples.append((frame, arm.pose.bones['pelvis'].matrix.copy(), max(0, .002 - minimum), minimum))
for frame, matrix, lift, _ in samples:
    use_clip(arm, 'Move', frame, unit_id=uid)
    matrix.translation.z += lift
    pelvis = arm.pose.bones['pelvis']
    pelvis.matrix = matrix
    pelvis.keyframe_insert('location', frame=frame, group='pelvis')
for action in bpy.data.actions:
    if action.name in unchanged:
        assert action_curve_digest(action) == unchanged[action.name]
after = invariants(arm)
assert before['rest_skeleton_sha256'] == after['rest_skeleton_sha256']
use_clip(arm, 'Idle', unit_id=uid)
candidate = out / (uid + '-update24-revision7-contact.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(candidate), check_existing=False)
refined.update(candidate=str(candidate), candidate_sha256=sha(candidate), verified_candidate_invariants=after,
               animation_changes=[{'clip': 'Move', 'kind': 'Measured pelvis support correction',
                                   'frames_baked': len(samples), 'maximum_lift_m': max(sample[2] for sample in samples),
                                   'previous_minimum_mesh_z_m': min(sample[3] for sample in samples)}],
               prior_candidate=str(previous), preserved_unchanged_action_hashes=unchanged,
               contact_correction_script_sha256=sha(Path(__file__)))
(out / 'refinement.json').write_text(json.dumps(refined, indent=2) + '\n')
shutil.copy2(Path(__file__), out / 'executed-contact-fix.py')
print('WC_KESH_MEASURED_MOVE_CORRECTION ' + json.dumps(refined['animation_changes']), flush=True)
