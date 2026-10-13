"""Rig and animate the Tide Caller's Meshy model in Blender (it has no legs, so library rigs do not fit it).

Run:  blender -b -P tools/blender/rig_tide_caller.py -- <model.glb> <output folder>
Builds a skeleton (hips, spine, chest, neck, head, two three-bone arms, a three-bone skirt of water, and one bone for
the loose droplets beside each hand), binds the mesh, writes six clips and exports body.fbx plus clip_<Name>.fbx.
The model is brought to centimetres facing -Y, standing on the floor. Candidate for owner review, not approved art.
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from monster_kit import fall, hold, jolt, keys, pose_at, strike, wave  # noqa: E402

source, out = Path(sys.argv[-2]), Path(sys.argv[-1])
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30
bpy.ops.import_scene.gltf(filepath=str(source))
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 0.01
meshes = [o for o in scene.objects if o.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for obj in meshes:
    obj.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
world_matrix = body.matrix_world.copy()
body.parent = None
body.matrix_world = world_matrix
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
# Weld the seams the file format splits, so the body is one surface and the droplets are separate pieces.
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.0002)
bpy.ops.object.mode_set(mode="OBJECT")
low = min(v.co.z for v in body.data.vertices)
tall = max(v.co.z for v in body.data.vertices) - low
K = 219.0 / tall                            # about 2.2 m tall
UNIT = tall / 1.902                         # the probe measured the model as 1.902 units tall
for vertex in body.data.vertices:
    vertex.co = Vector((vertex.co.x * K, vertex.co.y * K, (vertex.co.z - low) * K))
body.data.update()
K = 115.0 * 219.0 / (1.902 * 115.0)         # centimetres per probe unit
print("SIZE", tall, [round(max(getattr(v.co, a) for v in body.data.vertices) - min(getattr(v.co, a) for v in body.data.vertices)) for a in "xyz"], flush=True)
for other in [o for o in scene.objects if o != body]:
    bpy.data.objects.remove(other)
body.name = "TideCaller"
for index, image in enumerate(bpy.data.images):
    if image.size[0] and image.packed_file:
        image.filepath_raw = str(out / f"T_TideCaller_{index}.png")
        image.file_format = "PNG"
        image.save()


def cm(x, y, z):
    return Vector((x * K, y * K, (z + 0.952) * K))


# Loose pieces: the droplets that float beside each hand are separate islands of the mesh.
bm = bmesh.new()
bm.from_mesh(body.data)
bm.verts.ensure_lookup_table()
seen, islands = set(), []
for start in bm.verts:
    if start.index in seen:
        continue
    stack, island = [start], []
    seen.add(start.index)
    while stack:
        vert = stack.pop()
        island.append(vert.index)
        for edge in vert.link_edges:
            other = edge.other_vert(vert)
            if other.index not in seen:
                seen.add(other.index)
                stack.append(other)
    islands.append(island)
bm.free()
islands.sort(key=len, reverse=True)
drops = {"DropLeft": [], "DropRight": []}
for island in islands[1:]:
    centre = sum((body.data.vertices[i].co for i in island), Vector()) / len(island)
    drops["DropLeft" if centre.x > 0 else "DropRight"] += island
print("ISLANDS", [len(i) for i in islands[:8]], {k: len(v) for k, v in drops.items()}, flush=True)

bones = {"Hips": (cm(0, 0, -0.26), cm(0, 0, -0.12), None), "Spine": (cm(0, 0, -0.12), cm(0, 0, 0.18), "Hips"), "Chest": (cm(0, 0, 0.18), cm(0, 0, 0.52), "Spine"),
         "Neck": (cm(0, 0, 0.52), cm(0, -0.03, 0.66), "Chest"), "Head": (cm(0, -0.03, 0.66), cm(0, -0.06, 0.95), "Neck"),
         "Skirt1": (cm(0, 0, -0.26), cm(0, 0, -0.52), "Hips"), "Skirt2": (cm(0, 0, -0.52), cm(0, 0, -0.76), "Skirt1"), "Skirt3": (cm(0, 0, -0.76), cm(0, 0, -0.95), "Skirt2")}
for side, word in ((1, "Left"), (-1, "Right")):
    shoulder, elbow, wrist, tip = cm(side * 0.30, 0, 0.55), cm(side * 0.46, 0, 0.24), cm(side * 0.555, -0.01, 0.02), cm(side * 0.575, -0.02, -0.24)
    bones[word + "Arm"] = (shoulder, elbow, "Chest")
    bones[word + "ForeArm"] = (elbow, wrist, word + "Arm")
    bones[word + "Hand"] = (wrist, tip, word + "ForeArm")
    bones["Drop" + word] = (cm(side * 0.36, -0.02, -0.02), cm(side * 0.36, -0.02, -0.22), "Hips")
armature = bpy.data.armatures.new("Armature")
rig = bpy.data.objects.new("Armature", armature)
scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="EDIT")
for name, (head, tail, parent) in bones.items():
    bone = armature.edit_bones.new(name)
    bone.head, bone.tail = head, tail
    if parent:
        bone.parent = armature.edit_bones[parent]
    bone.use_deform = not name.startswith("Drop") or True
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type="ARMATURE_AUTO")
weighted = sum(1 for v in body.data.vertices if any(g.weight > 0.01 for g in v.groups))
print("AUTO_WEIGHTED", weighted, "of", len(body.data.vertices), flush=True)
if weighted < len(body.data.vertices) * 0.9:
    # Bone heat failed (it does on open or self-crossing meshes): weight every vertex by its nearest bones instead.
    for group in list(body.vertex_groups):
        body.vertex_groups.remove(group)
    groups = {name: body.vertex_groups.new(name=name) for name in bones}
    for vertex in body.data.vertices:
        near = []
        for name, (head, tail, _) in bones.items():
            if name.startswith("Drop"):
                continue
            along = tail - head
            t = max(0.0, min(1.0, (vertex.co - head).dot(along) / along.length_squared))
            near.append(((vertex.co - (head + along * t)).length, name))
        near.sort()
        picks = [(1.0 / max(d, 0.5) ** 4, name) for d, name in near[:3]]
        total = sum(w for w, _ in picks)
        for w, name in picks:
            groups[name].add([vertex.index], w / total, "REPLACE")
# The droplets follow their own bone and nothing else.
for name, indices in drops.items():
    if not indices:
        continue
    for group in body.vertex_groups:
        group.remove(indices)
    (body.vertex_groups.get(name) or body.vertex_groups.new(name=name)).add(indices, 1.0, "REPLACE")
# The base of the skirt stays planted: the lowest ring of vertices belongs to the last skirt bone alone.

rest = {bone.name: bone.matrix_local.to_3x3() for bone in armature.bones}
for bone in rig.pose.bones:
    bone.rotation_mode = "QUATERNION"


def apply(pose):
    for bone in rig.pose.bones:
        turn, shift = pose.get(bone.name, ((0, 0, 0), (0, 0, 0)))
        frame = rest[bone.name]
        bone.rotation_quaternion = (frame.inverted() @ Euler([math.radians(a) for a in turn]).to_matrix() @ frame).to_quaternion()
        bone.location = frame.inverted() @ Vector(shift)


def still(bone, turn, shift=(0, 0, 0)):
    return keys(bone, (0, turn, shift), (1, turn, shift))


def both(bone, turn, make=still, **more):
    """The same pose on both arms, mirrored: sideways and twisting turns change sign on the right."""
    x, y, z = turn
    return [make("Left" + bone, (x, y, z), **more), make("Right" + bone, (x, -y, -z), **more)]


PI = math.pi
# Turns are world-axis degrees: about X, negative lifts an arm forward and positive leans the body forward; about Y,
# negative lifts the left arm out sideways; about Z twists.
CLIPS = {
    "Idle": (90, both("Arm", (-6, -8, 0)) + [
        wave("Spine", (1.5, 0, 2.5), (0, 0, 1.5)), wave("Chest", (2, 0, -2), phase=0.8), wave("Neck", (2, 0, 3), phase=1.4), wave("Head", (2, 0, 4), phase=1.9),
        wave("LeftArm", (3, -5, 0), phase=0.3), wave("RightArm", (3, 5, 0), phase=0.9), wave("LeftForeArm", (-7, -3, 0), phase=1.0), wave("RightForeArm", (-7, 3, 0), phase=1.6),
        wave("LeftHand", (-8, 0, 0), phase=1.7), wave("RightHand", (-8, 0, 0), phase=2.3),
        wave("Skirt1", (0, 3, 0), phase=0.5), wave("Skirt2", (0, -5, 3), phase=1.4), wave("Skirt2", (4, 0, 0), cycles=2),
        wave("DropLeft", (0, 0, 0), (0, 0, 6), cycles=2), wave("DropRight", (0, 0, 0), (0, 0, 6), cycles=2, phase=2.0), wave("DropLeft", (0, 0, 25)), wave("DropRight", (0, 0, -25))]),
    # Gliding: leaning into the motion, arms and skirt streaming behind, the whole body rising and falling like a swell.
    "Move": (40, both("Arm", (28, -10, 0)) + both("ForeArm", (14, 0, 0)) + [
        still("Hips", (9, 0, 0)), still("Chest", (5, 0, 0)), still("Head", (-10, 0, 0)), still("Skirt2", (10, 0, 0)), still("Skirt3", (-14, 0, 0)),
        wave("Hips", (0, 0, 0), (0, 0, 4), cycles=2), wave("Spine", (2, 0, 4)), wave("Chest", (0, 0, -5), phase=0.6),
        wave("LeftArm", (8, 0, 0), cycles=2, phase=0.4), wave("RightArm", (8, 0, 0), cycles=2, phase=1.2), wave("LeftHand", (12, 0, 0), cycles=2, phase=1.0),
        wave("RightHand", (12, 0, 0), cycles=2, phase=1.8), wave("Skirt1", (0, 4, 0), cycles=2), wave("Skirt2", (6, -6, 0), cycles=2, phase=1.0),
        wave("DropLeft", (0, 0, 0), (0, 10, 5), cycles=2), wave("DropRight", (0, 0, 0), (0, 10, 5), cycles=2, phase=1.5)]),
    # The right arm draws back, gathering water, then whips forward and lets it fly.
    "Attack": (24, [
        strike("RightArm", (48, 14, 0), (-104, 6, 0)), strike("RightForeArm", (-58, 0, 0), (-8, 0, 0)), strike("RightHand", (-30, 0, 0), (26, 0, 0)),
        strike("LeftArm", (-24, -16, 0), (22, -24, 0)), strike("LeftForeArm", (-24, 0, 0), (0, 0, 0)),
        strike("Chest", (-6, 0, -22), (12, 0, 24)), strike("Spine", (-5, 0, -8), (9, 0, 10)), strike("Head", (0, 0, 14), (-6, 0, -12)),
        strike("Hips", (-3, 0, 0), (6, 0, 0), (0, 5, 2), (0, -10, -2)), strike("Skirt2", (-8, 0, 0), (12, 0, 0)), strike("DropRight", (0, 0, 0), (0, 0, 0), (0, 10, 12), (0, -40, 30))]),
    # The tide: both arms sweep up overhead as the body swells, then drive forward and down together.
    "Cast": (48, [
        keys("LeftArm", (0, (0, 0, 0)), (0.36, (-168, -22, 0)), (0.54, (-78, -8, 0)), (0.8, (-70, -8, 0)), (1, (0, 0, 0))),
        keys("RightArm", (0, (0, 0, 0)), (0.36, (-168, 22, 0)), (0.54, (-78, 8, 0)), (0.8, (-70, 8, 0)), (1, (0, 0, 0))),
        keys("LeftForeArm", (0, (0, 0, 0)), (0.2, (-40, 0, 0)), (0.36, (-10, 0, 0)), (0.54, (-18, 0, 0)), (1, (0, 0, 0))),
        keys("RightForeArm", (0, (0, 0, 0)), (0.2, (-40, 0, 0)), (0.36, (-10, 0, 0)), (0.54, (-18, 0, 0)), (1, (0, 0, 0))),
        keys("LeftHand", (0, (0, 0, 0)), (0.36, (-30, 0, 0)), (0.54, (40, 0, 0)), (1, (0, 0, 0))), keys("RightHand", (0, (0, 0, 0)), (0.36, (-30, 0, 0)), (0.54, (40, 0, 0)), (1, (0, 0, 0))),
        keys("Chest", (0, (0, 0, 0)), (0.36, (-16, 0, 0)), (0.54, (24, 0, 0)), (0.8, (20, 0, 0)), (1, (0, 0, 0))),
        keys("Spine", (0, (0, 0, 0)), (0.36, (-8, 0, 0)), (0.54, (12, 0, 0)), (0.8, (10, 0, 0)), (1, (0, 0, 0))),
        keys("Head", (0, (0, 0, 0)), (0.36, (-20, 0, 0)), (0.54, (10, 0, 0)), (1, (0, 0, 0))),
        keys("Hips", (0, (0, 0, 0)), (0.36, (0, 0, 0), (0, 4, 16)), (0.54, (4, 0, 0), (0, -10, -4)), (0.8, (4, 0, 0), (0, -8, -4)), (1, (0, 0, 0))),
        keys("Skirt2", (0, (0, 0, 0)), (0.36, (-12, 0, 0)), (0.54, (16, 0, 0)), (1, (0, 0, 0))), wave("Skirt1", (0, 6, 0), cycles=3), wave("Skirt2", (0, -8, 0), cycles=3, phase=1),
        keys("DropLeft", (0, (0, 0, 0)), (0.36, (0, 0, 120), (-10, 0, 110)), (0.54, (0, 0, 200), (0, -50, 60)), (1, (0, 0, 360))),
        keys("DropRight", (0, (0, 0, 0)), (0.36, (0, 0, -120), (10, 0, 110)), (0.54, (0, 0, -200), (0, -50, 60)), (1, (0, 0, -360)))]),
    "Hit": (12, [jolt("Chest", (-14, 0, 8), (0, 6, 0)), jolt("Spine", (-7, 0, 4)), jolt("Head", (-16, 0, 0)), jolt("LeftArm", (-10, -22, 0)), jolt("RightArm", (-10, 22, 0)),
                 jolt("Skirt2", (10, 0, 0)), jolt("DropLeft", (0, 0, 0), (8, 6, 10)), jolt("DropRight", (0, 0, 0), (-8, 6, 10))]),
    # It loses its shape: the body bows, the arms drop, and the whole figure sinks into the stone like spilled water.
    "Defeat": (38, [
        keys("Hips", (0, (0, 0, 0)), (0.25, (0, 0, 0), (0, 0, 8)), (0.9, (0, 0, 0), (0, 0, -205)), (1, (0, 0, 0), (0, 0, -205))),
        fall("Spine", (26, 0, 6), at=0.5), fall("Chest", (34, 0, -8), at=0.6), fall("Neck", (20, 0, 0), at=0.6), fall("Head", (28, 0, 10), at=0.6),
        fall("LeftArm", (10, 26, 0), at=0.5), fall("RightArm", (10, -26, 0), at=0.5), fall("LeftForeArm", (-30, 0, 0), at=0.6), fall("RightForeArm", (-30, 0, 0), at=0.6),
        fall("DropLeft", (0, 0, 0), (0, 0, -40), at=0.4), fall("DropRight", (0, 0, 0), (0, 0, -40), at=0.4), wave("Skirt2", (0, 6, 0), cycles=2)]),
}


def export(path, with_mesh, animated):
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    if with_mesh:
        body.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={"ARMATURE", "MESH"} if with_mesh else {"ARMATURE"},
                             add_leaf_bones=False, bake_anim=animated, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
                             bake_anim_simplify_factor=0.0, bake_anim_force_startend_keying=True, path_mode="COPY", embed_textures=True,
                             mesh_smooth_type="OFF", use_armature_deform_only=True, axis_forward="-Z", axis_up="Y")


apply({})
export(out / "body.fbx", True, False)
rig.animation_data_create()
for clip, (frames, entries) in CLIPS.items():
    rig.animation_data.action = bpy.data.actions.new(clip)
    for frame in range(frames + 1):
        apply(pose_at(entries, frame / frames))
        for bone in rig.pose.bones:
            bone.keyframe_insert("rotation_quaternion", frame=frame)
            bone.keyframe_insert("location", frame=frame)
    scene.frame_start, scene.frame_end = 0, frames
    export(out / f"clip_{clip}.fbx", False, True)

# Preview renders to judge the deformation.
world = bpy.data.worlds.new("World"); scene.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.6, 0.6, 0.62, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.2
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sun.data.energy = 2.5; sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
scene.collection.objects.link(sun)
camera = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera")); scene.collection.objects.link(camera); scene.camera = camera
camera.data.lens = 50; camera.data.clip_end = 9000
engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
scene.render.resolution_x, scene.render.resolution_y = 480, 560
for label, clip, at, angle in (("idle", "Idle", 0.25, 25), ("move", "Move", 0.3, 70), ("attack_wind", "Attack", 0.32, 40), ("attack_hit", "Attack", 0.5, 40),
                               ("cast_up", "Cast", 0.36, 30), ("cast_down", "Cast", 0.56, 30), ("hit", "Hit", 0.25, 40), ("defeat", "Defeat", 0.55, 40)):
    rig.animation_data.action = bpy.data.actions[clip]
    scene.frame_set(int(CLIPS[clip][0] * at))
    camera.location = (430 * math.sin(math.radians(angle)), -430 * math.cos(math.radians(angle)), 170)
    camera.rotation_euler = (Vector((0, 0, 115)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(out / f"preview_{label}.png")
    bpy.ops.render.render(write_still=True)
rig.animation_data.action = bpy.data.actions["Idle"]
bpy.ops.wm.save_as_mainfile(filepath=str(out / "tide_caller.blend"))
print("TIDE_CALLER_RIGGED", len(body.data.vertices), "vertices", len(bones), "bones", flush=True)
