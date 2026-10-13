"""Build the Slate Ram monster in Blender from code: stone slabs, a skeleton, baked colour and six animation clips.

Run:  blender -b -P tools/blender/build_slate_ram.py -- <output folder>
Writes body.fbx, clip_<Name>.fbx, slate_ram.blend, the baked colour image and preview renders. Pilot candidate for
the owner's "scripted Blender" monster route (2026-10-04); not approved art.

The model is built in centimetres, facing -Y, so that Unreal imports it at full size facing +Y.
"""
import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector, noise

OUT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
random.seed(417)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 0.01
scene.render.fps = 30

SLATE = [(0.078, 0.088, 0.108), (0.102, 0.114, 0.138), (0.060, 0.068, 0.086), (0.128, 0.138, 0.158)]
HORN = (0.400, 0.350, 0.260)
HOOF = (0.050, 0.050, 0.058)
MOSS = (0.170, 0.380, 0.100)
EYE = (0.250, 0.850, 1.000)
SOCKET = (0.020, 0.022, 0.030)
QUARTZ = (0.780, 0.800, 0.840)
parts = []


def finish(bm, bone, colour, name, chip=1.6, bevel=1.4, rough=1.7):
    """Turn a bmesh into a chipped, bevelled stone piece bound to one bone and painted one colour."""
    for vert in bm.verts:
        vert.co += Vector((random.uniform(-chip, chip), random.uniform(-chip, chip), random.uniform(-chip, chip)))
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=1, affect="EDGES", profile=0.5)
    if rough > 0:
        # Break the flat faces into rough, hand-split stone: finer facets pushed in and out by layered noise.
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
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.vertex_groups.new(name=bone).add(range(len(mesh.vertices)), 1.0, "REPLACE")
    paint = mesh.color_attributes.new("Paint", "FLOAT_COLOR", "POINT")
    for item in paint.data:
        item.color = (*colour, 1.0)
    parts.append(obj)
    return obj


