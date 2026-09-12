"""Seal the BW1 review evidence and update only its project art-state pointers."""
from pathlib import Path
import datetime, hashlib, json, subprocess, sys

repo=Path(r"C:/Users/iputu/Documents/Wonder Chess")
pilot=repo/"art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001"
asset=repo/"art-source/asset-studio/wc_u_human_guardian"
prefix=pilot.relative_to(asset).as_posix()
def read(path): return json.loads(path.read_text(encoding="utf-8-sig"))
def write(path,value): path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
before=read(pilot/"preservation_before.json")
preserved=[]
for item in before["files"]:
    path=Path(item["path"]); current=sha(path) if path.is_file() else None
    preserved.append({**item,"after_sha256":current,"unchanged":current==item["sha256"]})
assert all(item["unchanged"] for item in preserved), "Protected input changed; do not seal."
write(pilot/"preservation_after.json",{"checked_utc":now,"count":len(preserved),"all_unchanged":True,"files":preserved})

frozen=pilot/"ada_body_costume_checkpoint_r003_ART_REVISE.blend"
expected="03829ab406d6bd5e6a1c5f86e045e9f2edc720b05e620e70017667c59be8b3f8"
assert sha(frozen)==expected
work_hash=sha(pilot/"ada_body_costume_work.blend")
audit=read(pilot/"reviews/final_reopen_r003_audit.json")
assert all(audit["required_checks"].values()), "Final reopen checks failed."
assert audit["identity_observation"]["semantic_equality"]
assert audit["identity_observation"]["work_sha256"]==work_hash
movie=pilot/"motion-r003/ada_bw1_articulation_r003_review.mp4"
assert movie.is_file() and movie.stat().st_size>1000
metadata=read(pilot/"motion-r003/metadata.json")
assert metadata["source_sha256"]==expected
assert metadata["frame_count"]==169 and metadata["fps"]==24
video=read(pilot/"motion-r003/video_verification.json")
assert video["sha256"]==sha(movie) and video["frame_duration"]==169
motion_audit=read(pilot/"motion-r003/clothing_temporal_audit.json")
assert not motion_audit["extreme_vertex_events"]
assert not any(x["object"] in ["BW1_Leggings","BW1_CoatUpper_Continuous"] for x in motion_audit["temporal_flags"])

report=read(pilot/"reviews/as1_blockout_review.json")
report["author"]="Codex BW1 authoring pass"
report["method"]="Native MPFB full-source fitting; helper-derived coat; one CC0 glove/boot adaptation; original armor/equipment cages; actual temporary FK poses; two failed grip and knee corrections; independent image review. Technical r002 and r003 disable leggings and coat Solidify even-offset spikes without cage/weight/action edits."
report["notes"]=["ART_REVISE. No human approval.", "AS1 human reference approval remains unchanged. Body work independently authorized by BW1.", "Independent image review: reviews/independent_visual_review.md. The frozen candidate retains major art and motion defects.", "No replay/second-body fit or recipe promotion."]
artifacts=[
("ada_body_costume_checkpoint_r003_ART_REVISE.blend","source"),
("reviews/reference_comparison_r003.png","image"),
("captures/r003_context_front.png","image"),
("captures/r003_context_profile.png","image"),
("captures/r003_context_reversed_key.png","image"),
("captures/arm_pose_shoulder_raise.png","image"),
("captures/technical_r002_frame_129.png","image"),
("hand-pose-study/sword_grip_final.png","image"),
("motion-r003/ada_bw1_articulation_r003_review.mp4","video"),
("REVIEW.md","report"),
("reviews/independent_visual_review.md","report"),
("reviews/final_reopen_r003_audit.json","report"),
("body_preset_r003.json","report"),
("construction_records.json","report"),
("captures/edit_glove.png","image"),
("captures/edit_sleeve.png","image"),
("captures/edit_boot.png","image"),
("captures/edit_pauldron_clear.png","image"),
("captures/edit_greave_clear.png","image"),
("captures/edit_sole.png","image"),
("motion-r003/MOTION_REVIEW.md","report"),
("motion-r003/clothing_temporal_audit.json","report"),
("motion-r003/video_verification.json","report")]
for path,category in artifacts: assert (pilot/path).is_file(),path
report["artifacts"]=[{"path":prefix+"/"+p,"category":c} for p,c in artifacts]
observations={
"silhouette_and_proportions":("fail","Adult foundation exists, but armor/tailoring silhouette diverges materially from Ada; no accepted likeness score.",["reviews/reference_comparison_r003.png"]),
"camera_alignment":("fail","Fixed orthographic cameras and both three-quarter views executed. Painted reference/candidate pose are not pixel-registered; no perfect alignment claimed.",["captures/r003_context_front.png","captures/r003_context_profile.png"]),
"major_part_clearance":("fail","Shoulder/bracer gaps, failed grips, moving thigh/coat penetration and knee/greave coverage defects remain.",["captures/arm_pose_shoulder_raise.png","captures/technical_r002_frame_129.png","hand-pose-study/sword_grip_final.png"]),
"method_is_capable":("fail","Continuous cloth and footprint sole helped locally, but complete arm and leg methods failed; stop rules reached; no recipe promotion.",["reviews/independent_visual_review.md","motion-r003/ada_bw1_articulation_r003_review.mp4"])}
for check in report["checks"]:
    status,notes,ev=observations[check["id"]];check.update(status=status,notes=notes,evidence=[prefix+"/"+p for p in ev])
