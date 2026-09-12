"""Read-only saved-file evaluation of BW2 carry; no geometry, pose, or source saves."""
import bpy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
from mathutils import Vector

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
SOURCE = ROOT / 'grip_carry_diagnostic_input.blend'
EXPECTED = '4103457fe00a2b1ebe5477d3d8e633e0985f4b0fef8ea16cc820b51c04e4f224'
PROJECT = ROOT.parents[6]
HELPER = PROJECT / 'production/asset-studio/supplements/BW2/tools/contact_math.py'
HELPER_HASH = 'df6467f1f4beb341f8e2e1c515c9287af98685866eaa38fb789b76101c0f017d'
OUTPUT = OUT / 'carry_contact_measurements.json'


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def preservation():
    incoming = json.loads((ROOT / 'preservation_before.json').read_text())['files']
    rows = []
    for row in incoming:
        actual = sha(row['path'])
        rows.append({'path': row['path'], 'expected': row['sha256'],
                     'actual': actual, 'unchanged': actual == row['sha256']})
    return rows


def coordinates(mesh):
    result = np.empty(len(mesh.vertices) * 3, dtype=np.float64)
    mesh.vertices.foreach_get('co', result)
    return result.reshape((-1, 3))


def world_points(points, transform, metres):
    transform = np.array(transform, dtype=np.float64)
    return (points @ transform[:3, :3].T + transform[:3, 3]) * metres


def matrix_metres(transform, metres):
    result = np.array(transform, dtype=np.float64)
    result[:3, 3] *= metres
    return result


def polar_rotation(matrix3):
    left, singular, right = np.linalg.svd(matrix3)
    rotation = left @ right
    if np.linalg.det(rotation) <= 0:
        raise ValueError('Unexpected reflected transform')
    return rotation, singular


def drift(current, baseline, parent_scale):
    relative = np.linalg.inv(baseline) @ current
    rotation, singular = polar_rotation(relative[:3, :3])
    skew = np.array([rotation[2, 1] - rotation[1, 2],
                     rotation[0, 2] - rotation[2, 0],
                     rotation[1, 0] - rotation[0, 1]]) / 2
    angle = math.degrees(math.atan2(float(np.linalg.norm(skew)),
                                   float((np.trace(rotation) - 1) / 2)))
    return {'translation_mm': float(np.linalg.norm(current[:3, 3] - baseline[:3, 3]) * parent_scale * 1000),
            'rotation_deg': angle, 'affine_max_element_delta': float(np.abs(current - baseline).max()),
            'relative_scale_singular_values': singular.tolist()}


assert bpy.app.background
assert Path(bpy.data.filepath).resolve() == SOURCE.resolve()
assert sha(SOURCE) == EXPECTED
assert sha(HELPER) == HELPER_HASH
assert not OUTPUT.exists()
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('bw2_contact_math_measured', HELPER)
contact = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = contact
spec.loader.exec_module(contact)
before = preservation()
assert len(before) == 62 and all(row['unchanged'] for row in before)
scene = bpy.data.scenes['BW2_RIGHT_GRIP']
bpy.context.window.scene = scene
rig = bpy.data.objects['BW1_Temporary_Pose_Rig']
glove = bpy.data.objects['BW1_Glove_Pair_SourceFit']
holder = bpy.data.objects['BW2_FixedHandFrame_R']
handle = bpy.data.objects['BW2_Locked_Handle_28mm']
contract = json.loads(scene['BW2_hand_contract'])
carry = json.loads(scene['BW2_carry_spec'])
assert carry['held_frames'] == [25, 145]
assert scene.unit_settings.system == 'METRIC'
metres = float(scene.unit_settings.scale_length)
assert metres == 1.0, 'Expected verified BW2 metre convention; recheck measurements before conversion'
patches = {str(key): list(value['indices']) for key, value in contract['patches'].items()}
assert set(patches) == {'1', '2', '3', '4', '5'}
digit_names = {'1': 'thumb', '2': 'index', '3': 'middle', '4': 'ring', '5': 'little'}
scene.frame_set(1)
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
initial = glove.evaluated_get(deps).to_mesh()
expected_count = int(scene['BW2_patch_eval_count'])
assert len(initial.vertices) == expected_count
adjacency = [[] for _ in initial.vertices]
for edge in initial.edges:
    a, b = edge.vertices
    adjacency[a].append(b)
    adjacency[b].append(a)
pad_ids = set(index for indices in patches.values() for index in indices)
assert pad_ids and min(pad_ids) >= 0 and max(pad_ids) < expected_count
hand_ids = set()
queue = [next(iter(pad_ids))]
while queue:
    index = queue.pop()
    if index in hand_ids:
        continue
    hand_ids.add(index)
    queue.extend(item for item in adjacency[index] if item not in hand_ids)
