"""Isolated, production-preserving costume-change fixture for ART-04.

Run in Blender only after the runtime performance window is released. This
script never saves or exports to a production path and does not import Unreal.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sys

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from author_alpha import export_fbx_raw
from normalized_fbx import export_normalized_copy

UID = 'wc_u_human_guardian'
OUT = ROOT / 'reports/WC-330/ada-costume-roundtrip'
SOURCE = ROOT / f'art-source/heroes/{UID}/{UID}.blend'
PRODUCTION = ROOT / f'exports/heroes/{UID}'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def protected_files():
    paths = [SOURCE, *sorted(p for p in PRODUCTION.iterdir() if p.is_file())]
    return {relative(p): sha(p) for p in paths}


def actions_signature():
    state = {}
    for action in bpy.data.actions:
        curves = []
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        curves.append([curve.data_path, curve.array_index,
                            [[list(k.co), list(k.handle_left), list(k.handle_right),
                              k.interpolation] for k in curve.keyframe_points]])
        state[action.name] = curves
    return digest(state)


def invariants(arm, mesh):
    return {
        'rest_skeleton_sha256': digest({b.name: {
            'matrix': [list(row) for row in b.matrix_local],
            'parent': b.parent.name if b.parent else None,
            'head': list(b.head_local), 'tail': list(b.tail_local),
        } for b in arm.data.bones}),
        'actions_sha256': actions_signature(),
        'action_names': sorted(a.name for a in bpy.data.actions),
        'material_slots': [m.name if m else None for m in mesh.data.materials],
        'vertex_group_names': [g.name for g in mesh.vertex_groups],
        'armature_modifier_targets': [m.object.name for m in mesh.modifiers
            if m.type == 'ARMATURE' and m.object],
        'source_units': bpy.context.scene.unit_settings.scale_length,
    }


def geometry(mesh):
    data = mesh.data
    data.calc_loop_triangles()
    coords = [list(v.co) for v in data.vertices]
    return {
        'vertices': len(data.vertices), 'polygons': len(data.polygons),
        'triangles': len(data.loop_triangles),
        'bounds_min_m': [min(v[i] for v in coords) for i in range(3)],
        'bounds_max_m': [max(v[i] for v in coords) for i in range(3)],
        'positions_sha256': digest(coords),
        'uv_layer_names': [layer.name for layer in data.uv_layers],
    }


def main():
    if any((OUT / name).exists() for name in
           ('source-baseline.blend', 'source-changed.blend', 'source-change-manifest.json')):
        raise RuntimeError('Existing drill evidence must be preserved; do not overwrite it')
    OUT.mkdir(parents=True, exist_ok=True)
    protected = protected_files()
    baseline_source = OUT / 'source-baseline.blend'
    changed_source = OUT / 'source-changed.blend'
    shutil.copy2(SOURCE, baseline_source)
    assert sha(baseline_source) == protected[relative(SOURCE)]
    bpy.ops.wm.open_mainfile(filepath=str(baseline_source))
    arm = bpy.data.objects['Armature']
    mesh = bpy.data.objects['SK_' + UID]
    unit = next(u for u in json.loads((ROOT / 'data/units.json').read_text())['units']
                if u['id'] == UID)
    height = unit['height_m']
    before_geometry = geometry(mesh)
    before_invariants = invariants(arm, mesh)
    old_weights = [[(g.group, g.weight) for g in v.groups] for v in mesh.data.vertices]
    old_uv = {layer.name: [list(v.uv) for v in layer.data] for layer in mesh.data.uv_layers}
    assert len(before_invariants['action_names']) == 7
    baseline_fbx = OUT / 'baseline' / f'SK_{UID}.fbx'
    changed_fbx = OUT / 'changed' / f'SK_{UID}.fbx'
    for path in (baseline_fbx, changed_fbx):
        path.parent.mkdir(parents=True, exist_ok=True)
    export_normalized_copy(baseline_fbx, [arm, mesh], False, export_fbx_raw)
    assert invariants(arm, mesh) == before_invariants
    assert geometry(mesh) == before_geometry

    # The authored left gold fastener is a separate 40-vertex closed island.
    # Copy its geometry and custom data; leave every original vertex intact.
    center = Vector((.104, .139, .723)) * height
    destination = Vector((0, .1365, .687)) * height
    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bm.verts.ensure_lookup_table()
    originals = list(bm.verts)
    source_vertices = [v for v in originals if
        abs(v.co.x - center.x) < .0101 * height and
        abs(v.co.y - center.y) < .0071 * height and
        abs(v.co.z - center.z) < .0101 * height]
    assert len(source_vertices) == 40, f'Expected 40 fastener vertices, found {len(source_vertices)}'
    source_set = set(source_vertices)
    source_faces = {f for v in source_vertices for f in v.link_faces}
    assert all(set(f.verts).issubset(source_set) for f in source_faces), 'Fastener island is not isolated'
    source_edges = {e for f in source_faces for e in f.edges}
    result = bmesh.ops.duplicate(bm, geom=[*source_vertices, *source_edges, *source_faces])
    additions = [element for element in result['geom'] if isinstance(element, bmesh.types.BMVert)]
    assert len(additions) == 40
    for vertex in additions:
        offset = vertex.co - center
        vertex.co = destination + Vector((offset.x * 1.8, offset.y, offset.z * 1.8))
    bm.to_mesh(mesh.data)
    bm.free()
    mesh.data.update()
    after_geometry = geometry(mesh)
    after_invariants = invariants(arm, mesh)
    assert after_invariants == before_invariants, 'Rest/actions/material references changed'
    assert after_geometry['vertices'] - before_geometry['vertices'] == 40
    assert after_geometry['triangles'] - before_geometry['triangles'] == 76
    assert after_geometry['bounds_min_m'] == before_geometry['bounds_min_m']
    assert after_geometry['bounds_max_m'] == before_geometry['bounds_max_m']
    assert digest([list(v.co) for v in mesh.data.vertices[:before_geometry['vertices']]]) == before_geometry['positions_sha256']
    assert [[(g.group, g.weight) for g in v.groups]
            for v in mesh.data.vertices[:before_geometry['vertices']]] == old_weights
    assert all([list(v.uv) for v in mesh.data.uv_layers[name].data[:len(values)]] == values
               for name, values in old_uv.items()), 'Existing UV coordinates changed'
    # Inspect inherited weights: the copy remains rigidly attached to spine_03.
    group = mesh.vertex_groups['spine_03'].index
    copied_weights = [[(g.group, g.weight) for g in v.groups]
                      for v in mesh.data.vertices[before_geometry['vertices']:]]
    assert all(weights == [(group, 1.0)] for weights in copied_weights)
    bpy.ops.wm.save_as_mainfile(filepath=str(changed_source), check_existing=False)
    export_normalized_copy(changed_fbx, [arm, mesh], False, export_fbx_raw)
    assert invariants(arm, mesh) == before_invariants
    assert geometry(mesh) == after_geometry
    assert protected_files() == protected, 'Production files changed during isolated drill'
    result = {
        'status': 'BLENDER_EXECUTED_UNREAL_ROUNDTRIP_PENDING',
        'unit_id': UID,
        'expected_min_vertex_count_increase': 1,
        'blender_version': bpy.app.version_string,
        'change_description': 'Add a central gold breastplate medallion by copying the authored left gold fastener, enlarging X/Z by 1.8, and placing it at normalized body coordinates (0, .1365, .687), with its back touching the breastplate front. Existing material, UV, spine_03 weights, source vertices and skeleton/actions are preserved.',
        'production_source': relative(SOURCE),
        'production_source_sha256': protected[relative(SOURCE)],
        'baseline_source': relative(baseline_source),
        'baseline_source_sha256': sha(baseline_source),
        'changed_source': relative(changed_source),
        'changed_source_sha256': sha(changed_source),
        'baseline_fbx': relative(baseline_fbx), 'baseline_fbx_sha256': sha(baseline_fbx),
        'changed_fbx': relative(changed_fbx), 'changed_fbx_sha256': sha(changed_fbx),
        'baseline_geometry': before_geometry, 'changed_geometry': after_geometry,
        'geometry_delta': {'vertices': 40, 'triangles': 76, 'bounds_change_m': 0},
        'unchanged_invariants': before_invariants,
        'protected_production_files_sha256': protected,
        'production_files_preserved': True,
        'source_unchanged_original_vertices': True,
        'source_unchanged_original_weights_and_uvs': True,
        'clip_count_unchanged': 7,
        'export_profile': 'tools/blender/profiles/fbx_skeletal_cm_v1.json',
        'renders': [],
        'limits': ['Isolated source-copy drill, no production change',
                   'No beauty render or Unreal reference check is implied by export'],
    }
    (OUT / 'source-change-manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print('WC_ADA_COSTUME_SOURCE_DRILL_PASS ' + json.dumps(result['geometry_delta']), flush=True)


if __name__ == '__main__':
    main()
