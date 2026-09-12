"""Record this executed FH1 study and its limits; never issue art approval."""
import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

stage = Path(__file__).resolve().parents[1]
repo = Path.cwd().resolve()
assert repo.name == 'Wonder Chess' and stage.is_relative_to(repo)
stamp = datetime.now(timezone.utc).isoformat()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

before = json.loads((stage / 'preservation_before.json').read_text())
protected = [{**entry, 'actual_sha256': digest(repo / entry['path'])} for entry in before['files']]
for entry in protected:
    entry['matches'] = entry['sha256'] == entry['actual_sha256']
assert all(entry['matches'] for entry in protected)
operations = sorted((stage / 'operations').glob('*.py'))
for path in operations:
    ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
captures = sorted((stage / 'captures').glob('*.png'))
artifacts = []
for path in [stage/'ada_features_work.blend', stage/'ada_features_checkpoint_r004.blend',
             stage/'incoming_live_checkpoint.blend', stage/'scene_audit.json',
             stage/'reviews/independent_features_review.md'] + captures + sorted((stage/'references').glob('*.png')):
    artifacts.append({'path': path.relative_to(stage).as_posix(), 'bytes': path.stat().st_size, 'sha256': digest(path)})
audit = json.loads((stage/'scene_audit.json').read_text())
verification = {'updated_utc':stamp,'protected_files':protected,
    'python_ast_parse':{'status':'PASS','count':len(operations),'files':[p.name for p in operations],
                        'boundary':'Syntax only; Blender execution is recorded separately.'},
    'capture_count':len(captures),'artifacts':artifacts,
    'mesh_audit':audit['audit'],
    'blender_execution':'Executed in the visible Blender 5.1.1 session through existing MCP.',
    'native_computer_use':'Window selected, activated, observed; head selected and Edit Mode cage shown with @oai/sky.',
    'tool_recovery':'Final audit first rejected a hashlib import by Blender safe mode before execution; rewritten without that import and executed. Hashing performed here outside Blender; no security setting changed.',
    'art_status':'REVISE','human_forms_approval':False,'human_release_approval':False,
    'not_run':['deformation tests','self-intersection certification','production topology approval','UVs/bakes/production textures','rigging/animation','Unreal import/reimport','packaged-game asset verification']}
(stage/'verification.json').write_text(json.dumps(verification,indent=2)+'\n',encoding='utf-8')