assert pad_ids <= hand_ids
hand_ids = sorted(hand_ids)
topology = [(edge.vertices[0], edge.vertices[1]) for edge in initial.edges]
glove.evaluated_get(deps).to_mesh_clear()
rows = []
reference = {}
started = time.perf_counter()
for frame in range(1, 146):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    ge = glove.evaluated_get(deps)
    he = handle.evaluated_get(deps)
    re = rig.evaluated_get(deps)
    oe = holder.evaluated_get(deps)
    glove_mesh = ge.to_mesh()
    handle_mesh = he.to_mesh()
    assert len(glove_mesh.vertices) == expected_count
    assert [(edge.vertices[0], edge.vertices[1]) for edge in glove_mesh.edges] == topology
    points = world_points(coordinates(glove_mesh), ge.matrix_world, metres)
    raw_handle = coordinates(handle_mesh)
    zmin, zmax = float(raw_handle[:, 2].min()), float(raw_handle[:, 2].max())
    local_radius = float(np.linalg.norm(raw_handle[:, :2], axis=1).max())
    hw = np.array(he.matrix_world, dtype=np.float64)
    radii = local_radius * np.linalg.norm(hw[:3, :2], axis=0) * metres
    assert abs(float(radii[0] - radii[1])) < 1e-7
    radius = float(radii.mean())
    start, end = world_points(np.array([[0, 0, zmin], [0, 0, zmax]]), he.matrix_world, metres)
    length = float(np.linalg.norm(end - start))
    assert abs(radius - contract['radius_m']) < 1e-7
    assert abs(length - contract['endpoint_span_m']) < 1e-6
    wrist = matrix_metres(re.matrix_world @ re.pose.bones['wrist.R'].matrix, metres)
    scales = np.linalg.svd(wrist[:3, :3], compute_uv=False)
    assert float(scales.max() - scales.min()) < 1e-5
    holder_relative = np.linalg.inv(wrist) @ matrix_metres(oe.matrix_world, metres)
    handle_relative = np.linalg.inv(wrist) @ matrix_metres(he.matrix_world, metres)
    if frame == 25:
        reference = {'holder': holder_relative.copy(), 'handle': handle_relative.copy()}
    row = {'frame': frame, 'phase': 'HELD_REQUIRED' if frame >= 25 else 'OPEN_TO_CLOSE_NOT_REQUIRED',
           'handle_start_world_m': start.tolist(), 'handle_end_world_m': end.tolist(),
           'handle_radius_m': radius, 'handle_endpoint_span_m': length,
           'holder_in_wrist_affine': holder_relative.tolist(),
           'handle_in_wrist_affine': handle_relative.tolist(),
           'wrist_world_scale_singular_values': scales.tolist(), 'digits': {}}
    for key, indices in patches.items():
        samples = points[indices]
        screen = contact.screen_patch(samples.tolist(), start.tolist(), end.tolist(), radius,
                                      end_margin_m=contract['cap_margin_m'])
        point_results = [contact.cylinder_sample(point, start, end, radius) for point in samples]
        screen.update({'digit': digit_names[key], 'evaluated_indices': indices,
                       'world_points_m': samples.tolist(),
                       'axial_min_m': min(item['axial_m'] for item in point_results),
                       'axial_max_m': max(item['axial_m'] for item in point_results),
                       'inside_endpoint_span_fraction': sum(item['within_axial_span'] for item in point_results) / len(samples),
                       'inside_usable_span_fraction': sum(contract['cap_margin_m'] <= item['axial_m'] <= length - contract['cap_margin_m'] for item in point_results) / len(samples)})
        row['digits'][key] = screen
    worst = None
    negative_count = deep_count = 0
    for index in hand_ids:
        sample = contact.cylinder_sample(points[index], start, end, radius)
        distance = sample['signed_distance_m']
        negative_count += distance < 0
        deep_count += distance < -.0005
        if worst is None or distance < worst['signed_distance_m']:
            worst = {'evaluated_vertex': index, 'world_point_m': points[index].tolist(), **sample}
    row['whole_right_glove_vertex_screen'] = {
        'vertices': len(hand_ids), 'sampled_vertices_inside': negative_count,
        'sampled_vertices_deeper_than_0_5mm': deep_count,
        'maximum_sampled_penetration_mm': max(0, -worst['signed_distance_m'] * 1000), 'worst': worst}
    if frame >= 25:
        row['holder_drift_from_held_frame25'] = drift(holder_relative, reference['holder'], float(scales.mean()))
        row['handle_drift_from_held_frame25'] = drift(handle_relative, reference['handle'], float(scales.mean()))
    rows.append(row)
    ge.to_mesh_clear()
    he.to_mesh_clear()
    if frame % 24 == 1:
        print('FRAME', frame, 'pad_screens', {digit_names[key]: row['digits'][key]['status'] for key in patches}, flush=True)
