"""Fresh process verification of one promoted source, export hashes and skin/motion."""
import argparse,json,runpy,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import sha,invariants,action_curve_digest
parser=argparse.ArgumentParser();parser.add_argument('--unit',required=True);parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);uid=args.unit;out=args.output.resolve()
source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';export=ROOT/f'exports/heroes/{uid}'
manifest=json.loads((export/'export_manifest.json').read_text());result=json.loads((out/'export-result.json').read_text())
refined=json.loads((out/'refinement.json').read_text())
assert sha(source)==manifest['source_sha256']==result['source_sha256']
assert sha(export/'export_manifest.json')==result['manifest_sha256']
for name,expected in manifest['files'].items():assert sha(export/name)==expected,name
bpy.ops.wm.open_mainfile(filepath=str(source))
expected=refined.get('verified_candidate_invariants',refined['preserved_invariants'])
assert invariants(bpy.data.objects['Armature'])==expected
for clip,digest in refined.get('unchanged_action_sha256',{}).items():
    assert action_curve_digest(bpy.data.actions[f'AN_{uid}_{clip}'])==digest
saved=sys.argv
try:
    for collection in ('EXPORT','LOD_SOURCE'):
        sys.argv=['inspect_scene.py','--','--collection',collection,'--require-skin','--output',str(out/(collection+'-published-inspection.json'))]
        runpy.run_path(str(ROOT/'tools/blender/inspect_scene.py'),run_name='__main__')
    sys.argv=['audit_motion.py','--','--unit',uid,'--output',str(out/'published-motion-invariants.json')]
    runpy.run_path(str(ROOT/'tools/blender/audit_motion.py'),run_name='__main__')
finally:sys.argv=saved
for name in ('EXPORT-published-inspection.json','LOD_SOURCE-published-inspection.json','published-motion-invariants.json'):
    assert not json.loads((out/name).read_text()).get('errors'),name
record={'status':'PUBLISHED_SOURCE_EXPORT_AND_MOTION_CHECKS_PASS','unit_id':uid,
    'blender_version':bpy.app.version_string,'source_revision':manifest['source_revision'],
    'geometry_revision':manifest['geometry_source_revision'],'animation_revision':manifest['animation_revision'],
    'source_sha256':sha(source),'manifest_sha256':sha(export/'export_manifest.json'),
    'export_files_verified':len(manifest['files']),'triangles':manifest['triangles'],'lods':manifest['lods'],
    'modified_clips':[c['clip'] for c in refined.get('changed_clips',[])],
    'Unreal_reimport_verified':False,'final_art_accepted':False}
(out/'published-verification.json').write_text(json.dumps(record,indent=2)+'\n')
print('WC_REFINED_HERO_PUBLISHED_CHECKS_PASS '+json.dumps(record),flush=True)
