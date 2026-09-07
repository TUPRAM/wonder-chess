"""Render retained Orc candidates at native 60fps using the proven Workbench path."""
import argparse
import json
from pathlib import Path
import shutil
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/blender'))
from refine_update_ada import sha, use_clip
import refine_update_dwarves as review

parser = argparse.ArgumentParser()
parser.add_argument('--unit', choices=('wc_u_orc_warrior', 'wc_u_orc_mage', 'wc_u_orc_rogue'), required=True)
parser.add_argument('--candidate-dir', type=Path, required=True)
parser.add_argument('--review-name', default='workbench-review')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
candidate_dir = args.candidate_dir.resolve()
out = candidate_dir / args.review_name
out.mkdir(exist_ok=False)
for name in ('refinement.json', 'before-source.blend', 'before-export-manifest.json',
             'after-front.png', 'after-side.png', 'after-back.png', 'after-three-quarter.png'):
    shutil.copy2(candidate_dir / name, out / name)
refined = json.loads((out / 'refinement.json').read_text())
assert refined['unit_id'] == args.unit and sha(Path(refined['candidate'])) == refined['candidate_sha256']
unit = next(item for item in json.loads((ROOT / 'data/units.json').read_text(encoding='utf-8'))['units'] if item['id'] == args.unit)
shutil.copy2(Path(__file__), out / 'executed-review.py')
shutil.copy2(ROOT / 'tools/blender/refine_update_dwarves.py', out / 'executed-workbench-helper.py')
bpy.ops.wm.open_mainfile(filepath=refined['candidate'])
review.camera_view(unit, 'three-quarter', 384)
bpy.context.view_layer.update()
camera = bpy.context.scene.camera
inverse = camera.matrix_world.inverted()
arm = bpy.data.objects['Armature']
mesh = bpy.data.objects['SK_' + args.unit]
manifest = json.loads((out / 'before-export-manifest.json').read_text())
extent, evaluated_frames = 0, 0
for clip, spec in manifest['clips'].items():
    for frame in range(spec['frames'][0], spec['frames'][1] + 1):
        use_clip(arm, clip, frame, unit_id=args.unit)
        evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        geometry = evaluated.to_mesh()
        try:
            for vertex in geometry.vertices:
                point = inverse @ (evaluated.matrix_world @ vertex.co)
                extent = max(extent, abs(point.x), abs(point.y))
        finally:
            evaluated.to_mesh_clear()
        evaluated_frames += 1
fitted_scale = extent * 2.16
original_camera_view = review.camera_view
def fitted_camera_view(unit, view, resolution=768):
    original_camera_view(unit, view, resolution)
    if view == 'three-quarter':
        bpy.context.scene.camera.data.ortho_scale = fitted_scale
review.camera_view = fitted_camera_view
(out / 'all-frame-camera-fit.json').write_text(json.dumps({
    'method': 'Project every deformed vertex at every authored frame before rendering',
    'frames_evaluated': evaluated_frames, 'maximum_absolute_projected_extent_m': extent,
    'orthographic_scale_m': fitted_scale, 'padding_multiplier': 1.08}, indent=2) + '\n')
review.audit_and_record(unit, out)
assert sha(Path(refined['candidate'])) == refined['candidate_sha256']
print('WC_ORC_NATIVE_FRAME_REVIEW_RENDERED ' + args.unit, flush=True)
