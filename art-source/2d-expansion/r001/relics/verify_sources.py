"""Verify raw relic artwork provenance and document bounded source-stage inspection."""
from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

manifest_path = HERE / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
outputs = json.loads((HERE / "generation_outputs.json").read_text(encoding="utf-8"))
catalog = json.loads((ROOT / "data/vnext/catalog.json").read_text(encoding="utf-8"))
canonical = {row["id"]: row for row in catalog["relics"]}
selected = {}
for record in outputs:
    selected[record["id"]] = record

observations = {
    "wc_vn_r_quick_wick": "Revision2 removed the oversized floral vessel. Exposed ivory V with two separate amber flames and a small ferrule; wider negative space than the other icons. Verify 32 px recognition in engine.",
    "wc_vn_r_long_lens": "Long diagonal telescope and distant point remain distinct from the round Close Focus loupe.",
    "wc_vn_r_broad_canopy": "Broad three-lobe leaf canopy and exactly three separated luminous drops are visible.",
    "wc_vn_r_close_focus": "Large thick circular lens, short handle and one near concentrated point; outer shape differs from Long Lens.",
    "wc_vn_r_tight_choir": "Exactly three visible ivory pipe openings and a dark binding give a compact vertical bundle.",
    "wc_vn_r_silk_trigger": "Revision2 contains both tapered strand ends inside the square; central bronze catch and strong ivory diagonal retained. Fine silk frays are detail only.",
    "wc_vn_r_patient_lantern": "Rounded enclosed chamber, steady amber core and hanging loop contrast with Quick Wick's open V.",
    "wc_vn_r_far_hourglass": "Tall narrow pointed instrument with hourglass bulbs; its thin internal stream is decorative at 32 px. Native-size review must check the remaining outer silhouette.",
    "wc_vn_r_wide_hourglass": "Broad horizontal waist ring clearly separates it from Far Hourglass; central two-bulb hourglass remains visible.",
    "wc_vn_r_narrow_metronome": "Triangular dark wooden body, one pale pendulum and restrained arc; no numbers or clock face.",
    "wc_vn_r_urgent_shard": "One large diagonal glass shard, small bright leading point and a tapering amber trail; separated from telescope by facets and asymmetric outline."
}
checks = []
for item in manifest["items"]:
    identity = item["id"]
    path = HERE / item["source"]
    raw = Path(selected[identity]["src"])
    assert identity in canonical and canonical[identity]["name"] == item["name"], identity
    with Image.open(path) as image:
        image.load()
        width, height = image.size
        mode = image.mode
        image_format = image.format
    assert image_format == "PNG" and width == height and width >= 1024, identity
    assert mode == "RGB", (identity, mode)
    assert sha(path) == sha(raw), identity
    revision = selected[identity].get("revision", 1)
    item.update({
        "status": "GENERATED_SOURCE_VISUALLY_INSPECTED_PENDING_ENGINE_OWNER_REVIEW",
        "source_file": path.relative_to(ROOT).as_posix(),
        "sha256": sha(path),
        "bytes": path.stat().st_size,
        "width": width,
        "height": height,
        "mode": mode,
        "format": image_format,
        "generation_source_path": str(raw),
        "selected_revision": revision,
        "prompt_files": ["prompts/" + identity + ".txt"] + (["prompts/" + identity + "_revision.txt"] if revision == 2 else []),
        "visual_observation": observations[identity],
        "canonical_description_at_generation": canonical[identity]["description"],
        "target_cooked_dimensions": [512, 512],
        "raw_bytes_preserved": True,
        "human_approval": "PENDING",
        "engine_import": "ROOT_INTEGRATION_QUEUE_PENDING"
    })
    checks.append({"id": identity, "canonical_identity": "PASS", "png_decode": "PASS", "opaque_rgb": "PASS", "raw_hash_match": "PASS", "source_visual_inspection": "PASS_BOUNDED", "width": width, "height": height, "sha256": sha(path)})
references = []
for text in manifest.pop("reference_paths", []):
    path = Path(text)
    references.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "role": "material_and_shape_reference" if "ref03" in path.name else "owner_approved_material_backdrop_reference", "viewed_before_generation": True})
if references:
    manifest["references"] = references
manifest.update({
    "status": "COMPLETE_SOURCE_BATCH_PENDING_ENGINE_AND_OWNER_REVIEW",
    "verified_at_utc": datetime.now(timezone.utc).isoformat(),
    "canonical_catalog_sha256": sha(ROOT / "data/vnext/catalog.json"),
    "source_spec": "docs/vnext/art/2D_CONTENT_SPEC.md",
    "generated_calls": len(outputs),
    "selected_count": len(manifest["items"]),
    "existing_control": {"id": "wc_vn_r_heavy_bloom", "path": "art-source/2d-slice/r001/sources/heavy_bloom.png", "sha256": sha(ROOT / "art-source/2d-slice/r001/sources/heavy_bloom.png"), "mutated": False},
    "rejected_revisions": [
        {"path": "rejected/wc_vn_r_quick_wick_r1_vessel_too_large.png", "sha256": sha(HERE / "rejected/wc_vn_r_quick_wick_r1_vessel_too_large.png"), "reason": "Large floral vessel confused the distinct exposed-wick motif."},
        {"path": "rejected/wc_vn_r_silk_trigger_r1_cropped_strand.png", "sha256": sha(HERE / "rejected/wc_vn_r_silk_trigger_r1_cropped_strand.png"), "reason": "Main silk strand was clipped by two image boundaries."}
    ],
    "native_size_review": {"status": "NOT_RUN_IN_BROWSER_POLICY_BLOCK", "artifact": "size_review.html", "sizes_css_px": [32, 64, 128], "reason": "CUA denied the local file URL under browser security policy. No workaround was attempted. Source previews inspected; native Unreal size/state review is a separate required integration gate."},
    "acceptance_limits": ["Painted source studies, not vector or final UI acceptance.", "No engine import, cook, packaged review, disabled/focus/selection-state verification or human acceptance is claimed by this source subtask.", "Full-size source inspection cannot establish 32 px readability.", "Current relic mechanics and all canonical data were read only."]
})
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
report = {"status": "PASS_SOURCE_TECHNICAL_CHECKS_ENGINE_REVIEW_PENDING", "count": len(checks), "checks": checks, "not_run": ["native_browser_size_review_policy_block", "unreal_import", "cooked_game_size_and_states", "owner_art_acceptance"]}
(HERE / "source_verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": report["status"], "count": len(checks), "dimensions": sorted({(row["width"], row["height"]) for row in checks}), "selected_bytes": sum(item["bytes"] for item in manifest["items"]), "manifest": str(manifest_path)}))

