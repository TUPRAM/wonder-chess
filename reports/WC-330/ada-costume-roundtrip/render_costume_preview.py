"""Read-only baseline/changed source preview; no source or FBX saves."""
from pathlib import Path
import hashlib
import json
import bpy
from mathutils import Vector

OUT = Path(__file__).resolve().parent
records = []
for label in ('baseline', 'changed'):
    source = OUT / f'source-{label}.blend'
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source))
    scene = bpy.context.scene
    arm = bpy.data.objects['Armature']
    arm.animation_data_clear()
    for bone in arm.pose.bones:
        bone.location = (0, 0, 0)
        bone.rotation_euler = (0, 0, 0)
        bone.scale = (1, 1, 1)
    scene.frame_set(1)
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 16
    scene.render.resolution_x = 768
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.camera.data.type = 'ORTHO'
    scene.camera.data.ortho_scale = 1.28
    target = Vector((0, 0, 1.30))
    scene.camera.location = (0, 4, 1.45)
    scene.camera.rotation_euler = (target - scene.camera.location).to_track_quat('-Z', 'Y').to_euler()
    image = OUT / f'{label}-breastplate.png'
    scene.render.filepath = str(image)
    bpy.ops.render.render(write_still=True)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    records.append({'source': source.name, 'source_sha256': before,
                    'image': image.name, 'image_sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
                    'source_unchanged': True, 'view': 'front reference-pose torso detail'})
(OUT / 'preview-manifest.json').write_text(json.dumps(records, indent=2) + '\n')
print('WC_ADA_COSTUME_PREVIEW_PASS', flush=True)
