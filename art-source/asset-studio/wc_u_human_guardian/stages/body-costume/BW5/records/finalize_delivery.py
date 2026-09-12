"""Seal the executed BW5 delivery and record only its AS1 state update."""
from pathlib import Path
from datetime import datetime, timezone
import copy
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[5]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


report = ROOT / "REVIEW.md"
content = report.read_text(encoding="utf-8")
linked = []


def absolute_link(match):
    label, value = match.groups()
    raw = value.strip("<>")
    target = Path(raw) if Path(raw).is_absolute() else ROOT / raw
    target = target.resolve()
    assert target.is_file() or target == ROOT / "verification.json", target
    linked.append(str(target))
    return f"[{label}](<{target.as_posix()}>)"


content = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", absolute_link, content)
report.write_text(content, encoding="utf-8")

preservation = read(ROOT / "records/preservation_after.json")
assert preservation["checked"] == preservation["unchanged"] == 169
assert not preservation["mismatches"]
armor = read(ROOT / "armor/verification_r003.json")
assert armor["work_frozen_mesh_signatures_match"]
frozen = Path(armor["frozen"])
assert digest(frozen) == armor["frozen_sha256"]
assert digest(Path(armor["source_work"])) == armor["work_sha256"]
integrity = read(ROOT / "armor/records/surface_integrity_r003.json")
assert integrity["sha256"] == armor["frozen_sha256"]
assert integrity["source_authoring_action_curves_exactly_equal"]
assert len(integrity["parts"]) == 19
assert all(part[mode]["confirmed_transverse_self_pairs"] == 0
           for part in integrity["parts"].values() for mode in ("raw", "evaluated"))
motion = read(ROOT / "armor/motion/r003/source_record.json")
assert motion["sha256"] == armor["frozen_sha256"]
assert digest(Path(motion["movie"])) == motion["movie_sha256"]
video = read(ROOT / "armor/motion/r003/video_verification.json")
assert video["frames_decoded"] == 97
assert all(digest(ROOT / "armor/motion/r003/decoded" / name) == value
           for name, value in video["decoded_hashes"].items())
all97 = read(ROOT / "armor/records/r003_all97_crossings.json")
assert all97["sha256"] == armor["frozen_sha256"]
subframes = read(ROOT / "armor/records/r003_critical_subframes.json")
assert len(subframes["frames"]) == 8
assert subframes["sha256"] == armor["frozen_sha256"]
binding = read(ROOT / "reviews/torso_r003_motion_readonly/review_source_binding.json")
fit = read(ROOT / "analysis/R003_FINAL_FIT_SUMMARY.json")
assert fit["source_sha256"] == armor["frozen_sha256"]

state_path = REPO / "reports/implementation_state.json"
before = read(ROOT / "records/implementation_state_before.json")
state = read(state_path)
assert {k: v for k, v in state.items() if k != "as1_asset_studio"} == {
    k: v for k, v in before.items() if k != "as1_asset_studio"}
as1 = state["as1_asset_studio"]
old = before["as1_asset_studio"]
previous_fields = ("ada_status", "active_blend", "frozen_blend", "review_packet", "checkpoint",
                   "next_required_action", "user_feedback", "separate_art_review")
