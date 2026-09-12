import bpy,bmesh,math,json,ast
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_fitted_coat.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];bm=bmesh.new();bm.from_mesh(coat.data);bm.normal_update()
samples=[f.normal.y for f in bm.faces if 1.17<f.calc_center_median().z<1.40 and abs(f.calc_center_median().x)<.09 and f.calc_center_median().y>.06]
assert samples
flipped=sum(samples)/len(samples)<0
if flipped:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
for f in bm.faces:f.smooth=True
bm.to_mesh(coat.data);bm.free();coat.data.update()
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
g=coat.vertex_groups.new(name='BW6_Padding_Seam_Thickness')
for v in coat.data.vertices:
 p=v.co;neck=smooth((p.z-1.43)/.025)
 under=smooth((abs(p.x)-.14)/.02)*smooth((.245-abs(p.x))/.02)*smooth((p.z-1.25)/.03)*smooth((1.42-p.z)/.03)
 g.add([v.index],1-max(neck,under),'REPLACE')
solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY');solid.vertex_group=g.name;solid.thickness_vertex_group=.25
coat['BW6_wall']='Correct outward face orientation verified on anterior torso. Preserved6mm padded field; new sewn/turning collar and axilla transitions taper to1.5mm instead of overlapping inner walls.'
out=R/'ada_bw6_torso_oriented_work.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
base=R.parents[1]
for p,names in [(base/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(R.parent/'analysis/inspect_outside_work.py',['geom','screen'])]:
 t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
record={'source':str(out),'front_normal_mean_before':sum(samples)/len(samples),'reversed_faces':flipped,'poses':{}}
names=['BW6_PaddedCoat_Tailored','BW6_FrontPlate','BW6_BackPlate','BW6_NavyWaist','BW6_SideEnclosure_1','BW6_SideEnclosure_-1','BW4_CONTEXT_BW1_IndexedBody']
for fr in [1,20,49]:
 s.frame_set(fr);bpy.context.view_layer.update();gs={n:geom(bpy.data.objects[n]) for n in names};c=names[0];body=names[-1]
 pairs=[(c,body)]+[(n,c) for n in names[1:-1]]+[(names[3],names[1])]
 row={a+'__'+b:screen(gs[a],gs[b]) for a,b in pairs};row['coat_self']=screen(gs[c],gs[c],True);record['poses'][str(fr)]=row
 print('POSE',fr,{k:v['pairs'] for k,v in row.items()},flush=True)
(R/'records/oriented_probe.json').write_text(json.dumps(record,indent=2))
s.frame_set(1);s.cycles.samples=12;s.render.threads=4
for view in ['front','profile','three_quarter','back']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('oriented_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('BW6_ORIENTED_COMPLETE')
