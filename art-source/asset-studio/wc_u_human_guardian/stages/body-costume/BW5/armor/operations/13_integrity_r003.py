import bpy,json,ast,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];src=R/'ada_bw5_armor_checkpoint_r003_ART_REVISE.blend'
def action_curves(a):
    out=[]
    for layer in a.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for c in bag.fcurves:
                    out.append([c.data_path,c.array_index,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation] for k in c.keyframe_points]])
    return sorted(out,key=lambda x:(x[0],x[1]))
bpy.ops.wm.open_mainfile(filepath=str(R.parents[1]/'BW4/r001/armor/ada_armor_checkpoint_FINAL_ART_REVISE.blend'),use_scripts=False)
oldcurves=action_curves(bpy.data.objects['BW4_Armor_Independent_Rig'].animation_data.action)
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);rig=bpy.data.objects['BW4_Armor_Independent_Rig']
curves=action_curves(rig.animation_data.action);assert curves==oldcurves
q=R.parents[1]/'BW2/r001/integrated-independent/audit_integrated_geometry.py';t=ast.parse(q.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='segment_triangle'],type_ignores=[]),str(q),'exec'),globals())
q=R.parent/'shoulder/operations/03_audit.py';t=ast.parse(q.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in ['geom','cross']],type_ignores=[]),str(q),'exec'),globals())
out={}
for n in json.loads(s['BW5_owned_visible_parts']):
    ob=bpy.data.objects[n];entry={}
    for raw in [True,False]:
        q,ts,bv=geom(ob,raw);hits=[]
        for a,b in bv.overlap(bv):
            if a>=b or set(ts[a])&set(ts[b]):continue
            ta=q[list(ts[a])];tb=q[list(ts[b])];points=[]
            for one,two in [(ta,tb),(tb,ta)]:
                for i in range(3):
                    p=segment_triangle(one[i],one[(i+1)%3],two)
                    if p is not None:points.append(p)
            if points:hits.append({'triangles':[a,b],'world_point_m':np.mean(points,axis=0).tolist()})
        entry['raw' if raw else 'evaluated']={'confirmed_transverse_self_pairs':len(hits),'examples':hits[:4]}
    out[n]=entry
    print(n,entry['raw']['confirmed_transverse_self_pairs'],entry['evaluated']['confirmed_transverse_self_pairs'],flush=True)
record={'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_authoring_action_curves_exactly_equal':True,'curve_count':len(curves),'action_numeric_sha256':hashlib.sha256(json.dumps(curves).encode()).hexdigest(),'frame':1,'scope':'Nonadjacent transverse self-intersection screen on raw and evaluated owned visible rigid-to-spine geometry. Coplanar/tangency/containment not certified. No forms approval.','parts':out}
(R/'records/surface_integrity_r003.json').write_text(json.dumps(record,indent=2))
