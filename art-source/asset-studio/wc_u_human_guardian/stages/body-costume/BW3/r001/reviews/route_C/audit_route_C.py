"""Read-only routeC geometry queries. No fitting, pose overrides, or source saves."""
import bpy
import ast
import hashlib
import json
import math
import re
import time
from pathlib import Path
from collections import Counter
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BW2 = ROOT.parents[1] / 'BW2/r001'
SOURCE = ROOT / 'thumb_route_C_final_method_input.blend'
EXPECTED = '2dad0803a3e8bfd1974b3bf86dbf5377cd462807f02fb9e76f45463205ba2a1d'
assert bpy.app.background and Path(bpy.data.filepath).resolve() == SOURCE.resolve()
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
scene = bpy.data.scenes['BW3_COLLISION_FIRST']
bpy.context.window.scene = scene
rig = bpy.data.objects['BW3_Derived_Rig']
glove = bpy.data.objects['BW3_Derived_Glove']
body = bpy.data.objects['BW3_Derived_Body']
handle = bpy.data.objects['BW3_Locked_Handle_28mm']
rec = json.loads(scene['BW2_hand_contract'])
relative = Matrix(rec['frame_relative_to_wrist'])
deform = {bone.name for bone in rig.data.bones if bone.use_deform}
assert scene.unit_settings.scale_length == 1.0
scene.frame_set(1)
bpy.context.view_layer.update()
expected_groups = {obj.name: [vg.name for vg in obj.vertex_groups] for obj in (body, glove)}
topology_signatures = {}
pad_normals_current = {}
deps = bpy.context.evaluated_depsgraph_get()
reval = rig.evaluated_get(deps)
frame_world = reval.matrix_world @ reval.pose.bones['wrist.R'].matrix @ relative
he = handle.evaluated_get(deps)
mesh = he.to_mesh()
coords = np.array([list(vertex.co) for vertex in mesh.vertices])
local = np.array(frame_world.inverted() @ he.matrix_world)
zmin, zmax = coords[:, 2].min(), coords[:, 2].max()
ends = np.array([[0, 0, zmin], [0, 0, zmax]]) @ local[:3, :3].T + local[:3, 3]
C = ends.mean(axis=0)
axis = ends[1] - ends[0]
half = float(np.linalg.norm(axis) / 2)
axis /= np.linalg.norm(axis)
R = float(np.linalg.norm(coords[:, :2], axis=1).max() * np.linalg.norm(local[:3, 0]))
U = np.array([0., 0., 1.]); U -= np.dot(U, axis) * axis; U /= np.linalg.norm(U)
V = np.cross(axis, U); V /= np.linalg.norm(V)
he.to_mesh_clear()
assert abs(R - rec['radius_m']) < 1e-7
assert abs(half * 2 - rec['endpoint_span_m']) < 1e-6
definitions = []
for file, names in [
    (BW2 / 'integrated-independent/audit_integrated_geometry.py', ('segment_triangle', 'self_audit')),
    (BW2 / 'middle-independent/audit_triangle_interiors.py', ('clip', 'closest_projected', 'has_depth')),
    (ROOT / 'reviews/onset/audit_onset.py', ('label', 'cylinder')),
]:
    tree = ast.parse(file.read_text())
    definitions.extend(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names)
exec(compile(ast.Module(body=definitions, type_ignores=[]), str(__file__), 'exec'), globals())


def geometry(obj, raw):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    rr = rig.evaluated_get(dg)
    F = rr.matrix_world @ rr.pose.bones['wrist.R'].matrix @ relative
    Fi = F.inverted()
    mesh = ev.to_mesh()
    mesh.calc_loop_triangles()
    assert [vg.name for vg in obj.vertex_groups] == expected_groups[obj.name]
    identity = hashlib.sha256(repr([tuple(p.vertices) for p in mesh.polygons]).encode()).hexdigest()
    key = obj.name + ('_raw' if raw else '_eval')
    if key not in topology_signatures: topology_signatures[key] = (len(mesh.vertices), identity)
    assert topology_signatures[key] == (len(mesh.vertices), identity), 'Evaluated vertex/polygon correspondence changed'
    data = np.empty(len(mesh.vertices) * 3)
    mesh.vertices.foreach_get('co', data)
    transform = np.array(Fi @ ev.matrix_world)
    q = data.reshape((-1, 3)) @ transform[:3, :3].T + transform[:3, 3]
    assert np.isfinite(q).all(), 'Nonfinite geometry'
    if obj == glove and not raw:
        normalT = (Fi @ ev.matrix_world).to_3x3().inverted().transposed()
        for digit, patch in rec['patches'].items():
            pad_normals_current[digit] = np.array([list((normalT @ mesh.vertices[i].normal).normalized()) for i in patch['indices']])
    weights = [{obj.vertex_groups[group.group].name: float(group.weight)
                for group in vertex.groups
                if obj.vertex_groups[group.group].name in deform and group.weight > 1e-7}
               for vertex in mesh.vertices]
    # Reuse the checked onset region. Exclude torso/other-hand geometry explicitly.
    selected = {index for index, point in enumerate(q)
                if -.025 < point[1] < .25 and abs(point[0]) < .14 and abs(point[2]) < .15}
    if obj == body and raw:
        gi = obj.vertex_groups["body"].index
        selected &= {v.index for v in mesh.vertices if any(a.group == gi and a.weight > .5 for a in v.groups)}
    tris = [(triangle.index, tuple(triangle.vertices)) for triangle in mesh.loop_triangles
            if all(index in selected for index in triangle.vertices)]
    ev.to_mesh_clear()
    return q, weights, tris


