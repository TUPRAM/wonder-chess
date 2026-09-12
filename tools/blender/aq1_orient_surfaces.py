"""Orient known open facial and armor patches toward their intended exterior."""
import argparse,json,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import invariants
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();report=Path(a.report).resolve()
    assert out.is_relative_to(ROOT/'art-source/heroes/wc_u_human_guardian/candidates/AQ1') and not out.exists()
    before=invariants(bpy.data.objects['Armature']);records=[]
    prefixes=('eye_white_','eyelid_','eye_lash_','iris_','pupil_','brow_','mouth_','nose_nostril_')
    for ob in bpy.data.collections['AQ1_EDITABLE'].objects:
        axis=None
        if ob.name.startswith(prefixes) or ob.name=='armor_chest':axis=Vector((0,1,0))
        elif ob.name=='armor_back':axis=Vector((0,-1,0))
        elif ob.name.startswith('boot_toe_plate_') or ob.name=='hair_cap':axis=Vector((0,0,1))
        if axis is None:continue
        bm=bmesh.new();bm.from_mesh(ob.data);bm.normal_update()
        before_score=sum(f.normal.dot(axis)*f.calc_area() for f in bm.faces)
        if before_score<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.normal_update();bm.to_mesh(ob.data);ob.data.update()
        records.append({'part':ob.name,'area_weighted_normal_before':before_score,'reversed':before_score<0,'expected_outward_axis':list(axis)})
        bm.free()
    assert invariants(bpy.data.objects['Armature'])==before
    bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=False)
    report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps({'candidate':str(out),'normal_orientation':records,'invariants':before},indent=2))
if __name__=='__main__':main()
