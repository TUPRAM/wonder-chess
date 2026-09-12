import bpy,json
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent;source=R.parent/'armor/ada_bw5_armor_correction1.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
front=bpy.data.objects['BW4_Breastplate_ControlSurface'];coat=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous']
def bvh(o,evaluated=True):
 if evaluated:
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();v=[ev.matrix_world@v.co for v in me.vertices];t=[tuple(p.vertices) for p in me.polygons];ev.to_mesh_clear()
 else:v=[o.matrix_world@v.co for v in o.data.vertices];t=[tuple(p.vertices) for p in o.data.polygons]
 return BVHTree.FromPolygons(v,t)
bs={'coat':bvh(coat),'raw':bvh(front,False),'final':bvh(front)}
def hit(b,x,z):
 h=b.ray_cast(Vector((float(x),1,float(z))),Vector((0,-1,0)),2);return float(h[0].y) if h[0] else None
cage=np.array([front.matrix_world@v.co for v in front.data.vertices]);vrecords=[]
for i,p in enumerate(cage):
 y=hit(bs['coat'],p[0],p[2]);vrecords.append({'index':i,'row':i//19,'column':i%19,'world_m':p.tolist(),'coat_front_y_m':y,'gap_mm':(p[1]-y)*1000 if y is not None else None})
samples=[]
for z in np.arange(1.175,1.480,.005):
 for x in np.arange(0,.196,.005):
  h={k:hit(b,float(x),float(z)) for k,b in bs.items()}
  if h['coat'] is None or h['final'] is None:continue
  p=np.array([x,h['final'],z]);d=np.sum((cage-p)**2,axis=1);inds=np.argsort(d)[:4]
  samples.append({'x_m':float(x),'z_m':float(z),'hits_y_m':h,'final_outer_gap_mm':(h['final']-h['coat'])*1000,'raw_gap_mm':(h['raw']-h['coat'])*1000 if h['raw'] is not None else None,'final_minus_raw_mm':(h['final']-h['raw'])*1000 if h['raw'] is not None else None,'nearest_control_vertices':inds.tolist()})
negative=[r for r in samples if r['final_outer_gap_mm']<0];selected=[r for r in samples if abs(r['z_m']-1.3)<.0026 and abs(r['x_m']-.14)<.0201]
out={'source':str(source),'note':'Frame1 anterior ray: raw polygon tessellation vs final evaluated OUTER surface. Gap to coat +Y front. Sampled grid 5mm. Inner shell is additionally inward; outer gap zero is insufficient clearance.','vertices':vrecords,'samples':samples,'negative_count':len(negative),'worst':sorted(negative,key=lambda r:r['final_outer_gap_mm'])[:20],'selected_z1300':selected}
(R/'correction1_interpolation_diagnosis.json').write_text(json.dumps(out,indent=2,default=float));print('WORST',json.dumps(out['worst'][:6]));print('Z1300',json.dumps(selected));print('ROW4',json.dumps(vrecords[4*19+9:5*19],default=float));print('UPPER',json.dumps(sorted([r for r in negative if r['z_m']>1.4],key=lambda r:r['final_outer_gap_mm'])[:5]))