report["defects"]=[
{"id":"BW1-GRIP","severity":"major","status":"open","description":"Incorrect handle enclosure/opposing thumb; stopped after two corrective attempts."},
{"id":"BW1-ARM","severity":"major","status":"open","description":"Shoulder and bracer attachment/clearance fails raised-arm proof."},
{"id":"BW1-CLOTH","severity":"major","status":"open","description":"Root-weighted hanging panels intersect moving thighs."},
{"id":"BW1-KNEE","severity":"major","status":"open","description":"Cup coverage and greave overlap fail bend/kneel; two attachment corrections rejected."},
{"id":"BW1-SILHOUETTE","severity":"major","status":"open","description":"Floating torso panels, broad band-like armor, rough openings and boot junctions remain."},
{"id":"BW1-SPIKE","severity":"major","status":"fixed","description":"Reproducible leggings and coat Solidify spikes fixed by disabling even offset in technical r002 and r003 respectively; all-frame checks are separate evidence."}]
report["executed_commands"]=[prefix+"/operations/"+p.name for p in sorted((pilot/"operations").glob("*.py"))]
write(pilot/"reviews/as1_blockout_review.json",report)
ctl=repo/"production/asset-studio/tools/asset_studio/assetctl.py"
status=subprocess.run([sys.executable,str(ctl),"status","--workspace",str(asset)],text=True,capture_output=True)
assert status.returncode==0,status.stderr
gate_status=json.loads(status.stdout);write(pilot/"reviews/as1_gate_status.json",gate_status)
assert next(x for x in gate_status if x["stage"]=="references")["status"]=="accepted_current"
assert next(x for x in gate_status if x["stage"]=="forms")["status"]=="pending"
attempt=subprocess.run([sys.executable,str(ctl),"prepare","--workspace",str(asset),"--report",prefix+"/reviews/as1_blockout_review.json"],text=True,capture_output=True)
assert attempt.returncode==2,"A failed art report must not be sealed as a passing gate."
write(pilot/"reviews/as1_gate_rejection.json",{"expected_rejection":True,"exit_code":attempt.returncode,"stdout":attempt.stdout,"stderr":attempt.stderr,"approval_issued":False})
assert all(sha(Path(item["path"]))==item["sha256"] for item in before["files"]), "Protected input changed during gate check."

