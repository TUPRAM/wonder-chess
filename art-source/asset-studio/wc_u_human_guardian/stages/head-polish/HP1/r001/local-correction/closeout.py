from pathlib import Path
import ast,hashlib,json,datetime
REPO=Path('C:/Users/iputu/Documents/Wonder Chess')
STAGE=REPO/'art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
ROOT=STAGE/'local-correction'
def record(p):
    return {'path':p.relative_to(REPO).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
audit=json.loads((ROOT/'scene_audit.json').read_text())
live=json.loads((ROOT/'live_preservation.json').read_text())
assert audit['internal_nonmanifold']==audit['degenerate_faces']==audit['nonadjacent_self_overlap_pairs']==0
assert audit['topology_unchanged'] and not audit['negative_x_changed'] and not audit['neck_changed']
assert live['baseline_r014_geometry_unchanged'] and live['saved_camera_matrices_unchanged']
assert hashlib.sha256((STAGE/'ada_head_polish_checkpoint_r014.blend').read_bytes()).hexdigest()=='95f8c084c97914a9a6ab198764a3ba80f478dac6fbd8e5b3cc8132d37599d851'
scripts=list(ROOT.glob('*.py'))
for p in scripts:ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
verification={'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'EXECUTED_LOCAL_CORRECTION_REVISE','retained_revision':'r016','bounded_attempts':2,'human_forms_approval':False,'recommendation':'Retain improved opening; do not extend or mirror. Focused local sculpt-based rebuild of medial socket/upper-cheek and nasal-base/philtrum transition, transferred to a better editable control surface.','scope':'Anatomical-right connected region plus five shared midline columella/philtrum profile controls. Negative-X cage fixed; adjacent subdivided faces respond to shared controls.','mesh_audit':audit,'live_preservation':live,'sources':[record(STAGE/n) for n in ['ada_head_polish_work.blend','ada_head_polish_checkpoint_r016.blend','ada_head_polish_checkpoint_r014.blend']],'scripts':[record(p) for p in scripts],'captures':[record(p) for p in sorted((ROOT/'captures').glob('*.png'))],'reviews':[record(p) for p in [ROOT/'REVIEW_LOCAL.md',ROOT/'preservation.md',ROOT/'preservation.json',STAGE/'reviews/local_correction_review.md']],'image_comparison':'Same saved camera and lighting. Helper does no registration or aesthetic score.','not_run':['deformation/rigging','production textures/materials','animation','LODs','Unreal','human forms/release approval']}
(ROOT/'verification.json').write_text(json.dumps(verification,indent=2)+'\n',encoding='utf-8')
statepath=REPO/'reports/implementation_state.json';state=json.loads(statepath.read_text(encoding='utf-8'));a=state['as1_asset_studio'];rel=STAGE.relative_to(REPO).as_posix()
a.update(updated_utc=verification['updated_utc'],ada_status='head_local_correction_executed_revise',review_packet=rel+'/local-correction/REVIEW_LOCAL.md',checkpoint=rel+'/local-correction/verification.json',frozen_blend=rel+'/ada_head_polish_checkpoint_r016.blend',user_feedback='Priority eyes/sockets, then nose-to-mouth profile, then jaw/lower cheek. Strict one-region correction, two attempts, no hair-family work.',separate_art_review='r016 retained as best local result; lid coverage improved, major transition/profile defects remain. No extension, mirroring or forms approval.',next_required_action=verification['recommendation'])
a['ada_head_polish'].update(retained_geometry_revision='r016',status='EXECUTED_LOCAL_CORRECTION_REVISE',verification=rel+'/local-correction/verification.json',independent_review=rel+'/reviews/local_correction_review.md',bounded_local_attempts=2,local_changed_cage_vertices=len(audit['changed_indices']),shared_midline_controls=audit['shared_midline_changed'])
statepath.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
historical=STAGE/'REVIEW_HP1.md';text=historical.read_text(encoding='utf-8');marker='> Current continuation: '
if marker not in text:
    historical.write_text('> Current continuation: [r016 local correction review](local-correction/REVIEW_LOCAL.md). The working file now contains r016; this r014 report and its hashes remain historical evidence for the preserved r014 checkpoint.\n\n'+text,encoding='utf-8')
print(json.dumps({'status':verification['status'],'sources':verification['sources'],'scripts_parsed':len(scripts),'capture_count':len(verification['captures']),'review':str(ROOT/'REVIEW_LOCAL.md')},indent=2))
