"""Read canonical Ada in disposable background Blender; never save source data."""
import bpy
import datetime
import hashlib
import json
from pathlib import Path
import re

import numpy as np

OUT = Path(__file__).resolve().parent
SOURCE = Path(bpy.data.filepath)
EXPECTED = '54f04b8f28fd819eb22b7a4f6c8051484c6466513e6cd43d419c835b67d950b3'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mat(value):
    return [list(row) for row in value]


def curves(action):
    return [curve for layer in action.layers for strip in layer.strips
            for bag in strip.channelbags for curve in bag.fcurves]


def driver_paths(owner):
    ad = owner.animation_data
    return [d.data_path for d in ad.drivers] if ad else []


def xyz(mesh):
    values = np.empty(len(mesh.vertices)*3, dtype=np.float32)
    mesh.vertices.foreach_get('co', values)
    return values.reshape(-1, 3)


before = sha(SOURCE)
assert before == EXPECTED, before
rigs = [o for o in bpy.data.objects if o.type == 'ARMATURE']
assert len(rigs) == 1
rig = rigs[0]
scene = bpy.context.scene
rig.animation_data_create()
for track in rig.animation_data.nla_tracks:
    track.mute = True
meshes = [o for o in bpy.data.objects if o.type == 'MESH'
          and any(m.type == 'ARMATURE' and m.object == rig for m in o.modifiers)]
report = {
    'status': 'READ_ONLY_AUTHORED_SOURCE_INSPECTION_NOT_RUNTIME_VERIFICATION',
    'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'source': str(SOURCE), 'source_sha256_before': before,
    'blender_version': bpy.app.version_string,
    'fps': scene.render.fps, 'fps_base': scene.render.fps_base,
    'rig': rig.name, 'rig_world_matrix': mat(rig.matrix_world),
    'rig_bones': [{'name': b.name, 'parent': b.parent.name if b.parent else None,
                   'rest_matrix': mat(b.matrix_local), 'deform': b.use_deform}
                  for b in rig.data.bones],
    'digit_bones': [b.name for b in rig.data.bones if re.search(r'finger|thumb|digit', b.name, re.I)],
    'object_drivers': {o.name: driver_paths(o) for o in bpy.data.objects if driver_paths(o)},
    'pose_constraints': {p.name: [{'name': c.name, 'type': c.type} for c in p.constraints]
                         for p in rig.pose.bones if p.constraints},
    'meshes': {}, 'actions': {}, 'sample_interval_frames': .5,
    'source_saved': False, 'live_session_accessed': False,
}
selected = {}
for obj in meshes:
    groups = {g.index: g.name for g in obj.vertex_groups}
    right = [v.index for v in obj.data.vertices
             if [(groups[g.group], g.weight) for g in v.groups if g.weight > 1e-6] == [('hand_r', 1.0)]]
    left = [v.index for v in obj.data.vertices
            if [(groups[g.group], g.weight) for g in v.groups if g.weight > 1e-6] == [('hand_l', 1.0)]]
    selected[obj.name] = {'r': np.array(right), 'l': np.array(left)}
    adjacency = [set() for _ in obj.data.vertices]
    for edge in obj.data.edges:
        a, b = edge.vertices
        adjacency[a].add(b)
        adjacency[b].add(a)
    todo = set(range(len(adjacency)))
    parts = []
    while todo:
        stack = [todo.pop()]
        part = []
        while stack:
            i = stack.pop()
            part.append(i)
            neighbors = adjacency[i] & todo
            todo.difference_update(neighbors)
            stack.extend(neighbors)
        labels = sorted({groups[g.group] for i in part for g in obj.data.vertices[i].groups if g.weight > 1e-6})
        if labels in (['hand_r'], ['hand_l']):
            points = np.array([obj.data.vertices[i].co[:] for i in part])
            parts.append({'indices': sorted(part), 'vertex_count': len(part), 'groups': labels,
                          'bounds_min_source_m': points.min(axis=0).tolist(),
                          'bounds_max_source_m': points.max(axis=0).tolist()})
    report['meshes'][obj.name] = {
        'vertices': len(obj.data.vertices), 'polygons': len(obj.data.polygons),
        'shape_keys': [k.name for k in obj.data.shape_keys.key_blocks] if obj.data.shape_keys else [],
        'shape_key_drivers': driver_paths(obj.data.shape_keys) if obj.data.shape_keys else [],
        'modifiers': [{'name': m.name, 'type': m.type,
                       'show_viewport': m.show_viewport, 'show_render': m.show_render}
                      for m in obj.modifiers],
        'rigid_hand_vertices': {'right': len(right), 'left': len(left)},
        'single_hand_weighted_components': parts,
    }

