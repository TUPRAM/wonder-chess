"""Correct two observed r06 extreme-pose defects without touching action curves."""
import argparse,json,sys
from pathlib import Path
import bpy,bmesh
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import invariants,use_clip
from aq1_capture import setup,render_view
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();report=Path(a.report).resolve()
    assert out.is_relative_to(ROOT/'art-source/heroes/wc_u_human_guardian/candidates/AQ1') and not out.exists()
    arm=bpy.data.objects['Armature'];before=invariants(arm)
    cap=bpy.data.objects['hair_cap'];bm=bmesh.new();bm.from_mesh(cap.data)
    crown=[e for e in bm.edges if e.is_boundary and all(v.co.z>1.822 for v in e.verts)]
    if not crown:raise RuntimeError('Expected open top crown from actual r06 source')
    result=bmesh.ops.holes_fill(bm,edges=crown,sides=0)
    for f in result['faces']:
        f.smooth=True
    bm.normal_update();bm.to_mesh(cap.data);bm.free();cap.data.update()
    counts={}
    for name in ('coat_skirt','tabard_front','tabard_back'):
        ob=bpy.data.objects[name];changed=0
        for v in ob.data.vertices:
            t=max(0,min(1,(1.02-v.co.z)/.30))
            influence=.95*t
            if name.startswith('tabard'):
                v.co.y+=.004*(1 if name=='tabard_front' else -1)
            for vg in ob.vertex_groups:vg.remove([v.index])
            for key,w in [('pelvis',1-influence),('thigh_l' if v.co.x>=0 else 'thigh_r',influence)]:
                vg=ob.vertex_groups.get(key) or ob.vertex_groups.new(name=key);vg.add([v.index],w,'REPLACE')
            changed+=1
        counts[name]=changed
    assert invariants(arm)==before;use_clip(arm,'Idle')
    bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=False)
    report.mkdir(parents=True,exist_ok=True)
    (report/'change.json').write_text(json.dumps({'candidate':str(out),'observed_defects':['Open crown exposed skin in top-down Defeat view','Insufficient skirt thigh following exposed trousers through ivory coat'],'modified_skin_vertices':counts,'rig_and_curves':before,'approval':'pending'},indent=2))
    scene=setup()
    for clip,frame in [('Idle',1),('Attack',16),('Active',19),('Move',31),('Defeat',28),('Defeat',55)]:
        use_clip(arm,clip);scene.frame_set(frame);render_view(scene,report/f'{clip}_{frame:04d}.png','three_quarter',900)
if __name__=='__main__':main()
