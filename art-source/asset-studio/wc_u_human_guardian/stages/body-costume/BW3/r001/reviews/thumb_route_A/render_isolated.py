"""Read-only render isolation of the exact initial BW3 thumb route; never saves a blend."""
import bpy
import hashlib
import json
from pathlib import Path

ROOT = Path(r'C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW3/r001')
SOURCE = ROOT / 'thumb_route_A_initial.blend'
OUT = ROOT / 'reviews/thumb_route_A'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = sha(SOURCE)
assert Path(bpy.data.filepath).resolve() == SOURCE.resolve()
s = bpy.context.scene
assert s.frame_current == 25
rigs = {o.name: {'matrix_world': [list(row) for row in o.matrix_world], 'action': o.animation_data.action.name if o.animation_data and o.animation_data.action else None, 'pose': {p.name: [list(row) for row in p.matrix_basis] for p in o.pose.bones}} for o in s.objects if o.type == 'ARMATURE'}
output = []
for label, name in [('glove', 'BW3_Derived_Glove'), ('body', 'BW3_Derived_Body')]:
    for o in s.objects:
        if o.type == 'MESH':
            o.hide_render = o.name != name
            if o.name == name:
                o.hide_set(False)
    for view in ['oblique', 'axial', 'side']:
        s.camera = bpy.data.objects['BW3_cam_' + view]
        path = OUT / (label + '_frame25_handle_hidden_' + view + '.png')
        assert not path.exists(), path
        s.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        output.append({'path': str(path), 'sha256': sha(path), 'visible_mesh': name, 'camera': s.camera.name, 'camera_matrix': [list(row) for row in s.camera.matrix_world], 'ortho_scale': s.camera.data.ortho_scale})
after = sha(SOURCE)
assert after == before
for name, record in rigs.items():
    rig = bpy.data.objects[name]
    assert record['action'] == (rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None)
    assert record['pose'] == {p.name: [list(row) for row in p.matrix_basis] for p in rig.pose.bones}
metadata = {'source': str(SOURCE), 'source_hash_before': before, 'source_hash_after': after, 'source_unchanged': True, 'frame': s.frame_current, 'scene': s.name, 'renderer': s.render.engine, 'samples': s.cycles.samples, 'dimensions': [s.render.resolution_x, s.render.resolution_y], 'renders': output, 'rig_pose_unchanged': True, 'blend_saves': 0, 'limits': 'Temporary visibility isolation only. Same saved cameras, lighting, materials and poses. Images alone do not establish collision freedom or completed grip.'}
(OUT / 'capture_metadata.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
print('BW3_A_ISOLATION_COMPLETE ' + json.dumps({'images': len(output), 'source_unchanged': True, 'source_sha256': before}))
