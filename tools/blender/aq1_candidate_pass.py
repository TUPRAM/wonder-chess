"""Apply bounded semantic refinements on a retained candidate, never the canonical hero."""
import argparse,json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/blender'))
import aq1_author_forms as form
from refine_update_ada import invariants,use_clip
from aq1_capture import setup,render_view

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True)
    p.add_argument('--head',action='store_true');p.add_argument('--costume',action='store_true');p.add_argument('--equipment',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();report=Path(a.report).resolve()
    allowed=ROOT/'art-source/heroes/wc_u_human_guardian/candidates/AQ1'
    assert out.is_relative_to(allowed) and Path(bpy.data.filepath).resolve().is_relative_to(allowed)
    assert not out.exists();report.mkdir(parents=True,exist_ok=True)
    form.ARM=bpy.data.objects['Armature'];form.COL=bpy.data.collections['AQ1_EDITABLE'];form.PARTS=[]
    form.MATS={m.name[4:]:m for m in bpy.data.materials if m.name.startswith('AQ1_')}
    before=invariants(form.ARM);changes={}
    if a.head:
        from aq1_refine_head import refine_head
        changes['head']=refine_head(form)
    if a.costume:
        from aq1_refine_costume import refine_costume
        changes['costume']=refine_costume(form)
    if a.equipment:
        from aq1_equipment import build_equipment
        for ob in list(form.COL.objects):
            if ob.name in ('shield_shell','shield_rim','shield_crest','shield_straps','sword_blade','sword_guard','sword_grip','sword_pommel','hand_grip_r','hand_grip_l'):
                bpy.data.objects.remove(ob,do_unlink=True)
        changes['equipment']=[o.name for o in build_equipment(form.ARM,form.MATS,form.COL)]
    use_clip(form.ARM,'Idle');assert invariants(form.ARM)==before
    bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=False)
    counts={}
    for ob in form.COL.objects:
        if ob.type=='MESH':ob.data.calc_loop_triangles();counts[ob.name]=len(ob.data.loop_triangles)
    (report/'refinement.json').write_text(json.dumps({'candidate':str(out),'invariants':before,'changes':changes,'triangles':sum(counts.values()),'parts':counts,'approval':'pending'},indent=2))
    scene=setup()
    for view in ['front','side','back','three_quarter','face','grip','board']:render_view(scene,report/('material_'+view+'.png'),view)
    render_view(scene,report/'thumbnail96.png','board',96)
    scene.view_layers[0].material_override=form.make_material('clay_pass','ADB1B5',.72,0)
    for view in ['front','three_quarter','face']:render_view(scene,report/('clay_'+view+'.png'),view)
    print('AQ1_PASS_COMPLETE',str(out),sum(counts.values()),flush=True)

if __name__=='__main__':main()
