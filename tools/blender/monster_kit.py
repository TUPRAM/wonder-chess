"""Shared tools for building Wonder Chess monsters in Blender from code (owner's scripted-Blender route, 2026-10-04).

A monster is a list of shaped parts, each bound to exactly one bone and painted one colour; a skeleton; and a clip
recipe. `build` joins the parts, bakes the colour to one image, rigs, exports body.fbx and clip_<Name>.fbx, and
renders previews. Everything is in centimetres and faces -Y so Unreal imports it full size facing +Y.
"""
import math
import random
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector, noise

parts = []
scene = None


def reset(seed):
    global scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 0.01
    scene.render.fps = 30
    parts.clear()
    random.seed(seed)


def turned(turn):
    return Euler([math.radians(a) for a in turn]).to_matrix().to_4x4()


def finish(bm, bone, colour, name="part", chip=0.0, bevel=0.0, rough=0.0, smooth=False):
    """Turn a bmesh into one piece bound to one bone and painted one colour."""
    if chip:
        for vert in bm.verts:
            vert.co += Vector((random.uniform(-chip, chip), random.uniform(-chip, chip), random.uniform(-chip, chip)))
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=1, affect="EDGES", profile=0.5)
    if rough > 0:
        # Rough, hand-split surfaces: finer facets pushed in and out by layered noise.
        bmesh.ops.triangulate(bm, faces=[face for face in bm.faces if len(face.verts) > 4])
        bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=1, use_grid_fill=True)
        bm.normal_update()
        seed = Vector((random.uniform(0, 90), random.uniform(0, 90), random.uniform(0, 90)))
        for vert in bm.verts:
            vert.co += vert.normal * rough * noise.fractal(vert.co * 0.055 + seed, 1.0, 2.0, 3)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.polygons.foreach_set("use_smooth", [smooth] * len(mesh.polygons))
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.vertex_groups.new(name=bone).add(range(len(mesh.vertices)), 1.0, "REPLACE")
    paint = mesh.color_attributes.new("Paint", "FLOAT_COLOR", "POINT")
    for item in paint.data:
        item.color = (*colour, 1.0)
    parts.append(obj)
    return obj


def slab(centre, size, bone, colour, turn=(0, 0, 0), sides=8, taper=1.0, name="slab", chip=1.6, bevel=1.4, rough=1.7):
    """A many-sided plate: its outline lies in X-Z and its thickness runs along Y."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=sides, radius1=1, radius2=1, depth=1)
    bmesh.ops.rotate(bm, verts=bm.verts, matrix=Matrix.Rotation(math.radians(90), 3, "X"))
    spin = Matrix.Rotation(random.uniform(0, math.tau / sides), 3, "Y")
    for vert in bm.verts:
        vert.co = spin @ vert.co
        reach = random.uniform(0.80, 1.10) if chip else 1.0
        front = taper if vert.co.y < 0 else 1.0
        vert.co = Vector((vert.co.x * size[0] * 0.5 * reach * front, vert.co.y * size[1], vert.co.z * size[2] * 0.5 * reach * front))
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(centre)) @ turned(turn), verts=bm.verts)
    return finish(bm, bone, colour, name, chip, bevel, rough)


def block(centre, size, bone, colour, turn=(0, 0, 0), name="block", chip=1.6, bevel=1.6, rough=1.7):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=1, use_grid_fill=True)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(centre)) @ turned(turn) @ Matrix.Diagonal((*size, 1)), verts=bm.verts)
    return finish(bm, bone, colour, name, chip, bevel, rough)


def lump(centre, size, bone, colour, name="lump", detail=2, chip=0.0, rough=0.0, smooth=True, turn=(0, 0, 0), squash=None):
    """A rounded mass. `squash` (0..1) flattens everything below the middle, for caps and domes."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=detail, radius=1)
    if squash is not None:
        for vert in bm.verts:
            if vert.co.z < 0:
                vert.co.z *= squash
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(centre)) @ turned(turn) @ Matrix.Diagonal((*size, 1)), verts=bm.verts)
    return finish(bm, bone, colour, name, chip, 0, rough, smooth)