statepath=repo/"reports/implementation_state.json";state=read(statepath)
snapshot=pilot/"implementation_state_before_BW1.json"
if not snapshot.exists(): snapshot.write_bytes(statepath.read_bytes())
old_as1=dict(state["as1_asset_studio"])
state["as1_asset_studio"]["bw1_previous_mp1_context"]={key:old_as1[key] for key in ["ada_status","review_packet","checkpoint","active_blend","frozen_blend","next_required_action","user_feedback","separate_art_review"] if key in old_as1}
rel=pilot.relative_to(repo).as_posix()
state["as1_asset_studio"].update({
"updated_utc":now,"ada_status":"BW1_BODY_COSTUME_EXECUTED_ART_REVISE",
"active_blend":rel+"/ada_body_costume_work.blend",
"frozen_blend":rel+"/ada_body_costume_checkpoint_r003_ART_REVISE.blend",
"review_packet":rel+"/REVIEW.md","checkpoint":rel+"/verification.json",
"user_feedback":"User authorized independent BW1 full-body/costume study from retained MP1 source; preserve head ART_REVISE, no hair/game changes.",
"next_required_action":"Retain indexed foundation, continuous garment and right footprint sole. A new bounded intervention must solve one fixed-dimension hand/handle contact before recipe promotion; shoulder/knee suspension and moving panels remain separate ART_REVISE tasks.",
"separate_art_review":"Neither complete arm/grip nor leg/boot proof passed. Grip and knee stop rules reached. Technical r003 fixed Solidify miter spikes; no human art approval.",
"ada_body_costume_bw1":{
"status":"EXECUTED_ART_REVISE","technical_revision":"r003",
"frozen_sha256":expected,"source_indexed_vertices":19158,"original_shape_keys_preserved":38,"candidate_shape_keys":44,
"complete_arm_proof":"FAIL_ART_REVISE","complete_leg_proof":"FAIL_ART_REVISE",
"original_files_preserved":True,"approved_reference":"accepted_current",
"local_rig_bones":163,"canonical_skeleton_changed":False,
"source_adaptations":["MRT toigo_gloves_short CC0","MRT toigo_ankle_boots_male CC0"],
"human_forms_approval":False,"runtime_integration":"NOT_RUN",
"independent_replay":"NOT_RUN","second_body_fit":"NOT_RUN","recipes_promoted":0,"neural_training":"NOT_RUN",
"verification":rel+"/verification.json","review":rel+"/REVIEW.md","movie":rel+"/motion-r003/ada_bw1_articulation_r003_review.mp4"}})
# All non-art top-level state, and all historical MP1/ACB1/HP1 records, remain exact JSON values.
prior=read(snapshot)
assert all(state[k]==prior[k] for k in prior if k!="as1_asset_studio")
for key in ["ada_mpfb_mp1","ada_closure_acb1","ada_head_polish","human_approvals"]:
    assert state["as1_asset_studio"][key]==prior["as1_asset_studio"][key]
write(statepath,state)
verification={
"status":"EXECUTED_REVIEWABLE_ART_REVISE","checked_utc":now,
"frozen_file":frozen.name,"frozen_sha256":expected,"work_file_sha256":work_hash,"work_file_identical_to_frozen":work_hash==expected,"work_file_semantically_equal_to_frozen":True,
"protected_inputs":{"count":len(preserved),"all_unchanged":True,"details":"preservation_after.json"},
"reopen_audit":"reviews/final_reopen_r003_audit.json","source_measurements":"reviews/body_measurements.json",
"art_review":"reviews/independent_visual_review.md","human_forms_approval":False,
"brief_and_references":"accepted_current","downstream_gates":"pending","failed_gate_rejected_as_expected":True,
"actual_motion":{"file":"motion-r003/ada_bw1_articulation_r003_review.mp4","sha256":sha(movie),"frames":169,"fps":24,"seconds":169/24,"source_sha256":expected,"scope":"Temporary FK range diagnostic, not retargeted runtime Move"},
"art_outcomes":{"body_foundation":"retained_candidate","continuous_cloth":"static_improvement_only","footprint_sole":"local_improvement_only","grips":"failed_two_corrections","arm_assembly":"ART_REVISE","knee_attachment":"failed_two_corrections","leg_assembly":"ART_REVISE"},
"technical_fixes":[{"object":"BW1_CoatUpper_Continuous","modifier":"Padded garment thickness","property":"use_even_offset","before":True,"after":False,"thickness_m":.006,"offset":-1,"old_spike_evidence":"motion-r002/coat_even_offset_false_temporal_audit.json"},{"object":"BW1_Leggings","modifier":"Garment thickness","property":"use_even_offset","before":True,"after":False,"thickness_m":.002,"offset":-1,"old_spike_evidence":"motion-final/leggings_modifier_isolation.json"}],
"not_run":["second_body_fit","independent_recipe_replay","neural_training","final_textures","production_animation_bank","runtime_skeleton_change","export_import_reimport","Unreal_package_tests","human_approval"],
"game_state_preserved":True,"runtime_source_edited":False,
"test_scope":"Targeted Blender source/reopen/numeric/visual/motion checks only. No full game or infrastructure suite rerun because no gameplay/tool implementation changed.",
"artifact_hashes":[{"path":p,"sha256":sha(pilot/p)} for p,c in artifacts]}
write(pilot/"verification.json",verification)
print(json.dumps({"protected":len(preserved),"all_preserved":True,"frozen_sha256":expected,"movie":str(movie),"art_status":"ART_REVISE","gate_rejection":attempt.stderr.strip(),"verification":str(pilot/"verification.json")},indent=2))
