"""Tailor the three retained Stormstep sources without replacing their broad rigs."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil
import sys

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/blender'))
from author_alpha import Geometry
from refine_update_ada import components, invariants, render_views, sha, use_clip

IDS = ('wc_u_orc_warrior', 'wc_u_orc_mage', 'wc_u_orc_rogue')


def recolor(mesh, part, swatch):
    selected = set(part['indices'])
    for polygon in mesh.data.polygons:
        if all(index in selected for index in polygon.vertices):
            for loop in polygon.loop_indices:
                old = mesh.data.uv_layers.active.data[loop].uv
                old.x = (swatch % 4 + (old.x * 4) % 1) / 4
                old.y = (swatch // 4 + (old.y * 4) % 1) / 4


def append_geometry(mesh, geometry, label):
    data = bpy.data.meshes.new(label)
    data.from_pydata(geometry.vertices, [], geometry.faces)
    data.materials.append(mesh.data.materials[0])
    uv = data.uv_layers.new(name=mesh.data.uv_layers.active.name)
    for polygon, color in zip(data.polygons, geometry.colors):
        for loop in polygon.loop_indices:
            co = data.vertices[data.loops[loop].vertex_index].co
            uv.data[loop].uv = ((color % 4 + .35 + .15 * math.sin(co.x * 7)) / 4,
                                (color // 4 + .35 + .15 * math.sin(co.z * 5)) / 4)
        polygon.use_smooth = color in (6, 7, 8, 9, 14)
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    piece = bpy.data.objects.new(label, data)
    mesh.users_collection[0].objects.link(piece)
    for index, weights in enumerate(geometry.weights):
        for bone, weight in weights.items():
            if weight > 0:
                group = piece.vertex_groups.get(bone) or piece.vertex_groups.new(name=bone)
                group.add([index], weight, 'REPLACE')
    hidden = mesh.hide_get()
    mesh.hide_set(False)
    bpy.ops.object.select_all(action='DESELECT')
    piece.select_set(True)
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.join()
    mesh.hide_set(hidden)


def remove_parts(mesh, parts):
    selected = {index for part in parts for index in part['indices']}
    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.verts[index] for index in selected], context='VERTS')
    bm.to_mesh(mesh.data)
    bm.free()
    mesh.data.update()


def closed_sheet(geometry, position, rows, columns, color, weight_at):
    vertices, weights, faces = [], [], []
    for back in (False, True):
        for row in range(rows):
            for col in range(columns):
                point = Vector(position(col / (columns - 1), row / (rows - 1)))
                if back:
                    point.z -= .009
                vertices.append(tuple(point))
                weights.append(weight_at(point))
    count = rows * columns
    for back in (0, 1):
        offset = back * count
        for row in range(rows - 1):
            for col in range(columns - 1):
                first = offset + row * columns + col
                face = (first, first + 1, first + columns + 1, first + columns)
                faces.append(tuple(reversed(face)) if back else face)
    boundary = list(range(columns)) + [row * columns + columns - 1 for row in range(1, rows)]
    boundary += list(range(count - 2, count - columns - 1, -1))
    boundary += [row * columns for row in range(rows - 2, 0, -1)]
    for first, second in zip(boundary, boundary[1:] + boundary[:1]):
        faces.append((first, second, second + count, first + count))
    geometry.add(vertices, faces, color, weights=weights)


def costume_details(mesh, uid, height):
    geometry = Geometry()
    def arm_weight(point):
        amount = max(0, min(.85, (abs(point.x) / height - .075) / .20))
        return {'spine_03': 1 - amount, 'upperarm_' + ('l' if point.x > 0 else 'r'): amount}

    if uid == 'wc_u_orc_warrior':
        # Two shaped half-rings preserve the round mantle and leave a neck opening.
        for sign in (-1, 1):
            def position(u, v):
                angle = -math.pi / 2 + math.pi * v
                x = sign * (.072 + .242 * u) * math.cos(angle)
                y = (.072 + .082 * u) * math.sin(angle)
                z = .835 - .040 * u - (.013 + .065 * abs(math.sin(angle))) * u * u
                z += .014 * math.sin(math.pi * u) * math.cos(angle)
                return Vector((x, y, z)) * height
            closed_sheet(geometry, position, 17, 9, 0, arm_weight)
            edge = [position(1, step / 24) + Vector((0, 0, .004)) for step in range(25)]
            geometry.tube(edge, [.006 * height] * len(edge), 1, sides=6,
                          weights=[arm_weight(point) for point in edge])
            inner = [position(.73, step / 18) + Vector((0, 0, .006)) for step in range(19)]
            geometry.tube(inner, [.0025 * height] * len(inner), 10, sides=5,
                          weights=[arm_weight(point) for point in inner])
        # Red woven hip knot and two short tails, kept close to the existing belt.
        geometry.loft([((.315, .08, 1.075), .048, .044), ((.32, .08, 1.105), .059, .050),
                       ((.31, .08, 1.132), .035, .035)], 1, 'pelvis', 10)
        geometry.plate([(.31, 1.105), (.35, 1.095), (.375, .897), (.335, .923)], .093, .017, 1, 'pelvis')
        geometry.plate([(.292, 1.10), (.32, 1.08), (.303, .918), (.275, .945)], .09, .017, 1, 'pelvis')
    elif uid == 'wc_u_orc_mage':
        for sign in (-1, 1):
            def position(u, v):
                x = sign * (.053 + .245 * u)
                y = (-.114 + .228 * v) * (.66 + .34 * u)
                z = .794 + .004 * math.sin(math.pi * v) - .050 * u ** 1.8
                return Vector((x, y, z)) * height
            closed_sheet(geometry, position, 9, 11, 1, arm_weight)
            edge = [position(1, step / 16) + Vector((0, 0, .005)) for step in range(17)]
            geometry.tube(edge, [.007] * len(edge), 3, sides=6,
                          weights=[arm_weight(point) for point in edge])
        arc = [(height * .115 * math.cos(a), -.231, 1.47 + height * .048 * math.sin(a))
               for a in [math.pi * (.12 + .76 * index / 20) for index in range(21)]]
        geometry.tube(arc, [.008] * len(arc), 1, 'spine_03', 6)
        # Three separate braid ties reinforce the authored three-part rhythm.
        for x in (-.107, 0, .107):
            geometry.loft([((x, -.212, 1.615), .027, .028), ((x, -.212, 1.64), .027, .028)], 3, 'head', 10)
    else:
        def position(u, v):
            x = .069 + .222 * u
            y = -.17 + .34 * v
            z = 1.51 - .115 * u ** 1.7 + .010 * math.sin(math.pi * v)
            return (x, y, z)
        closed_sheet(geometry, position, 9, 9, 0, arm_weight)
        # Close-fitting pale hair tie; route patch uses the existing sash palette.
        geometry.plate([(-.128, 1.806), (.128, 1.806), (.115, 1.838), (-.115, 1.838)], -.159, .019, 8, 'head')
        geometry.plate([(.06, 1.235), (.15, 1.25), (.143, 1.34), (.056, 1.325)], .218, .014, 1, 'spine_02')
        geometry.tube([(.08, .230, 1.258), (.098, .231, 1.282), (.121, .231, 1.28), (.128, .230, 1.314)],
                      [.006] * 4, 9, 'spine_02', 5)
    append_geometry(mesh, geometry, 'Stormstep_TailoredDetails')


def open_balance_hand(mesh):
    geometry = Geometry()
    for index in range(4):
        x = .694 + index * .035
        bottom = .713 + (.012 if index in (0, 3) else 0)
        geometry.tube([(x, .113, .828), (x + .004, .116, .793),
                       (x + .007, .127, bottom + .015), (x + .007, .128, bottom)],
                      [.020, .020, .016, .006], 6, 'hand_l', 8)
    append_geometry(mesh, geometry, 'Rok_OpenBalanceFingers')


def alter(mesh, uid, height):
    records, remove = [], []
    for part in components(mesh):
        count, groups = part['count'], part['groups']
        center = Vector(part['center_m'])
        vertices = [mesh.data.vertices[index] for index in part['indices']]
        if groups == ['head'] and count == 112:
            for vertex in vertices:
                lower = max(0, min(1, (.883 * height - vertex.co.z) / (.057 * height)))
                vertex.co.x *= 1 - (.11 if uid.endswith('rogue') else .055) * lower
                vertex.co.y += .007 * math.exp(-((vertex.co.z / height - .87) / .035) ** 2)
            records.append('refined cheek and jaw planes on the existing face')
        elif groups == ['head'] and count == 5:
            for vertex in vertices:
                vertex.co.y = part['bounds_min_m'][1] + (vertex.co.y - part['bounds_min_m'][1]) * .68
                vertex.co.x *= .92
            recolor(mesh, part, 6)
            records.append('smaller skin-colored nose projection')
        elif groups == ['head'] and count == 15:
            if center.z / height > .90:
                for vertex in vertices:
                    vertex.co.z = center.z + (vertex.co.z - center.z) * .52 - .009
                    vertex.co.y -= .007
                records.append('softened brows keep warm eyes open')
            else:
                for vertex in vertices:
                    vertex.co.z += .004 + .005 * abs(vertex.co.x) / max(.001, part['bounds_max_m'][0])
                records.append('restrained upward mouth corners')
        elif groups == ['head'] and count == 21:
            for vertex in vertices:
                vertex.co.z = part['bounds_min_m'][2] + (vertex.co.z - part['bounds_min_m'][2]) * .80
                vertex.co.y = center.y + (vertex.co.y - center.y) * .78
            records.append('shorter rounded tusks clear of the mouth')
        elif count == 60 and any(group.startswith('thigh_') for group in groups):
            recolor(mesh, part, 9 if uid != 'wc_u_orc_mage' else 2)
            records.append('authored cloth trousers instead of skin-colored lower body')
        elif groups in (['hand_l'], ['hand_r']) and count == 70:
            for vertex in vertices:
                for axis in (0, 1):
                    radius = (part['bounds_max_m'][axis] - part['bounds_min_m'][axis]) / 2
                    delta = vertex.co[axis] - center[axis]
                    vertex.co[axis] = center[axis] + math.copysign((abs(delta) / radius) ** .72 * radius, delta)
                vertex.co.z = center.z + (vertex.co.z - center.z) * .92
                if uid.endswith('warrior') and groups == ['hand_l']:
                    vertex.co.z = center.z + (vertex.co.z - center.z) * .74
                    vertex.co.y = center.y + (vertex.co.y - center.y) * .80
            records.append('shaped palm and open balance off-hand' if uid.endswith('warrior') else 'shaped grip palm')
        elif groups in (['hand_l'], ['hand_r']) and count == 40:
            sign = 1 if groups == ['hand_l'] else -1
            for vertex in vertices:
                vertex.co.x += sign * .015
                vertex.co.y += .007
                vertex.co.z = center.z + (vertex.co.z - center.z) * .78
            records.append('wrapped thumb fits existing weapon handle')
        elif count == 112 and any(group.startswith('upperarm_') for group in groups):
            first = sum((v.co for v in vertices[:16]), Vector()) / 16
            second = sum((v.co for v in vertices[16:32]), Vector()) / 16
            for vertex in vertices[:16]:
                vertex.co = first.lerp(second, .12) + (vertex.co - first) * .67
            for vertex in vertices[16:32]:
                vertex.co = second + (vertex.co - second) * .94
            if uid.endswith('warrior'):
                recolor(mesh, part, 2)
            records.append('rounded shoulder cap under curved garment')
        elif groups == ['spine_03'] and count == 20:
            remove.append(part)
        if uid == 'wc_u_orc_warrior':
            if count == 96:
                recolor(mesh, part, 2)
                records.append('brown padded cuirass distinguishes ochre mantle')
            elif groups == ['pelvis'] and count == 32:
                recolor(mesh, part, 1)
                records.append('red woven waist sash')
            elif groups in (['clavicle_l'], ['clavicle_r']) and count == 24:
                remove.append(part)
            elif groups == ['hand_r'] and count == 20:
                for vertex in vertices:
                    vertex.co.x = center.x + (vertex.co.x - center.x) * 1.17
                    vertex.co.y = center.y + (vertex.co.y - center.y) * 1.17
                records.append('axe handle widened to meet retained palm')
            elif groups == ['hand_r'] and count == 24:
                for vertex in vertices:
                    vertex.co.x = -.72 + (vertex.co.x + .72) * .90
                records.append('compact broad axe clears neighboring silhouettes')
        elif uid == 'wc_u_orc_mage':
            if groups == ['pelvis'] and count in (16, 20) and center.z < 1:
                for vertex in vertices:
                    t = max(0, min(1, (1.06 - vertex.co.z) / .74))
                    vertex.co.x *= 1 - .32 * t
                    vertex.co.y += math.copysign(.025 * math.sin(math.pi * t), vertex.co.y)
                    if abs(vertex.co.x) < .065:
                        vertex.co.x += math.copysign(.019 * t, vertex.co.x)
                records.append('tapered split coat gives knees and boots clearance')
            elif groups == ['head'] and count == 119:
                shift = .023 if center.x > .045 else (-.023 if center.x < -.045 else 0)
                for vertex in vertices:
                    vertex.co.x += shift
                records.append('three braids separated at the nape')
            elif groups == ['hand_r'] and count == 27:
                for vertex in vertices:
                    t = max(0, min(1, (vertex.co.z - 1.65) / .44))
                    vertex.co.x += math.copysign(.026 * t, center.x + .73)
                records.append('fork tips opened around bounded sky stone')
            elif groups == ['hand_r'] and count == 56:
                for vertex in vertices:
                    vertex.co = center + (vertex.co - center) * .72
                records.append('small sky stone preserves staff negative space')
        else:
            if groups == ['spine_02'] and count == 10:
                recolor(mesh, part, 1)
                records.append('tan diagonal courier sash')
            elif groups == ['neck'] and count == 40:
                for vertex in vertices:
                    vertex.co.z -= .022
                    vertex.co.y *= .90
                records.append('high scarf loop lowered clear of chin')
            elif groups in (['hand_l'], ['hand_r']) and count == 24:
                sign = 1 if groups == ['hand_l'] else -1
                for vertex in vertices:
                    t = max(0, min(1, (vertex.co.z - .90) / .45))
                    vertex.co.z = .90 + (vertex.co.z - .90) * .78
                    vertex.co.x += sign * .023 * math.sin(t * math.pi)
                records.append('short rounded paired courier blades')
        if groups == ['pelvis'] and count == 24 and center.z < height * .51:
            for vertex in vertices:
                t = max(0, min(1, (height * .54 - vertex.co.z) / (height * .18)))
                vertex.co.x *= 1 - .16 * t
                vertex.co.y += .010 * math.sin(math.pi * t)
            records.append('short garment panels taper around the hip')
    mesh.data.update()
    if remove:
        remove_parts(mesh, remove)
        records.append('replaced rigid shoulder plates with closed curved cloth')
    if mesh.name in ('SK_' + uid, 'COSTUME_SK_' + uid):
        costume_details(mesh, uid, height)
    if uid.endswith('warrior') and mesh.name in ('SK_' + uid, 'BODY_SK_' + uid):
        open_balance_hand(mesh)
        records.append('four short rounded fingers define the open balance hand')
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--unit', choices=IDS, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--skip-render', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    uid, out = args.unit, args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    source = ROOT / f'art-source/heroes/{uid}/{uid}.blend'
    exports = ROOT / f'exports/heroes/{uid}'
    manifest = json.loads((exports / 'export_manifest.json').read_text())
    assert manifest['source_revision'] == 6 and sha(source) == manifest['source_sha256']
    shutil.copy2(source, out / 'before-source.blend')
    shutil.copy2(exports / 'export_manifest.json', out / 'before-export-manifest.json')
    shutil.copy2(Path(__file__), out / 'executed-refinement.py')
    bpy.ops.wm.open_mainfile(filepath=str(source))
    arm = bpy.data.objects['Armature']
    before = invariants(arm)
    height = manifest['height_m']
    changes = {name: alter(bpy.data.objects[name], uid, height) for name in
               ('SK_' + uid, 'BODY_SK_' + uid, 'COSTUME_SK_' + uid, 'EQUIPMENT_SK_' + uid)}
    assert invariants(arm) == before
    use_clip(arm, 'Idle', unit_id=uid)
    candidate = out / (uid + '-update24-revision7.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(candidate), check_existing=False)
    renders = [] if args.skip_render else render_views(out, 'after')
    assert sha(source) == manifest['source_sha256']
    record = {'status': 'SOURCE_REFINEMENT_CANDIDATE_NOT_PROMOTED', 'unit_id': uid,
              'source_before_sha256': manifest['source_sha256'], 'candidate': str(candidate),
              'candidate_sha256': sha(candidate), 'blender_version': bpy.app.version_string,
              'preserved_invariants': before, 'changes': changes, 'renders': renders,
              'refinement_script_sha256': sha(Path(__file__)),
              'limits': ['Current geometry requires seven-clip rendered review', 'LODs pending regeneration',
                         'Unreal not imported', 'Final art not accepted']}
    (out / 'refinement.json').write_text(json.dumps(record, indent=2) + '\n')
    print('WC_ORC_SOURCE_REFINED ' + uid, flush=True)


if __name__ == '__main__':
    main()