held = [row for row in rows if row['frame'] >= 25]
summary = {}
for key in patches:
    summary[digit_names[key]] = {
        'held_frames': len(held),
        'passed_frames': sum(row['digits'][key]['status'] == 'PASS_SAMPLED_NUMERIC_SCREEN' for row in held),
        'failed_frames': [row['frame'] for row in held if row['digits'][key]['status'] != 'PASS_SAMPLED_NUMERIC_SCREEN'],
        'min_gap_mm': min(row['digits'][key]['min_gap_mm'] for row in held),
        'maximum_median_gap_mm': max(row['digits'][key]['median_gap_mm'] for row in held),
        'maximum_p95_gap_mm': max(row['digits'][key]['p95_gap_mm'] for row in held),
        'max_gap_mm': max(row['digits'][key]['max_gap_mm'] for row in held),
        'minimum_band_fraction': min(row['digits'][key]['contact_fraction'] for row in held),
        'all_held_usable_axial_spans_valid': all(row['digits'][key]['axial_region_valid'] for row in held)}
after = preservation()
report = {
    'status': 'MEASURED_NUMERICAL_SCREENS_ONLY', 'source': str(SOURCE), 'source_sha256': EXPECTED,
    'source_sha256_after': sha(SOURCE), 'source_unchanged': sha(SOURCE) == EXPECTED,
    'helper': str(HELPER), 'helper_sha256': HELPER_HASH, 'helper_unchanged': sha(HELPER) == HELPER_HASH,
    'script_sha256': sha(__file__), 'blender_version': bpy.app.version_string,
    'elapsed_seconds': time.perf_counter() - started,
    'coordinate_space': 'WORLD_METERS', 'scene_unit_scale_length': metres,
    'action': rig.animation_data.action.name, 'carry_spec': carry, 'stored_hand_contract': contract,
    'frame_count': len(rows), 'held_frame_count': len(held), 'fps': scene.render.fps,
    'original_pad_indices_preserved': True, 'evaluated_vertex_count': expected_count,
    'right_glove_component_vertex_count': len(hand_ids),
    'component_definition': 'Entire evaluated connected glove component containing every stored right-digit pad index; fixed indices established at frame1 and identical evaluated topology asserted at every frame.',
    'protected_before': before, 'protected_after': after,
    'all62_protected_files_preserved': len(after) == 62 and all(row['unchanged'] for row in before + after),
    'held_summary_per_digit': summary,
    'maximum_held_glove_vertex_penetration_mm': max(row['whole_right_glove_vertex_screen']['maximum_sampled_penetration_mm'] for row in held),
    'maximum_held_holder_drift_mm': max(row['holder_drift_from_held_frame25']['translation_mm'] for row in held),
    'maximum_held_holder_drift_deg': max(row['holder_drift_from_held_frame25']['rotation_deg'] for row in held),
    'maximum_held_handle_drift_mm': max(row['handle_drift_from_held_frame25']['translation_mm'] for row in held),
    'maximum_held_handle_drift_deg': max(row['handle_drift_from_held_frame25']['rotation_deg'] for row in held),
    'frames': rows, 'source_saved': False, 'art_approval': False,
    'limitations': [
        'All-frame vertex/pad sampling against the measured ideal circular cylinder is not a triangle-interior or continuous-time collision test.',
        'The actual96-sided polygonal cylinder is represented by its circumradius; at14mm this differs from its inscribed face radius by about0.0075mm.',
        'Only the glove surface is measured here; underlying body skin, self-collision, guard/pommel, force closure and runtime compatibility are not certified.',
        'Rigid helper functions are not used on scaled wrist matrices. Full affine wrist-relative transforms are retained; translation drift is converted using verified uniform wrist scale. Polar rotation isolates orientation drift without changing scene geometry.',
        'Frames1-24 are open-to-close and do not require persistent contact. Held frames25-145 each retain the complete measured sample distributions.',
    ],
}
assert report['source_unchanged'] and report['helper_unchanged'] and report['all62_protected_files_preserved']
with OUTPUT.open('x', encoding='utf-8') as stream:
    json.dump(report, stream, indent=2, allow_nan=False)
    stream.write('\n')
print(json.dumps({key: value for key, value in report.items() if key.startswith('maximum_held') or key in ('held_summary_per_digit', 'all62_protected_files_preserved', 'elapsed_seconds')}, indent=2), flush=True)
