"""Bounded r01 correction: sleeve/armor clearance and fitted costume forms."""
import argparse,json,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import invariants,use_clip
import aq1_author_forms as form
from aq1_capture import setup,render_view

def radial_fit(ob,axis_a,axis_b,factor):
    axis=(axis_b-axis_a).normalized()
    for v in ob.data.vertices:
        origin=axis_a+axis*(v.co-axis_a).dot(axis)
        v.co=origin+(v.co-origin)*factor
    ob.data.update()

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True);p.add_argument('--head',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    out=Path(a.output).resolve();assert out.is_relative_to(ROOT/'art-source/heroes/wc_u_human_guardian/candidates/AQ1');assert not out.exists()
    report=Path(a.report);report.mkdir(parents=True,exist_ok=True)
    arm=bpy.data.objects['Armature'];saved=invariants(arm);col=bpy.data.collections['AQ1_EDITABLE']
    for s in ('l','r'):
        radial_fit(bpy.data.objects['bracer_'+s],arm.data.bones['lowerarm_'+s].head_local,arm.data.bones['lowerarm_'+s].tail_local,1.19)
        radial_fit(bpy.data.objects['greave_'+s],arm.data.bones['calf_'+s].head_local,arm.data.bones['calf_'+s].tail_local,1.24)
        sh=arm.data.bones['upperarm_'+s].head_local
        ob=bpy.data.objects['armor_pauldron_'+s]
        for v in ob.data.vertices:v.co.z=sh.z+(v.co.z-sh.z)*.78
        ob.data.update()
        toe=bpy.data.objects['boot_toe_plate_'+s]
        for v in toe.data.vertices:v.co.z=.068+(v.co.z-.077)*.64;v.co.y=.158+(v.co.y-.151)*1.12
        sole=bpy.data.objects['boot_sole_'+s]
        for v in sole.data.vertices:v.co.z-=.009
    ob=bpy.data.objects['coat_skirt']
    for v in ob.data.vertices:
        t=max(0,min(1,(1.04-v.co.z)/.23));v.co.x*=1+.25*t;v.co.y*=1+.05*t
    ob.data.update()
    ob=bpy.data.objects['armor_chest']
    for v in ob.data.vertices:
        if v.co.z>1.36:
            v.co.x*=1.29;v.co.z+=.040*(abs(v.co.x)/.22)**.8;v.co.y+=.007
    ob.data.update()
    for name,rough in [('AQ1_steel',.47),('AQ1_steel_dark',.51),('AQ1_hair',.66)]:
        mat=bpy.data.materials.get(name)
        if mat:mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=rough
    if a.head:
        form.ARM=arm;form.COL=col;form.MATS={m.name[4:]:m for m in bpy.data.materials if m.name.startswith('AQ1_')};form.PARTS=[]
        from aq1_refine_head import refine_head
        refine_head(form)
    use_clip(arm,'Idle');assert invariants(arm)==saved
    bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=False)
    counts={}
    for ob in col.objects:ob.data.calc_loop_triangles();counts[ob.name]=len(ob.data.loop_triangles)
    (report/'refinement.json').write_text(json.dumps({'source':str(out),'part_triangles':counts,'triangles':sum(counts.values()),'invariants':saved,'changes':['Expanded fitted bracer/greave clearance over sleeves and legs','Flattened upper pauldron profile','Wrapped ivory skirt over thigh volume','Shaped upper chest toward collar/shoulders','Refined boot toe/sole silhouette','Reduced steel/hair gloss'],'head_refined':a.head,'art_approval':'pending'},indent=2))
    scene=setup()
    for view in ['front','three_quarter','face','side','grip','shield_back','board']:render_view(scene,report/('material_'+view+'.png'),view)
    scene.view_layers[0].material_override=form.make_material('clay_r02','ADB1B5',.72,0)
    for view in ['front','three_quarter','face']:render_view(scene,report/('clay_'+view+'.png'),view)
    print('AQ1_REFINED',str(out),flush=True)

if __name__=='__main__':main()