def measure(obj, frame, raw):
    scene.frame_set(math.floor(frame), subframe=frame - math.floor(frame))
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    rr = rig.evaluated_get(dg)
    F = rr.matrix_world @ rr.pose.bones['wrist.R'].matrix @ relative
    he = handle.evaluated_get(dg)
    fixture_transform = np.array(F.inverted() @ he.matrix_world)
    current_ends = np.array([[0, 0, zmin], [0, 0, zmax]]) @ fixture_transform[:3, :3].T + fixture_transform[:3, 3]
    current_center = current_ends.mean(axis=0)
    current_axis = current_ends[1] - current_ends[0]
    current_span = np.linalg.norm(current_axis)
    current_axis /= current_span
    current_radius = float(np.linalg.norm(coords[:, :2], axis=1).max() * np.linalg.norm(fixture_transform[:3, 0]))
    axis_angle = math.degrees(math.acos(float(np.clip(np.dot(axis, current_axis), -1, 1))))
    fixture = {'center_drift_mm': float(np.linalg.norm(current_center-C)*1000), 'endpoint_max_drift_mm': float(np.max(np.linalg.norm(current_ends-ends,axis=1))*1000), 'axis_drift_degrees': axis_angle, 'span_m': float(current_span), 'radius_m': current_radius}
    fixture['within_0_01mm_0_001deg'] = fixture['endpoint_max_drift_mm'] <= .01 and axis_angle <= .001
    assert fixture['within_0_01mm_0_001deg'], 'Actual fixture drift invalidates fixed-coordinate query'
    rig_scale = list(rr.matrix_world.to_scale())
    pose_scale_error = max(abs(float(v)-1.) for pb in rr.pose.bones for v in pb.scale)
    open_error = max(abs(bone.matrix_basis[i][j] - (1 if i == j else 0))
                     for bone in rr.pose.bones if re.match(r'finger[2-5]-.*\.R$', bone.name)
                     for i in range(4) for j in range(4))
    assert open_error < 1e-6, 'Other digits are not actually open'
    states = [(m, m.show_viewport) for m in obj.modifiers]
    if raw:
        for m, flag in states:
            if m.type != "ARMATURE": m.show_viewport = False
    q, weights, tris = geometry(obj, raw)
    for m, flag in states: m.show_viewport = flag
    intersections = self_audit(q, tris)
    categories = Counter()
    examples = {}
    for pair in intersections['pairs']:
        labels = []
        for indices in pair['vertices']:
            average = {}
            for index in indices:
                for name, value in weights[index].items():
                    average[name] = average.get(name, 0.) + value / 3
            labels.append(label(average))
        category = '/'.join(sorted(labels))
        categories[category] += 1
        examples.setdefault(category, pair)
    result = {'frame': frame, 'object': obj.name, 'surface': 'raw_posed_cage' if raw else 'evaluated_level1', 'evaluated_vertices': len(q),
              'selected_hand_triangles': len(tris), 'non_thumb_open_matrix_error': open_error,
              'crossing_pair_count': intersections['confirmed_nonadjacent_transverse_pairs'],
              'categories': dict(categories), 'first_examples': examples,
              'fixture': fixture, 'rig_world_scale': rig_scale, 'maximum_pose_scale_error_from1': pose_scale_error,
              'cylinder': cylinder(q, tris)}
    assert pose_scale_error < 1e-6, 'Unexpected pose scaling'
    if obj == glove and not raw:
        shifted = q - C
        ax = shifted @ axis
        gaps = (np.linalg.norm(shifted - np.outer(ax, axis), axis=1) - R) * 1000
        result['pads'] = {}
        for digit, patch in rec['patches'].items():
            indices = patch['indices']; values = gaps[indices]; axial = ax[indices]
            radial = shifted[indices] - np.outer(axial, axis)
            unitradial = radial / np.maximum(np.linalg.norm(radial,axis=1,keepdims=True),1e-15)
            facing = np.sum(pad_normals_current[digit] * -unitradial, axis=1)
            result['pads'][digit] = {
                'indices': indices, 'count': len(indices), 'min_gap_mm': float(values.min()),
                'median_gap_mm': float(np.median(values)), 'p95_gap_mm': float(np.percentile(values, 95)),
                'max_gap_mm': float(values.max()), 'band_fraction': float(np.mean((values >= -.5) & (values <= 1.))),
                'usable_axial_fraction': float(np.mean(np.abs(axial) <= half - .002)),
                'min_axial_mm': float(axial.min() * 1000), 'max_axial_mm': float(axial.max() * 1000),
                'mean_normal_hand': np.mean(pad_normals_current[digit],axis=0).tolist(),
                'normal_dot_toward_cylinder_min': float(facing.min()), 'normal_dot_toward_cylinder_mean': float(facing.mean()),
            }
    if frame <= 25 or frame % 20 == 0 or frame == 145: print('SAMPLE', obj.name, 'raw' if raw else 'evaluated', frame, 'crossings', result['crossing_pair_count'], result['categories'],
          'min_vertex_mm', result['cylinder']['minimum_vertex_sdf_mm'],
          'deep_triangle', bool(result['cylinder']['deeper_than_0_5mm']), flush=True)
    return result