def tube(points, radii, bone, colour, sides=7, ridge=0.0, name="tube", rough=0.0, smooth=True, chip=0.0, flat=1.0):
    """A swept limb, root, horn or stalk through `points` with a radius at each. `flat` squashes the cross-section."""
    points = [Vector(p) for p in points]
    if not isinstance(radii, (list, tuple)):
        radii = [radii] * len(points)
    bm = bmesh.new()
    rings, normal = [], None
    for index, point in enumerate(points):
        ahead = (points[min(index + 1, len(points) - 1)] - points[max(index - 1, 0)]).normalized()
        if normal is None:
            normal = ahead.cross(Vector((1, 0, 0)))
            if normal.length < 0.1:
                normal = ahead.cross(Vector((0, 1, 0)))
        normal = (normal - ahead * normal.dot(ahead)).normalized()
        other = ahead.cross(normal).normalized()
        radius = radii[index] * (1 + ridge * (1 if index % 2 == 0 else -1))
        rings.append([bm.verts.new(point + (normal * math.cos(k / sides * math.tau) + other * math.sin(k / sides * math.tau) * flat) * radius)
                      for k in range(sides)])
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            bm.faces.new((a[k], a[(k + 1) % sides], b[(k + 1) % sides], b[k]))
    bm.faces.new(rings[0])
    bm.faces.new(list(reversed(rings[-1])))
    return finish(bm, bone, colour, name, chip, 0, rough, smooth)


def arc(start, end, bulge, steps=6):
    """Points from start to end bowed sideways by the vector `bulge` at the middle."""
    start, end, bulge = Vector(start), Vector(end), Vector(bulge)
    return [start.lerp(end, k / steps) + bulge * math.sin(k / steps * math.pi) for k in range(steps + 1)]


def spike(base, tip, radius, bone, colour, sides=5, name="spike"):
    return tube([base, Vector(base).lerp(Vector(tip), 0.5), tip], [radius, radius * 0.55, radius * 0.06], bone, colour, sides, name=name, smooth=False)


def pane(points, bone, colour, thick=0.8, name="pane"):
    """A thin flat plate through the given corners (a leaf, a wing panel, a shard), solid on both sides."""
    points = [Vector(p) for p in points]
    normal = Vector((0, 0, 0))
    for k in range(len(points)):
        normal += (points[k] - points[0]).cross(points[(k + 1) % len(points)] - points[0])
    normal = normal.normalized() if normal.length > 1e-6 else Vector((0, 0, 1))
    bm = bmesh.new()
    top = [bm.verts.new(p + normal * thick * 0.5) for p in points]
    bottom = [bm.verts.new(p - normal * thick * 0.5) for p in points]
    bm.faces.new(top)
    bm.faces.new(list(reversed(bottom)))
    for k in range(len(points)):
        n = (k + 1) % len(points)
        bm.faces.new((top[n], top[k], bottom[k], bottom[n]))
    return finish(bm, bone, colour, name)


def leaf(base, tip, width, bone, colour, name="leaf"):
    base, tip = Vector(base), Vector(tip)
    side = (tip - base).cross(Vector((0.3, 0.2, 1))).normalized() * width * 0.5
    middle = base.lerp(tip, 0.45)
    return pane([base, middle + side, tip, middle - side], bone, colour, 0.7, name)


# ---- Animation recipes. Turns are world-axis degrees and shifts are centimetres, both relative to the rest pose. ---
def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def wave(bone, turn=(0, 0, 0), shift=(0, 0, 0), phase=0.0, cycles=1):
    return ("wave", bone, turn, shift, phase, cycles)


def spin(bone, turns=1):
    return ("spin", bone, turns)


def leg(upper, lower=None, foot=None, phase=0.0, swing=27, bend=30, bend_sign=1):
    return ("leg", upper, lower, foot, phase, swing, bend, bend_sign)


def keys(bone, *frames):
    """frames: (time 0..1, turn, shift) with shift optional."""
    return ("keys", bone, [(f[0], f[1], f[2] if len(f) > 2 else (0, 0, 0)) for f in frames])


