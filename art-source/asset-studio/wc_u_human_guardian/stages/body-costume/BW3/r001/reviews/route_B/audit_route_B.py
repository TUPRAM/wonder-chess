"""Read-only routeB geometry queries. No fitting, pose overrides, or source saves."""
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
from mathutils import Matrix
from mathutils.bvhtree import BVHTree

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BW2 = ROOT.parents[1] / 'BW2/r001'
SOURCE = ROOT / 'thumb_route_B_clearance.blend'
EXPECTED = 'd6ea683f2224a06a63786bc0c3349c3acd22e71e568e48ec2ddcfd21704d3556'
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
    data = np.empty(len(mesh.vertices) * 3)
    mesh.vertices.foreach_get('co', data)
    transform = np.array(Fi @ ev.matrix_world)
    q = data.reshape((-1, 3)) @ transform[:3, :3].T + transform[:3, 3]
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
              'cylinder': cylinder(q, tris)}
    if obj == glove and not raw:
        shifted = q - C
        ax = shifted @ axis
        gaps = (np.linalg.norm(shifted - np.outer(ax, axis), axis=1) - R) * 1000
        result['pads'] = {}
        for digit, patch in rec['patches'].items():
            indices = patch['indices']; values = gaps[indices]; axial = ax[indices]
            result['pads'][digit] = {
                'indices': indices, 'count': len(indices), 'min_gap_mm': float(values.min()),
                'median_gap_mm': float(np.median(values)), 'p95_gap_mm': float(np.percentile(values, 95)),
                'max_gap_mm': float(values.max()), 'band_fraction': float(np.mean((values >= -.5) & (values <= 1.))),
                'usable_axial_fraction': float(np.mean(np.abs(axial) <= half - .002)),
                'min_axial_mm': float(axial.min() * 1000), 'max_axial_mm': float(axial.max() * 1000),
            }
    print('SAMPLE', obj.name, 'raw' if raw else 'evaluated', frame, 'crossings', result['crossing_pair_count'], result['categories'],
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
    variant = {'object': obj.name, 'surface': 'raw_posed_cage' if raw else 'evaluated_level1', 'integer_frames': [], 'half_frames': [], 'endpoint145': None, 'first_onsets': {}}
    report['variants'].append(variant)
    for frame in range(1, 26):
        variant['integer_frames'].append(measure(obj, frame, raw))
        (OUT / 'route_B_results.json').write_text(json.dumps(report, indent=2) + '\n')
    halves = set()
    for test in events.values():
        first = next((row['frame'] for row in variant['integer_frames'] if test(row)), None)
        if first and first > 1:
            halves.add(first - .5)
    for frame in sorted(halves):
        variant['half_frames'].append(measure(obj, frame, raw))
    variant['endpoint145'] = measure(obj, 145, raw)
    samples = sorted(variant['integer_frames'] + variant['half_frames'], key=lambda row: row['frame'])
    for key, test in events.items():
        first = next((row['frame'] for row in samples if test(row)), None)
        prior = max((row['frame'] for row in samples if first is not None and row['frame'] < first), default=None)
        variant['first_onsets'][key] = {'first_detected_frame': first, 'previous_sample_frame': prior}
    (OUT / 'route_B_results.json').write_text(json.dumps(report, indent=2) + '\n')
report['status'] = 'COMPLETE_READ_ONLY_GEOMETRY_SCREEN'
report['source_sha256_after'] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert report['source_sha256_after'] == EXPECTED
report['elapsed_seconds'] = time.perf_counter() - started
report['limits'] = [
    'Self-crossing pairs exclude shared-vertex triangles and confirm transverse crossings; coplanar overlap/tangency is not classified.',
    'Hand ROI follows the previously checked onset bounds in metric semantic-hand coordinates; unrelated torso/left hand are excluded.',
    'Dominant deform-group labels approximate anatomical regions, not exact web segmentation.',
    'Half-frame samples narrow detected onset intervals but are not continuous collision detection.',
    'Open non-thumb pads are reported for context and are not required to grip; persistent collision is still a defect.',
]
(OUT / 'route_B_results.json').write_text(json.dumps(report, indent=2) + '\n')
print('COMPLETE', report['elapsed_seconds'], [(variant['object'], variant['first_onsets']) for variant in report['variants']], flush=True)
