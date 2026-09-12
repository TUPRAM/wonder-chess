"""Read a frozen BW2 file in background Blender; write a NEW JSON report only.

Prepared but not run against a candidate at authoring time. The candidate must
already be opened by Blender with --background --factory-startup --disable-autoexec.
Arguments after --: --candidate-sha256 HASH --output NEW.json
No operators, saves, exports, pose assignments, or geometry changes are made.
Loading the baseline adds data only to this disposable background process.
"""
import argparse
import datetime
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BODY_ROOT = ROOT.parents[1]
BASELINE = BODY_ROOT / 'BW1/r001/ada_body_costume_checkpoint_r003_ART_REVISE.blend'
BASELINE_HASH = '03829ab406d6bd5e6a1c5f86e045e9f2edc720b05e620e70017667c59be8b3f8'
PRESERVATION = ROOT / 'preservation_before.json'
OLD_ACTION = 'BW1_DIAGNOSTIC_RANGE_ART_REVISE'
RIG = 'BW1_Temporary_Pose_Rig'
GLOVE = 'BW1_Glove_Pair_SourceFit'


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def content_hash(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def array_hash(data, field, width, dtype):
    values = np.empty(len(data) * width, dtype=dtype)
    data.foreach_get(field, values)
    return hashlib.sha256(values.tobytes()).hexdigest()


def matrix(value):
    return [list(row) for row in value]


def json_value(value):
    if hasattr(value, 'to_dict'):
        return {key: json_value(item) for key, item in value.to_dict().items()}
    if hasattr(value, 'to_list'):
        return [json_value(item) for item in value.to_list()]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def properties(owner):
    return {key: json_value(owner[key]) for key in owner.keys()}


def mesh_source(obj):
    """Preserve the exact array checks used by the BW1 successor audits."""
    data = obj.data
    group_names = {group.index: group.name for group in obj.vertex_groups}
    weights = [sorted((group_names[item.group], float(item.weight)) for item in vertex.groups)
               for vertex in data.vertices]
    result = {
        'vertices': len(data.vertices),
        'edges': len(data.edges),
        'polygons': len(data.polygons),
        'coordinate_hash': array_hash(data.vertices, 'co', 3, np.float32),
        'edge_hash': array_hash(data.edges, 'vertices', 2, np.int32),
        'corner_vertex_hash': array_hash(data.loops, 'vertex_index', 1, np.int32),
        'polygon_sizes_hash': array_hash(data.polygons, 'loop_total', 1, np.int32),
        'polygon_material_hash': array_hash(data.polygons, 'material_index', 1, np.int32),
        'weights_hash': content_hash(weights),
        'group_names_in_order': [group.name for group in obj.vertex_groups],
        'uv_hashes': {layer.name: array_hash(layer.data, 'uv', 2, np.float32)
                      for layer in data.uv_layers},
        'point_source_indices': {
            attr.name: array_hash(attr.data, 'value', 1, np.int32)
            for attr in data.attributes
            if attr.domain == 'POINT' and attr.data_type == 'INT' and 'source' in attr.name.lower()
        },
        'shape_keys': [],
    }
    if data.shape_keys:
        result['shape_keys'] = [
            {'name': key.name, 'value': key.value,
             'coordinate_hash': array_hash(key.data, 'co', 3, np.float32),
             'relative_key': key.relative_key.name}
            for key in data.shape_keys.key_blocks
        ]
    return result


def action_source(action):
    """Same curve representation as BW1, including handles and interpolation."""
    curves = []
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    curves.append({
                        'path': curve.data_path, 'array_index': curve.array_index,
                        'extrapolation': curve.extrapolation,
                        'keyframes': [
                            {'co': list(key.co), 'left': list(key.handle_left),
                             'right': list(key.handle_right), 'interpolation': key.interpolation,
                             'easing': key.easing, 'handle_left_type': key.handle_left_type,
                             'handle_right_type': key.handle_right_type}
                            for key in curve.keyframe_points
                        ],
                    })
    return {'frame_range': list(action.frame_range), 'curves': curves}


def modifier_record(modifier, canonical_names=None):
    result = {'name': modifier.name, 'type': modifier.type}
    for prop in modifier.bl_rna.properties:
        key = prop.identifier
        if key in ('rna_type', 'name', 'type') or prop.type == 'COLLECTION' or prop.is_readonly:
            continue
        try:
            value = getattr(modifier, key)
            if prop.type == 'POINTER':
                value = (canonical_names or {}).get(value.as_pointer(), value.name) if value else None
            elif getattr(prop, 'is_array', False):
                value = list(value)
            if isinstance(value, (str, int, float, bool, list)) or value is None:
                result[key] = value
        except (AttributeError, TypeError):
            continue
    return result


def rigid_rest(obj):
    return {
        'matrix_world': matrix(obj.matrix_world),
        'matrix_basis': matrix(obj.matrix_basis),
        'bones': [
            {'name': bone.name, 'parent': bone.parent.name if bone.parent else None,
             'deform': bone.use_deform, 'matrix_local': matrix(bone.matrix_local),
             'head_local': list(bone.head_local), 'tail_local': list(bone.tail_local),
             'inherit_scale': bone.inherit_scale}
            for bone in obj.data.bones
        ],
    }


def hierarchy(obj):
    action = obj.animation_data.action if obj.animation_data else None
    return {
        'name': obj.name, 'type': obj.type,
        'data': obj.data.name if obj.data else None,
        'parent': obj.parent.name if obj.parent else None,
        'parent_type': obj.parent_type, 'parent_bone': obj.parent_bone,
        'matrix_world': matrix(obj.matrix_world), 'matrix_basis': matrix(obj.matrix_basis),
        'matrix_parent_inverse': matrix(obj.matrix_parent_inverse),
        'action': action.name if action else None,
        'constraints': [
            {'name': constraint.name, 'type': constraint.type,
             'target': constraint.target.name if getattr(constraint, 'target', None) else None,
             'subtarget': getattr(constraint, 'subtarget', None),
             'influence': constraint.influence, 'mute': constraint.mute}
            for constraint in obj.constraints
        ],
        'collections': [collection.name for collection in obj.users_collection],
        'properties': properties(obj),
    }


def protected_check(rows):
    result = []
    for item in rows:
        path = Path(item['path'])
        try:
            actual = file_hash(path)
            result.append({'path': str(path), 'expected': item['sha256'],
                           'actual': actual, 'unchanged': actual == item['sha256']})
        except OSError as error:
            result.append({'path': str(path), 'expected': item['sha256'],
                           'unchanged': False, 'error': str(error)})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    output = args.output.resolve()
    if output.parent != Path(__file__).resolve().parent or output.exists():
        raise ValueError('Output must be a new file in this BW2 reviews directory')
    if not bpy.app.background:
        raise RuntimeError('This audit may run only in disposable background Blender')
    candidate = Path(bpy.data.filepath).resolve()
    if candidate.parent != ROOT or candidate.suffix.lower() != '.blend':
        raise ValueError('Open an explicitly frozen BW2/r001 .blend candidate first')
    initial_hash = file_hash(candidate)
    if initial_hash != args.candidate_sha256.lower():
        raise ValueError('Candidate does not match the caller-supplied expected hash')
    if file_hash(BASELINE) != BASELINE_HASH:
        raise ValueError('Protected BW1 r003 baseline hash mismatch')
    incoming = json.loads(PRESERVATION.read_text(encoding='utf-8'))['files']
    protected_before = protected_check(incoming)
    scene = bpy.data.scenes.get('BW2_RIGHT_GRIP')
    if scene is None:
        raise ValueError('BW2_RIGHT_GRIP scene is missing')
    bpy.context.window.scene = scene
    bpy.context.view_layer.update()

    # Snapshot the candidate before baseline loading can introduce suffixed IDs.
    current_objects = {obj.name: obj for obj in bpy.data.objects}
    current_meshes = {name: mesh_source(obj) for name, obj in current_objects.items()
                      if obj.type == 'MESH'}
    current_modifiers = {name: [modifier_record(mod) for mod in obj.modifiers]
                         for name, obj in current_objects.items() if obj.type == 'MESH'}
    current_rig = current_objects.get(RIG)
    current_rest = rigid_rest(current_rig) if current_rig else None
    old_action = bpy.data.actions.get(OLD_ACTION)
    current_action = action_source(old_action) if old_action else None
    old_action_fake_user = old_action.use_fake_user if old_action else False
    action_rows = []
    for action in bpy.data.actions:
        payload = action_source(action)
        action_rows.append({'name': action.name, 'fake_user': action.use_fake_user,
                            'frame_range': payload['frame_range'],
                            'curve_count': len(payload['curves']),
                            'content_sha256': content_hash(payload),
                            'slots': [slot.identifier for slot in action.slots]})
    owned_hierarchy = {name: hierarchy(obj) for name, obj in current_objects.items()
                       if name.startswith('BW2_') or name == RIG}
    pose_rows = [{
        'name': bone.name, 'rotation_mode': bone.rotation_mode,
        'matrix_basis': matrix(bone.matrix_basis), 'pose_matrix': matrix(bone.matrix),
        'head_armature_space': list(bone.head), 'tail_armature_space': list(bone.tail),
        'constraint_count': len(bone.constraints)} for bone in current_rig.pose.bones] if current_rig else []
    bound_action = current_rig.animation_data.action if current_rig and current_rig.animation_data else None
    scene_record = {'name': scene.name, 'properties': properties(scene),
                    'frame': scene.frame_current, 'range': [scene.frame_start, scene.frame_end],
                    'fps': scene.render.fps, 'fps_base': scene.render.fps_base,
                    'camera': scene.camera.name if scene.camera else None,
                    'saved_shading': {'studio_light': scene.display.shading.studio_light,
                                      'studiolight_rotate_z': scene.display.shading.studiolight_rotate_z,
                                      'light': scene.display.shading.light}}
    scene_inventory = [{'name': item.name, 'fake_user': item.use_fake_user,
                        'objects': len(item.objects)} for item in bpy.data.scenes]

    with bpy.data.libraries.load(str(BASELINE), link=False) as (source, target):
        baseline_names = list(source.objects)
        target.objects = list(baseline_names)  # Blender mutates target lists on exit.
        target.actions = [OLD_ACTION] if OLD_ACTION in source.actions else []
    baseline_objects = dict(zip(baseline_names, target.objects))
    canonical_names = {obj.as_pointer(): name for name, obj in baseline_objects.items() if obj}
    comparisons = {}
    modifier_changes = []
    for name, obj in baseline_objects.items():
        if obj is None or obj.type != 'MESH':
            continue
        before = mesh_source(obj)
        after = current_meshes.get(name)
        comparisons[name] = {
            'present': after is not None, 'exact_source_arrays_equal': before == after,
            'changed_fields': [key for key in before if after is None or before[key] != after.get(key)],
            'bw1_r003': before, 'bw2': after,
        }
        prior_mods = [modifier_record(mod, canonical_names) for mod in obj.modifiers]
        new_mods = current_modifiers.get(name, [])
        if len(prior_mods) != len(new_mods):
            modifier_changes.append({'object': name, 'property': 'stack_length',
                                     'before': len(prior_mods), 'after': len(new_mods), 'allowed': False})
        for index, (prior, new) in enumerate(zip(prior_mods, new_mods)):
            for key in sorted(set(prior) | set(new)):
                if prior.get(key) == new.get(key):
                    continue
                allowed = (name == GLOVE and prior.get('type') == new.get('type') == 'SUBSURF'
                           and key == 'levels' and prior.get(key) == 0 and new.get(key) == 1)
                modifier_changes.append({'object': name, 'index': index, 'modifier': prior['name'],
                                         'property': key, 'before': prior.get(key),
                                         'after': new.get(key), 'allowed': allowed})
    baseline_action = action_source(target.actions[0]) if target.actions else None
    baseline_rig = baseline_objects.get(RIG)
    # Rest matrices/endpoints come from bone data, not posed y_axis assumptions.
    baseline_rest = rigid_rest(baseline_rig) if baseline_rig else None
    rest_bones_equal = (current_rest is not None and baseline_rest is not None
                        and current_rest['bones'] == baseline_rest['bones'])
    holder = owned_hierarchy.get('BW2_FixedHandFrame_R')
    handle = owned_hierarchy.get('BW2_Locked_Handle_28mm')
    glove_subsurf = [mod for mod in current_modifiers.get(GLOVE, []) if mod['type'] == 'SUBSURF']
    cloth = {}
    for name, thickness in [('BW1_CoatUpper_Continuous', .006), ('BW1_Leggings', .002)]:
        mods = [mod for mod in current_modifiers.get(name, []) if mod['type'] == 'SOLIDIFY']
        cloth[name] = {'modifiers': mods, 'expected_thickness_m': thickness,
                       'preserved': len(mods) == 1 and math.isclose(mods[0].get('thickness', 0), thickness,
                                                                  rel_tol=0, abs_tol=1e-8)
                       and mods[0].get('use_even_offset') is False and mods[0].get('offset') == -1.0}
    protected_after = protected_check(incoming)
    unique_paths = {str(Path(row['path']).resolve()).casefold() for row in incoming}
    required = {
        'candidate_hash_matches_expected_and_unchanged': file_hash(candidate) == initial_hash,
        'baseline_r003_hash_preserved': file_hash(BASELINE) == BASELINE_HASH,
        'incoming_inventory_contains_exactly62_unique_paths': len(incoming) == len(unique_paths) == 62,
        'all62_incoming_hashes_preserved_before_and_after': all(row['unchanged'] for row in protected_before + protected_after),
        'all_original_baseline_mesh_source_arrays_preserved': bool(comparisons) and all(row['exact_source_arrays_equal'] for row in comparisons.values()),
        'old492_action_curves_and_keys_preserved': current_action is not None and current_action == baseline_action and len(current_action['curves']) == 492,
        'old_action_retained_with_fake_user': old_action_fake_user,
        'rig_rest_bones_preserved': rest_bones_equal,
        'rig_object_basis_preserved': current_rest is not None and baseline_rest is not None and current_rest['matrix_basis'] == baseline_rest['matrix_basis'],
        'only_allowed_original_modifier_change': all(row['allowed'] for row in modifier_changes),
        'glove_viewport_and_render_subdivision_equal1': len(glove_subsurf) == 1 and glove_subsurf[0].get('levels') == glove_subsurf[0].get('render_levels') == 1,
        'coat6mm_and_leggings2mm_even_offset_false_preserved': all(row['preserved'] for row in cloth.values()),
        'new_grip_action_separate_from_old_action': bound_action is not None and bound_action.name.startswith('BW2_') and bound_action.name != OLD_ACTION,
        'holder_parented_once_to_right_wrist': holder is not None and holder['parent'] == RIG and holder['parent_type'] == 'BONE' and holder['parent_bone'] == 'wrist.R' and not holder['constraints'],
        'handle_parented_once_to_holder': handle is not None and handle['parent'] == 'BW2_FixedHandFrame_R' and not handle['constraints'],
        'handle_has_no_second_armature_deformation': handle is not None and not any(mod['type'] == 'ARMATURE' for mod in current_modifiers.get('BW2_Locked_Handle_28mm', [])),
    }
    out = {
        'schema_version': 'bw2.checkpoint_preservation.1',
        'status': 'PRESERVATION_CHECKS_PASS_ART_NOT_APPROVED' if all(required.values()) else 'PRESERVATION_CHECKS_REVISE',
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'candidate': str(candidate), 'candidate_sha256': initial_hash,
        'baseline': str(BASELINE), 'baseline_sha256': BASELINE_HASH,
        'script_sha256': file_hash(__file__), 'blender_version': bpy.app.version_string,
        'preservation_manifest_sha256': file_hash(PRESERVATION), 'required_checks': required,
        'protected_before': protected_before, 'protected_after': protected_after,
        'mesh_comparison_count': len(comparisons), 'mesh_comparisons': comparisons,
        'new_meshes_excluded_from_preservation_comparison': sorted(set(current_meshes) - set(comparisons)),
        'new_mesh_source_records': {name: current_meshes[name] for name in sorted(set(current_meshes) - set(comparisons))},
        'original_modifier_changes': modifier_changes, 'cloth_settings': cloth,
        'scene': scene_record, 'scenes': scene_inventory, 'owned_hierarchy': owned_hierarchy,
        'current_rig_rest': current_rest, 'baseline_rig_rest': baseline_rest,
        'current_rig_pose': pose_rows, 'actions': action_rows,
        'old_action_source_sha256': content_hash(current_action) if current_action else None,
        'bound_grip_action': bound_action.name if bound_action else None,
        'source_saved': False, 'art_approval': False,
        'limitations': [
            'This verifies saved source arrays and declared structural separation, not contact quality or all-frame deformation.',
            'Changed pose matrices and owned BW2 objects/actions are recorded separately; new proxy/glyph meshes are not mistaken for preserved baseline geometry.',
            'Bone rest data use matrix_local/head_local/tail_local; stored pose endpoints are already armature-space.',
            'Hierarchy checks exclude duplicate object constraints on the holder/handle but are not a general dependency-cycle proof.',
            'Independent saves may differ in byte serialization; compare separately against the same baseline and do not require byte identity between work and frozen files.',
        ],
    }
    with output.open('x', encoding='utf-8') as stream:
        json.dump(out, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'output': str(output), 'status': out['status'],
                      'required_checks': required, 'mesh_comparison_count': len(comparisons)}, indent=2))


if __name__ == '__main__':
    main()
