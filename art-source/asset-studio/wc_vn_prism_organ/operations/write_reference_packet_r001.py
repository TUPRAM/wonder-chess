"""Record the bounded Prism Organ reference attempt; does not generate or modify images."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct

asset = Path(__file__).resolve().parents[1]
repo = asset.parents[2]
ref = asset / "inputs/references/r001"
original = Path("C:/Users/iputu/.codex/generated_images/01a08b7d-cb87-7ea2-8059-a957477f4188/exec-666c12a9-b0f6-4735-a1d7-54f06a045ef5.png")
utc = datetime.now(timezone.utc).isoformat()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

image = ref / "prism_organ_reference_candidate.png"
assert original.is_file() and sha(original) == sha(image)
direction = asset / "inputs/direction_r001.png"
assert sha(direction) == sha(asset.parent / "wc_vn_direction/inputs/wonder_vnext_direction_r001.png")
width, height = struct.unpack(">II", image.read_bytes()[16:24])

manifest = {
    "schema_version": "1.0.0", "asset_id": "wc_vn_prism_organ", "name": "Prism Organ",
    "kind": "creature", "design_revision": "prism_organ_reference_candidate_r001", "rules_version": "1.0.0",
    "contract": {"scope": "art_only_no_gameplay_changes", "gameplay_id": "wc_vn_prism_organ",
                 "source_forward": "+Y", "source_up": "+Z", "authoring_unit": "meter",
                 "proposed_bounds_m": [1.35, 0.90, 2.20], "proposed_hover_clearance_m": 0.25,
                 "dimensions_status": "provisional_targets_not_measured_or_approved",
                 "body_family": "floating_assembly", "gameplay_footprint_cells": 1,
                 "reference_authority": "owner_selected_direction_only_specific_reference_candidate_unapproved",
                 "max_candidates_per_stage": 2, "authorized_generations_this_task": 1, "max_external_spend": 0},
    "rights": {"status": "generated_reference_provenance_recorded_human_reference_review_pending",
               "external_upload_authorized": False,
               "authorized_builtin_reference_use": "Current root task explicitly authorized built-in image generation using the owner-selected local direction; no unrelated upload or API fallback."},
    "notes": ["One owner: Codex art_pipeline_audit. Independent asset lane; no legacy/Bellback changes.",
              "Full creature gate route retained; rigid assembly treatment requires a later compatible skeleton contract.",
              "Reference r001 is ART_REVISE; direction approval is not reference, forms or release approval."]}
write(asset / "asset.json", manifest)

parts = []
for i in range(1, 6):
    parts.append({"id": f"pipe_p{i}", "diagram_id": f"P{i}", "role": "ceramic resonator pipe with framed glass aperture",
                  "parent": f"cradle_p{i}", "symmetry": "unique indexed height and position; do not mirror identity",
                  "material": "ivory ceramic, aged brass trim, framed teal/amber glass", "export": "rigid part with one declared transform driver",
                  "dimensional_relationship": "five-pipe shallow-arc proposal; exact ratios and plan positions unresolved",
                  "authoring_source": "selected direction plus r001 proposal, not approved geometry", "risk": "assembled/exploded height order conflicts"})
    parts.append({"id": f"cradle_p{i}", "role": "individual pipe support collar", "parent": "hoop_h1", "symmetry": "indexed attachment",
                  "material": "aged brass", "export": "rigid attachment, preserve clearance", "dimensional_relationship": "must not penetrate glass aperture",
                  "authoring_source": "written proposal only; generated diagram does not resolve it", "risk": "missing detailed interface"})
for part_id, role, parent, material, risk in [
    ("hoop_h1", "upper retaining hoop", "assembly_root", "aged brass", "cradle height and attachment unresolved"),
    ("hoop_h2", "lower retaining hoop and emitter carrier", "assembly_root", "aged brass", "image ambiguously puts emitters on both hoops"),
    ("resonator_c1", "suspended stained-glass chamber", "assembly_root", "framed stained glass and ceramic", "image shows opaque urn instead of resolved glass core"),
    ("emitter_e1", "first ordered-beam visual channel, single amber band", "hoop_h2", "amber crystal and brass gimbal", "upper/lower attachment conflict"),
    ("emitter_e2", "second ordered-beam visual channel, double teal band", "hoop_h2", "teal crystal and brass gimbal", "orthogonal relation unproven"),
]:
    parts.append({"id": part_id, "role": role, "parent": parent, "symmetry": "named distinct part",
                  "material": material, "export": "rigid indexed transform; emitter sockets contain no gameplay logic",
                  "dimensional_relationship": "review against proposed assembled bounds; no measurement accepted",
                  "authoring_source": "selected direction and r001 construction proposal", "risk": risk})
for i in range(1, 5):
    parts.append({"id": f"containment_k{i}", "diagram_id": f"K{i}", "role": "finite floating containment key",
                  "parent": "resonator_c1", "symmetry": "four indexed radial positions", "material": "faceted muted stone/glass",
                  "export": "rigid child driver with bounded float envelope", "dimensional_relationship": "must remain outside chamber and hoop envelope",
                  "authoring_source": "written four-part proposal; image count inconsistent", "risk": "front image shows six fragments"})
write(asset / "inputs/semantic_parts_r001.json", {"asset_id": "wc_vn_prism_organ", "status": "proposed_not_approved",
      "assembly_root": "nonrendering floor-centered +Y-forward +Z-up root", "parts": parts,
      "budget_targets": {"lod_triangles": [18000, 9000, 3000], "material_slots": 3, "atlas_max_px": 2048, "transform_joints": 20},
      "budget_status": "authoring_targets_not_measured", "runtime_authority": "actual core events and committed cells only"})

provenance = {
    "schema": "wonder_vnext.reference_candidate.1", "asset_id": "wc_vn_prism_organ", "recorded_utc": utc,
    "classification": "ART_REVISE_generated_construction_candidate", "image_viewed": True,
    "visual_review": "VISUAL_REVIEW.md", "human_reference_approval": "not_received",
    "source": {"original_path": str(original), "project_path": str(image.relative_to(asset)).replace("\\", "/"),
               "sha256": sha(image), "bytes": image.stat().st_size, "dimensions_px": [width, height], "copied_without_modification": True},
    "generation": {"tool": "builtin image_gen.imagegen", "attempts_this_task": 1, "result": "succeeded",
                   "returned_output_file": original.name, "model_version": "not_returned_in_tool_fields", "seed": "not_returned",
                   "reference_input_path": str(direction), "reference_input_sha256": sha(direction),
                   "prompt_path": "generation_prompt.txt", "prompt_sha256": sha(ref / "generation_prompt.txt"),
                   "reference_pixels_supplied": True, "editable_layers": False, "orthographic_guarantee": False,
                   "additional_paid_api_job": False, "fallback_cli_used": False},
    "authority": {"direction_packet": "../wc_vn_direction/packet_manifest.json",
                  "direction_decision": "Use this direction", "decision_scope": "direction only, recorded by root; no new human decision inferred",
                  "canonical_source": "data/vnext/catalog.json", "canonical_source_sha256": sha(repo / "data/vnext/catalog.json"),
                  "hero_snapshot_sha256": sha(asset / "inputs/canonical_hero_snapshot_r001.json")},
    "not_run": ["Blender", "3D geometry measurement", "rig or motion", "Unreal import", "packaged art review", "human reference/forms/release approval"]}
write(ref / "provenance.json", provenance)

brief = json.loads((asset / "reports/brief_r001.json").read_text(encoding="utf-8-sig"))
brief["author"] = "Codex art_pipeline_audit"
brief["method"] = "Read canonical hero and owner-selected direction, initialized separate AS1 creature lane, defined proposed dimensions/parts/budgets, used one built-in image request, verified native image copy hashes and viewed actual result."
notes = ["Original stable gameplay identity and full creature route retained; independent art-only workspace.",
         "Selected input and exact prompt/output provenance recorded; only requested built-in reference use; no API fallback or extra purchase.",
         "Meters, +Y/+Z, one-cell occupancy, proposed bounds and actual strategy-camera review requirement declared; no measurements claimed.",
         "Finite indexed parts, provisional LOD/material/texture/joint targets, movement requirements and human gate dependencies declared."]
for check, note in zip(brief["checks"], notes):
    check.update(status="pass", notes=note, evidence=["BRIEF.md", "asset.json", "inputs/semantic_parts_r001.json"])
brief["artifacts"] = [{"path": p, "category": c} for p, c in [
    ("BRIEF.md", "source"), ("asset.json", "source"), ("inputs/semantic_parts_r001.json", "source"),
    ("inputs/canonical_hero_snapshot_r001.json", "source"), ("inputs/direction_r001.png", "image"),
    ("inputs/references/r001/generation_prompt.txt", "source"), ("inputs/references/r001/provenance.json", "report")]]
brief["executed_commands"] = ["assetctl.py init (new wc_vn_prism_organ creature lane)", "assetctl.py report-template brief/references",
    "image_gen.imagegen with actual owner-selected local reference", "view_image original direction and candidate", "SHA256 original/copy comparison"]
brief["notes"] = ["Brief observations complete; independent technical review pending. This is not a reference approval.",
                  "Generated reference has major defects; they are tracked in the separate references ART_REVISE report and do not represent achieved construction."]
write(asset / "reports/brief_r001.json", brief)

report = json.loads((asset / "reports/references_r001_ART_REVISE.json").read_text(encoding="utf-8-sig"))
report["author"] = "Codex art_pipeline_audit"
report["method"] = "Viewed the generated full sheet, compared visible assembled and exploded components to the selected direction and declared finite inventory, and recorded contradictions without certifying orthographic geometry."
for check in report["checks"]:
    check.update(status="not_run" if check["id"] == "identity_locked" else "fail",
                 evidence=["inputs/references/r001/VISUAL_REVIEW.md", "inputs/references/r001/prism_organ_reference_candidate.png"],
                 notes="Specific reference has no human approval." if check["id"] == "identity_locked" else "Major visible construction contradictions remain; see the exact per-defect visual review.")
descriptions = ["Front/three-quarter floating key inventory exceeds exploded K1-K4.",
                "Two emitter identities, hoop attachment and orthogonal relation are ambiguous across views.",
                "Pipe heights/order do not reconcile between assembled and exploded views.",
                "Lower resonator appears opaque; dossier stained-glass core is unresolved.",
                "Individual cradle interfaces and hoop/pipe clearances are unresolved.",
                "Generated view labels do not establish shared orthographic camera or measurements.",
                "Stray numeral after proposed-construction title."]
report["defects"] = [{"id": f"PR-REF-{i:03}", "severity": "major" if i < 7 else "minor", "status": "open", "description": d} for i, d in enumerate(descriptions, 1)]
report["artifacts"] = [{"path": "inputs/references/r001/" + p, "category": c} for p, c in [
    ("prism_organ_reference_candidate.png", "image"), ("generation_prompt.txt", "source"), ("provenance.json", "report"), ("VISUAL_REVIEW.md", "report")]]
report["executed_commands"] = ["One image_gen.imagegen request", "Native Copy-Item without resampling", "Get-FileHash original/copy", "view_image candidate"]
report["notes"] = ["ART_REVISE. Do not prepare or approve the references gate with these major defects open.",
                  "Direction only was selected by the owner. No modeling, camera calibration or human reference review occurred."]
write(asset / "reports/references_r001_ART_REVISE.json", report)
write(asset / "operations/reference_attempt_r001.json", {"asset_id": "wc_vn_prism_organ", "owner": "Codex art_pipeline_audit",
      "recorded_utc": utc, "attempt": 1, "result": "image_generated_reference_ART_REVISE", "scope": "brief and one reference image only",
      "output_sha256": sha(image), "image_viewed": True, "human_approval_issued": False,
      "next_operation": "Reconcile finite parts and attachment diagram before another generation/modeling; independent brief review is available."})
write(asset / "capabilities.json", {"recorded_utc": utc, "image_generation": "builtin image_gen.imagegen actually succeeded once",
      "image_review": "view_image actually used", "hashing": "SHA256 original/copy comparison passed",
      "asset_ledger": "assetctl init and report-template executed", "Blender": "not invoked in this task", "Unreal": "not invoked for this art asset",
      "network_policy": "no third-party uploads, API fallback, or additional paid job"})
print(json.dumps({"asset_id": "wc_vn_prism_organ", "reference_status": "ART_REVISE", "image_sha256": sha(image), "dimensions_px": [width, height], "image_bytes": image.stat().st_size}))