def strike(bone, wind, hit, shift_wind=(0, 0, 0), shift_hit=(0, 0, 0)):
    soft = tuple(v * 0.7 for v in hit)
    return keys(bone, (0, (0, 0, 0)), (0.32, wind, shift_wind), (0.5, hit, shift_hit), (0.64, soft, tuple(v * 0.8 for v in shift_hit)), (1, (0, 0, 0)))


def hold(bone, turn, shift=(0, 0, 0)):
    return keys(bone, (0, (0, 0, 0)), (0.2, turn, shift), (0.82, turn, shift), (1, (0, 0, 0)))


def jolt(bone, turn, shift=(0, 0, 0)):
    return keys(bone, (0, (0, 0, 0)), (0.25, turn, shift), (1, (0, 0, 0)))


def fall(bone, turn, shift=(0, 0, 0), at=0.6):
    return keys(bone, (0, (0, 0, 0)), (at, turn, shift), (1, turn, shift))


def pose_at(entries, t):
    pose = {}

    def add(bone, turn, shift):
        old = pose.get(bone, ((0, 0, 0), (0, 0, 0)))
        pose[bone] = (tuple(a + b for a, b in zip(old[0], turn)), tuple(a + b for a, b in zip(old[1], shift)))

    for entry in entries:
        kind = entry[0]
        if kind == "wave":
            _, bone, turn, shift, phase, cycles = entry
            value = math.sin(t * math.tau * cycles + phase)
            add(bone, tuple(a * value for a in turn), tuple(a * value for a in shift))
        elif kind == "spin":
            add(entry[1], (0, 0, 360 * entry[2] * t), (0, 0, 0))
        elif kind == "leg":
            _, upper, lower, foot, phase, swing, bend, sign = entry
            angle = t * math.tau + phase
            lift = max(0.0, -math.cos(angle))    # the joint folds while the limb comes forward
            add(upper, (swing * math.sin(angle), 0, 0), (0, 0, 0))
            if lower:
                add(lower, (bend * lift * sign, 0, 0), (0, 0, 0))
            if foot:
                add(foot, (-0.5 * bend * lift * sign, 0, 0), (0, 0, 0))
        else:
            _, bone, frames = entry
            for (t0, turn0, shift0), (t1, turn1, shift1) in zip(frames, frames[1:]):
                if t <= t1 or (t1, turn1, shift1) == frames[-1]:
                    k = ease((t - t0) / max(1e-6, t1 - t0))
                    add(bone, tuple(a + (b - a) * k for a, b in zip(turn0, turn1)), tuple(a + (b - a) * k for a, b in zip(shift0, shift1)))
                    break
    return pose


LENGTHS = {"Idle": 75, "Move": 28, "Attack": 24, "Cast": 38, "Hit": 12, "Defeat": 34}