for clip in ('Idle', 'Move', 'Attack', 'Active', 'Hit', 'Defeat', 'Victory'):
    action = bpy.data.actions[f'AN_wc_u_human_guardian_{clip}']
    rig.animation_data.action = action
    if action.slots:
        rig.animation_data.action_slot = action.slots[0]
    fc = curves(action)
    start, end = action.frame_range
    paths = sorted({c.data_path for c in fc})
    data = {
        'action': action.name, 'frames': [start, end],
        'duration_seconds': (end-start)*scene.render.fps_base/scene.render.fps,
        'curve_count': len(fc), 'paths': paths,
        'non_bone_paths': [p for p in paths if not p.startswith('pose.bones[')],
        'digit_or_morph_paths': [p for p in paths if re.search(r'finger|thumb|digit|key_blocks', p, re.I)],
        'weapon_curves': [{'path': c.data_path, 'axis': c.array_index,
                           'key_value_min': min(k.co.y for k in c.keyframe_points),
                           'key_value_max': max(k.co.y for k in c.keyframe_points)}
                          for c in fc if 'weapon_' in c.data_path],
        'sample_count': 0, 'weapon_hand_relative_max_matrix_delta': {'r': 0.0, 'l': 0.0},
        'rigid_hand_vertex_max_delta_in_hand_frame_m': {
            o.name: {'r': 0.0, 'l': 0.0} for o in meshes},
    }
    first_transforms = {}
    first_points = {}
    for step in range(round((end-start)*2)+1):
        frame = start + step*.5
        scene.frame_set(int(frame), subframe=frame-int(frame))
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        rig_eval = rig.evaluated_get(depsgraph)
        for side in ('r', 'l'):
            hand_world = rig_eval.matrix_world @ rig_eval.pose.bones[f'hand_{side}'].matrix
            relative = np.array(hand_world.inverted() @ rig_eval.matrix_world @ rig_eval.pose.bones[f'weapon_{side}'].matrix)
            if side not in first_transforms:
                first_transforms[side] = relative
                data[f'weapon_{side}_relative_to_hand_at_first_frame'] = relative.tolist()
            data['weapon_hand_relative_max_matrix_delta'][side] = max(
                data['weapon_hand_relative_max_matrix_delta'][side],
                float(np.max(np.abs(relative-first_transforms[side]))))
        for obj in meshes:
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            try:
                assert len(mesh.vertices) == len(obj.data.vertices), (obj.name, len(mesh.vertices))
                points = xyz(mesh)
                for side in ('r', 'l'):
                    indices = selected[obj.name][side]
                    if not len(indices):
                        continue
                    transform = np.array((rig_eval.matrix_world @ rig_eval.pose.bones[f'hand_{side}'].matrix).inverted() @ evaluated.matrix_world)
                    hand_points = points[indices] @ transform[:3, :3].T + transform[:3, 3]
                    key = (obj.name, side)
                    if key not in first_points:
                        first_points[key] = hand_points
                    delta = float(np.max(np.linalg.norm(hand_points-first_points[key], axis=1)))
                    data['rigid_hand_vertex_max_delta_in_hand_frame_m'][obj.name][side] = max(
                        data['rigid_hand_vertex_max_delta_in_hand_frame_m'][obj.name][side], delta)
            finally:
                evaluated.to_mesh_clear()
        data['sample_count'] += 1
    report['actions'][clip] = data

report['all_other_action_paths'] = {
    a.name: sorted({c.data_path for c in curves(a)})
    for a in bpy.data.actions if a.name not in [v['action'] for v in report['actions'].values()]}
report['source_sha256_after'] = sha(SOURCE)
report['source_preserved'] = report['source_sha256_after'] == before
assert report['source_preserved']
target = OUT / 'actual_game_grip_source_audit.json'
assert not target.exists(), target
target.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'report': str(target), 'bone_count': len(rig.data.bones),
                  'digit_bones': report['digit_bones'], 'meshes': list(report['meshes']),
                  'clips': {n: {'samples': v['sample_count'],
                                'weapon_relative_delta': v['weapon_hand_relative_max_matrix_delta'],
                                'hand_vertex_delta_m': v['rigid_hand_vertex_max_delta_in_hand_frame_m']}
                            for n, v in report['actions'].items()},
                  'source_preserved': report['source_preserved']}, indent=2))
