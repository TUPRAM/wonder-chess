"""Measure a model before rigging it: bounds, width at each height, and four plain renders.

Run:  blender -b -P tools/blender/probe_model.py -- <model.glb> <output folder>
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

source, out = Path(sys.argv[-2]), Path(sys.argv[-1])
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source))
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
points = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
low = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
high = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
bands = []
for step in range(20):
    z0, z1 = low.z + (high.z - low.z) * step / 20, low.z + (high.z - low.z) * (step + 1) / 20
    inside = [p for p in points if z0 <= p.z < z1]
    if inside:
        bands.append({"z": round((z0 + z1) / 2, 3), "x": [round(min(p.x for p in inside), 3), round(max(p.x for p in inside), 3)],
                      "y": [round(min(p.y for p in inside), 3), round(max(p.y for p in inside), 3)], "count": len(inside)})
(out / "probe.json").write_text(json.dumps({"low": list(low), "high": list(high), "vertices": len(points), "objects": [o.name for o in meshes], "bands": bands}, indent=1))
scene = bpy.context.scene
world = bpy.data.worlds.new("World"); scene.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.6, 0.6, 0.62, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.2
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sun.data.energy = 2.5; sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
scene.collection.objects.link(sun)
camera = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera")); scene.collection.objects.link(camera); scene.camera = camera
camera.data.type = "ORTHO"
size = max(high.x - low.x, high.z - low.z, high.y - low.y) * 1.15
camera.data.ortho_scale = size
centre = (low + high) / 2
scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
scene.render.resolution_x = scene.render.resolution_y = 600
for label, angle in (("front", 0), ("left", 90), ("back", 180), ("right", 270)):
    camera.location = centre + Vector((math.sin(math.radians(angle)), -math.cos(math.radians(angle)), 0)) * size * 3
    camera.rotation_euler = (centre - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(out / f"probe_{label}.png")
    bpy.ops.render.render(write_still=True)
print("PROBED", list(low), list(high))
