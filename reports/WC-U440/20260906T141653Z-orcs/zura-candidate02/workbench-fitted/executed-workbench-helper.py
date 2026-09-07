"""Incrementally refine Borin, Tessa and Dagna on their retained family rigs."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import runpy
import shutil
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from author_alpha import Geometry, make_mesh
from refine_update_ada import components, invariants, use_clip, export_revision
from hand_contacts import place_hand

IDS = ('wc_u_dwarf_guardian', 'wc_u_dwarf_ranger', 'wc_u_dwarf_warrior')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def camera_view(unit, view, resolution=768):
    scene = bpy.context.scene
    scene.render.resolution_x = scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.media_type = 'IMAGE'
    scene.render.image_settings.file_format = 'PNG'
    scene.cycles.samples = 12 if resolution > 384 else 4
    camera = scene.camera
    height = unit['height_m']
    views = {'front': (0, 5, height * .60), 'side': (5, 0, height * .60),
             'back': (0, -5, height * .60), 'three-quarter': (3, 5, height * 1.50),
             'game-angle': (0, height * 2.5, height * 4.3), 'face': (.6, 5, height * .92)}
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = height * (1.52 if view != 'face' else .43)
    camera.location = views[view]
    camera.rotation_euler = (Vector((0, 0, height * (.57 if view != 'face' else .91))) - camera.location).to_track_quat('-Z', 'Y').to_euler()


def render(unit, out, prefix):
    for view in ('front', 'side', 'back', 'three-quarter', 'face', 'game-angle'):
        camera_view(unit, view)
        target = out / f'{prefix}-{view}.png'
        if target.exists():
            raise RuntimeError(f'Preserve existing evidence: {target}')
        bpy.context.scene.render.filepath = str(target)
        bpy.ops.render.render(write_still=True)


def inspect(unit, out, source):
    arm = bpy.data.objects['Armature']
    mesh = bpy.data.objects['SK_' + unit['id']]
    record = {'unit_id': unit['id'], 'source': str(source), 'source_sha256': sha(source),
              'blender_version': bpy.app.version_string, 'invariants': invariants(arm),
              'objects': [{'name': item.name, 'type': item.type, 'hidden': item.hide_render}
                          for item in bpy.data.objects],
              'components': [{key: value for key, value in part.items() if key != 'indices'}
                             for part in components(mesh)]}
    write(out / 'source-inspection.json', record)
    use_clip(arm, 'Idle', unit_id=unit['id'])
    render(unit, out, 'before')


def edit_islands(mesh, unit):
    """Reshape retained authored islands; only Dagna's two hammer plates change topology."""
    h = unit['height_m']
    uid = unit['id']
    changes, remove = [], set()
    for part in components(mesh):
        group, count = part['groups'], part['count']
        center = Vector(part['center_m']) / h
        vertices = [mesh.data.vertices[index] for index in part['indices']]
        change = None
        if group == ['head'] and count == 112:
            for vertex in vertices:
                v = vertex.co / h
                jaw = max(0, min(1, (.875 - v.z) / .047))
                v.x *= 1 - (.07 if uid.endswith('guardian') else .11) * jaw
                vertex.co = v * h
            change = 'retained jaw planes tapered beneath broad dwarf cheeks'
        elif group == ['head'] and count == 5:
            for vertex in vertices:
                vertex.co.x *= .88
                vertex.co.y = .077 * h + (vertex.co.y - .077 * h) * .66
            change = 'nose projection softened while retaining authored wedge topology'
        elif group == ['head'] and count in (6, 4):
            for vertex in vertices:
                vertex.co.z = center.z * h + (vertex.co.z - center.z * h) * 1.25
            change = 'eye opening expanded vertically without moving eye centers'
        elif group == ['head'] and count == 15 and center.z > .9:
            for vertex in vertices:
                vertex.co.z = center.z * h + (vertex.co.z - center.z * h) * .65 - .003 * h
                vertex.co.y = center.y * h + (vertex.co.y - center.y * h) * .70
            change = 'brows shaped into thinner expressive arches'
        elif group == ['head'] and count == 15 and center.z < .9:
            for vertex in vertices:
                t = min(1, abs(vertex.co.x / h) / .029)
                vertex.co.z += h * (.001 + (.004 if uid.endswith('ranger') else .0015) * t)
            change = 'mouth corners shaped for individual expression'
        elif group in (['hand_l'], ['hand_r']) and count == 70:
            for vertex in vertices:
                for axis in (0, 1):
                    radius = (part['bounds_max_m'][axis] - part['bounds_min_m'][axis]) / 2
                    delta = vertex.co[axis] - center[axis] * h
                    vertex.co[axis] = center[axis] * h + math.copysign((abs(delta) / radius) ** .80 * radius, delta)
            change = 'palms flattened across supported grip while retaining skin weights'
        elif group == ['pelvis'] and count == 24 and center.z < .45:
            for vertex in vertices:
                v = vertex.co / h
                low = max(0, min(1, (.477 - v.z) / .167))
                v.x *= 1 - .09 * low
                v.y += .014 * low * (1 - min(1, abs(v.x) / .20))
                vertex.co = v * h
            change = 'apron and coat hems curved away from knees with separated lower folds'
        elif group in (['clavicle_l'], ['clavicle_r']) and count == 24:
            for vertex in vertices:
                v = vertex.co / h
                low = max(0, min(1, (.798 - v.z) / .078))
                v.y *= 1 - .13 * low
                v.x = center.x + (v.x - center.x) * (1 - .06 * low)
                vertex.co = v * h
            change = 'shoulder shell bottom tucked toward arm to reveal head and elbow'
        elif uid.endswith('guardian') and group == ['head'] and count == 30:
            for vertex in vertices:
                v = vertex.co / h
                v.x = center.x + (v.x - center.x) * .80
                v.y = center.y + (v.y - center.y) * .72
                v.z += .009 * max(0, min(1, (.82 - v.z) / .1))
                vertex.co = v * h
            change = 'paired beard cores narrowed for sculpted braid relief and shoulder clearance'
        elif uid.endswith('guardian') and group == ['head'] and count in (64, 24):
            for vertex in vertices:
                v = vertex.co / h
                if v.y > 0:
                    v.z += .005 * min(1, v.y / .08)
                vertex.co = v * h
            change = 'front helmet arch raised above the visible brows'
        elif uid.endswith('ranger') and group == ['head'] and count == 24 and center.z > .96:
            for vertex in vertices:
                v = vertex.co / h
                v.x = center.x + (v.x - center.x) * 1.35
                vertex.co = v * h
            change = 'copper fringe locks broadened while keeping forehead goggle clear'
        elif uid.endswith('ranger') and group == ['hand_r'] and count == 114:
            target = Vector((-.370 + .105, .055, .375 + .210))
            rotate = Matrix.Rotation(math.pi / 2, 3, 'Z')
            for vertex in vertices:
                vertex.co = (target + rotate @ ((vertex.co / h - center) * 1.18)) * h
            change = 'decorative wheel rotated onto side plane and enlarged for a visible crank silhouette'
        elif uid.endswith('ranger') and group == ['hand_r'] and count == 16 and center.z > .45:
            for ring in (0, 3):
                indices = vertices[ring * 4: ring * 4 + 4]
                for vertex in indices:
                    vertex.co.x = center.x * h + (vertex.co.x - center.x * h) * .89
                    vertex.co.z = center.z * h + (vertex.co.z - center.z * h) * .97
            change = 'stock cap bevels widened without moving the supported center grip'
        elif uid.endswith('warrior') and group == ['hand_r'] and count == 16 and center.z > .60:
            remove.update(part['indices'])
            change = 'flat hammer head and bar replaced by purpose-shaped chamfered forge housing'
        elif uid.endswith('warrior') and group == ['head'] and count == 119:
            for vertex in vertices:
                v = vertex.co / h
                v.x *= 1.16
                v.y = -.088 + (v.y + .088) * 1.20 - .005
                v.z = .934 + (v.z - .934) * 1.16 + .009
                vertex.co = v * h
            change = 'coiled rear braid broadened and lifted clear of shoulder armor'
        if change:
            changes.append({'first_vertex': part['first_vertex'], 'count': count, 'change': change})
    if remove:
        bm = bmesh.new()
        bm.from_mesh(mesh.data)
        bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.verts[index] for index in sorted(remove)], context='VERTS')
        bm.to_mesh(mesh.data)
        bm.free()
    mesh.data.update()
    return changes


