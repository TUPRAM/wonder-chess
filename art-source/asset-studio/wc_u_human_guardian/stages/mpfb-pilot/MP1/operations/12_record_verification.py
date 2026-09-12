"""Record evidence for this executed MP1 trial; no asset mutations or approvals."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys

repo = Path(r"C:/Users/iputu/Documents/Wonder Chess")
root = Path(r"C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/mpfb-pilot/MP1")
asset = repo / "art-source/asset-studio/wc_u_human_guardian"
support = Path(r"C:/Users/iputu/Documents/Project Support/Wonder Chess/mpfb-pilot")
def record(path):
    path = Path(path)
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

protected = [
    (asset / "stages/head-polish/HP1/r001/ada_head_polish_checkpoint_r016.blend", "775815688dc4aa30dce7085b78ef79bf9ff89f603f243af9110d8ef7b8d00b6b"),
    (asset / "stages/head-closure/ACB1/ada_closure_checkpoint_ACB1_ART_REVISE.blend", "5deb2ead3d282a6ea0646452f2ee85a35506a5f4b1a1d275b8711623dbe96e2c"),
]
preservation = []
for path, expected in protected:
    observed = record(path)
    observed.update({"expected_sha256": expected, "matches_original": observed["sha256"] == expected})
    assert observed["matches_original"], observed
    preservation.append(observed)

package = record(support / "add-on-mpfb-v2.0.17.zip")
assert package["sha256"] == "4f0a879d64a39bf646fbf5f53601ac678855da329d650617dca5737548239a87"
package.update({
    "download_url": "https://extensions.blender.org/download/sha256:4f0a879d64a39bf646fbf5f53601ac678855da329d650617dca5737548239a87/add-on-mpfb-v2.0.17.zip",
    "installed_version": "2.0.17",
    "blender_version": "5.1.1",
    "module": "bl_ext.user_default.mpfb",
    "install_path": "C:/Users/iputu/AppData/Roaming/Blender Foundation/Blender/5.1/extensions/user_default/mpfb",
    "install_method": "Executed Blender extensions.package_install_files from the inspected local archive; enabled in the live session.",
    "scope": "Bundled core graphics only. No extra asset packs, paid services or remote art uploads.",
    "package_inspection": "2384 archive entries; no path traversal or native executable entries observed. Focused inspection, not a complete security audit.",
    "preferences": "No broad preferences save; Blender online access remained disabled. Extension may require enabling next session.",
    "license": record(support / "MPFB-v2.0.17-LICENSE.md"),
    "license_url": "https://raw.githubusercontent.com/makehumancommunity/mpfb2/v2.0.17/LICENSE.md",
    "license_declared_by_tagged_file": {"code": "GPLv3", "bundled_core_graphics": "CC0"}
})
assert package["license"]["sha256"] == "5cefb60680cb9efd4550a2e65d719021cfbec9dad3658481d11d48ae863ce04d"

status_command = [sys.executable, str(repo / "production/asset-studio/tools/asset_studio/assetctl.py"), "status", "--workspace", str(asset)]
status = json.loads(subprocess.check_output(status_command, cwd=repo, text=True))
lookup = {row["stage"]: row["status"] for row in status}
assert lookup["brief"] == lookup["references"] == "accepted_current"
assert lookup["forms"] == "pending"
(root / "as1_status.json").write_text(json.dumps(status, indent=2) + "\n")
reopen = json.loads((root / "reopen_verification.json").read_text())
work_reopen = json.loads((root / "reopen_work_verification.json").read_text())
assert reopen["status"] == work_reopen["status"] == "PASS"
checkpoint = record(root / "ada_mpfb_checkpoint_r002_verified.blend")
assert checkpoint["sha256"] == "9ccfd9fdd87ddeac89761809f9ea725e50c0e874e6ca8f3a9bc539430badac5a"
implementation = json.loads((repo / "reports/implementation_state.json").read_text())
assert implementation["as1_asset_studio"]["ada_mpfb_mp1"]["frozen_sha256"] == checkpoint["sha256"]
required_captures = [
    "comparison_front.png", "comparison_profile.png", "comparison_three_quarter.png",
    "comparison_primary_fit.png", "comparison_reverse_key.png", "reference_comparison.png",
    "final_openings_front.png", "final_cage_three_quarter.png", "diagnostics.png"
]
for name in required_captures:
    assert (root / "captures" / name).is_file(), name
for path in root.rglob("*.json"):
    json.loads(path.read_text(encoding="utf-8-sig"))

result = {
    "trial": "MP1",
    "recorded_utc": datetime.now(timezone.utc).isoformat(),
    "art_status": "ART_REVISE",
    "method_decision": "Retain the MPFB connected foundation; the trial does not prove a completed Ada or successful slider-only lip closure.",
    "authorization": "Latest user expressly requested a separate untextured MPFB Ada head trial; accepted original-method asset manifest preserved.",
    "checkpoint": checkpoint,
    "working_file": record(root / "ada_mpfb_work.blend"),
    "package": package,
    "preservation": preservation,
    "reference_sources": [record(asset / "stages/head-polish/HP1/r001/references" / name) for name in ["ada_portrait.png", "supplementary_construction.png"]],
    "unchanged_authority_files_current_hashes": [record(asset / p) for p in ["asset.json", "state.json", "reviews/references/accepted_f6ea0a9d2e1f427790481f24f4b6b346.json"]],
    "as1_status": status,
    "reopen_checkpoint": reopen,
    "reopen_work": work_reopen,
    "save_issue": {
        "initial_check": "FAIL: MP1_ADA_HEAD missing from first saved r002 scene list although present in the live session with zero users.",
        "failed_snapshot": record(root / "ada_mpfb_checkpoint_r002.blend"),
        "failed_log": "reopen_verification.log",
        "correction": "Set explicit scene fake users, save work and new verified checkpoint, reopen both in separate Blender background processes. No geometry change.",
        "new_check": "PASS"
    },
    "executed_evidence": {
        "blender_generation_and_native_targets": True,
        "live_mcp_and_computer_use": True,
        "uniform_clay_front_profile_three_quarter_primary_reverse": True,
        "eyes_hidden_real_openings": True,
        "actual_edit_mode_cage_capture": True,
        "independent_actual_image_review": True,
        "static_geometry_observations": True,
        "frozen_r016_rerendered_without_saving": True
    },
    "render_limits": "Saved cameras, neutral clay and lighting used for before/after. Primary-fit is only approximate to the illustration; no registered likeness percentage. Diagnostic eyes are separately labeled.",
    "mesh_check_limits": "Static degeneracy, edge-use, boundary and nonadjacent BVH screening only; not exhaustive collision or deformation certification.",
    "remaining_major_defects": ["MP1-M01 compact rounded eye shape and raised lower-lid rim", "MP1-M02 parted projecting lips", "MP1-M03 generic soft lower cheek and jaw"],
    "not_run": ["hair family", "production UV/bake/materials", "rigging and deformation", "animation", "LODs", "Unreal import", "packaged-game or performance tests", "new reusable toolkit", "human forms or release approval"],
    "approval_issued": False,
    "artifact_hashes": [record(p) for p in sorted(root.rglob("*")) if p.is_file() and p.name != "verification.json"],
    "operations_limit": "Numbered files are exact successful session operations plus focused reopen/evidence checks; they are not independently replayable pipeline guarantees.",
    "cost": "No additional software subscription or generation service fees. Local compute and existing tools were used."
}
(root / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"status": "PASS", "protected_hashes_match": len(preservation), "reference_gate": lookup["references"], "forms_gate": lookup["forms"], "checkpoint_reopen": reopen["status"], "work_reopen": work_reopen["status"], "captured_artifacts": len(result["artifact_hashes"]), "art_status": result["art_status"]}, indent=2))

