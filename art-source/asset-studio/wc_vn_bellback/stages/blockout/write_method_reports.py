"""Record observed failed forms and verify local evidence; never prepare/approve gates."""
import hashlib, json
from pathlib import Path
from datetime import datetime, timezone

ASSET=Path(__file__).resolve().parents[2]
ROOT=ASSET.parents[2]
AUTHOR='Codex /root/balance_experiment'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,data):p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def path(p):return p.relative_to(ASSET).as_posix()
def artifact(p,category):return dict(path=path(p),category=category)
def check(id,status,evidence,notes):return dict(id=id,status=status,evidence=[path(p) for p in evidence],notes=notes)

reviewed=[
 'renders/front_clay.png','renders/back_clay.png','renders/right_clay.png','renders/left_clay.png',
 'renders/threequarter_clay.png','renders/threequarter_ids.png',
 'review/face_closeup_clay.png','review/paw_contact_clay.png','review/bell_cavity_and_carrier.png',
 'review/native96_preview.png','review_supplement/open_cavity_underside.png',
 'review_supplement/clapper_and_open_carrier_saddles_hidden.png',
 'review_crowded_aligned/crowded12_board_lab_projection_1920x1080.png',
 'review_crowded_aligned/crowded12_board_lab_elevation_detail.png']
r3=ASSET/'stages/blockout/r003'
defects=[
 dict(id='face_identity',severity='major',status='open',category='shape',observation='Flattened oval head, projecting button eyes and thin curved mouth remain toy-like rather than aged animal anatomy.',evidence=['renders/front_clay.png','review/face_closeup_clay.png'],next_operation='Focused controlled sculpt of inset orbit/lids, muzzle projection, brow and jaw planes.'),
 dict(id='bark_root_anatomy',severity='major',status='open',category='shape',observation='Displaced grooves form serrated trenches; inflated shoulder masses and blocky limb transitions remain.',evidence=['renders/right_clay.png','renders/left_clay.png','review/paw_contact_clay.png'],next_operation='Sculpt broad continuous root planes and load-bearing taper before any bark detail; abandon point-distance cuts.'),
 dict(id='bell_body_relationship',severity='major',status='open',category='shape',observation='Clean oversized-looking bell and boxy support dominate; dimensional compliance has not produced the integrated organic identity.',evidence=['renders/right_clay.png','review/bell_cavity_and_carrier.png'],next_operation='Retain accepted bell dimensions and clearance; reshape support integration and adjacent body forms.'),
 dict(id='board_identity',severity='major',status='open',category='readability',observation='Bell is visible in static board proxy; organic identity, face and facing distinctions remain weak.',evidence=['review_crowded_aligned/crowded12_board_lab_projection_1920x1080.png'],next_operation='After fixing primary forms, review native board scale and then actual gameplay; static Blender evidence is insufficient for acceptance.')]
audit=read(r3/'model_audit.json');source=r3/audit['source']
assert sha(source)==audit['source_sha256']
for item in reviewed:assert (r3/item).is_file(),item
write(r3/'visual_review.json',dict(stage='blockout',verdict='ART_REVISE',reviewed_utc=datetime.now(timezone.utc).isoformat(),
 source_sha256=sha(source),author=AUTHOR,review_kind='Actual pixel self-critique; independent parent corroborated r002 and bounded r003 method change.',
 viewed=reviewed,defects=defects,positive_observations=['Four toes per paw and planted stance are visible.','Right-side branch and dorsal bell silhouette exist.','Supplementary views reveal actual open carrier and clapper.'],
 source_mesh_count=len(audit['parts']),source_triangle_count=sum(p['triangles'] for p in audit['parts']),
 remaining_gate='No blockout approval; no human forms submission. All downstream gates pending.',
 next_method='Stop procedural iteration. Focused direct creature sculpt intervention; see reports/FORMS_METHOD_REVIEW.md.',
 limitations=['Aesthetic reference is not registered to model cameras.','Static Blender lab-camera proxy, not Unreal gameplay capture.','Source-ID materials are not an accepted material or texture pass.']))

