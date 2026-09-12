import json,hashlib,copy,re
from pathlib import Path
from datetime import datetime,timezone
root=Path(r"C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001")
repo=Path(r"C:/Users/iputu/Documents/Wonder Chess")
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
frozen=read(root/"reviews/final_frozen_audit.json")
work=read(root/"reviews/final_work_audit.json")
chain=read(root/"reviews/final_source_chain_and_equivalence.json")
contact=read(root/"reviews/carry_contact_measurements.json")
geo=read(root/"integrated-independent/integrated_geometry_audit.json")
video=read(root/"motion-carry-final/video_verification.json")
sheets=read(root/"motion-carry-final/contact_sheet_manifest.json")
assert all(frozen["required_checks"].values()) and all(work["required_checks"].values())
assert all(chain["required_checks"].values())
assert video["decoded_frames"]==145 and sheets["total_frames"]==145
assert geo["variants"][0]["self_intersections"]["confirmed_nonadjacent_transverse_pairs"]==375
assert contact["held_frame_count"]==121
assert all(v["passed_frames"]==121 for v in contact["held_summary_per_digit"].values())
assert sha(Path(frozen["candidate"]))==frozen["candidate_sha256"]
assert sha(Path(work["candidate"]))==work["candidate_sha256"]
paths=["ada_bw2_grip_work.blend","ada_bw2_grip_checkpoint_r001_ART_REVISE.blend","REVIEW.md","records/frozen_scene_contract.json","captures/comparison_BW2_initial_vs_retained.png","baseline-r003/comparison_BW1_r003_vs_BW2.png","captures/actual_posed_cage_axial.png","captures/actual_posed_cage_back.png","captures/grip_retained_reversed_light.png","captures/integrated_axial_handle_hidden.png","motion-carry-final/ada_bw2_fixed_handle_ART_REVISE.mp4"]
for p in paths: assert (root/p).is_file(),p
review={"status":"VISUALLY_REVIEWED_ART_REVISE","reviewer":"Codex","human_approval":False,"all_native_frames_seen_in_sheets":145,"sheet_files":[v["file"] for v in sheets["sheets"]],"native_detail_frames":[14,25,93,121],"live_timeline_playback_operated_with_computer_use":True,"observations":["Hand and fixture remain within the movie frame across the unskipped sequence.","Thumb-web fold develops during closure and persists in the held movement.","Middle/ring and thumb-neighbor intersections remain unresolved; no accepted grasp.","Source camera tracks translation only; wrist/arm rotations are visible. This is an authoring diagnostic, not game animation."],"continuous_collision_certification":False}
(root/"records/temporal_visual_review.json").write_text(json.dumps(review,indent=2)+"\n",encoding="utf-8")
record={"schema_version":"bw2.local_result.1","status":"EXECUTED_ART_REVISE","utc":datetime.now(timezone.utc).isoformat(),"scope":"anatomical-right fixed-handle grip only","scene":"BW2_RIGHT_GRIP","inspection_frame":37,"source_parent_sha256":frozen["baseline_sha256"],"files":{p:{"sha256":sha(root/p),"bytes":(root/p).stat().st_size} for p in paths},"evidence":{"frame_axes":"calibration-independent/finger_axis_calibration.json","joint_probes":90,"frozen_preservation":"reviews/final_frozen_audit.json","work_preservation":"reviews/final_work_audit.json","source_chain":"reviews/final_source_chain_and_equivalence.json","contact":"reviews/carry_contact_measurements.json","geometry":"integrated-independent/integrated_geometry_audit.json","local_weight_diagnosis":"integrated-independent/web_weight_diagnosis.json","movie_decode":"motion-carry-final/video_verification.json","all_frame_visual_review":"records/temporal_visual_review.json"},"preservation":{"files_unchanged":62,"original_mesh_records_exact":61,"old_animation_curves_exact":492,"original_body_vertices":19158,"original_shape_keys":38,"candidate_shape_keys":44,"coat_even_offset":False,"coat_inward_thickness_m":0.006,"leggings_even_offset":False,"leggings_inward_thickness_m":0.002},"gates":{"F01":"PASS_COORDINATE_AND_VISUAL_CALIBRATION","F02":"PASS_REVERSIBLE_SMALL_ANGLE_PROBES_ONLY","G01":"FAIL_SELF_INTERSECTION_ART_REVISE","G02":"FIXTURE_ATTACHMENT_MEASURED_FULL_GRIP_FAIL_ART_REVISE","G03":"NOT_RUN","A01":"NOT_RUN","C01":"NOT_RUN","K01":"NOT_RUN","B01":"NOT_RUN","V01":"NOT_RUN_FULL_CHARACTER","T01":"GRIP_DIAGNOSTIC_145_FRAMES_EXECUTED_OLD_169_PROBE_PRESERVED_FULL_COSTUME_RETEST_NOT_RUN","P01":"PASS_REOPEN_AND_PRESERVATION","R01":"AUTHORING_ONLY_RUNTIME_NOT_RUN","RP1":"NOT_RUN","RP2":"NOT_RUN"},"contact_sample_screens":contact["held_summary_per_digit"],"held_frames":121,"max_handle_drift_mm":contact["maximum_held_handle_drift_mm"],"max_handle_drift_deg":contact["maximum_held_handle_drift_deg"],"static_ideal_cylinder_max_triangle_depth_mm":geo["variants"][0]["cylinder"]["max_triangle_depth_mm_interval"],"glove_self_crossing_pairs":375,"body_self_crossing_pairs":567,"actual_sword_fit":"NOT_RUN_FAILED_GRIP_GATE","human_forms_approval":False,"recipes_promoted":0,"canonical_skeleton_changed":False,"runtime_integration":"NOT_RUN","neural_training":"NOT_RUN","next_intervention":"Collision-free thumb opposition and web construction on an isolated body/glove copy; separately resolve middle/ring neighbor clearance before contact optimization."}
(root/"verification.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
state_path=repo/"reports/implementation_state.json"
with state_path.open(encoding="utf-8",newline="") as f: raw=f.read()
state=json.loads(raw)
before=read(root/"implementation_state_before_BW2.json")
assert state==before,"Unexpected concurrent implementation-state change"
updated=copy.deepcopy(state);as1=updated["as1_asset_studio"]
fields=["ada_status","review_packet","checkpoint","active_blend","frozen_blend","next_required_action","separate_art_review"]
as1["bw2_previous_bw1_context"]={k:as1.get(k) for k in fields}
rel=root.relative_to(repo).as_posix()
as1.update({"ada_status":"BW2_RIGHT_GRIP_EXECUTED_ART_REVISE","review_packet":rel+"/REVIEW.md","checkpoint":rel+"/verification.json","active_blend":rel+"/ada_bw2_grip_work.blend","frozen_blend":rel+"/ada_bw2_grip_checkpoint_r001_ART_REVISE.blend","next_required_action":record["next_intervention"],"separate_art_review":"Verified frame, fixed fixture and improved pad wrap. Complete grasp fails:375 glove self-crossing pairs including middle/ring and thumb/web; no sword fit or human approval."})
as1["ada_body_contact_bw2"]={"status":record["status"],"revision":"r001","frozen_sha256":frozen["candidate_sha256"],"protected_files_unchanged":62,"approved_reference":"accepted_current","right_grip":"FAIL_ART_REVISE","sampled_contact_held_frames":121,"motion_frames":145,"movie_decoded_frames":145,"glove_self_crossing_pairs":375,"body_self_crossing_pairs":567,"local_rig_bones":163,"canonical_skeleton_changed":False,"human_forms_approval":False,"runtime_integration":"NOT_RUN","independent_replay":"NOT_RUN","second_body_fit":"NOT_RUN","recipes_promoted":0,"neural_training":"NOT_RUN","verification":rel+"/verification.json","review":rel+"/REVIEW.md","movie":rel+"/motion-carry-final/ada_bw2_fixed_handle_ART_REVISE.mp4"}
assert {k:v for k,v in state.items() if k!="as1_asset_studio"}=={k:v for k,v in updated.items() if k!="as1_asset_studio"}
for k,v in state["as1_asset_studio"].items():
    if k not in fields: assert as1[k]==v,k
newline="\r\n" if "\r\n" in raw else "\n"
with state_path.open("w",encoding="utf-8",newline="") as f:f.write((json.dumps(updated,indent=2,ensure_ascii=False)+"\n").replace("\n",newline))
assert read(state_path)==updated
changes={"scope":"Only current AS1 art pointers and new BW2 record; previous BW1 pointers retained.","before_sha256":sha(root/"implementation_state_before_BW2.json"),"after_sha256":sha(state_path),"outside_as1_unchanged":True,"historical_as1_members_unchanged":True,"changed_existing_as1_fields":fields,"added_as1_fields":["bw2_previous_bw1_context","ada_body_contact_bw2"]}
(root/"records/implementation_state_change.json").write_text(json.dumps(changes,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"verification":str(root/"verification.json"),"status":record["status"],"outside_as1_unchanged":True,"delivery_files_hashed":len(paths),"motion_frames_reviewed":145}))

