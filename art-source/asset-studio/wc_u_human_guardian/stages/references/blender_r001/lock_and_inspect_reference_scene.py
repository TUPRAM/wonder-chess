"""Lock reference-only objects, inspect actual saved matrices, save a separate result."""
from pathlib import Path
import hashlib
import json
import sys
import bpy
from mathutils import Vector

root = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
dest = root / 'ada_reference_scene_r001.blend'
assert not dest.exists()
spec = json.loads((root / 'calibration_r001.json').read_text())
scene = bpy.context.scene
assert not any(ob.type != 'EMPTY' for ob in scene.objects), 'Reference scene must have no geometry/cameras/rig.'
assert scene.unit_settings.system == 'METRIC' and abs(scene.unit_settings.scale_length - 1) < 1e-8
assert scene['source_forward'] == '+Y' and scene['anatomical_left'] == '-X'
collection = bpy.data.collections['AS1_REFERENCES_R001']
collection.hide_select = True
rows = []
for view in spec['views']:
    ob = bpy.data.objects['AS1_REF_body_' + view['view']]
    assert ob.type == 'EMPTY' and ob.empty_display_type == 'IMAGE'
    ob.hide_render = True
    ob.hide_select = True
    ob.lock_location = ob.lock_rotation = ob.lock_scale = (True, True, True)
    ob.empty_image_side = 'FRONT'
    ob.empty_image_depth = 'BACK'
    ob.color = (1, 1, 1, .55)
    ob.use_empty_image_alpha = True
    ob['authority'] = 'unapproved_generated_construction_candidate'
    ob['projection_accuracy'] = 'not_certified_orthographic'
    ob['crop_rectangle_xyxy'] = view['source_crop_xyxy']
    ob['crown_source_y_px'] = view['crown_source_y_px']
    ob['sole_source_y_px'] = view['sole_source_y_px']
    ob['crown_to_sole_m'] = 1.82
    ob['scale_policy'] = 'one uniform scale per complete native crop; no per-part stretching'
    ob['unresolved_design_conflict'] = 'Generated rear panel has no split; approved document will control split, not these pixels.'
    image_path = Path(bpy.path.abspath(ob.data.filepath))
    image_sha = hashlib.sha256(image_path.read_bytes()).hexdigest()
    assert image_sha == view['image_sha256']
    assert list(ob.data.size) == view['image_dimensions_px']
    for actual_row, expected_row in zip(ob.matrix_world, view['matrix_world']):
        assert all(abs(a - e) < 1e-6 for a, e in zip(actual_row, expected_row))
    x0, y0, _, _ = view['source_crop_xyxy']
    w, h = view['image_dimensions_px']
    mpp = view['meters_per_pixel']
    local_x = (view['centerline_source_x_px'] - x0 - w / 2) * mpp
    ground = ob.matrix_world @ Vector((local_x, (h / 2 - (view['sole_source_y_px'] - y0)) * mpp, 0))
    crown = ob.matrix_world @ Vector((local_x, (h / 2 - (view['crown_source_y_px'] - y0)) * mpp, 0))
    assert abs(ground.z) < 1e-6 and abs(crown.z - 1.82) < 1e-6
    ob.data.pack()
    rows.append({
        'name': ob.name, 'view': view['view'], 'dimensions_px': list(ob.data.size),
        'image_sha256': image_sha, 'matrix_world': [list(r) for r in ob.matrix_world],
        'display_size_m': ob.empty_display_size, 'empty_image_offset': list(ob.empty_image_offset),
        'ground_world': list(ground), 'crown_world': list(crown),
        'hide_render': ob.hide_render, 'hide_select': ob.hide_select,
        'locked_location_rotation_scale': list(ob.lock_location) + list(ob.lock_rotation) + list(ob.lock_scale),
        'image_side': ob.empty_image_side, 'packed_image': bool(ob.data.packed_file)})
scene['status'] = 'reference_placement_executed_owner_reference_approval_pending'
scene['reference_image_revision'] = 'ada_construction_r002.png'
scene['no_orthographic_certification'] = True
scene['rear_split_conflict'] = 'r002 back is only candidate placement; prior selected back plus construction decisions control split.'
view_quat = Vector((0, -1, 0)).to_track_quat('-Z', 'Y')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            region = area.spaces.active.region_3d
            region.view_perspective = 'ORTHO'
            region.view_rotation = view_quat
            region.view_location = (0, 0, .91)
            region.view_distance = 3
bpy.ops.wm.save_as_mainfile(filepath=str(dest), check_existing=True)
report = {
    'status': 'reference_placement_executed_not_art_approval', 'blender_version': bpy.app.version_string,
    'candidate': dest.name, 'candidate_sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
    'scene_unit': 'meter', 'source_forward': '+Y', 'source_up': '+Z',
    'anatomical_left': '-X', 'anatomical_right': '+X',
    'object_count': len(scene.objects), 'image_empty_count': len(rows),
    'mesh_objects': sum(ob.type == 'MESH' for ob in scene.objects),
    'armature_objects': sum(ob.type == 'ARMATURE' for ob in scene.objects),
    'camera_objects': sum(ob.type == 'CAMERA' for ob in scene.objects),
    'references': rows, 'human_approval': False, 'old_ada_source_loaded': False,
    'limitations': ['Generated views are approximate artwork, not certified orthographic projections.',
                   'Crown-to-sole scale is a chosen 1.82 m construction interpretation, not recovered physical data.',
                   'Rear split conflict remains controlled by written decisions and original reference priority.',
                   'No model, rig, texture, motion, export or Unreal integration exists in this scene.']}
(root / 'saved_scene_audit_r001.json').write_text(json.dumps(report, indent=2) + '\n')
print('AS1_LOCKED_REFERENCE_ONLY_SCENE_SAVED', str(dest))
