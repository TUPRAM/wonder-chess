import bpy
import json
from pathlib import Path

root = Path(r"C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/mpfb-pilot/MP1")
assert Path(bpy.data.filepath).name in {"ada_mpfb_checkpoint_r002_verified.blend", "ada_mpfb_work.blend"}
scene = bpy.data.scenes["MP1_ADA_HEAD"]
head = bpy.data.objects["MP1_Head_r002"]
source = bpy.data.objects["MP1_MpfbFoundation_Source"]
visible_meshes = sorted(o.name for o in scene.objects if o.type == "MESH" and not o.hide_render)
assert visible_meshes == ["MP1_Eye_L", "MP1_Eye_R", "MP1_Head_r002"], visible_meshes
assert len(head.data.vertices) == 4271
assert len(head.data.polygons) == 4246
assert len(source.data.vertices) == 19158
assert len(source.data.shape_keys.key_blocks) == 38
assert any(m.type == "SUBSURF" and m.levels == 2 for m in head.modifiers)
audit = json.loads((root / "geometry_audit.json").read_text())
max_matrix_delta = 0.0
for name, record in audit["cameras_lights"].items():
    obj = bpy.data.objects[name]
    delta = max(abs(obj.matrix_world[i][j] - record["matrix"][i][j]) for i in range(4) for j in range(4))
    assert delta <= 1e-6, (name, delta)
    max_matrix_delta = max(max_matrix_delta, delta)
result = {
    "status": "PASS",
    "blender_version": bpy.app.version_string,
    "file": bpy.data.filepath,
    "head_vertices": len(head.data.vertices),
    "head_faces": len(head.data.polygons),
    "source_vertices": len(source.data.vertices),
    "source_shape_keys": len(source.data.shape_keys.key_blocks),
    "visible_meshes": visible_meshes,
    "scenes": sorted(s.name for s in bpy.data.scenes),
    "camera_light_matrix_max_delta_to_saved_audit": max_matrix_delta,
    "automatic_script_execution": bpy.context.preferences.filepaths.use_scripts_auto_execute,
    "file_save_performed": False,
    "limits": "Reopen and data-presence verification only; no artistic or deformation approval."
}
output_name = "reopen_work_verification.json" if Path(bpy.data.filepath).name == "ada_mpfb_work.blend" else "reopen_verification.json"
(root / output_name).write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