started = time.perf_counter()
report = {'status': 'RUNNING', 'source': str(SOURCE), 'source_sha256': EXPECTED,
          'action': rig.animation_data.action.name, 'fixture_actual_hand_space': {
              'center': C.tolist(), 'axis': axis.tolist(), 'radius_m': R, 'endpoint_span_m': half * 2},
          'method': 'Reuse checked BW2 triangle-slab and nonadjacent transverse crossing queries; actual derived evaluated and raw posed body/glove. Raw body is restricted to skin group. Thumb authored route only, digits2-5 asserted open. No pose overrides or optimization.',
          'variants': [], 'source_saved': False, 'art_approval': False}
events = {
    'any_self_crossing': lambda row: row['crossing_pair_count'] > 0,
    'palm_thumb_crossing': lambda row: row['categories'].get('palm/thumb', 0) > 0,
    'thumb_other_digit_crossing': lambda row: any('thumb' in key and key not in ('palm/thumb', 'thumb/thumb') and value > 0 for key, value in row['categories'].items()),
    'middle_ring_crossing': lambda row: row['categories'].get('middle/ring', 0) > 0,
    'handle_entry': lambda row: bool(row['cylinder']['entry']),
    'handle_deeper_than0_5mm': lambda row: bool(row['cylinder']['deeper_than_0_5mm']),
}
for obj, raw in ((glove, False), (glove, True), (body, False), (body, True)):
    variant = {'object': obj.name, 'surface': 'raw_posed_cage' if raw else 'evaluated_level1', 'integer_frames': [], 'quarter_frames': [], 'endpoint145': None, 'first_onsets': {}}
    report['variants'].append(variant)
    for frame in range(1, 146):
        variant['integer_frames'].append(measure(obj, frame, raw))
        (OUT / 'route_C_results.json').write_text(json.dumps(report, indent=2) + '\n')
    halves = set()
    for test in events.values():
        first = next((row['frame'] for row in variant['integer_frames'] if test(row)), None)
        if first and first > 1:
            halves.update([first - .75, first - .5, first - .25])
    for frame in sorted(halves):
        variant['quarter_frames'].append(measure(obj, frame, raw))
    variant['endpoint145'] = variant['integer_frames'][-1]
    samples = sorted(variant['integer_frames'] + variant['quarter_frames'], key=lambda row: row['frame'])
    for key, test in events.items():
        first = next((row['frame'] for row in samples if test(row)), None)
        prior = max((row['frame'] for row in samples if first is not None and row['frame'] < first), default=None)
        variant['first_onsets'][key] = {'first_detected_frame': first, 'previous_sample_frame': prior}
    (OUT / 'route_C_results.json').write_text(json.dumps(report, indent=2) + '\n')
report['status'] = 'COMPLETE_READ_ONLY_GEOMETRY_SCREEN'
report['topology_vertex_identity_signatures'] = topology_signatures
report['vertex_group_index_name_tables'] = expected_groups
report['source_sha256_after'] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert report['source_sha256_after'] == EXPECTED
report['elapsed_seconds'] = time.perf_counter() - started
report['limits'] = [
    'Self-crossing pairs exclude shared-vertex triangles and confirm transverse crossings; coplanar overlap/tangency is not classified.',
    'Hand ROI follows the previously checked onset bounds in metric semantic-hand coordinates; unrelated torso/left hand are excluded.',
    'Dominant deform-group labels approximate anatomical regions, not exact web segmentation.',
    'Quarterframe samples narrow detected onset intervals but are not continuous collision detection.',
    'Other digits remain OPEN: this is the thumb approach and carrying study, not a complete grip.',
]
(OUT / 'route_C_results.json').write_text(json.dumps(report, indent=2) + '\n')
print('COMPLETE', report['elapsed_seconds'], [(variant['object'], variant['first_onsets']) for variant in report['variants']], flush=True)