report = '''# Ada FH1 - nose, mouth, ear and head construction

Status: **EXECUTED AND COMBINED; VISUAL FORMS REVISE.** No human approval was issued.

The user requested nose, mouth, ears and facial/head geometry first, then combination and edge repair. All four have executed editable source in the new FH1 candidate. The supplied portrait and turnaround remain authoritative. A generated supplementary construction sheet clarifies hidden anatomy but is not an approved replacement reference or a Blender render.

## Open and inspect

- `ada_features_work.blend`: live working file.
- `ada_features_checkpoint_r004.blend`: saved review checkpoint.
- Scene `FH1_NOSE_STUDY`: initial and revised original nasal cage, including real nostril vaults.
- Scene `FH1_MOUTH_STUDY`: initial and revised lip/perioral cages, including closed contact support.
- Scene `FH1_EAR_STUDY`: original and revised continuous pinna/helix/concha cage.
- Scene `FH1_HEAD_SHAPE_STUDY`: original jaw/face/cranium envelope before features.
- Scene `FH1_COMBINED_HEAD`: current `FH1_Combined_Head_Control_Cage_r004`, with separate diagnostic eyeballs.

The combined skin has **1,621 control vertices and 1,564 faces**: 1,562 quads and two six-sided nostril-vault caps. It has one connected component. Nose (32), mouth (34), two ears (20 each), and two orbital regions (20 each) reuse their shared boundary indices. It is not an object join presented as a weld, and it does not use the rejected MR1 zipper bridge or old head geometry.

## What changed and what remains

| Part | Executed change | Remaining visual limitation |
|---|---|---|
| Nose | Original editable bridge/tip/alar cage; actual recessed nostrils; smaller downward-facing apertures and restrained projection | Pinched nasal root, weak base/columella differentiation, stepped philtrum transition |
| Mouth | Original upper/lower lips and perioral volume; narrow closed contact line; reduced projection and lateral taper | Soft cupid bow and rounded lower-center/under-lip transition |
| Ears | Original continuous shell, rim, concha, antihelix/tragus/lobe controls; thinner revised profile; both ears attached | Broad oval-dish appearance and insufficiently distinct folds/lobe |
| Head/jaw | Original sparse face, jaw, chin and skull; narrower lower jaw; rounded crown with quad cap | Angular rear-skull/neck silhouette; cheek/jaw planes and expression still differ from Ada |
| Joins | Shared-index attachment, corrected medial nose/eye ordering, removed exposed outer-globe crescents and repaired distorted crown cap | Surface pinching at inner brow/root/under-eye remains; visual continuity is not approved |

The two broad assembly corrections did not eliminate the inner-brow/root defect. A subsequent specific interface diagnosis found the nasal boundary lateral to the inner orbital controls; correcting that order removed the conspicuous strip edge but still left pinched forms. Do not continue with general smoothing or another whole-head deformation pass. Retain R004 and use one directly edited nasal-root/inner-brow/subnasal study if further work is authorized or steered.

## Evidence and boundaries

- The actual Blender session created and saved the geometry. Native Computer Use selected/observed the window and exposed the editable cage.
- `captures/combined_initial_*` and `captures/combined_r004_*` use matching cameras for this run's before/after comparison. This is a within-FH1 comparison, not a registered likeness measurement against the illustrations.
- `captures/final_uniform_clay_*`, `final_openings_*`, `final_reversed_key_*` and `final_control_cage_*` show untextured surfaces, genuine openings, opposite lighting and the actual unsmoothed cage.
- `scene_audit.json` records current geometry observations, named scene objects, cameras and render settings. Historical failed objects and review wire overlays are hidden and excluded from the current render allowlist.
- Structural checks find no degenerate faces or unexpected non-manifold edges. The four intended boundary loops are the neck (40), mouth interior (34), and eyelid openings (20 each). These checks do not certify deformation, self-intersection freedom, artistic quality, or runtime suitability.
- `reviews/independent_features_review.md` records an independent inspection of the actual pixels, with per-region REVISE statuses and image hashes.
- `verification.json` records final hashes and protected-file checks. The incoming unsaved MR1 session was saved to `incoming_live_checkpoint.blend` before starting FH1. The seven protected source/reference files match their pre-run hashes.
- Torso, armor, collar, neck, hair studies and gameplay were not remodeled. No UV, production texture, rigging, animation, LOD, Unreal or packaging work was performed.

The next useful modeling intervention is a directly edited inner-brow/nasal-root and nasal-base/philtrum region with clear anatomical planes, judged in the same front/profile/three-quarter cameras. The ear and skull/jaw remain separate revision items. Forms and release approval remain with Pram.
'''
(stage/'REVIEW_FH1.md').write_text(report,encoding='utf-8')

# Review page lays out original PNG files; it does not alter rendered pixels.
html='''<!doctype html><meta charset="utf-8"><title>Ada FH1 review</title>
<style>body{font:16px system-ui;background:#181a1d;color:#ece9e2;margin:32px;max-width:1500px}h1{font-size:30px}p{max-width:1000px;line-height:1.5}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0 0 24px}img{width:100%;display:block}figcaption{padding:10px;background:#282c31}a{color:#dbc08a}.status{color:#ffd38a}@media(max-width:800px){.grid,.pair{grid-template-columns:1fr}}</style>
<h1>Ada - new feature and head studies</h1><p class="status">Executed and combined. Artistic status: REVISE. Human forms approval: pending.</p>
<p>These are actual Blender captures. Nose, lips, ears and the new head are connected in one editable skin mesh. Pinching around the inner brow and nose, the nasal-base transition, ear folds and skull/jaw shape still need work.</p>
<div class="grid">'''
for view,label in [('front','Front'),('profile','Profile'),('three_quarter','Three-quarter')]:
    html+=f'<figure><img src="captures/combined_r004_{view}.png"><figcaption>Current - {label}</figcaption></figure>'
