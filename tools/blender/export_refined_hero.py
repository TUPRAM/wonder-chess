"""Promote one inspected geometry refinement through the measured export profile."""
import argparse, json, shutil, sys
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import export_revision, sha, invariants

parser=argparse.ArgumentParser()
parser.add_argument('--unit',required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--refinement-script',type=Path,required=True)
parser.add_argument('--resume-staged',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);out=args.output.resolve()
refined=json.loads((out/'refinement.json').read_text());candidate=Path(refined['candidate'])
assert sha(candidate)==refined['candidate_sha256']
assert len(json.loads((out/'motion-sequences.json').read_text())['clips'])==7
assert (out/'normal-speed-evidence.json').is_file()
if not args.resume_staged:
    bpy.ops.wm.open_mainfile(filepath=str(candidate))
    export_revision(out,args.unit,args.refinement_script.resolve())
else:
    source=ROOT/f'art-source/heroes/{args.unit}/{args.unit}.blend'
    revision=source.with_name(args.unit+'_revision7.blend')
    export=ROOT/f'exports/heroes/{args.unit}';stage=out/'normalized-export'
    before=json.loads((out/'before-export-manifest.json').read_text())
    manifest=json.loads((stage/'export_manifest.json').read_text())
    assert sha(source)==before['source_sha256']
    assert sha(revision)==manifest['source_sha256']
    assert len(list(stage.glob('*.fbx')))==10
    for name,expected in manifest['files'].items():
        assert sha(stage/name if (stage/name).is_file() else export/name)==expected,name
    bpy.ops.wm.open_mainfile(filepath=str(revision))
    assert invariants(bpy.data.objects['Armature'])==refined.get('verified_candidate_invariants',refined['preserved_invariants'])
    # Only declared ordinary files are promotion inputs. Blender .fbm folders
    # remain retained staging evidence; the texture exports already exist.
    for name in manifest['files']:
        if (stage/name).is_file():shutil.copy2(stage/name,export/name)
    shutil.copy2(revision,source);shutil.copy2(stage/'export_manifest.json',export/'export_manifest.json')
    result={'status':'EXPORTED_ENGINE_REIMPORT_PENDING','source':str(source),
        'source_sha256':sha(source),'revision_source':str(revision),'mesh_exports':3,'animation_exports':7,
        'portrait':str(export/'portrait.png'),'manifest':str(export/'export_manifest.json'),
        'manifest_sha256':sha(export/'export_manifest.json'),'candidate_invariants_preserved':True,
        'animations_modified_by_refinement':[clip['clip'] for clip in refined.get('changed_clips',[])],
        'lods':manifest['lods'],'fbx_profile':manifest['fbx_profile'],
        'recovery':'Verified complete stage and declared files; skipped generated .fbm directories during promotion',
        'recovery_script_sha256':sha(Path(__file__))}
    (out/'export-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('WC_REFINED_EXPORT_STAGE_RESUMED '+args.unit,flush=True)
