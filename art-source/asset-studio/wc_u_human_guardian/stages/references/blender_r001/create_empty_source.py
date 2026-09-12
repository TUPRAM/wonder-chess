"""Create a new empty Ada reference workspace. No current asset is read or appended."""
from pathlib import Path
import math
import sys
import bpy

root = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
dest = root / 'ada_reference_empty_source_r001.blend'
assert not dest.exists(), 'Immutable source destination already exists.'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for collection in list(bpy.data.collections):
    bpy.data.collections.remove(collection)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.length_unit = 'METERS'
scene.unit_settings.scale_length = 1
scene.render.fps = 60
scene['asset_id'] = 'wc_u_human_guardian'
scene['status'] = 'empty_reference_workspace_no_model_no_approval'
scene['source_forward'] = '+Y'
scene['source_up'] = '+Z'
scene['anatomical_left'] = '-X'
scene['anatomical_right'] = '+X'
scene['height_m'] = 1.82
scene['geometry_provenance'] = 'Factory-startup empty source; no previous Ada asset opened or reused.'
c = bpy.data.collections.new('AS1_COORDINATE_HELPERS')
scene.collection.children.link(c)
c.hide_select = True
for name, kind, loc, size, rot in [
    ('ORIGIN_GROUND_Z_0', 'CIRCLE', (0, 0, 0), .10, (0, 0, 0)),
    ('HEIGHT_1_82_M', 'SPHERE', (0, 0, 1.82), .025, (0, 0, 0)),
    ('FORWARD_POS_Y', 'SINGLE_ARROW', (0, 0, 0), .5, (-math.pi / 2, 0, 0)),
    ('UP_POS_Z', 'SINGLE_ARROW', (0, 0, 0), 1.82, (0, 0, 0)),
    ('ANATOMICAL_RIGHT_POS_X', 'SINGLE_ARROW', (0, 0, 0), .35, (0, math.pi / 2, 0)),
]:
    ob = bpy.data.objects.new(name, None)
    c.objects.link(ob)
    ob.empty_display_type = kind
    ob.empty_display_size = size
    ob.location = loc
    ob.rotation_euler = rot
    ob.hide_render = True
    ob.hide_select = True
    ob.lock_location = ob.lock_rotation = ob.lock_scale = (True, True, True)
assert all(ob.type == 'EMPTY' for ob in scene.objects)
assert len(bpy.data.meshes) == 0 or not any(me.users for me in bpy.data.meshes)
root.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(dest), check_existing=True)
print('AS1_EMPTY_REFERENCE_SOURCE_SAVED', str(dest))
