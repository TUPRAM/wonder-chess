from pathlib import Path
import ast,copy,datetime,hashlib,json,re,subprocess
from PIL import Image
repo=Path(__file__).resolve().parents[8]
stage=Path(__file__).resolve().parent.parent
assert repo.name=='Wonder Chess' and stage.name=='r001'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
protected=json.loads((stage/'preservation_before.json').read_text(encoding='utf-8'))['files']
checks=[]
for item in protected:
    path=repo/item['path'];actual=sha(path)
    checks.append(dict(item,actual_sha256=actual,unchanged=actual==item['sha256']))
assert all(x['unchanged'] for x in checks),'Protected file changed'
baseline_hash=sha(stage/'baseline_source.blend')
assert baseline_hash==checks[0]['sha256'],'Staged baseline mismatch'
scripts=sorted((stage/'operations').glob('*.py'))
for path in scripts:ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
images=[]
for path in sorted((stage/'captures').glob('*.png')):
    with Image.open(path) as im:
        dimensions=list(im.size);im.verify()
    images.append({'path':path.relative_to(stage).as_posix(),'pixels':dimensions,'sha256':sha(path)})
status_command=['python',str(repo/'production/asset-studio/tools/asset_studio/assetctl.py'),'status','--workspace',str(repo/'art-source/asset-studio/wc_u_human_guardian')]
result=subprocess.run(status_command,cwd=repo,check=True,text=True,capture_output=True)
gates=json.loads(result.stdout)
assert next(x for x in gates if x['stage']=='references')['status']=='accepted_current'
assert all(x['status']=='pending' for x in gates if x['stage'] not in ['brief','references'])
(stage/'reference_gate_status.json').write_text(json.dumps(gates,indent=2)+'\n',encoding='utf-8')
for name in ['REVIEW_MR1.md','FOCUSED_INTERVENTION.md']:
    p=stage/name;text=p.read_text(encoding='utf-8')
    text=re.sub(r'\]\((C:/[^)]+)\)',r'](<\1>)',text)
    p.write_text(text,encoding='utf-8')