html+='</div><h2>Matching before and after cameras</h2><div class="pair">'
for prefix,label in [('combined_initial','Initial FH1 assembly'),('combined_r004','Current FH1 R004')]:
    html+=f'<figure><img src="captures/{prefix}_three_quarter.png"><figcaption>{label}</figcaption></figure>'
html+='</div><h2>Construction evidence</h2><div class="grid">'
for file,label in [('final_control_cage_three_quarter','Actual control cage'),('final_openings_front','Eyeballs hidden - real openings'),('final_reversed_key_three_quarter','Reversed key lighting')]:
    html+=f'<figure><img src="captures/{file}.png"><figcaption>{label}</figcaption></figure>'
html+='</div><h2>Independent component studies</h2><div class="grid">'
for file,label in [('nose_r002_three_quarter','Nose study'),('mouth_r002_three_quarter','Mouth study'),('ear_r002_three_quarter','Ear study')]:
    html+=f'<figure><img src="captures/{file}.png"><figcaption>{label}</figcaption></figure>'
html+='</div><p><a href="REVIEW_FH1.md">Full review</a> · <a href="ada_features_checkpoint_r004.blend">Editable Blender checkpoint</a> · <a href="verification.json">Verification record</a></p>'
(stage/'REVIEW_FH1.html').write_text(html,encoding='utf-8')

state_path=repo/'reports/implementation_state.json'
state=json.loads(state_path.read_text(encoding='utf-8-sig'));as1=state['as1_asset_studio']
if 'fh1_previous_checkpoint' not in as1:
    as1['fh1_previous_checkpoint']={key:as1.get(key) for key in ['ada_status','review_packet','checkpoint','active_blend','frozen_blend','next_required_action','separate_art_review']}
relative=stage.relative_to(repo).as_posix()
as1.update({'updated_utc':stamp,'ada_status':'features_and_head_executed_combined_forms_revise',
    'review_packet':relative+'/REVIEW_FH1.md','checkpoint':relative+'/verification.json',
    'active_blend':relative+'/ada_features_work.blend','frozen_blend':relative+'/ada_features_checkpoint_r004.blend',
    'user_feedback':'Requested original nose, mouth, ears and facial/head geometry, then combination and edge repair.',
    'separate_art_review':'FH1 independent review: all regions remain REVISE despite visible component and interface improvements. No human forms approval.',
    'next_required_action':'Directly edit one inner-brow/nasal-root and nasal-base/philtrum study; preserve FH1 R004 and review matched views. Ear and skull/jaw structure remain revision items.',
    'ada_features_head':{'stage':'FH1','revision':'r001','retained_geometry_revision':'r004','status':'EXECUTED_COMBINED_REVISE',
        'original_geometry':True,'protected_sources_preserved':True,'current_skin_vertices':1621,'current_skin_faces':1564,
        'human_forms_approval':False,'runtime_integration':'NOT_RUN','verification':relative+'/verification.json',
        'independent_review':relative+'/reviews/independent_features_review.md'}})
assert as1['human_approvals']=={'references':True,'forms':False,'release':False}
state_path.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'protected_hashes':'7/7 PASS','python_files_parsed':len(operations),'captures':len(captures),
                  'work_source_sha256':digest(stage/'ada_features_work.blend'),
                  'frozen_source_sha256':digest(stage/'ada_features_checkpoint_r004.blend'),
                  'state_updated':str(state_path),'art_status':'REVISE'},indent=2))