def slab(centre, size, bone, colour=None, turn=(0, 0, 0), sides=8, taper=1.0, name="slab", chip=1.6, bevel=1.4, rough=1.7):
    """A many-sided plate of stone: its outline lies in X-Z and its thickness runs along Y."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=sides, radius1=1, radius2=1, depth=1)
    bmesh.ops.rotate(bm, verts=bm.verts, matrix=Matrix.Rotation(math.radians(90), 3, "X"))
    spin = Matrix.Rotation(random.uniform(0, math.tau / sides), 3, "Y")
    for vert in bm.verts:
        vert.co = spin @ vert.co
        reach = random.uniform(0.80, 1.10)
        front = taper if vert.co.y < 0 else 1.0
        vert.co = Vector((vert.co.x * size[0] * 0.5 * reach * front, vert.co.y * size[1], vert.co.z * size[2] * 0.5 * reach * front))
    place = Matrix.Translation(Vector(centre)) @ Euler([math.radians(a) for a in turn]).to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=place, verts=bm.verts)
    return finish(bm, bone, colour or random.choice(SLATE), name, chip, bevel, rough)


def block(centre, size, bone, colour, turn=(0, 0, 0), name="block", chip=1.6, bevel=1.6):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=1, use_grid_fill=True)
    place = Matrix.Translation(Vector(centre)) @ Euler([math.radians(a) for a in turn]).to_matrix().to_4x4() @ Matrix.Diagonal((*size, 1))
    bmesh.ops.transform(bm, matrix=place, verts=bm.verts)
    return finish(bm, bone, colour, name, chip, bevel)


def lump(centre, size, bone, colour, name="lump", detail=1, chip=1.2):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=detail, radius=1)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(centre)) @ Matrix.Diagonal((*size, 1)), verts=bm.verts)
    return finish(bm, bone, colour, name, chip, 0, 0)


def horn(side):
    """A ridged spiral horn: up and back from the brow, down behind the cheek, forward and out to a blunt broken tip."""
    bm = bmesh.new()
    rings, sides, steps = [], 8, 44
    for step in range(steps + 1):
        t = step / steps
        angle = -0.5 + t * 1.42 * math.tau
        curl = 21 - 9 * t
        centre = Vector((side * (19 + 20 * t * t + 4 * t), -100 + curl * math.sin(angle), 111 + curl * math.cos(angle)))
        ahead = Vector((side * (40 * t + 4) / (1.42 * math.tau), curl * math.cos(angle), -curl * math.sin(angle))).normalized()
        across = ahead.cross(Vector((side, 0, 0)))
        across = across.normalized() if across.length > 0.01 else Vector((0, 0, 1))
        other = ahead.cross(across).normalized()
        thick = (13.5 - 10 * t) * (1.16 if step % 2 == 0 else 0.90)
        ring = [bm.verts.new(centre + (across * math.cos(k / sides * math.tau) + other * math.sin(k / sides * math.tau)) * thick)
                for k in range(sides)]
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            bm.faces.new((a[k], a[(k + 1) % sides], b[(k + 1) % sides], b[k]))
    bm.faces.new(rings[0])
    bm.faces.new(list(reversed(rings[-1])))
    return finish(bm, "Head", HORN, "horn", chip=0.5, bevel=0, rough=0)


# ---- Body: overlapping plates from chest to rump, each a little different. -----------------------------------------
profile = [(-66, 74, 76, 86), (-49, 90, 92, 90), (-31, 96, 96, 91), (-12, 88, 86, 87), (8, 80, 76, 83), (28, 78, 72, 82),
           (48, 76, 72, 81), (66, 66, 62, 79)]
for index, (y, width, height, z) in enumerate(profile):
    slab((random.uniform(-2, 2), y, z + random.uniform(-2, 3)), (width, random.uniform(19, 24), height), "Chest" if index < 4 else "Body",
         turn=(random.uniform(-7, 7), random.uniform(-6, 6), random.uniform(-4, 4)), name=f"body{index}")
# Shoulder plates lie over the withers like armour, and two more over the haunches.
slab((-20, -40, 132), (54, 9, 50), "Chest", turn=(72, 0, -16), sides=6, name="shoulderL")
slab((20, -40, 132), (54, 9, 50), "Chest", turn=(72, 0, 16), sides=6, name="shoulderR")
slab((0, -22, 138), (30, 8, 40), "Chest", turn=(60, 0, 3), sides=5, name="withers")
slab((-15, 46, 113), (38, 5, 36), "Body", turn=(80, 0, -12), sides=6, name="haunchL")
slab((15, 46, 113), (38, 5, 36), "Body", turn=(80, 0, 12), sides=6, name="haunchR")
slab((0, 80, 80), (44, 9, 42), "Body", turn=(-12, 0, 0), name="rump")
slab((0, 91, 92), (12, 16, 12), "Tail", turn=(-35, 0, 0), sides=5, taper=0.5, name="tail")
# Neck and head.
slab((0, -80, 95), (58, 11, 60), "Neck", turn=(-14, 0, 4), name="neck0")
slab((0, -92, 101), (50, 11, 52), "Neck", turn=(-20, 0, -5), name="neck1")
slab((0, -113, 100), (44, 28, 48), "Head", turn=(30, 0, 0), taper=0.62, sides=8, name="skull")
slab((0, -134, 86), (25, 15, 25), "Head", turn=(38, 0, 0), taper=0.8, sides=6, colour=SLATE[2], name="muzzle")
slab((0, -117, 121), (46, 7, 22), "Head", turn=(64, 0, 0), sides=6, colour=SLATE[3], name="brow")
slab((0, -126, 78), (20, 12, 9), "Head", turn=(34, 0, 0), sides=6, colour=SLATE[2], name="jaw")
for side in (-1, 1):
    horn(side)
    lump((side * 17.5, -128, 105), (5.0, 3.4, 6.0), "Head", SOCKET, "socket", chip=0.2)
    lump((side * 19.8, -130, 105), (3.0, 2.4, 3.8), "Head", EYE, "eye", chip=0.0)
    slab((side * 9, -140, 82), (5, 3, 4), "Head", colour=SOCKET, turn=(38, 0, 0), sides=5, name="nostril", chip=0.2, bevel=0.3)
    # Legs: thigh, shin and hoof, each its own stone.
    for label, y, x, lean in (("Front", -44, 25, -4), ("Rear", 50, 23, 6)):
        prefix = label + ("Left" if side > 0 else "Right")
        block((side * x, y, 52), (28, 32, 38), prefix + "UpLeg", random.choice(SLATE), turn=(lean, 0, side * 4), name="thigh")
        slab((side * (x + 13), y - 2, 44), (20, 5, 20), prefix + "UpLeg", turn=(0, 0, 90 + side * 8), sides=5, name="kneeplate")
        block((side * x, y + (2 if label == "Rear" else 0), 27), (20, 22, 26), prefix + "Leg", random.choice(SLATE), turn=(-lean, 0, 0), name="shin")
        for toe in (-1, 1):
            slab((side * x + toe * 5.5, y - 4, 8), (11, 26, 15), prefix + "Foot", colour=HOOF, turn=(0, 0, toe * 5), sides=5, taper=0.7, name="hoof", chip=0.5, bevel=0.8, rough=0.6)
# Quartz veins: thin pale wedges let into three plates.
slab((22, -29, 96), (5, 12.5, 40), "Chest", colour=QUARTZ, turn=(0, 24, 0), sides=4, name="quartz0", chip=0.3, bevel=0.3)
slab((-27, 30, 84), (4, 12.5, 34), "Body", colour=QUARTZ, turn=(0, -18, 0), sides=4, name="quartz1", chip=0.3, bevel=0.3)
slab((6, -113, 118), (3, 20, 14), "Head", colour=QUARTZ, turn=(30, 30, 0), sides=4, name="quartz2", chip=0.3, bevel=0.3)
# Moss in the seams of the back, and a few fern blades.
for y, x, bone in ((-58, 9, "Chest"), (-20, -12, "Chest"), (0, 14, "Chest"), (20, -8, "Body"), (40, 10, "Body"), (60, -4, "Body"), (-39, 0, "Chest")):
    z = 121 if y < 0 else 116
    lump((x, y, z), (random.uniform(9, 14), random.uniform(7, 10), random.uniform(3.5, 5)), bone, MOSS, "moss")
    lump((x + random.uniform(-8, 8), y + random.uniform(-5, 5), z + 2), (5, 4.5, 3), bone, (0.24, 0.47, 0.13), "moss")
for x, y, bone, tilt in ((-13, -19, "Chest", -25), (-9, -22, "Chest", 10), (11, 41, "Body", 28), (-4, 61, "Body", -18), (15, 1, "Chest", 20)):
    slab((x, y, 131), (5, 1.0, 22), bone, colour=(0.20, 0.50, 0.14), turn=(random.uniform(-20, 20), tilt, random.uniform(0, 180)), sides=4, taper=1.0,
         name="fern", chip=0.2, bevel=0)

# ---- Join, unwrap and bake the colour. -----------------------------------------------------------------------------
bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
ram = bpy.context.view_layer.objects.active
ram.name = "SlateRam"
ram.data.name = "SlateRam"
for polygon in ram.data.polygons:
    polygon.use_smooth = False
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.004)
bpy.ops.object.mode_set(mode="OBJECT")

image = bpy.data.images.new("T_SlateRam_Color", 2048, 2048, alpha=False)
painted = bpy.data.materials.new("SlateRamBake")
painted.use_nodes = True
nodes, links = painted.node_tree.nodes, painted.node_tree.links
nodes.clear()
paint = nodes.new("ShaderNodeVertexColor"); paint.layer_name = "Paint"
coords = nodes.new("ShaderNodeTexCoord")
grain = nodes.new("ShaderNodeTexNoise"); grain.inputs["Scale"].default_value = 0.09; grain.inputs["Detail"].default_value = 8
fine = nodes.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 0.9; fine.inputs["Detail"].default_value = 4
# Slate splits in sheets: thin dark lines follow each plate's layers, bent a little by noise.
layers = nodes.new("ShaderNodeTexWave"); layers.wave_type = "BANDS"; layers.bands_direction = "Z"
layers.inputs["Scale"].default_value = 0.34; layers.inputs["Distortion"].default_value = 5; layers.inputs["Detail"].default_value = 3
layers.inputs["Detail Scale"].default_value = 0.6
sharp = nodes.new("ShaderNodeValToRGB"); sharp.color_ramp.elements[0].position = 0.0; sharp.color_ramp.elements[1].position = 0.22
sharp.color_ramp.elements[0].color = (0.50, 0.52, 0.56, 1); sharp.color_ramp.elements[1].color = (1, 1, 1, 1)
shade = nodes.new("ShaderNodeAmbientOcclusion"); shade.inputs["Distance"].default_value = 22; shade.samples = 16
deep = nodes.new("ShaderNodeValToRGB"); deep.color_ramp.elements[0].position = 0.25; deep.color_ramp.elements[1].position = 0.95
deep.color_ramp.elements[0].color = (0.16, 0.17, 0.22, 1)
# Worn edges catch the light: convex corners are paler than the faces.
geometry = nodes.new("ShaderNodeNewGeometry")
edge = nodes.new("ShaderNodeValToRGB"); edge.color_ramp.elements[0].position = 0.50; edge.color_ramp.elements[1].position = 0.60
edge.color_ramp.elements[0].color = (1, 1, 1, 1); edge.color_ramp.elements[1].color = (2.3, 2.3, 2.2, 1)
ramp = nodes.new("ShaderNodeMapRange"); ramp.inputs["To Min"].default_value = 0.55; ramp.inputs["To Max"].default_value = 1.5
ramp2 = nodes.new("ShaderNodeMapRange"); ramp2.inputs["To Min"].default_value = 0.9; ramp2.inputs["To Max"].default_value = 1.1


def times(a, b):
    node = nodes.new("ShaderNodeMixRGB"); node.blend_type = "MULTIPLY"; node.inputs["Fac"].default_value = 1
    links.new(a, node.inputs["Color1"]); links.new(b, node.inputs["Color2"])
    return node.outputs["Color"]


links.new(coords.outputs["Object"], grain.inputs["Vector"]); links.new(coords.outputs["Object"], fine.inputs["Vector"])
links.new(coords.outputs["Object"], layers.inputs["Vector"])
links.new(grain.outputs["Fac"], ramp.inputs["Value"]); links.new(fine.outputs["Fac"], ramp2.inputs["Value"])
links.new(layers.outputs["Fac"], sharp.inputs["Fac"]); links.new(shade.outputs["AO"], deep.inputs["Fac"])
links.new(geometry.outputs["Pointiness"], edge.inputs["Fac"])
colour = times(paint.outputs["Color"], ramp.outputs["Result"])
colour = times(colour, ramp2.outputs["Result"])
colour = times(colour, sharp.outputs["Color"])
colour = times(colour, deep.outputs["Color"])
colour = times(colour, edge.outputs["Color"])
glow = nodes.new("ShaderNodeEmission"); links.new(colour, glow.inputs["Color"])
output = nodes.new("ShaderNodeOutputMaterial"); links.new(glow.outputs["Emission"], output.inputs["Surface"])
target = nodes.new("ShaderNodeTexImage"); target.image = image; nodes.active = target
ram.data.materials.append(painted)
scene.render.engine = "CYCLES"
scene.cycles.samples = 24
scene.cycles.device = "CPU"
scene.render.bake.margin = 6
bpy.ops.object.bake(type="EMIT")
image.filepath_raw = str(OUT / "T_SlateRam_Color.png")
image.file_format = "PNG"
image.save()

final = bpy.data.materials.new("M_SlateRam")
final.use_nodes = True
shader = final.node_tree.nodes["Principled BSDF"]
texture = final.node_tree.nodes.new("ShaderNodeTexImage"); texture.image = image
final.node_tree.links.new(texture.outputs["Color"], shader.inputs["Base Color"])
shader.inputs["Roughness"].default_value = 0.82
ram.data.materials.clear()
ram.data.materials.append(final)

# ---- Skeleton: every stone follows exactly one bone, so the plates shift against each other but never bend. --------
bones = {"Hips": ((0, 0, 78), (0, 0, 92), None), "Body": ((0, 20, 80), (0, 60, 80), "Hips"), "Chest": ((0, -10, 82), (0, -60, 84), "Body"),
         "Neck": ((0, -68, 92), (0, -96, 102), "Chest"), "Head": ((0, -98, 104), (0, -138, 88), "Neck"), "Tail": ((0, 84, 90), (0, 100, 96), "Body")}
for side, word in ((1, "Left"), (-1, "Right")):
    for label, y, x, parent in (("Front", -44, 25, "Chest"), ("Rear", 50, 23, "Body")):
        prefix = label + word
        bones[prefix + "UpLeg"] = ((side * x, y, 68), (side * x, y, 39), parent)
        bones[prefix + "Leg"] = ((side * x, y, 39), (side * x, y, 15), prefix + "UpLeg")
        bones[prefix + "Foot"] = ((side * x, y, 15), (side * x, y - 6, 2), prefix + "Leg")
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
bpy.ops.object.mode_set(mode="OBJECT")
ram.parent = rig
ram.modifiers.new("Armature", "ARMATURE").object = rig
rest = {bone.name: bone.matrix_local.to_3x3() for bone in armature.bones}
for bone in rig.pose.bones:
    bone.rotation_mode = "QUATERNION"

# ---- Animation. Each clip is written as a pose for every frame: world-axis turns (degrees) and shifts (cm). --------
LEGS = ("FrontLeft", "FrontRight", "RearLeft", "RearRight")


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def keyed(t, keys):
    """Value at t from (time, value) keys, eased between neighbours."""
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return v0 + (v1 - v0) * ease((t - t0) / (t1 - t0))
    return keys[-1][1]


def idle(t):
    wave = math.sin(t * math.tau)
    return {"Body": ((0.8 * wave, 0, 0), (0, 0, 1.0 * wave)), "Chest": ((1.6 * wave, 0, 0), (0, 0, 0.8 * wave)),
            "Neck": ((3.5 * math.sin(t * math.tau - 0.7), 0, 3 * math.sin(t * math.tau)), (0, 0, 0)),
            "Head": ((2.5 * math.sin(t * math.tau - 1.3), 0, 5 * math.sin(t * math.tau - 0.4)), (0, 0, 0)),
            "Tail": ((6 * math.sin(2 * t * math.tau), 0, 16 * math.sin(2 * t * math.tau)), (0, 0, 0))}


def walk(t):
    phase = t * math.tau
    pose = {"Body": ((1.5 * math.sin(2 * phase), 3.0 * math.sin(phase), 0), (0, 0, 1.6 * math.sin(2 * phase + 0.6))),
            "Chest": ((1.5 * math.sin(2 * phase + 1.0), -2.0 * math.sin(phase), 0), (0, 0, 0)),
            "Neck": ((4 * math.sin(2 * phase + 0.4), 0, 0), (0, 0, 0)), "Head": ((3 * math.sin(2 * phase - 0.3), 0, 0), (0, 0, 0)),
            "Tail": ((0, 0, 10 * math.sin(phase)), (0, 0, 0))}
    for leg in LEGS:
        swing = phase + (0 if leg in ("FrontLeft", "RearRight") else math.pi) + (0.5 if leg.startswith("Rear") else 0)
        lift = max(0.0, -math.cos(swing))    # the knee folds while the leg comes forward
        pose[leg + "UpLeg"] = ((27 * math.sin(swing), 0, 0), (0, 0, 0))
        pose[leg + "Leg"] = ((30 * lift * (1 if leg.startswith("Front") else -0.6), 0, 0), (0, 0, 0))
        pose[leg + "Foot"] = ((-16 * lift, 0, 0), (0, 0, 0))
    return pose


def attack(t):
    lunge = keyed(t, [(0, 0), (0.32, 9), (0.5, -24), (0.62, -20), (1, 0)])
    head = keyed(t, [(0, 0), (0.32, -24), (0.5, 34), (0.64, 22), (1, 0)])
    brace = keyed(t, [(0, 0), (0.32, 10), (0.5, -22), (1, 0)])
    pose = {"Body": ((keyed(t, [(0, 0), (0.32, -5), (0.5, 7), (1, 0)]), 0, 0), (0, lunge, keyed(t, [(0, 0), (0.32, 2), (0.5, -5), (1, 0)]))),
            "Chest": ((keyed(t, [(0, 0), (0.32, -5), (0.5, 8), (1, 0)]), 0, 0), (0, 0, 0)),
            "Neck": ((head * 0.6, 0, 0), (0, 0, 0)), "Head": ((head * 0.5, 0, 0), (0, 0, 0)),
            "Tail": ((keyed(t, [(0, 0), (0.5, -30), (1, 0)]), 0, 0), (0, 0, 0))}
    for leg in LEGS:
        pose[leg + "UpLeg"] = ((-brace if leg.startswith("Front") else -brace * 0.7, 0, 0), (0, 0, 0))
        pose[leg + "Leg"] = ((brace * 0.6 if leg.startswith("Front") else 0, 0, 0), (0, 0, 0))
    return pose


def cast(t):
    low = keyed(t, [(0, 0), (0.18, 1), (0.85, 1), (1, 0)])
    paw = keyed(t, [(0, 0), (0.2, -38), (0.34, 16), (0.5, -38), (0.64, 16), (0.8, -10), (1, 0)])
    knee = keyed(t, [(0, 0), (0.2, 48), (0.34, 6), (0.5, 48), (0.64, 6), (1, 0)])
    return {"Body": ((6 * low, 0, 0), (0, 7 * low, -3 * low)), "Chest": ((6 * low, 0, 0), (0, 0, 0)),
            "Neck": ((22 * low, 0, 0), (0, 0, 0)), "Head": ((16 * low + 3 * math.sin(t * 6 * math.tau) * low, 0, 0), (0, 0, 0)),
            "FrontRightUpLeg": ((paw, 0, 0), (0, 0, 0)), "FrontRightLeg": ((knee, 0, 0), (0, 0, 0)), "FrontRightFoot": ((-knee * 0.4, 0, 0), (0, 0, 0)),
            "Tail": ((-25 * low, 0, 12 * math.sin(t * 5 * math.tau) * low), (0, 0, 0))}


def hit(t):
    jolt = keyed(t, [(0, 0), (0.25, 1), (1, 0)])
    return {"Body": ((-5 * jolt, 0, 0), (0, 8 * jolt, 1.5 * jolt)), "Chest": ((-4 * jolt, 3 * jolt, 0), (0, 0, 0)),
            "Neck": ((-12 * jolt, 0, 8 * jolt), (0, 0, 0)), "Head": ((-9 * jolt, 0, 10 * jolt), (0, 0, 0)),
            "FrontLeftUpLeg": ((-9 * jolt, 0, 0), (0, 0, 0)), "FrontRightUpLeg": ((-9 * jolt, 0, 0), (0, 0, 0))}


def defeat(t):
    fold = keyed(t, [(0, 0), (0.45, 1), (1, 1)])
    tip = keyed(t, [(0, 0), (0.3, 0), (0.75, 1), (0.86, 0.94), (1, 1)])
    pose = {"Body": ((0, 68 * tip, 0), (14 * tip, 0, -36 * fold - 8 * tip)), "Chest": ((4 * fold, 6 * tip, 0), (0, 0, 0)),
            "Neck": ((14 * fold, 0, 10 * tip), (0, 0, 0)), "Head": ((10 * fold, 8 * tip, 0), (0, 0, 0)), "Tail": ((-20 * fold, 0, 0), (0, 0, 0))}
    for leg in LEGS:
        front = leg.startswith("Front")
        pose[leg + "UpLeg"] = (((-55 if front else 50) * fold, 0, 0), (0, 0, 0))
        pose[leg + "Leg"] = (((100 if front else -95) * fold, 0, 0), (0, 0, 0))
    return pose


CLIPS = {"Idle": (idle, 75, True), "Move": (walk, 28, True), "Attack": (attack, 24, False), "Cast": (cast, 38, False), "Hit": (hit, 12, False),
         "Defeat": (defeat, 34, False)}


def apply(pose):
    for bone in rig.pose.bones:
        turn, shift = pose.get(bone.name, ((0, 0, 0), (0, 0, 0)))
        frame = rest[bone.name]
        world = Euler([math.radians(a) for a in turn]).to_matrix()
        bone.rotation_quaternion = (frame.inverted() @ world @ frame).to_quaternion()
        bone.location = frame.inverted() @ Vector(shift)


def write(name):
    maker, frames, loops = CLIPS[name]
    rig.animation_data_create()
    action = bpy.data.actions.new(name)
    rig.animation_data.action = action
    for frame in range(frames + 1):
        apply(maker(frame / frames))
        for bone in rig.pose.bones:
            bone.keyframe_insert("rotation_quaternion", frame=frame)
            bone.keyframe_insert("location", frame=frame)
    scene.frame_start, scene.frame_end = 0, frames
    return action


def export(path, with_mesh, animated):
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    if with_mesh:
        ram.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={"ARMATURE", "MESH"} if with_mesh else {"ARMATURE"},
                             add_leaf_bones=False, bake_anim=animated, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
                             bake_anim_simplify_factor=0.0, bake_anim_force_startend_keying=True, path_mode="COPY", embed_textures=True,
                             mesh_smooth_type="FACE", use_armature_deform_only=True, axis_forward="-Z", axis_up="Y")


apply({})
export(OUT / "body.fbx", True, False)
for clip in CLIPS:
    write(clip)
    export(OUT / f"clip_{clip}.fbx", False, True)

# ---- Preview renders: the rest pose from four sides and one frame of each clip. ------------------------------------
world = bpy.data.worlds.new("World"); scene.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.57, 0.6, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sun.data.energy = 3.2; sun.rotation_euler = (math.radians(48), 0, math.radians(-35))
scene.collection.objects.link(sun)
floor_mesh = bpy.data.meshes.new("Floor"); floor_bm = bmesh.new(); bmesh.ops.create_grid(floor_bm, x_segments=1, y_segments=1, size=600); floor_bm.to_mesh(floor_mesh)
floor = bpy.data.objects.new("Floor", floor_mesh); scene.collection.objects.link(floor)
ground = bpy.data.materials.new("Ground"); ground.use_nodes = True
ground.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.42, 0.38, 0.32, 1); floor.data.materials.append(ground)
camera = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera")); scene.collection.objects.link(camera); scene.camera = camera
camera.data.lens = 50; camera.data.clip_end = 5000
scene.render.resolution_x, scene.render.resolution_y = 640, 520
scene.cycles.samples = 40
try:
    preferences = bpy.context.preferences.addons["cycles"].preferences
    preferences.compute_device_type = "OPTIX"; preferences.get_devices()
    for device in preferences.devices:
        device.use = True
    scene.cycles.device = "GPU"
except Exception:
    scene.cycles.device = "CPU"


def shot(name, angle, frame, action=None, height=150, distance=470):
    rig.animation_data.action = action
    if action is None:
        apply({})
    scene.frame_set(frame)
    camera.location = (distance * math.sin(math.radians(angle)), -distance * math.cos(math.radians(angle)), height)
    aim = Vector((0, -15, 72)) - camera.location
    camera.rotation_euler = aim.to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(OUT / f"preview_{name}.png")
    bpy.ops.render.render(write_still=True)


for label, angle in (("front", 28), ("side", 90), ("back", 200), ("other", -70)):
    shot("rest_" + label, angle, 0)
for clip, frame in (("Move", 7), ("Attack", 12), ("Cast", 8), ("Defeat", 34)):
    shot(clip, 55, frame, bpy.data.actions[clip])
rig.animation_data.action = bpy.data.actions["Idle"]
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "slate_ram.blend"))
print("SLATE_RAM_BUILT", len(ram.data.polygons), "faces")
