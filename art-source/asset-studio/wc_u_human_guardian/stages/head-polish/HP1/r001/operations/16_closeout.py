"""Record executed HP1 evidence without issuing an art approval."""
import ast,hashlib,json,html
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPO=next(p for p in ROOT.parents if (p/'reports/implementation_state.json').exists())
REL=ROOT.relative_to(REPO).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
audit=json.loads((ROOT/'scene_audit.json').read_text())
assert audit['object']=='HP1_HEAD_POLISH_Head_r014'
assert audit['components']==[1670]
assert not audit['nonmanifold_internal_edges'] and not audit['degenerate_faces']
assert audit['evaluated']['nonadjacent_self_overlap_pairs']==0
scripts=[]
for path in sorted((ROOT/'operations').glob('*.py')):
    ast.parse(path.read_text(encoding='utf-8'));scripts.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)})
sourcefiles=['ada_head_polish_work.blend','ada_head_polish_checkpoint_r014.blend']
verification={'updated_utc':datetime.now(timezone.utc).isoformat(),'status':'EXECUTED_HEAD_POLISH_REVISE','retained_revision':'r014','scope':'Head skin and diagnostic globes only; no hair, eyebrow or eyelash edits. Original torso/armor/neck assets and reference approval preserved. Candidate head bottom boundary repaired.','geometry_checks':audit,'sources':[{'path':f,'bytes':(ROOT/f).stat().st_size,'sha256':sha(ROOT/f)} for f in sourcefiles],'references':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in sorted((ROOT/'references').glob('*.png'))],'captures':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in sorted((ROOT/'captures').glob('*.png'))],'scripts_parsed':scripts,'preservation_report':'reviews/preservation.json','independent_art_review':'reviews/independent_head_polish.md','human_forms_approval':False,'near_perfect_reference_match':False,'next_action':'Focused human control-cage or sculpt correction of one connected medial-eye/nasal-sidewall/upper-muzzle region, preserving the fixed cameras and retained r014. Resolve lid coverage, short columella/philtrum and independent cheek plane before extending. User feedback on regional priority remains pending.'}
(ROOT/'verification.json').write_text(json.dumps(verification,indent=2)+'\n',encoding='utf-8')
md=f'''# Ada HP1 head polish — r014

**Executed, reviewed, retained at REVISE. The requested near-perfect 2D likeness has not been achieved. No human forms approval was recorded.**

This run continued from the original FH1 r004 head in a separate HP1 work file, using the visible Blender 5.1.1 session and its existing MCP. Native Computer Use was used to reopen/focus and inspect Blender. No current legacy Ada mesh was used as a new foundation. Hair, eyebrows and eyelashes were excluded. The source portrait stayed authoritative; the supplementary construction sheet supported other views.

## Retained files

- [Editable working Blender file](ada_head_polish_work.blend)
- [Frozen r014 checkpoint](ada_head_polish_checkpoint_r014.blend)
- [Executed scene audit](scene_audit.json)
- [File hashes and verification](verification.json)
- [Independent visual review](reviews/independent_head_polish.md)
- [Original-source preservation review](reviews/preservation.md)

Active Blender scene: `HP1_HEAD_POLISH`. Active skin: `HP1_HEAD_POLISH_Head_r014`. `HP1_BASELINE` retains the incoming FH1 head for comparison. Failed and superseded HP1 objects remain hidden. `HP1_CAGE_REVIEW` is a separate evidence scene containing an unsubdivided copy and actual cage edges.

## What changed

- Rebuilt the orbital boundary flow, then changed eyelid topology: actual openings, inset wall, margin, lid volume, crease and independent socket transition.
- Added an independent nasal bulb section. Reduced the overprojected first tip attempt and refined the columella/upper-muzzle relationship.
- Refined the upper-lip volume and shifted the mouth slightly upward/backward for the primary portrait comparison.
- Reduced excessive lateral head breadth and cheek inflation. Lowered the ears with a continuous junction adjustment.
- Rejected the r012 ear-base jaw shelf. Retained a restrained lower jaw turn on the cleaner r011 surface.
- Repaired crossing neck-edge arcs, including an inherited baseline issue.
- Added a weak-perspective primary-portrait camera using approximate manually read landmarks. The neutral front/profile/three-quarter cameras were retained.

## Actual image evidence

The before/after renders below use the same camera and lighting. The sheet helper labels its composition “no registration”; that means the helper performed no image registration. The two source renders themselves use the same saved Blender camera. The illustrated-reference fit is approximate and is not a silhouette metric or an artistic score.

![Same-camera baseline and r014 comparison]({(ROOT/'captures/primary_before_after.png').as_posix()})

![Retained r014 front]({(ROOT/'captures/r014_front.png').as_posix()})

![Actual editable cage]({(ROOT/'captures/r014_cage_three_quarter.png').as_posix()})

Additional captures include profile, opposite three-quarter, rear, reversed key lighting and eyes hidden to expose the lid openings. Files are in `captures/`. No new AI artwork was generated in HP1.

## Remaining major defects

1. Upper-lid coverage and corner/plane flow still produce too much exposed globe and a startled expression.
2. The nasal underside-to-philtrum profile still forms a swept recess instead of clearly separated but connected columella, short philtrum and upper-muzzle volume.
3. The jaw/lower-cheek contour remains too generic and weak compared with Ada’s firm diagonal turn.
4. Reversed lighting still exposes uneven medial-socket and cheek transitions.

The independent reviewer retained r014 as the best current candidate and identified these as major defects. Successful scripts, a cleaner surface, or valid topology do not clear them. The current method has not resolved the required likeness, so this is an affected-stage art stop with a focused intervention brief, not a completed head or a downstream production gate.

## Focused intervention brief

Preserve r014, the approved reference and the saved cameras. Work on one connected anatomical-right region spanning the medial eyelid, nasal sidewall, columella/philtrum and upper cheek. Use directly edited control-cage planes or a sculpt correction that can be transferred back to this editable surface. Keep the real openings and nasal vaults. Establish the lid/canthus and nasal-base-to-lip profile explicitly; give the cheek its own plane. Show the same front/profile/three-quarter, primary-pose and reversed-key views before mirroring or extending. Reject the r012 ear-base shelf. No hair-family work or production stages.

The optional feedback prompt asks which remaining mismatch is most important: nose/mouth profile, cheek/jaw/chin outline, or eyes/sockets. It does not request or record forms approval. No answer had arrived when this packet was written.

The applicable [wca-organic instruction]({(REPO/'.agents/skills/wca-organic/SKILL.md').as_posix()}) states: “Two no-improvement attempts require a method review or focused human intervention.” It also states: “A missing editor or poor required visual result blocks the affected stage.” The visual result, rather than editor access, is the remaining limitation.

## Verification boundaries

The retained skin has **1,670 vertices and 1,612 faces**: 1,608 quads, two five-sided nasal section joins and two six-sided nostril-vault caps. It is one connected component. The four intended open boundaries are the two eyes (20 edges each), mouth (34), and head bottom/neck interface (40). There are no unintended internal non-manifold edges or degenerate faces in this check.

The level-2 evaluated surface has 26,042 vertices, 25,816 faces and 51,632 triangulated equivalents. Blender’s BVH overlap check found **zero non-adjacent self-overlap pairs** after excluding face pairs sharing vertices. This is a single neutral-pose geometric check, not a deformation or production certification. Source/render allowlists and camera matrices are in `scene_audit.json`.

All nine protected FH1/MR1/r003/reference files match their recorded hashes. The active HP1 scene contains only the retained skin and two diagnostic eye meshes as renderable geometry. No hair-family object is linked to that scene. Source preservation and operation scope were checked independently.

Not run: topology for deformation, final UVs/bakes/materials, rigging, animation, LODs, Unreal import, reimport, packaged-game review, or human forms/release approval. Full gameplay test suites were not rerun for these art edits. Operation scripts were parsed and the relevant Blender operations, renders and geometry observations were executed.
'''
(ROOT/'REVIEW_HP1.md').write_text(md,encoding='utf-8')
page='''<!doctype html><html><meta charset="utf-8"><title>Ada HP1 — shape review</title><style>body{margin:0;background:#202225;color:#e7e8e9;font:17px/1.6 system-ui}main{max-width:1250px;margin:auto;padding:32px}h1{font-size:32px}b{color:#f5d294}img{max-width:100%;display:block;margin:20px auto}a{color:#9cd7ef}.row{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.row img{width:100%}figure{margin:0}figcaption{font-size:14px;color:#bfc5c9}li{margin:9px 0}</style><main><h1>Ada · Head shape review</h1><p><b>r014 retained · REVISE · No human forms approval</b></p><p>The head is improved, but the requested near-perfect likeness has not been achieved. Hair, eyebrows and eyelashes were untouched.</p><img src="captures/primary_before_after.png" alt="Same-camera incoming head and r014"><div class="row"><figure><img src="captures/r014_front.png"><figcaption>Uniform clay · front</figcaption></figure><figure><img src="captures/r014_profile.png"><figcaption>Uniform clay · profile</figcaption></figure><figure><img src="captures/r014_reverse_key.png"><figcaption>Reversed key lighting</figcaption></figure></div><h2>Remaining shape work</h2><ul><li>Lid coverage, corners and the exposed-globe expression.</li><li>Nasal underside, columella and philtrum profile.</li><li>Firm diagonal jaw and independent lower-cheek plane.</li><li>Uneven socket/cheek transitions visible under opposite lighting.</li></ul><div class="row"><figure><img src="references/ada_portrait.png"><figcaption>Primary identity reference · native 210×197</figcaption></figure><figure><img src="captures/r014_cage_three_quarter.png"><figcaption>Actual editable cage</figcaption></figure><figure><img src="captures/r014_openings.png"><figcaption>Globes hidden · actual lid openings</figcaption></figure></div><p>Focused mesh check: one connected skin, no unintended internal non-manifold edges, no degenerate faces, and no detected non-adjacent self-overlaps in the evaluated neutral pose. These results do not establish artistic approval.</p><p><a href="ada_head_polish_checkpoint_r014.blend">Frozen Blender checkpoint</a> · <a href="REVIEW_HP1.md">Full review and intervention brief</a> · <a href="verification.json">Verification and hashes</a></p></main></html>'''
(ROOT/'REVIEW_HP1.html').write_text(page,encoding='utf-8')
statepath=REPO/'reports/implementation_state.json';state=json.loads(statepath.read_text(encoding='utf-8'));a=state['as1_asset_studio']
if 'hp1_previous_checkpoint' not in a:a['hp1_previous_checkpoint']={k:a[k] for k in ['ada_status','review_packet','checkpoint','active_blend','frozen_blend','next_required_action','separate_art_review']}
a.update(updated_utc=verification['updated_utc'],ada_status='head_polish_executed_likeness_revise',review_packet=REL+'/REVIEW_HP1.md',checkpoint=REL+'/verification.json',active_blend=REL+'/ada_head_polish_work.blend',frozen_blend=REL+'/ada_head_polish_checkpoint_r014.blend',user_feedback='Polish head toward near-perfect 2D reference shape; exclude hair, eyebrows and eyelashes. Optional regional-priority feedback remains pending.',separate_art_review='Independent r014 review: meaningful improvement and best current checkpoint; four major shape defects remain. No human forms approval.',next_required_action=verification['next_action'])
a['ada_head_polish']={'stage':'HP1','revision':'r001','retained_geometry_revision':'r014','status':verification['status'],'protected_sources_preserved':True,'hair_eyebrows_eyelashes_touched':False,'current_skin_vertices':1670,'current_skin_faces':1612,'neutral_pose_nonadjacent_self_overlap_pairs':0,'human_forms_approval':False,'near_perfect_reference_match':False,'runtime_integration':'NOT_RUN','verification':REL+'/verification.json','independent_review':REL+'/reviews/independent_head_polish.md'}
statepath.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sources':verification['sources'],'captures':len(verification['captures']),'scripts_parsed':len(scripts),'status':verification['status'],'report':str(ROOT/'REVIEW_HP1.md')},indent=2))
