from pathlib import Path
import json,hashlib,ast
from PIL import Image
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
audit=json.loads((R/'records/retained_all97_audit.json').read_text());reopen=json.loads((R/'records/reopen_preservation_sections.json').read_text());caps=json.loads((R/'records/capture_manifest.json').read_text());movie=json.loads((R/'motion/verification.json').read_text());append=json.loads((R/'records/append_helper_test.json').read_text())
assert audit['frame_count']==97 and len(audit['frames'])==97 and sum(v['pairs'] for row in audit['frames'].values() for v in row.values())==0
assert all(v['pairs']==0 for v in audit['raw_self'].values());assert sha(audit['source'])==audit['sha256']==audit['sha256_after']
for item in reopen['native_reopen']:
 assert sha(item['file'])==item['sha256'];assert all(item['unchanged_protected_geometry_weights_world'].values()) and all(item['unchanged_cameras'].values()) and all(item['unchanged_rig_rest_and_sampled_pose'].values())
assert sha(reopen['baseline'])==reopen['baseline_sha256'];assert sha(movie['movie'])==movie['sha256'] and movie['frames']==97 and movie['native_movie_reopen'];assert append['helper_executed'] and append['source_preserved']
for c in caps['captures']:
 assert sha(c['path'])==c['sha256'];Image.open(c['path']).verify()
for p in (R/'operations').glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
ast.parse((R/'append_backplate.py').read_text())
files=sorted(p for p in R.rglob('*') if p.is_file() and p!=R/'verification.json' and p.suffix in ('.blend','.json','.py','.png','.mp4','.md'))
record={'status':'LOCAL_REVIEW_CANDIDATE','human_approval':False,'game_and_unreal':'NOT_RUN','source_preserved':True,'owned':['BW6_BackPlate_Rebuilt'],'rigid_owner':'spine01','all97_authoring_transverse_checks':'PASS_WITH_RECORDED_QUERY_LIMITS','raw_self':'PASS_WITH_RECORDED_QUERY_LIMITS','work_and_frozen_reopened':True,'append_helper_executed':True,'movie97_rendered_encoded_reopened':True,'full_movie_visual_approval':False,'visually_inspected':['baseline_pair_back.png','initial_pair_back.png','initial_context_profile_1.png','correction1_pair_back.png','correction2_pair_back.png','retained_actual_cage_back.png','retained_uniform_clay_reversed_key.png','actual_posterior_section_z1.445_f49.png','BW6_BACKPLATE_BEFORE_AFTER.png','motion/decoded/frame_0049.png','motion/decoded/frame_0073.png'],'frozen_sha256':audit['sha256'],'artifacts':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
(R/'verification.json').write_text(json.dumps(record,indent=2));print('BW6_BACKPLATE_ARTIFACTS_VERIFIED',len(files))