def build(name, out, bones, clips, height, lengths=None, texture=2048):
    """Join the parts, bake colour, rig, export and render. `clips` maps clip name to a list of recipe entries."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    lengths = {**LENGTHS, **(lengths or {})}
    always = clips.get("Always", [])
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    body = bpy.context.view_layer.objects.active
    body.name = name
    body.data.name = name
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003)
    bpy.ops.object.mode_set(mode="OBJECT")

    image = bpy.data.images.new(f"T_{name}_Color", texture, texture, alpha=False)
    painted = bpy.data.materials.new(name + "Bake")
    painted.use_nodes = True
    nodes, links = painted.node_tree.nodes, painted.node_tree.links
    nodes.clear()
    paint = nodes.new("ShaderNodeVertexColor"); paint.layer_name = "Paint"
    coords = nodes.new("ShaderNodeTexCoord")
    grain = nodes.new("ShaderNodeTexNoise"); grain.inputs["Scale"].default_value = 0.09; grain.inputs["Detail"].default_value = 8
    fine = nodes.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 0.9; fine.inputs["Detail"].default_value = 4
    shade = nodes.new("ShaderNodeAmbientOcclusion"); shade.inputs["Distance"].default_value = 0.06 * height + 10; shade.samples = 16
    deep = nodes.new("ShaderNodeValToRGB"); deep.color_ramp.elements[0].position = 0.25; deep.color_ramp.elements[1].position = 0.95
    deep.color_ramp.elements[0].color = (0.20, 0.21, 0.26, 1)
    geometry = nodes.new("ShaderNodeNewGeometry")
    edge = nodes.new("ShaderNodeValToRGB"); edge.color_ramp.elements[0].position = 0.50; edge.color_ramp.elements[1].position = 0.60
    edge.color_ramp.elements[0].color = (1, 1, 1, 1); edge.color_ramp.elements[1].color = (1.9, 1.9, 1.85, 1)
    ramp = nodes.new("ShaderNodeMapRange"); ramp.inputs["To Min"].default_value = 0.6; ramp.inputs["To Max"].default_value = 1.45
    ramp2 = nodes.new("ShaderNodeMapRange"); ramp2.inputs["To Min"].default_value = 0.9; ramp2.inputs["To Max"].default_value = 1.1

    def times(a, b):
        node = nodes.new("ShaderNodeMixRGB"); node.blend_type = "MULTIPLY"; node.inputs["Fac"].default_value = 1
        links.new(a, node.inputs["Color1"]); links.new(b, node.inputs["Color2"])
        return node.outputs["Color"]

    links.new(coords.outputs["Object"], grain.inputs["Vector"]); links.new(coords.outputs["Object"], fine.inputs["Vector"])
    links.new(grain.outputs["Fac"], ramp.inputs["Value"]); links.new(fine.outputs["Fac"], ramp2.inputs["Value"])
    links.new(shade.outputs["AO"], deep.inputs["Fac"]); links.new(geometry.outputs["Pointiness"], edge.inputs["Fac"])
    colour = times(paint.outputs["Color"], ramp.outputs["Result"])
    colour = times(colour, ramp2.outputs["Result"])
    colour = times(colour, deep.outputs["Color"])
    colour = times(colour, edge.outputs["Color"])
    glow = nodes.new("ShaderNodeEmission"); links.new(colour, glow.inputs["Color"])
    output = nodes.new("ShaderNodeOutputMaterial"); links.new(glow.outputs["Emission"], output.inputs["Surface"])
    target = nodes.new("ShaderNodeTexImage"); target.image = image; nodes.active = target
    body.data.materials.append(painted)
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.cycles.device = "CPU"
    scene.render.bake.margin = 6
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.bake(type="EMIT")
    image.filepath_raw = str(out / f"T_{name}_Color.png")
    image.file_format = "PNG"
    image.save()
    final = bpy.data.materials.new("M_" + name)
    final.use_nodes = True
    shader = final.node_tree.nodes["Principled BSDF"]
    sample = final.node_tree.nodes.new("ShaderNodeTexImage"); sample.image = image
    final.node_tree.links.new(sample.outputs["Color"], shader.inputs["Base Color"])
    shader.inputs["Roughness"].default_value = 0.8
    body.data.materials.clear()
    body.data.materials.append(final)

    if bones is None:
        # A static prop (projectile, debris, effect piece): no skeleton, one mesh file.
        bpy.ops.object.select_all(action="DESELECT")
        body.select_set(True)
        bpy.context.view_layer.objects.active = body
        bpy.ops.export_scene.fbx(filepath=str(out / f"{name}.fbx"), use_selection=True, object_types={"MESH"}, path_mode="COPY", embed_textures=True,
                                 mesh_smooth_type="FACE", axis_forward="-Z", axis_up="Y")
        print("PROP_BUILT", name, len(body.data.polygons), "faces", flush=True)
        return

    armature = bpy.data.armatures.new("Armature")
    rig = bpy.data.objects.new("Armature", armature)
    scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    for bone_name, (head, tail, parent) in bones.items():
        bone = armature.edit_bones.new(bone_name)
        bone.head, bone.tail = head, tail
        if parent:
            bone.parent = armature.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    missing = {group.name for group in body.vertex_groups} - set(bones)
    if missing:
        raise RuntimeError(f"{name}: parts are bound to bones that do not exist: {sorted(missing)}")
    body.parent = rig
    body.modifiers.new("Armature", "ARMATURE").object = rig
    rest = {bone.name: bone.matrix_local.to_3x3() for bone in armature.bones}
    for bone in rig.pose.bones:
        bone.rotation_mode = "QUATERNION"

    def apply(pose):
        for bone in rig.pose.bones:
            turn, shift = pose.get(bone.name, ((0, 0, 0), (0, 0, 0)))
            frame = rest[bone.name]
            bone.rotation_quaternion = (frame.inverted() @ Euler([math.radians(a) for a in turn]).to_matrix() @ frame).to_quaternion()
            bone.location = frame.inverted() @ Vector(shift)

    def export(path, with_mesh, animated):
        bpy.ops.object.select_all(action="DESELECT")
        rig.select_set(True)
        if with_mesh:
            body.select_set(True)
        bpy.context.view_layer.objects.active = rig
        bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={"ARMATURE", "MESH"} if with_mesh else {"ARMATURE"},
                                 add_leaf_bones=False, bake_anim=animated, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
                                 bake_anim_simplify_factor=0.0, bake_anim_force_startend_keying=True, path_mode="COPY", embed_textures=True,
                                 mesh_smooth_type="FACE", use_armature_deform_only=True, axis_forward="-Z", axis_up="Y")

    apply({})
    export(out / "body.fbx", True, False)
    rig.animation_data_create()
    for clip in ("Idle", "Move", "Attack", "Cast", "Hit", "Defeat"):
        entries = list(clips.get(clip, [])) + (list(always) if clip != "Defeat" else [])
        frames = lengths[clip]
        rig.animation_data.action = bpy.data.actions.new(clip)
        for frame in range(frames + 1):
            apply(pose_at(entries, frame / frames))
            for bone in rig.pose.bones:
                bone.keyframe_insert("rotation_quaternion", frame=frame)
                bone.keyframe_insert("location", frame=frame)
        scene.frame_start, scene.frame_end = 0, frames
        export(out / f"clip_{clip}.fbx", False, True)

    world = bpy.data.worlds.new("World"); scene.world = world; world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.57, 0.6, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sun.data.energy = 3.2
    sun.rotation_euler = (math.radians(48), 0, math.radians(-35)); scene.collection.objects.link(sun)
    floor_mesh = bpy.data.meshes.new("Floor"); floor_bm = bmesh.new(); bmesh.ops.create_grid(floor_bm, x_segments=1, y_segments=1, size=1500)
    floor_bm.to_mesh(floor_mesh); floor = bpy.data.objects.new("Floor", floor_mesh); scene.collection.objects.link(floor)
    ground = bpy.data.materials.new("Ground"); ground.use_nodes = True
    ground.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.42, 0.38, 0.32, 1); floor.data.materials.append(ground)
    camera = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera")); scene.collection.objects.link(camera); scene.camera = camera
    camera.data.lens = 50; camera.data.clip_end = 9000
    scene.render.resolution_x, scene.render.resolution_y = 520, 440
    scene.cycles.samples = 32
    try:
        preferences = bpy.context.preferences.addons["cycles"].preferences
        preferences.compute_device_type = "OPTIX"; preferences.get_devices()
        for device in preferences.devices:
            device.use = True
        scene.cycles.device = "GPU"
    except Exception:
        scene.cycles.device = "CPU"
    distance = height * 3.1 + 90
    for label, angle, clip, at in (("front", 28, None, 0), ("side", 90, None, 0), ("back", 205, None, 0), ("attack", 55, "Attack", 0.5),
                                   ("cast", 40, "Cast", 0.5), ("defeat", 55, "Defeat", 1.0)):
        rig.animation_data.action = bpy.data.actions[clip] if clip else None
        if clip is None:
            apply({})
        scene.frame_set(int(lengths[clip] * at) if clip else 0)
        camera.location = (distance * math.sin(math.radians(angle)), -distance * math.cos(math.radians(angle)), height * 1.05 + 30)
        camera.rotation_euler = (Vector((0, 0, height * 0.5)) - camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out / f"preview_{label}.png")
        bpy.ops.render.render(write_still=True)
    rig.animation_data.action = bpy.data.actions["Idle"]
    bpy.ops.wm.save_as_mainfile(filepath=str(out / f"{name}.blend"))
    print("MONSTER_BUILT", name, len(body.data.polygons), "faces", len(bones), "bones", flush=True)
