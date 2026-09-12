"""Measured r04 clearance correction, retaining semantic source and rig."""
import argparse,json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from aq1_capture import setup,render_view
from refine_update_ada import invariants,use_clip
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();report=Path(a.report).resolve()
    assert out.is_relative_to(ROOT/'art-source/heroes/wc_u_human_guardian/candidates/AQ1') and not out.exists()
    arm=bpy.data.objects['Armature'];before=invariants(arm)
    # Observed r04 toe-roof clipping: lift only the forged cap, not the boot or rig.
    for side in ('l','r'):
        ob=bpy.data.objects['boot_toe_plate_'+side]
        for v in ob.data.vertices:v.co.z+=.018
        ob.data.update()
    # Reduce excess skirt volume while retaining the actual thigh envelope.
    skirt=bpy.data.objects['coat_skirt']
    for v in skirt.data.vertices:
        if v.co.z<.95:v.co.x*=.95
    skirt.data.update()
    # Each upper shoulder is a curved steel shell with a shallow central ridge.
    for side in ('l','r'):
        ob=bpy.data.objects['armor_pauldron_'+side];cx=arm.data.bones['upperarm_'+side].head_local.x
        for v in ob.data.vertices:
            local=abs(v.co.x-cx);v.co.z+=.009*max(0,1-local/.15)*(1-min(1,abs(v.co.y)/.13))
        ob.data.update()
    use_clip(arm,'Idle');assert invariants(arm)==before
    bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=False)
    report.mkdir(parents=True,exist_ok=True)
    (report/'refinement.json').write_text(json.dumps({'source':str(out),'changes':['18mm toe-cap clearance after observed clipping','5 percent skirt lateral reduction below waist','Subtle pauldron crown ridge'],'invariants':before,'art_approval':'pending'},indent=2))
    scene=setup()
    for view in ('three_quarter','side','face','grip','board'):render_view(scene,report/('material_'+view+'.png'),view)

if __name__=='__main__':main()
