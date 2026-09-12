"""Read-only two-file evaluated-surface binding; no repeated collision query."""
import bpy
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / 'grip_integrated_contact_r001.blend'
FINAL = ROOT / 'ada_bw2_grip_checkpoint_r001_ART_REVISE.blend'
STATIC_HASH = '9509750f833cec0c8cac90cd866215a732baed67571d1d444c7b718f441f877d'
FINAL_HASH = 'd64d5900317541710d5ef29939d12559e5ecef31777a7e9261158cbccb7a41cf'
NAMES = ['BW1_Glove_Pair_SourceFit', 'BW1_IndexedBody']
TOLERANCE_M = 1e-6


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def numeric_hash(collection, attribute, width, dtype):
    array = np.empty(len(collection) * width, dtype=dtype)
    collection.foreach_get(attribute, array)
    return hashlib.sha256(array.tobytes()).hexdigest()


def snapshot(path, expected, frame):
    assert sha(path) == expected
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
    scene = bpy.data.scenes['BW2_RIGHT_GRIP']
    bpy.context.window.scene = scene
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    assert scene.unit_settings.system == 'METRIC' and scene.unit_settings.scale_length == 1.0
    deps = bpy.context.evaluated_depsgraph_get()
    rows = {}
    for name in NAMES:
        obj = bpy.data.objects[name].evaluated_get(deps)
        mesh = obj.to_mesh()
        local = np.empty(len(mesh.vertices) * 3, dtype=np.float64)
        mesh.vertices.foreach_get('co', local)
        local = local.reshape((-1, 3))
        transform = np.array(obj.matrix_world, dtype=np.float64)
        world = local @ transform[:3, :3].T + transform[:3, 3]
        rows[name] = {
            'local': local, 'world': world, 'matrix_world': transform,
            'topology': {'vertex_count': len(mesh.vertices), 'edge_count': len(mesh.edges),
                         'polygon_count': len(mesh.polygons),
                         'edges_sha256': numeric_hash(mesh.edges, 'vertices', 2, np.int32),
                         'corners_sha256': numeric_hash(mesh.loops, 'vertex_index', 1, np.int32),
                         'polygon_sizes_sha256': numeric_hash(mesh.polygons, 'loop_total', 1, np.int32)},
        }
        obj.to_mesh_clear()
    rig = bpy.data.objects['BW1_Temporary_Pose_Rig']
    action = rig.animation_data.action if rig.animation_data else None
    return rows, {'source': str(path), 'sha256': expected, 'evaluated_frame': frame,
                  'scene': scene.name, 'action': action.name if action else None}


assert bpy.app.background
static, source_record = snapshot(STATIC, STATIC_HASH, 1)
final, final_record = snapshot(FINAL, FINAL_HASH, 37)
comparisons = {}
for name in NAMES:
    before, after = static[name], final[name]
    shapes_match = before['local'].shape == after['local'].shape
    row = {'topology_exact': before['topology'] == after['topology'],
           'static_topology': before['topology'], 'final_topology': after['topology'],
           'static_world_matrix': before['matrix_world'].tolist(),
           'final_world_matrix': after['matrix_world'].tolist(),
           'world_matrix_max_element_difference': float(np.abs(before['matrix_world'] - after['matrix_world']).max()),
           'vertex_array_shapes_equal': shapes_match}
    if shapes_match:
        local_delta = np.linalg.norm(after['local'] - before['local'], axis=1)
        world_delta = np.linalg.norm(after['world'] - before['world'], axis=1)
        row.update({'local_coordinates_exact': bool(np.array_equal(before['local'], after['local'])),
                    'world_coordinates_exact': bool(np.array_equal(before['world'], after['world'])),
                    'local_max_vertex_difference_bu': float(local_delta.max()),
                    'world_max_vertex_difference_m': float(world_delta.max()),
                    'world_p95_vertex_difference_m': float(np.percentile(world_delta, 95)),
                    'worst_world_vertex_index': int(np.argmax(world_delta)),
                    'vertices_exceeding1um': int(np.count_nonzero(world_delta > TOLERANCE_M)),
                    'static_evaluated_local_f64_sha256': hashlib.sha256(before['local'].tobytes()).hexdigest(),
                    'final_evaluated_local_f64_sha256': hashlib.sha256(after['local'].tobytes()).hexdigest()})
    row['within_declared_float_tolerance'] = (shapes_match and row['topology_exact']
                                              and row['world_max_vertex_difference_m'] <= TOLERANCE_M
                                              and row['world_matrix_max_element_difference'] <= 1e-6)
    comparisons[name] = row
result = {'status': 'STATIC_GEOMETRY_BOUND_TO_FINAL' if all(row['within_declared_float_tolerance'] for row in comparisons.values()) else 'REVISE_STATIC_BINDING',
          'static_input': source_record, 'final_input': final_record,
          'world_coordinate_tolerance_m': TOLERANCE_M,
          'world_matrix_element_tolerance': 1e-6,
          'objects': comparisons,
          'static_sha256_after': sha(STATIC), 'final_sha256_after': sha(FINAL),
          'both_sources_unchanged': sha(STATIC) == STATIC_HASH and sha(FINAL) == FINAL_HASH,
          'method': 'Full evaluated glove and underlying-body indexed vertex arrays and world matrices compared at static frame1 versus final held frame37. No triangle/self-collision test was repeated.',
          'limitations': 'Binds the static evaluated geometry evidence to final held frame37 within1micrometre tolerance. Does not independently prove every held frame has identical self-intersections or reclassify coplanar/tangential contacts.',
          'source_saved': False, 'art_approval': False, 'script_sha256': sha(__file__)}
assert result['both_sources_unchanged']
with (ROOT / 'reviews/static_geometry_to_final_binding.json').open('x', encoding='utf-8') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps(result, indent=2))