def additional_forms(unit, category):
    g = Geometry()
    uid = unit['id']
    if category == 'BODY':
        # Three shallow knuckle creases follow each existing rigidly weighted palm.
        for side, sign in (('l', 1), ('r', -1)):
            for z in (.380, .392, .404):
                x = sign * .370
                g.tube([(x - .019, .087, z), (x, .0945, z - .002), (x + .019, .087, z)],
                       [.0013, .0018, .0013], 14, 'hand_' + side, 5)
        if uid.endswith('guardian'):
            for sign in (-1, 1):
                for strand in range(3):
                    points = []
                    for index in range(19):
                        t = index / 18
                        angle = t * math.pi * 4 + strand * 2 * math.pi / 3
                        radius = .023 * (1 - .56 * t)
                        points.append((sign * (.039 + .015 * t) + math.cos(angle) * radius,
                                       .064 + .029 * math.sin(math.pi * t) + math.sin(angle) * radius * .67,
                                       .862 - .125 * t))
                    g.tube(points, [.0115 * (1 - .52 * index / 18) for index in range(19)], 7, 'head', 7)
            # Two joined swept moustache forms leave the mouth readable.
            for sign in (-1, 1):
                g.tube([(sign * .004, .088, .866), (sign * .024, .089, .862), (sign * .043, .079, .854)],
                       [.009, .012, .006], 7, 'head', 8, depth=.60)
        elif uid.endswith('ranger'):
            for sign in (-1, 1):
                for index, (x, z) in enumerate(((.032, .889), (.047, .885), (.062, .890))):
                    y = .015 + .070 * math.sqrt(1 - (x / .101) ** 2) + .002
                    g.ellipsoid((sign * x, y, z), (.0022, .0014, .0018), 7, 'head', 3, 6)
    elif category == 'COSTUME':
        if uid.endswith('guardian'):
            for z, width in ((.705, .140), (.652, .136), (.601, .125)):
                g.plate([(-width, z + .038), (0, z + .050), (width, z + .038),
                         (width * .91, z), (0, z - .010), (-width * .91, z)],
                        -.105, .014, 0, 'spine_02', bevel=.09)
            for sign in (-1, 1):
                g.tube([(sign * .050, -.010, 1.007), (sign * .047, .030, .994),
                        (sign * .032, .067, .970)], [.005, .005, .003], 2, 'head', 6)
        elif uid.endswith('ranger'):
            # Low flat case remains; the X stitches conform to its surrounding jacket.
            for sign in (-1, 1):
                g.tube([(sign * .13, -.054, .764), (sign * .075, -.102, .735),
                        (-sign * .045, -.114, .644), (-sign * .105, -.090, .56)],
                       [.0045] * 4, 3, 'spine_02', 5)
            g.plate([(-.036, .752), (.036, .752), (.026, .70), (-.026, .70)], .111, .014, 3, 'spine_03')
        else:
            # Original low crossed harness and two broad apron seam folds.
            for sign in (-1, 1):
                g.tube([(sign * .13, -.060, .759), (sign * .065, -.116, .694),
                        (-sign * .100, -.107, .565)], [.012, .013, .012], 2, 'spine_02', 6, depth=.38)
                g.tube([(sign * .054, .124, .463), (sign * .074, .126, .404),
                        (sign * .103, .122, .331)], [.0045, .004, .0025], 5, 'pelvis', 6)
    elif category == 'EQUIPMENT':
        x, y, z = -.370, .055, .375
        if uid.endswith('guardian'):
            g.loft([((x, y, z + .238), .134, .087), ((x, y, z + .247), .148, .096),
                    ((x, y, z + .263), .148, .096), ((x, y, z + .270), .135, .088)], 2, 'hand_r', 16)
            g.loft([((x, y, z + .233), .116, .073), ((x, y, z + .240), .130, .083)], 5, 'hand_r', 16)
            g.loft([((x, y, z + .322), .102, .078), ((x, y, z + .335), .099, .076)], 0, 'hand_r', 16)
        elif uid.endswith('ranger'):
            g.tube([(x + .025, y, z + .11), (x + .061, y, z + .11),
                    (x + .087, y, z + .11)], [.020, .021, .018], 5, 'hand_r', 8)
            for sign in (-1, 1):
                g.plate([(x + sign * .012, z + .105), (x + sign * .034, z + .105),
                         (x + sign * .037, z + .236), (x + sign * .022, z + .246)], y + .044, .013, 2, 'hand_r')
            for index in range(4):
                angle = index * math.pi / 2
                g.tube([(x + .105, y, z + .210),
                        (x + .105, y + .039 * math.sin(angle), z + .210 + .039 * math.cos(angle))],
                       [.006, .005], 2, 'hand_r', 6)
            g.tube([(x + .025, y, z + .210), (x + .12, y, z + .210)], [.013, .013], 5, 'hand_r', 8)
        else:
            polygon = [(x - .150, z + .245), (x + .145, z + .245), (x + .173, z + .271),
                       (x + .173, z + .382), (x + .147, z + .411), (x - .146, z + .411),
                       (x - .173, z + .382), (x - .173, z + .271)]
            g.plate(polygon, y, .213, 4, 'hand_r', bevel=.115)
            # Recessed broad forge-mark panel; deliberately no dense pseudo-text.
            g.plate([(x - .088, z + .287), (x + .088, z + .287), (x + .088, z + .344),
                     (x - .088, z + .344)], y + .109, .011, 1, 'hand_r', bevel=.14)
            for sign in (-1, 1):
                g.plate([(x + sign * .036, z + .301), (x + sign * .050, z + .314),
                         (x + sign * .036, z + .328), (x + sign * .023, z + .314)],
                        y + .117, .006, 2, 'hand_r')
        if not uid.endswith('ranger'):
            for zz in (z + .115, z + .141, z + .192):
                g.loft([((x, y, zz), .024, .024), ((x, y, zz + .012), .024, .024)], 2, 'hand_r', 10)
    return g


