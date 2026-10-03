"""Import one un-rigged Meshy hero model as a static mesh candidate at <destination>/SM_<name>. Not approved art.

Reads WC_STATIC_IMPORT (a JSON job: source, destination, name, report). An existing destination is refused.
"""
import json
import os
import traceback
from pathlib import Path

import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
job = json.loads(Path(os.environ["WC_STATIC_IMPORT"]).read_text(encoding="utf-8"))
report = {"destination": job["destination"], "status": "STARTED"}
try:
    base = job["destination"]
    if unreal.EditorAssetLibrary.does_directory_exist(base):
        raise RuntimeError("Destination already exists; choose a new candidate folder")
    task = unreal.AssetImportTask()
    task.filename, task.destination_path = str(root / job["source"]), base
    task.automated = task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    meshes = [asset for asset in (unreal.EditorAssetLibrary.load_asset(path) for path in
                                  unreal.EditorAssetLibrary.list_assets(base, recursive=True))
              if isinstance(asset, unreal.StaticMesh)]
    if len(meshes) != 1:
        raise RuntimeError(f"Expected one static mesh, found {len(meshes)}")
    target = f"{base}/SM_{job['name']}"
    if not unreal.EditorAssetLibrary.rename_asset(meshes[0].get_path_name().split(".")[0], target):
        raise RuntimeError("Could not name the mesh")
    mesh = unreal.EditorAssetLibrary.load_asset(target)
    bounds = mesh.get_bounds()
    report.update(mesh=target, triangles=mesh.get_num_triangles(0),
                  origin_cm=[round(v, 1) for v in (bounds.origin.x, bounds.origin.y, bounds.origin.z)],
                  half_extent_cm=[round(v, 1) for v in (bounds.box_extent.x, bounds.box_extent.y, bounds.box_extent.z)])
    unreal.EditorAssetLibrary.save_directory(base, only_if_is_dirty=False, recursive=True)
    report["status"] = "IMPORTED"
except Exception:
    report["status"] = "FAILED"
    report["error"] = traceback.format_exc()
path = root / job["report"]
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
