import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/mpfb-pilot/MP1")
assert bpy.data.filepath.replace("\\", "/").endswith("/ada_head_polish_checkpoint_r016.blend")
s = bpy.data.scenes["HP1_HEAD_POLISH"]
bpy.context.window.scene = s
allowed = {"HP1_HEAD_POLISH_Head_r016", "HP1_HEAD_POLISH_Eye_R", "HP1_HEAD_POLISH_Eye_L"}
clay = bpy.data.materials.new("MP1_Matched_Clay_Baseline")
clay.use_nodes = True
p = clay.node_tree.nodes.get("Principled BSDF")
p.inputs["Base Color"].default_value = (.5, .5, .5, 1)
p.inputs["Roughness"].default_value = .65
for o in s.objects:
    if o.type == "MESH":
        o.hide_render = o.name not in allowed
        if o.name in allowed:
            o.data.materials.clear()
            o.data.materials.append(clay)
            for f in o.data.polygons:
                f.material_index = 0
s.cycles.samples = 48
s.render.resolution_percentage = 100
for label in ["front", "profile", "three_quarter", "primary_fit"]:
    s.camera = bpy.data.objects["HP1_HEAD_POLISH_" + label]
    s.render.resolution_x = 840 if label == "primary_fit" else 900
    s.render.resolution_y = 788 if label == "primary_fit" else 900
    s.render.filepath = str(ROOT / "captures" / ("baseline_clay_" + label + ".png"))
    bpy.ops.render.render(write_still=True)
key = bpy.data.objects["HP1_HEAD_POLISH_Key"]
fill = bpy.data.objects["HP1_HEAD_POLISH_Fill"]
for light in [key, fill]:
    light.location.x = -light.location.x
    light.rotation_euler = (Vector((0, -.008, 1.680)) - light.location).to_track_quat("-Z", "Y").to_euler()
s.camera = bpy.data.objects["HP1_HEAD_POLISH_three_quarter"]
s.render.resolution_x = s.render.resolution_y = 900
s.render.filepath = str(ROOT / "captures" / "baseline_clay_reverse_key.png")
bpy.ops.render.render(write_still=True)
print("Matched r016 captures rendered. No save operation performed.")

