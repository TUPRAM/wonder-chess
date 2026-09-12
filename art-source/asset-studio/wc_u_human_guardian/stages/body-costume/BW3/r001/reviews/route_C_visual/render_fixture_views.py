"""Read-only saved-camera route C fixture diagnostics; never saves a blend."""
import bpy
import hashlib
import json
from pathlib import Path

out = Path(__file__).resolve().parent
source = out.parents[1] / 'thumb_route_C_final_method_input.blend'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = sha(source)
assert before == '2dad0803a3e8bfd1974b3bf86dbf5377cd462807f02fb9e76f45463205ba2a1d'
assert Path(bpy.data.filepath).resolve() == source
scene = bpy.context.scene
scene.frame_set(25)
rig = bpy.data.objects['BW3_Derived_Rig']
pose = {p.name: [list(row) for row in p.matrix_basis] for p in rig.pose.bones}
for obj in scene.objects:
    if obj.type == 'MESH':
        obj.hide_render = obj.name not in ['BW3_Derived_Glove', 'BW3_Locked_Handle_28mm']
        if not obj.hide_render:
            obj.hide_set(False)
images = []
for view in ['palm', 'side', 'axial', 'back']:
    scene.camera = bpy.data.objects['BW3_cam_' + view]
    path = out / ('C_fixture_' + view + '.png')
    assert not path.exists()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    images.append({'file': str(path), 'sha256': sha(path), 'camera': scene.camera.name,
                   'matrix_world': [list(row) for row in scene.camera.matrix_world],
                   'ortho_scale': scene.camera.data.ortho_scale})
assert pose == {p.name: [list(row) for row in p.matrix_basis] for p in rig.pose.bones}
assert before == sha(source)
record = {'source': str(source), 'source_sha256_before_after': before, 'source_unchanged': True,
          'action': rig.animation_data.action.name, 'frame': 25, 'pose_unchanged': True,
          'camera_and_light_transforms_unchanged': True, 'engine': scene.render.engine,
          'samples': scene.cycles.samples, 'images': images,
          'scope': 'THUMB APPROACH ONLY / OTHER FINGERS OPEN / NOT A GRIP; no source saved'}
(out / 'fixture_views_metadata.json').write_text(json.dumps(record, indent=2) + '\n')
print('C_FIXTURE_VIEWS_DONE')
