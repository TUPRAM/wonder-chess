"""Bake and export one isolated Ada art experiment with immutable provenance."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from aq1_bake import bake_candidate
from aq1_capture import setup,render_view
from refine_update_ada import invariants,use_clip
from normalized_fbx import export_normalized_copy
from author_alpha import export_fbx_raw
UID='wc_u_human_guardian'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--export',required=True);p.add_argument('--report',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(bpy.data.filepath).resolve();out=Path(a.output).resolve();export=Path(a.export).resolve();report=Path(a.report).resolve()
    allowed=ROOT/'art-source/heroes'/UID/'candidates/AQ1'
    assert all(x.is_relative_to(allowed) for x in (source,out,export));assert source.exists() and not out.exists() and not export.exists()
    report.mkdir(parents=True,exist_ok=True)
    arm=bpy.data.objects['Armature'];before=invariants(arm);parts=list(bpy.data.collections['AQ1_EDITABLE'].objects)
    parts=[o for o in parts if o.type=='MESH'];mesh,bake=bake_candidate(parts,arm,export,texture_size=1024)
    for ob in parts:ob.hide_render=True;ob.hide_set(True)
    # Retain editable high/low sources, show exactly one runtime export copy.
    mesh.hide_render=False;mesh.hide_set(False)
    for ob in bpy.context.scene.objects:
        if ob.name.startswith('AQ1_ReviewGround'):ob.hide_render=True
    use_clip(arm,'Idle');assert invariants(arm)==before
    bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=False)
    canonical=json.loads((ROOT/'exports/heroes'/UID/'export_manifest.json').read_text())
    export_normalized_copy(export/f'SK_{UID}.fbx',[arm,mesh],False,export_fbx_raw)
    for clip,spec in canonical['clips'].items():
        use_clip(arm,clip);bpy.context.scene.frame_start,bpy.context.scene.frame_end=spec['frames']
        export_normalized_copy(export/f'AN_{UID}_{clip}.fbx',[arm],True,export_fbx_raw)
    assert invariants(arm)==before
    manifest={'unit_id':UID,'status':'AQ1_unapproved_comparison_candidate','source_sha256':sha(out),'form_source':source.relative_to(ROOT).as_posix(),'form_source_sha256':sha(source),
        'units_source_sha256':sha(ROOT/'data/units.json'),'source_revision':'AQ1','fps':60,'clips':canonical['clips'],'invariants':before,
        'triangles':bake['triangles'],'materials':1,'texture_size':1024,'fbx_profile':'tools/blender/profiles/fbx_skeletal_cm_v1.json',
        'lods':[],'budget_status':'15k target; up-to25k comparison experiment needs Pram acceptance before promotion' if bake['triangles']>15000 else 'within15k target',
        'author_scripts':{p.name:sha(p) for p in (ROOT/'tools/blender').glob('aq1_*.py')},'files':{p.name:sha(p) for p in export.iterdir() if p.suffix in ('.fbx','.png')}}
    if bake['triangles']>25000:raise RuntimeError('Candidate exceeds AQ1 comparison envelope; inspect topology before importing')
    (export/'export_manifest.json').write_text(json.dumps(manifest,indent=2));(report/'export.json').write_text(json.dumps(manifest,indent=2))
    use_clip(arm,'Idle');scene=setup()
    for v in ('front','side','back','three_quarter','face','grip','board','shield_back'):render_view(scene,report/('material_'+v+'.png'),v)
    render_view(scene,report/'thumbnail96.png','board',96)
    print('AQ1_BAKE_EXPORT_COMPLETE',str(out),bake['triangles'],flush=True)

if __name__=='__main__':main()