for revision in ['r001','r003']:
    base=ASSET/'stages/blockout'/revision; info=read(base/'model_audit.json')
    refs=[base/'renders/front_clay.png',base/'renders/right_clay.png',base/'renders/threequarter_clay.png']
    main=base/info['source']; assert sha(main)==info['source_sha256']
    arts=[artifact(main,'source'),artifact(base/'model_audit.json','report'),artifact(base/'visual_review.json','report')]+[artifact(p,'image') for p in refs]
    if revision=='r003':arts += [artifact(r3/p,'image') for p in reviewed if r3/p not in refs]+[artifact(r3/'construction_review.json','report'),artifact(r3/'review_crowded_aligned.json','report')]
    report=dict(schema_version='1.0.0',asset_id='wc_vn_bellback',stage='blockout',author=AUTHOR,
      method=info['method'],checks=[
      check('silhouette_and_proportions','fail',refs,'Reference dimensions and planted stance exist, but face and integrated organic proportions do not meet the approved aesthetic target.'),
      check('camera_alignment','fail',[base/'model_audit.json'],'Four fixed orthographic directions and three-quarter captures executed. Raster aesthetic reference is not registered; no camera-alignment or likeness-overlay pass is claimed.'),
      check('major_part_clearance','not_run',[base/'model_audit.json'],'Static construction only. No animation or complete motion-clearance check. R003 supplementary views reveal existing carrier and clapper without certifying motion.'),
      check('method_is_capable','fail',refs,'Actual required visual result is poor. Stop this construction method; no advancement based on successful script execution.')],
      artifacts=arts,defects=defects if revision=='r003' else [dict(severity='major',status='open',observation='Toy anatomy, applied eyes/brows and bark strips fail primary-form likeness.')],
      executed_commands=[dict(operation='Blender factory-startup background build',script=path(base/'operations/build_bellback.py'),log=path(base/'operations/blender-build.log'),exit_code=0)],
      notes=['Diagnostic failed report only; not prepared or approved.','Human forms gate and downstream production stages were not run.','See reports/FORMS_METHOD_REVIEW.md for observed discrepancies and retry stop.'])
    write(ASSET/f'reports/blockout_{revision}.json',report)

pending=read(ASSET/'reports/forms_r001.json')
pending.update(author=AUTHOR,method='Formal forms stage did not start because blockout candidates r001-r003 fail the art review.',
 artifacts=[artifact(r3/'visual_review.json','report'),artifact(source,'source'),artifact(r3/'renders/threequarter_clay.png','image')],
 defects=[dict(severity='major',status='open',observation='Upstream modeled primary forms and likeness require revision.')],
 notes=['Not a human forms submission. No preparation or approval requested for the failed sources.','All checks remain not_run for the formal forms gate. Actual preliminary visual failures are recorded in blockout_r003.json.'])
for c in pending['checks']:c.update(status='not_run',evidence=[path(r3/'visual_review.json')],notes='Blocked by unresolved major upstream form defects; no human forms gate review occurred.')
write(ASSET/'reports/forms_r001.json',pending)

operations=[]
for revision in ['r001','r002','r003']:
    base=ASSET/'stages/blockout'/revision;info=read(base/'model_audit.json')
    assert sha(base/info['source'])==info['source_sha256']
    for script in sorted((base/'operations').glob('*.py')):
        operations.append(dict(id=f'bellback-{revision}-{script.stem}',owner=AUTHOR,asset_id='wc_vn_bellback',
          script=path(script),script_sha256=sha(script),permitted_output_root=path(base),
          intended_change='Construct isolated candidate from accepted reference dimensions' if script.name.startswith('build') else 'Read-only review captures; source must remain unchanged',
          expected_source_sha256=None if script.name.startswith('build') else info['source_sha256'],
          result_source_sha256=info['source_sha256'],source_size_bytes=(base/info['source']).stat().st_size,
          allowed_part_ids=sorted({p['wc_part_id'] for p in info['parts']}),
          status='failed: unused clay material absent after reopening; source unchanged' if revision=='r002' and script.stem=='review_construction' else 'completed',
          exit_code=1 if revision=='r002' and script.stem=='review_construction' else 0))

summary=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),verdict='ART_REVISE',operations=operations,
 artifact_hashes=[dict(path=path(p),sha256=sha(p),bytes=p.stat().st_size) for p in sorted((ASSET/'stages/blockout').rglob('*')) if p.is_file() and p.suffix in {'.blend','.png','.py','.log'}],
 notes=['Hash inventory records actual saved files. Successful build/render is not a form-quality pass.',
 'R001 floor-bevel setup failure preserved separately before successful source build.',
 'Initial r003 board captures had hidden floor tiles; supplementary placement was half a cell off X; final aligned captures supersede only those crowded views.',
 'No gate prepare or approval mutation is performed by this script.'])
write(ASSET/'reports/forms_evidence_inventory.json',summary)

# Schema/evidence validation verifies records only; deliberately does not call gate prepare.
import jsonschema
schema=read(ROOT/'production/asset-studio/schemas/review_report.schema.json')
for report_name in ['blockout_r001.json','blockout_r003.json','forms_r001.json']:
    report=read(ASSET/'reports'/report_name);jsonschema.validate(report,schema)
    listed={a['path'] for a in report['artifacts']}
    for a in report['artifacts']:assert (ASSET/a['path']).is_file()
    for c in report['checks']:assert set(c['evidence']).issubset(listed)
print(json.dumps(dict(report_schema_validation='pass',artifact_paths='pass',source_hashes='pass',art_quality='ART_REVISE',r003_meshes=len(audit['parts']),r003_triangles=sum(p['triangles'] for p in audit['parts']))))