current_artifacts=['baseline_source.blend','ada_method_proof_work.blend','face_proof_r002.blend','hair_mass_proof_r002.blend','contextual_head_candidate_final.blend','scene_audit_and_capture_recipe_final.json','baseline_inventory.json','REVIEW_MR1.md','FOCUSED_INTERVENTION.md']
manifest=[]
for rel in current_artifacts:
    p=stage/rel;manifest.append({'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)})
for p in sorted((stage/'reviews').glob('*.md'))+scripts:
    manifest.append({'path':p.relative_to(stage).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
history=[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'current_delivery':p.name in current_artifacts} for p in sorted(stage.glob('*.blend'))]
verification={'verified_utc':now,'protected_files':checks,'protected_files_passed':len(checks),'protected_files_failed':0,'baseline_source_sha256':baseline_hash,'operation_scripts_parsed':len(scripts),'operation_syntax_failures':0,'png_files_decoded':len(images),'png_decode_failures':0,'reference_gate':'accepted_current','human_forms_approval':False,'human_release_approval':False,'source_metadata':'scene_audit_and_capture_recipe_final.json','local_geometry_boundary':'Counts and sampled clearance only; no artistic or production acceptance inferred','full_repository_tests':'NOT_RUN_NOT_RELEVANT_TO_GEOMETRY_EDITS','file_load_boundary':'Sources saved in actual GUI Blender through MCP; frozen snapshots not separately cold-reopened','ui_boundary':'Native Blender inspection and edit-mode control executed earlier; final snapshot did not show Blender, so native input stopped'}
(stage/'verification.json').write_text(json.dumps(verification,indent=2)+'\n',encoding='utf-8')
report={'stage':'MR1','revision':'r001','completed_utc':now,'status':'EXECUTED_LOCAL_METHODS_ACCEPTED_CONTEXT_REVISE','blender_executed':True,'blender_version':'5.1.1','baseline_status':'r003_REVISE_preserved','baseline_source_sha256':baseline_hash,'face_method':{'status':'METHOD_PROOF_ACCEPTED','scope':'isolated eye/socket/cheek cage only','source':'face_proof_r002.blend','vertices':100,'quads':80,'corrective_passes':2,'review':'reviews/face_final_review.md'},'hair_method':{'status':'METHOD_PROOF_ACCEPTED','scope':'one broad leading clump and its local foundation contact','source':'hair_mass_proof_r002.blend','vertices':90,'quads':88,'corrective_passes':1,'review':'reviews/hair_r002_review.md'},'contextual_head':{'status':'REVISE','source':'contextual_head_candidate_final.blend','review':'reviews/context_final_review.md','primary_hair_masses':4,'joined_head_vertices':19016,'joined_head_faces':19050,'bridge_triangles':460,'source_regional_boundary_vertices':68,'source_retained_head_boundary_vertices':392,'critical_visual_defects':['serrated forehead/nasal/cheek transitions despite connected topology','unsupported counter-sweep underside gap','abrupt plate-like rear gathering overlaps','wide fixed expression; likeness unestablished'],'retained_braid':'unchanged; wider captures show lower taper and finite tie/tail','attempts':'initial peripheral assembly followed by connected bridge; both contextual interfaces visibly fail','stop_reason':'Independent review recommends one short deliberate transition band, not another broad bridge or smoothing pass'},'human_approvals':{'references':'accepted_current_prior_user_approval','forms':False,'release':False},'next_action':'Prove one anatomical-right nasal-to-upper-cheek transition band with compatible sampling and surface tangents; then verify counter-sweep and rear-gathering contacts individually','not_run':['production topology approval','production UV/bake/textures/materials','rigging','skinning','animation','LODs','FBX','Unreal','packaged gameplay','human forms approval','human release approval'],'preservation':'verification.json','capture_recipes':'scene_audit_and_capture_recipe_final.json','artifacts':manifest,'captures':images,'blend_snapshot_inventory':history,'staging_record_boundary':'staging_record.json describes only initial copies, before Blender execution'}
(stage/'session_report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
state_path=repo/'reports/implementation_state.json';raw=state_path.read_text(encoding='utf-8');state=json.loads(raw);before=copy.deepcopy(state)
asset=state['as1_asset_studio'];prefix=stage.relative_to(repo).as_posix()
(stage/'as1_state_before_MR1.json').write_text(json.dumps(asset,indent=2)+'\n',encoding='utf-8')
asset['r003_baseline']={k:asset[k] for k in ['ada_status','review_packet','checkpoint','active_blend','frozen_blend','separate_art_review']}
asset['updated_utc']=now;asset['ada_status']='local_methods_accepted_contextual_head_revise'
asset['review_packet']=prefix+'/REVIEW_MR1.md';asset['checkpoint']=prefix+'/session_report.json'
asset['active_blend']=prefix+'/ada_method_proof_work.blend';asset['frozen_blend']=prefix+'/contextual_head_candidate_final.blend'
asset['next_required_action']=report['next_action']
asset['separate_art_review']='Local eye and single hair methods accepted by independent agent review; connected head, expanded hairstyle, likeness and human forms approval remain REVISE/unapproved'
asset['ada_method_recovery']={'stage':'MR1','revision':'r001','workspace':prefix,'status':report['status'],'baseline_source_sha256':baseline_hash,'original_files_preserved':True,'face_method_status':'METHOD_PROOF_ACCEPTED','hair_method_status':'METHOD_PROOF_ACCEPTED','contextual_head_status':'REVISE','human_forms_approval':False,'runtime_integration_status':'NOT_RUN','verification':prefix+'/verification.json','review':prefix+'/reviews/context_final_review.md'}
state_path.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
after=json.loads(state_path.read_text(encoding='utf-8'))
before.pop('as1_asset_studio');after.pop('as1_asset_studio');assert before==after,'Unrelated implementation state changed'
print(json.dumps({'protected_files_passed':len(checks),'operation_scripts_parsed':len(scripts),'png_files_decoded':len(images),'reference_gate':'accepted_current','face_method':'METHOD_PROOF_ACCEPTED','hair_method':'METHOD_PROOF_ACCEPTED','contextual_head':'REVISE','unrelated_state_preserved':True,'report':str(stage/'REVIEW_MR1.md')},indent=2))