def append_geometry(mesh, geometry, unit):
    if not geometry.vertices:
        return
    arm = bpy.data.objects['Armature']
    extra = make_mesh(geometry, unit, arm, mesh.data.materials[0])
    extra.name = 'WC_DwarfRefinement_Additions'
    hidden, render_hidden = mesh.hide_get(), mesh.hide_render
    mesh.hide_set(False)
    bpy.ops.object.select_all(action='DESELECT')
    extra.select_set(True)
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.join()
    mesh.hide_set(hidden)
    mesh.hide_render = render_hidden


def refine(unit, out, source):
    uid = unit['id']
    export = ROOT / 'exports/heroes' / uid
    manifest = json.loads((export / 'export_manifest.json').read_text())
    if manifest['source_revision'] != 6 or sha(source) != manifest['source_sha256']:
        raise RuntimeError('Expected the inspected revision6 production source')
    if (out / 'refinement.json').exists():
        raise RuntimeError('Use fresh refinement evidence; do not overwrite history')
    shutil.copy2(source, out / 'before-source.blend')
    shutil.copy2(export / 'export_manifest.json', out / 'before-export-manifest.json')
    arm = bpy.data.objects['Armature']
    before = invariants(arm)
    changes = {}
    for prefix in ('', 'BODY_', 'COSTUME_', 'EQUIPMENT_'):
        mesh = bpy.data.objects[prefix + 'SK_' + uid]
        changes[mesh.name] = edit_islands(mesh, unit)
        categories = ('BODY', 'COSTUME', 'EQUIPMENT') if not prefix else (prefix[:-1],)
        for category in categories:
            append_geometry(mesh, additional_forms(unit, category), unit)
    if before != invariants(arm):
        raise RuntimeError('Geometry refinement changed shared rig or existing animation curves')
    use_clip(arm, 'Idle', unit_id=uid)
    candidate = out / (uid + '-update24-revision7.blend')
    camera_view(unit, 'three-quarter')
    bpy.ops.wm.save_as_mainfile(filepath=str(candidate), check_existing=False)
    render(unit, out, 'after')
    if sha(source) != manifest['source_sha256']:
        raise RuntimeError('Production source changed during isolated trial')
    write(out / 'refinement.json', {'status': 'SOURCE_REFINEMENT_RENDERED_NOT_PROMOTED',
          'unit_id': uid, 'source_before_sha256': manifest['source_sha256'], 'candidate': str(candidate),
          'candidate_sha256': sha(candidate), 'changes': changes, 'preserved_invariants': before,
          'limits': ['No current Unreal reimport', 'Continuous motion review and art acceptance pending', 'LODs not yet regenerated']})


