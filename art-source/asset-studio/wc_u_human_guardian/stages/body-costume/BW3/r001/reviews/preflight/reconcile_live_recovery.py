"""Read-only BW3 recovery reconciliation against saved BW2; never saves a blend."""
import bpy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BW2 = ROOT.parents[1] / 'BW2/r001'
LIVE = ROOT / 'bw3_preedit_live_recovery.blend'
BASELINE = BW2 / 'ada_bw2_grip_checkpoint_r001_ART_REVISE.blend'
LIVE_HASH = '90b41de2b655069482eada4fcfe05f31c5fddcb6379335414cc1af8e2f3c5502'
BASELINE_HASH = 'd64d5900317541710d5ef29939d12559e5ecef31777a7e9261158cbccb7a41cf'
HELPER = BW2 / 'reviews/audit_bw2_checkpoint.py'
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('bw2_preservation_helpers', HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def differences(before, after, path=''):
    if type(before) != type(after):
        return [{'path': path, 'baseline': before, 'recovery': after}]
    if isinstance(before, dict):
        result = []
        for key in sorted(set(before) | set(after)):
            if key not in before or key not in after:
                result.append({'path': path + '/' + key,
                               'baseline': before.get(key, 'MISSING'),
                               'recovery': after.get(key, 'MISSING')})
            else:
                result += differences(before[key], after[key], path + '/' + key)
        return result
    if isinstance(before, list):
        if len(before) != len(after):
            return [{'path': path + '/length', 'baseline': len(before), 'recovery': len(after)}]
        return [item for index, (a, b) in enumerate(zip(before, after))
                for item in differences(a, b, path + '/' + str(index))]
    return [] if before == after else [{'path': path, 'baseline': before, 'recovery': after}]


def pose_and_world(scene):
    bpy.context.view_layer.update()
    rig = bpy.data.objects['BW1_Temporary_Pose_Rig']
    return {
        'rig_pose': {bone.name: {'basis': helper.matrix(bone.matrix_basis),
                                'matrix': helper.matrix(bone.matrix),
                                'rotation_mode': bone.rotation_mode,
                                'constraints': [(constraint.name, constraint.type, constraint.influence, constraint.mute)
                                                for constraint in bone.constraints]}
                     for bone in rig.pose.bones},
        'object_world': {obj.name: helper.matrix(obj.matrix_world) for obj in scene.objects},
    }


def snapshot(path, expected):
    assert sha(path) == expected
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
    scene = bpy.data.scenes['BW2_RIGHT_GRIP']
    bpy.context.window.scene = scene
    bpy.context.view_layer.update()
    initial_frame = scene.frame_current
    record = {
        'file': str(path), 'hash': expected, 'frame_saved': initial_frame,
        'objects': sorted(bpy.data.objects.keys()), 'scenes': sorted(bpy.data.scenes.keys()),
        'mesh_sources': {obj.name: helper.mesh_source(obj) for obj in bpy.data.objects if obj.type == 'MESH'},
        'modifiers': {obj.name: [helper.modifier_record(mod) for mod in obj.modifiers]
                      for obj in bpy.data.objects if obj.type == 'MESH'},
        'rigs': {obj.name: {'bones': helper.rigid_rest(obj)['bones'],
                           'object_basis': helper.matrix(obj.matrix_basis)}
                 for obj in bpy.data.objects if obj.type == 'ARMATURE'},
        'actions': {action.name: {'payload': helper.action_source(action),
                                  'fake_user': action.use_fake_user,
                                  'slots': [slot.identifier for slot in action.slots]}
                    for action in bpy.data.actions},
        'object_structures': {obj.name: {'parent': obj.parent.name if obj.parent else None,
                                         'parent_type': obj.parent_type, 'parent_bone': obj.parent_bone,
                                         'parent_inverse': helper.matrix(obj.matrix_parent_inverse),
                                         'constraints': helper.hierarchy(obj)['constraints'],
                                         'data_name': obj.data.name if obj.data else None,
                                         'action': obj.animation_data.action.name if obj.animation_data and obj.animation_data.action else None}
                              for obj in bpy.data.objects},
        'cameras': {obj.name: {'type': obj.data.type, 'ortho_scale': obj.data.ortho_scale,
                              'lens': obj.data.lens, 'shift_x': obj.data.shift_x,
                              'shift_y': obj.data.shift_y, 'clip_start': obj.data.clip_start,
                              'clip_end': obj.data.clip_end}
                    for obj in bpy.data.objects if obj.type == 'CAMERA'},
        'scene_state': {'camera': scene.camera.name if scene.camera else None,
                        'range': [scene.frame_start, scene.frame_end],
                        'fps': scene.render.fps, 'fps_base': scene.render.fps_base,
                        'render_engine': scene.render.engine,
                        'resolution': [scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage],
                        'properties': helper.properties(scene)},
        'saved_pose_and_world': pose_and_world(scene),
    }
    record['common_frames'] = {}
    for frame in (9, 37):
        scene.frame_set(frame)
        record['common_frames'][str(frame)] = pose_and_world(scene)
    record['hash_after'] = sha(path)
    return record


assert bpy.app.background
baseline = snapshot(BASELINE, BASELINE_HASH)
recovery = snapshot(LIVE, LIVE_HASH)
fields = ('objects', 'scenes', 'mesh_sources', 'modifiers', 'rigs', 'actions',
          'object_structures', 'cameras', 'scene_state', 'common_frames')
checks = {field + '_exact_equal': baseline[field] == recovery[field] for field in fields}
diff = {field: differences(baseline[field], recovery[field]) for field in fields if not checks[field + '_exact_equal']}
saved_live_pose_matches_baseline_frame = (recovery['saved_pose_and_world'] == baseline['common_frames'].get(str(recovery['frame_saved'])))
geometry_fields = ('mesh_sources', 'modifiers', 'rigs', 'actions', 'object_structures')
geometry_equal = all(checks[field + '_exact_equal'] for field in geometry_fields)
result = {
    'status': 'NO_ASSET_DATA_CHANGES_ONLY_FRAME_OR_UI_STATE' if all(checks.values()) and saved_live_pose_matches_baseline_frame else 'RECONCILIATION_DIFFERENCES_REQUIRE_CLASSIFICATION',
    'baseline': {'file': str(BASELINE), 'sha256': BASELINE_HASH, 'saved_frame': baseline['frame_saved']},
    'recovery': {'file': str(LIVE), 'sha256': LIVE_HASH, 'saved_frame': recovery['frame_saved']},
    'checks': checks, 'core_geometry_rig_action_data_equal': geometry_equal,
    'recovery_saved_pose_matches_baseline_at_same_frame': saved_live_pose_matches_baseline_frame,
    'differences': diff,
    'mesh_object_count': len(baseline['mesh_sources']),
    'action_curve_counts': {name: len(value['payload']['curves']) for name, value in baseline['actions'].items()},
    'source_hashes_after': {'baseline': sha(BASELINE), 'recovery': sha(LIVE), 'helper': sha(HELPER)},
    'sources_unchanged': sha(BASELINE) == BASELINE_HASH and sha(LIVE) == LIVE_HASH,
    'source_saved': False, 'blender_version': bpy.app.version_string,
    'method': 'Fresh saved-file opens; exact indexed source-array/action/key/modifier/rest-rig comparison, with bone/object pose evaluated at common frames9 and37 to distinguish frame motion from source changes. UI screens/layouts are not treated as asset geometry.',
    'limitation': 'This reconciles what the recovery blend serialized. Unsaved changes that Blender did not serialize cannot be reconstructed from it. No art or collision acceptance is produced.'}
assert result['sources_unchanged']
with (HERE / 'live_recovery_reconciliation.json').open('x', encoding='utf-8') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
for label, data in [('saved_baseline', baseline), ('live_recovery', recovery)]:
    with (HERE / (label + '_semantic_snapshot.json')).open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')
print(json.dumps({key: value for key, value in result.items() if key != 'differences'}, indent=2))
print('DIFFERENCES', json.dumps(diff))
