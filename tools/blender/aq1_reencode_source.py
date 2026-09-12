"""Freeze a source texture-encoding correction and re-export unchanged geometry."""
import argparse,hashlib,json,shutil,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import invariants,use_clip
from normalized_fbx import export_normalized_copy
from author_alpha import export_fbx_raw
from aq1_capture import setup,render_view
UID='wc_u_human_guardian'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--export',required=True);p.add_argument('--prior-export',required=True);p.add_argument('--report',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();export=Path(a.export).resolve();prior=Path(a.prior_export).resolve();report=Path(a.report).resolve()
    allowed=ROOT/'art-source/heroes'/UID/'candidates/AQ1';assert out.is_relative_to(allowed) and export.is_relative_to(allowed) and not out.exists()
    color=export/f'T_{UID}_BaseColor.png';assert color.exists() and color.read_bytes()[24]==8
    report.mkdir(parents=True,exist_ok=True);arm=bpy.data.objects['Armature'];before=invariants(arm)
    material=bpy.data.materials['M_AQ1_Ada_Baked'];replaced=[]
    new=bpy.data.images.load(str(color),check_existing=False);new.colorspace_settings.name='sRGB'
    for node in material.node_tree.nodes:
        if node.type=='TEX_IMAGE' and node.label=='BaseColor':replaced.append(node.image.name);node.image=new
    assert len(replaced)==1
    mesh=next(o for o in bpy.data.collections['AQ1_BAKED_EXPORT'].objects if o.type=='MESH')
    use_clip(arm,'Idle');bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=False)
    manifest=json.loads((prior/'export_manifest.json').read_text())
    export_normalized_copy(export/f'SK_{UID}.fbx',[arm,mesh],False,export_fbx_raw)
    for clip,spec in manifest['clips'].items():
        use_clip(arm,clip);bpy.context.scene.frame_start,bpy.context.scene.frame_end=spec['frames']
        export_normalized_copy(export/f'AN_{UID}_{clip}.fbx',[arm],True,export_fbx_raw)
    for key in ('Normal','ORM'):shutil.copy2(prior/f'T_{UID}_{key}.png',export/f'T_{UID}_{key}.png')
    shutil.copy2(prior/'bake-metadata.json',export/'prior-bake-metadata.json')
    assert before==invariants(arm)
    manifest.update(source_sha256=sha(out),source_revision='AQ1_BaseColor8',source_change='Only source BaseColor image encoding:16-bit sRGB PNG to8-bit sRGB PNG; geometry, weights, actions and data maps unchanged',
        prior_source_sha256=manifest['source_sha256'],prior_export_manifest_sha256=sha(prior/'export_manifest.json'),
        texture_contract={'BaseColor':'PNG RGB8 sRGB','Normal':'PNG RGB16 linear tangent+Y','ORM':'PNG RGB16 linear R=AO G=roughness B=metallic'},
        files={p.name:sha(p) for p in export.iterdir() if p.suffix in ('.fbx','.png')})
    (export/'export_manifest.json').write_text(json.dumps(manifest,indent=2));(report/'source-change.json').write_text(json.dumps(manifest,indent=2))
    use_clip(arm,'Idle');scene=setup()
    for view in ('front','face','three_quarter'):render_view(scene,report/('material_'+view+'.png'),view)
    print('AQ1_TEXTURE_SOURCE_REEXPORTED',str(out),flush=True)
if __name__=='__main__':main()