def sample(frame, times, values):
    for index in range(1, len(times)):
        if frame <= times[index]:
            t = max(0, min(1, (frame - times[index - 1]) / max(1, times[index] - times[index - 1])))
            t = t * t * (3 - 2 * t)
            return values[index - 1] * (1 - t) + values[index] * t
    return values[-1]


def weapon_pose(unit, arm, clip, frame, end, release):
    h = unit['height_m']
    uid = unit['id']
    times = [1, max(2, release // 2), release, min(end, release + 8), end]
    def value(values):
        return sample(frame, times, values)
    if uid.endswith('warrior') and clip == 'Active':
        arm.pose.bones['spine_02'].rotation_euler.y = math.radians(value([0, -22, 24, 11, 0]))
        arm.pose.bones['spine_02'].rotation_euler.x = math.radians(value([0, -3, 4, 2, 0]))
        arm.pose.bones['head'].rotation_euler.y = math.radians(value([0, 9, -9, -4, 0]))
    elif uid.endswith('guardian') and clip == 'Active':
        arm.pose.bones['spine_02'].rotation_euler.y = 0
        arm.pose.bones['spine_02'].rotation_euler.x = math.radians(value([0, -3, 4, 1, 0]))
        arm.pose.bones['head'].rotation_euler.x = math.radians(value([0, 2, -3, -1, 0]))
    bpy.context.view_layer.update()
    spine = arm.pose.bones['spine_02']
    body = spine.matrix @ spine.bone.matrix_local.inverted()
    body_rotation = body.to_3x3()
    def position(point):
        return body @ (Vector(point) * h)
    def rotation(x=0, y=0, z=0):
        return body_rotation @ Matrix.Rotation(math.radians(z), 3, 'Z') @ Matrix.Rotation(math.radians(y), 3, 'Y') @ Matrix.Rotation(math.radians(x), 3, 'X')
    if uid.endswith('ranger'):
        active = clip == 'Active'
        pull = value([0, -.068 if active else -.025, .06 if active else .03, .015, 0])
        rise = value([0, .040 if active else .020, .040 if active else .020, .010, 0])
        turn = rotation(-76 + value([0, -10 if active else -5, -7, -2, 0]))
        target = position((-.05, .10 + pull, .58 + rise))
        support_offset = (.08, 0, .11)
        support_rotation = rotation(0, -20, 0)
    elif uid.endswith('guardian'):
        if clip == 'Active':
            target = position((-.09, .15 + value([.01, 0, 0, 0, .01]), .47 + value([0, -.003, -.008, -.003, 0])))
            turn = rotation(value([0, 4, -7, -2, 0]), 65, 0)
        else:
            target = position((-.09 + value([0, -.012, .030, .015, 0]),
                               .16 + value([0, -.014, -.035, -.010, 0]), .47 + value([0, .035, .025, .012, 0])))
            turn = rotation(value([0, 9, -20, -8, 0]), 65, value([0, -25, 27, 11, 0]))
        support_offset, support_rotation = (0, 0, .17), rotation(0, -35, 0)
    else:
        active = clip == 'Active'
        target = position((-.09 + value([0, -.005, .035, .012, 0]),
                           .16 + value([0, -.014, -.050 if active else -.025, -.010, 0]),
                           .47 + value([0, .025 if active else .105, .030 if active else .070, .014, 0])))
        turn = rotation(value([0, 5 if active else -25, -14 if active else -30, -8, 0]),
                        value([65, 65 if active else 45, 65 if active else 74, 69, 65]),
                        value([0, -27 if active else -3, 38 if active else 7, 15 if active else 3, 0]))
        support_offset, support_rotation = (0, 0, .17), rotation(0, -35, 0)
    error = place_hand(arm, 'r', target, turn, h)
    right = arm.pose.bones['hand_r']
    support = right.matrix @ right.bone.matrix_local.inverted() @ (right.bone.tail_local + Vector(support_offset) * h)
    error = max(error, place_hand(arm, 'l', support, support_rotation, h))
    return error


def refine_motion(unit, out):
    uid = unit['id']
    refined = json.loads((out / 'refinement.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=refined['candidate'])
    arm = bpy.data.objects['Armature']
    old = invariants(arm)
    manifest = json.loads((out / 'before-export-manifest.json').read_text())
    records = []
    for clip in ('Attack', 'Active'):
        spec = manifest['clips'][clip]
        start, end = spec['frames']
        action = bpy.data.actions[spec['action']]
        use_clip(arm, clip, unit_id=uid)
        baseline = {}
        for frame in range(start, end + 1):
            bpy.context.scene.frame_set(frame)
            baseline[frame] = {bone.name: (bone.rotation_euler.copy(), bone.location.copy()) for bone in arm.pose.bones}
        maximum_error = 0
        previous = {}
        for frame in range(start, end + 1):
            bpy.context.scene.frame_set(frame)
            for bone in arm.pose.bones:
                bone.rotation_euler, bone.location = baseline[frame][bone.name]
            maximum_error = max(maximum_error, weapon_pose(unit, arm, clip, frame, end, spec['release_frame']))
            for bone in arm.pose.bones:
                if bone.name in previous:
                    bone.rotation_euler.make_compatible(previous[bone.name])
                previous[bone.name] = bone.rotation_euler.copy()
                bone.keyframe_insert(data_path='rotation_euler', frame=frame, group=bone.name)
                bone.keyframe_insert(data_path='location', frame=frame, group=bone.name)
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for key in curve.keyframe_points:
                            key.interpolation = 'LINEAR'
        records.append({'clip': clip, 'frames': spec['frames'], 'release_frame': spec['release_frame'],
                        'frames_baked': end - start + 1, 'maximum_support_reach_clamp_m': maximum_error})
        if maximum_error > .025:
            index = len(list(out.glob('motion-refinement-failure*.json'))) + 1
            write(out / f'motion-refinement-failure-{index:02d}.json', records)
            raise RuntimeError(f'{uid} {clip}: support hand unreachable by {maximum_error:.5f}m')
    current = invariants(arm)
    if old['rest_skeleton_sha256'] != current['rest_skeleton_sha256']:
        raise RuntimeError('Rest rig changed during action-only refinement')
    candidate = out / (uid + '-update24-motion7.blend')
    use_clip(arm, 'Idle', unit_id=uid)
    bpy.ops.wm.save_as_mainfile(filepath=str(candidate), check_existing=False)
    refined.update(candidate=str(candidate), candidate_sha256=sha(candidate), changed_clips=records,
                   verified_candidate_invariants=current)
    write(out / 'refinement.json', refined)


def audit_and_record(unit, out):
    uid = unit['id']
    refined = json.loads((out / 'refinement.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=refined['candidate'])
    arm = bpy.data.objects['Armature']
    mesh = bpy.data.objects['SK_' + uid]
    manifest = json.loads((out / 'before-export-manifest.json').read_text())
    old_arguments = sys.argv
    try:
        sys.argv = ['inspect_scene.py', '--', '--collection', 'EXPORT', '--require-skin', '--output', str(out / 'structure-inspection.json')]
        runpy.run_path(str(ROOT / 'tools/blender/inspect_scene.py'), run_name='__main__')
    finally:
        sys.argv = old_arguments
    records, errors = [], []
    scene = bpy.context.scene
    for clip, spec in manifest['clips'].items():
        use_clip(arm, clip, unit_id=uid)
        minimum, max_width, root_drift, scale_drift = math.inf, 0, 0, 0
        for frame in range(spec['frames'][0], spec['frames'][1] + 1):
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
            geometry = evaluated.to_mesh()
            try:
                minimum = min(minimum, min(vertex.co.z for vertex in geometry.vertices))
                max_width = max(max_width, max(vertex.co.x for vertex in geometry.vertices) - min(vertex.co.x for vertex in geometry.vertices))
            finally:
                evaluated.to_mesh_clear()
            root_drift = max(root_drift, arm.pose.bones['root'].location.length)
            scale_drift = max(scale_drift, max(abs(value - 1) for bone in arm.pose.bones for value in bone.scale))
        record = {'clip': clip, 'frames_evaluated': spec['frames'][1] - spec['frames'][0] + 1,
                  'minimum_all_vertex_z_m': minimum, 'maximum_mesh_width_m': max_width,
                  'maximum_root_translation_m': root_drift, 'maximum_pose_scale_error': scale_drift}
        records.append(record)
        if minimum < -.001 or root_drift > 1e-6 or scale_drift > 1e-6:
            errors.append(f'{clip}: all-frame floor/root/scale check failed')
    write(out / 'motion-invariants.json', {'status': 'FAIL' if errors else 'PASS_ALL_FRAMES',
          'unit_id': uid, 'clips': records, 'errors': errors,
          'limits': ['Numerical deformed-mesh checks do not establish continuous visual acceptance', 'No current Unreal import/playback']})
    if errors:
        raise RuntimeError('; '.join(errors))
    # Workbench playback is a real rendering of all 60fps authored samples.
    camera_view(unit, 'three-quarter', 384)
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'TEXTURE'
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    for material in mesh.data.materials:
        if material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image and 'BaseColor' in node.image.name:
                    material.node_tree.nodes.active = node
    scene.render.image_settings.media_type = 'VIDEO'
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    clips = []
    for clip, spec in manifest['clips'].items():
        use_clip(arm, clip, unit_id=uid)
        scene.frame_start, scene.frame_end = spec['frames']
        path = out / f'continuous_{clip}.mp4'
        if path.exists():
            raise RuntimeError('Preserve existing continuous review render')
        scene.render.filepath = str(path)
        bpy.ops.render.render(animation=True)
        clips.append({'clip': clip, 'path': str(path), 'sha256': sha(path), 'source_fps': 60,
                      'frames': spec['frames'], 'release_frame': spec['release_frame'],
                      'visual_acceptance': 'not established by successful video rendering'})
    scene.render.image_settings.media_type = 'IMAGE'
    scene.render.image_settings.file_format = 'PNG'
    for clip, spec in manifest['clips'].items():
        camera_view(unit, 'three-quarter', 384)
        frames = sorted({spec['frames'][0], spec['frames'][1], spec['frames'][1] // 2,
                         spec['release_frame'] or spec['frames'][1] // 3,
                         max(1, (spec['release_frame'] or spec['frames'][1] // 2) - 6)})
        for frame in frames:
            use_clip(arm, clip, frame, unit_id=uid)
            scene.render.filepath = str(out / f'pose_{clip}_{frame:03d}.png')
            bpy.ops.render.render(write_still=True)
    write(out / 'motion-sequences.json', {'status': 'ALL_SEVEN_CLIPS_RENDERED_VISUAL_REVIEW_PENDING',
          'unit_id': uid, 'renderer': 'Blender Workbench; original textured source mesh', 'resolution': [384, 384],
          'clips': clips, 'source_fps': 60, 'rendered_frame_sampling': 'every authored frame',
          'limits': ['No listening or skill-effect synchronization review', 'No current Unreal playback acceptance']})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('inspect', 'refine', 'motion', 'record', 'export'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--ids', nargs='+', choices=IDS, default=list(IDS))
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    units = {unit['id']: unit for unit in json.loads((ROOT / 'data/units.json').read_text(encoding='utf-8'))['units']}
    for uid in args.ids:
        out = args.output.resolve() / uid
        out.mkdir(parents=True, exist_ok=True)
        source = ROOT / 'art-source/heroes' / uid / (uid + '.blend')
        bpy.ops.wm.open_mainfile(filepath=str(source))
        if args.mode == 'inspect':
            inspect(units[uid], out, source)
        elif args.mode == 'refine':
            refine(units[uid], out, source)
        elif args.mode == 'motion':
            refine_motion(units[uid], out)
        elif args.mode == 'record':
            audit_and_record(units[uid], out)
        elif args.mode == 'export':
            refined = json.loads((out / 'refinement.json').read_text())
            bpy.ops.wm.open_mainfile(filepath=refined['candidate'])
            export_revision(out, uid, Path(__file__))


if __name__ == '__main__':
    main()
