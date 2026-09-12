"""Render preserved BW1 frame 1 with BW2 diagnostic cameras, without saving a blend."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Matrix

ROOT = Path(r'C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume')
BASELINE = ROOT / 'BW1/r001/ada_body_costume_checkpoint_r003_ART_REVISE.blend'
CANDIDATE = ROOT / 'BW2/r001/ada_bw2_grip_checkpoint_r001_ART_REVISE.blend'
OUT = ROOT / 'BW2/r001/baseline-r003'
EXPECTED = {
    str(BASELINE): '03829ab406d6bd5e6a1c5f86e045e9f2edc720b05e620e70017667c59be8b3f8',
    str(CANDIDATE): 'd64d5900317541710d5ef29939d12559e5ecef31777a7e9261158cbccb7a41cf',
}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
before = {p: sha(p) for p in EXPECTED}
assert before == EXPECTED, before
assert Path(bpy.data.filepath).resolve() == CANDIDATE.resolve()
s = bpy.context.scene
views = ['palm', 'side', 'axial']
camera_names = ['BW2_cam_' + n for n in views]
light_names = ['BW2_light_key', 'BW2_light_fill', 'BW2_light_rim']
mat_names = {}
for dst, src in [('BW1_Glove_Pair_SourceFit', 'BW1_Glove_Pair_SourceFit'), ('BW1_Sword_Handle_R', 'BW2_Locked_Handle_28mm')]:
    mat_names[dst] = [m.name if m else None for m in bpy.data.objects[src].data.materials]
object_matrices = {n: [list(row) for row in bpy.data.objects[n].matrix_world] for n in camera_names + light_names}
settings = {
    'engine': s.render.engine,
    'resolution_x': s.render.resolution_x,
    'resolution_y': s.render.resolution_y,
    'resolution_percentage': s.render.resolution_percentage,
    'pixel_aspect_x': s.render.pixel_aspect_x,
    'pixel_aspect_y': s.render.pixel_aspect_y,
    'film_transparent': s.render.film_transparent,
    'samples': s.cycles.samples,
    'use_denoising': s.cycles.use_denoising,
    'use_adaptive_sampling': s.cycles.use_adaptive_sampling,
    'adaptive_threshold': s.cycles.adaptive_threshold,
    'view_transform': s.view_settings.view_transform,
    'look': s.view_settings.look,
    'exposure': s.view_settings.exposure,
    'gamma': s.view_settings.gamma,
    'display_device': s.display_settings.display_device,
    'file_format': s.render.image_settings.file_format,
    'color_mode': s.render.image_settings.color_mode,
    'color_depth': s.render.image_settings.color_depth,
    'compression': s.render.image_settings.compression,
    'world': s.world.name if s.world else None,
}
candidate_record = {'scene': s.name, 'saved_frame': s.frame_current, 'mat_names': mat_names, 'settings': settings, 'object_matrices': object_matrices}

bpy.ops.wm.open_mainfile(filepath=str(BASELINE), load_ui=False, use_scripts=False)
s = bpy.context.scene
rig = bpy.data.objects['BW1_Temporary_Pose_Rig']
action = rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None
saved_frame = s.frame_current
s.frame_set(1)
bpy.context.view_layer.update()
baseline_pose = {p.name: {'rotation_mode': p.rotation_mode, 'matrix_basis': [list(row) for row in p.matrix_basis]} for p in rig.pose.bones if p.name.endswith('.R') and ('finger' in p.name or 'thumb' in p.name or 'wrist' in p.name)}
handle = bpy.data.objects['BW1_Sword_Handle_R']
handle_matrix = [list(row) for row in handle.matrix_world]
handle_dimensions = list(handle.dimensions)
for o in s.objects:
    if o.type == 'MESH':
        o.hide_render = o.name not in mat_names
        if o.name in mat_names:
            o.hide_set(False)
    if o.type == 'LIGHT':
        o.hide_render = True

unique_mats = list(dict.fromkeys(m for values in mat_names.values() for m in values if m))
with bpy.data.libraries.load(str(CANDIDATE), link=False) as (available, appended):
    appended.objects = camera_names + light_names
    appended.materials = unique_mats[:]
    appended.worlds = [settings['world']] if settings['world'] else []
materials = dict(zip(unique_mats, appended.materials))
for name, obj in zip(camera_names + light_names, appended.objects):
    assert obj and obj.type in {'CAMERA', 'LIGHT'}, name
    s.collection.objects.link(obj)
    obj.parent = None
    obj.matrix_world = Matrix(object_matrices[name])
    obj.hide_render = False
    obj.hide_set(False)
for name, names in mat_names.items():
    obj = bpy.data.objects[name]
    obj.data.materials.clear()
    for mat_name in names:
        if mat_name:
            obj.data.materials.append(materials[mat_name])
if appended.worlds:
    s.world = appended.worlds[0]

s.render.engine = settings['engine']
for name in ['resolution_x','resolution_y','resolution_percentage','pixel_aspect_x','pixel_aspect_y','film_transparent']:
    setattr(s.render, name, settings[name])
for name in ['samples','use_denoising','use_adaptive_sampling','adaptive_threshold']:
    setattr(s.cycles, name, settings[name])
for name in ['view_transform','look','exposure','gamma']:
    setattr(s.view_settings, name, settings[name])
s.display_settings.display_device = settings['display_device']
for name in ['file_format','color_mode','color_depth','compression']:
    setattr(s.render.image_settings, name, settings[name])
s.use_nodes = False
s.render.use_border = False
s.render.use_crop_to_border = False
OUT.mkdir(parents=True, exist_ok=True)
renders = []
for view in views:
    s.camera = bpy.data.objects['BW2_cam_' + view]
    path = OUT / ('BW1_r003_frame1_' + view + '.png')
    assert not path.exists(), path
    s.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    renders.append({'view': view, 'path': str(path), 'sha256': sha(path), 'camera_matrix': [list(row) for row in s.camera.matrix_world], 'camera_type': s.camera.data.type, 'ortho_scale': s.camera.data.ortho_scale})
after = {p: sha(p) for p in EXPECTED}
assert after == before
assert action == (rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None)
assert handle_matrix == [list(row) for row in handle.matrix_world]
result = {'status': 'EXECUTED_RENDER_ONLY_NOT_ART_ACCEPTANCE', 'input_hashes_before': before, 'input_hashes_after': after, 'protected_inputs_unchanged': True, 'candidate_camera_light_material_source': candidate_record, 'baseline_scene': s.name, 'baseline_saved_frame': saved_frame, 'rendered_frame': 1, 'baseline_action_retained': action, 'baseline_hand_pose_at_frame1': baseline_pose, 'baseline_handle_world_matrix_unchanged': handle_matrix, 'baseline_handle_dimensions_bu': handle_dimensions, 'visible_mesh_allowlist': list(mat_names), 'renders': renders, 'limits': ['No blend saved; all scene changes are temporary render isolation and diagnostic materials/cameras/lights.', 'Baseline pose and handle placement remain original frame 1; not re-posed to match BW2.', 'Same cameras and lighting do not imply same pose, handle geometry or artistic approval.', 'No geometric registration, warping or image retouching.']}
(OUT / 'capture_metadata.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print('BASELINE_R003_CAPTURE_COMPLETE ' + json.dumps({'renders': len(renders), 'action': action, 'protected_inputs_unchanged': True}))