as1["bw5_previous_bw4_context"] = {k: copy.deepcopy(old[k]) for k in previous_fields}
prefix = ROOT.relative_to(REPO).as_posix()
as1.update({
    "updated_utc": datetime.now(timezone.utc).isoformat(),
    "ada_status": "BW5_ARMOR_PROPORTION_FIT_EXECUTED_ART_REVISE",
    "active_blend": prefix + "/armor/ada_bw5_armor_work.blend",
    "frozen_blend": prefix + "/armor/ada_bw5_armor_checkpoint_r003_ART_REVISE.blend",
    "review_packet": prefix + "/REVIEW.md",
    "checkpoint": prefix + "/verification.json",
    "user_feedback": "BW5 armor proportion and fit primary; independent fixed-hand root/web repair. Retain selected 30x26mm, 110mm exposed candidate hilt. Preserve masters and game; no approval claims.",
    "separate_art_review": "All lanes ART_REVISE. Torso shorter/shallower but upper gap, flat planes, old collar and waist/side/bending conflicts remain. Separate shoulder self-folds and suspension fail. Hand transverse screen clears but anatomy/contact fail.",
    "next_required_action": "Bounded methods parked. Reconstruct upper plate/neckline and side closure against a designed padded-collar interface; separately redesign cap suspension and thickness-safe edge. Hand needs local palm/thenar/proximal-knuckle sculpt/control surface, not tighter repeated rings. No canonical promotion or dependent runtime work until local construction is credible.",
})
as1["ada_proportion_fit_bw5"] = {
    "status": "EXECUTED_ART_REVISE",
    "primary_lane": "ARMOR_PROPORTION_AND_FIT",
    "armor_revision": "r003_integrity_repair_after_bounded_construction",
    "armor_frozen_sha256": armor["frozen_sha256"],
    "shoulder_frozen_sha256": digest(ROOT / "shoulder/ada_bw5_shoulder_checkpoint_ART_REVISE.blend"),
    "hand_frozen_sha256": digest(ROOT / "hand/ada_bw5_hand_checkpoint_ART_REVISE.blend"),
    "protected_inputs_unchanged": 169,
    "plate_H_over_W": {"BW4": fit["ratios"]["BW4"]["H/W"], "BW5": fit["ratios"]["BW5_r003"]["H/W"]},
    "collar_fullspan_over_W": fit["ratios"]["BW5_r003"]["C/W"],
    "waist_exposure_over_plate_H": fit["ratios"]["BW5_r003"]["U/H"],
    "armor_integer_frames": 97,
    "armor_extra_subframes": 8,
    "separate_static_torso_diagnostics": 2,
    "armor_owned_part_self_query": "19 parts, zero raw/evaluated confirmed transverse pairs at frame1; not complete fit acceptance",
    "torso_fit": "FAILED_UPPER_GAP_FLAT_PLANES_COLLAR_SIDE_WAIST_AND_BENDING",
    "shoulder": "SEPARATE_REJECTED_STUDY_SELF_FOLDS_AND_SUSPENSION_FAILURE_NOT_ADOPTED",
    "hand": "SEPARATE_CORRECTION1_RETAINED_TRANSVERSE_SCREEN_CLEAR_FORMS_AND_ALL_PAD_GROUP_CONTACT_FAIL",
    "collar": "FAILED_BW5_EXPERIMENT_HIDDEN_OLD_BW4_CONTEXT_RESTORED_UNAPPROVED",
    "source_save_reopen": "EXECUTED_ALL_THREE_LANES",
    "motion": "Armor and shoulder native97-frame authoring diagnostics; hand48-frame static camera orbit. Not seven game clips.",
    "reference_gate_changed": False,
    "human_forms_approval": False,
    "canonical_assets_replaced": False,
    "canonical_skeleton_changed": False,
    "new_cuff_bracer_integration": "NOT_RUN_LOCAL_GATE_FAILED",
    "seven_game_clips_and_transitions": "NOT_RUN",
    "unreal_import_reimport_packaged": "NOT_RUN",
    "recipes_promoted": 0,
    "review": prefix + "/REVIEW.md",
    "verification": prefix + "/verification.json",
}
allowed = set(previous_fields) | {"updated_utc", "bw5_previous_bw4_context", "ada_proportion_fit_bw5"}
assert all(as1[k] == value for k, value in old.items() if k not in allowed)
assert as1["human_approvals"] == old["human_approvals"]
write(state_path, state)
write(ROOT / "records/state_update_verification.json", {
    "changed_scope": "as1_asset_studio BW5 current pointers, review and new stage only",
    "non_as1_top_level_values_unchanged": True,
    "historical_stage_records_and_human_approvals_unchanged": True,
    "state_sha256": digest(state_path),
    "changed_as1_keys": sorted(k for k in as1 if as1.get(k) != old.get(k)),
})

included = set()
for folder in ("armor", "hand", "shoulder", "analysis", "reviews", "records"):
    for path in (ROOT / folder).rglob("*"):
        if path.is_file() and path.suffix.lower() in {".blend", ".json", ".md", ".mp4", ".py"}:
            included.add(path)
for name in linked:
    path = Path(name)
    if path.exists() and path != ROOT / "verification.json":
        included.add(path)
included.add(report)
artifacts = {path.relative_to(ROOT).as_posix(): digest(path) for path in sorted(included)}
verification = {
    "status": "EXECUTED_ART_REVISE",
    "verified_utc": datetime.now(timezone.utc).isoformat(),
    "primary_source": armor["frozen"],
    "primary_source_sha256": armor["frozen_sha256"],
    "protected_inputs_checked": 169,
    "protected_inputs_unchanged": 169,
    "save_reopen": {"armor": "armor/verification_r003.json", "hand": "hand/verification.json", "shoulder": "shoulder/verification.json"},
    "reference_and_human_approvals_unchanged": True,
    "original_context_mesh_key_records_unchanged_in_armor": 93,
    "historical_camera_and_action_data_preserved": True,
    "primary_armor_owned_self_screen": {"parts": 19, "frame": 1, "raw_and_evaluated_confirmed_transverse_pairs": 0},
    "armor_all97_crossing_summary": all97["summary"],
    "armor_extra_frames": [entry["frame"] for entry in subframes["frames"]],
    "armor_static_bend_and_twist_tests": 2,
    "armor_movie_sha256": motion["movie_sha256"],
    "armor_encoded_frames_decoded_and_hash_checked": 97,
    "visual_review": "All97 latest encoded armor frames in chronological sheets, native stills; separate shoulder97 and hand8/48 temporal samples. No real-time playback claim.",
    "visual_review_record": "reviews/independent_hand_torso_visual_REVIEW.md",
    "interpretation": "Torso proportion improved; full fit, shoulder construction/suspension and hand form/contact remain failed. Geometry screens do not confer art approval.",
    "not_run": ["Canonical candidate seven animations/transitions", "Game bind conversion", "New cuff/bracer integration", "Unreal import/reimport", "Packaged tests", "Second-body fit", "Human forms approval"],
    "canonical_replacement": False,
    "recipe_promotion": False,
    "artifact_count": len(artifacts),
    "artifacts": artifacts,
}
write(ROOT / "verification.json", verification)
assert all(Path(p).is_file() for p in linked)
assert all(digest(ROOT / p) == h for p, h in artifacts.items())
assert read(state_path) == state
print(json.dumps({"status": verification["status"], "artifact_hashes_verified": len(artifacts), "report_links_verified": len(linked), "protected_unchanged": 169, "state_scope_verified": True, "armor_source_sha256": armor["frozen_sha256"]}))
