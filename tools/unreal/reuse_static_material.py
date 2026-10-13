"""Give a rigged copy of a model the material of its original static import, so it keeps the same look.

Reads WC_REUSE_MATERIAL (JSON: {"skeletal": asset path, "material": asset path, "report": path}). The material is
marked usable on skeletal meshes and assigned to every slot of the skeletal mesh.
"""
import json
import os
import traceback
from pathlib import Path

import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
job = json.loads(Path(os.environ["WC_REUSE_MATERIAL"]).read_text(encoding="utf-8"))
report = {"status": "STARTED"}
try:
    mesh = unreal.EditorAssetLibrary.load_asset(job["skeletal"])
    material = unreal.EditorAssetLibrary.load_asset(job["material"])
    if not isinstance(mesh, unreal.SkeletalMesh) or material is None:
        raise RuntimeError("Mesh or material is missing")
    base = material.get_base_material() if isinstance(material, unreal.MaterialInstance) else material
    base.set_editor_property("used_with_skeletal_mesh", True)
    unreal.MaterialEditingLibrary.recompile_material(base)
    unreal.EditorAssetLibrary.save_loaded_asset(base)
    slots = mesh.materials
    for slot in slots:
        slot.material_interface = material
    mesh.set_editor_property("materials", slots)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    report.update(status="ASSIGNED", slots=len(slots), material=job["material"])
except Exception:
    report["status"] = "FAILED"
    report["error"] = traceback.format_exc()
path = root / job["report"]
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
