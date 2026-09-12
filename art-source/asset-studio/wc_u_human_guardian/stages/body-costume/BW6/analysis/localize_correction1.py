"""Locate existing transverse queries by actual geometry; read-only source."""
import bpy, json, ast, hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent;BASE=R.parents[1]
SOURCE=R.parent/'armor/ada_bw6_torso_correction1.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
for p,names in [(BASE/'BW4/r001/armor/operations/08_verify_and_motion.py',['geom']),(BASE/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle'])]:
 t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
def classify(p):
 x,y,z=p;ax=abs(x)
 if ax>.23:return 'sleeve'
 if z>1.45:return 'neck_upper_shoulder'
 if ax>.17 and z>1.30:return 'armhole_shoulder'
 if z<1.16:return 'waist_hem'
 return 'torso'
def query(a,b):
 qa,ta,ba=geom(a);qb,tb,bb=geom(b);hits=[]
 rawvs=[a.matrix_world@v.co for v in a.data.vertices]
 raw=BVHTree.FromPolygons(rawvs,[tuple(p.vertices) for p in a.data.polygons])
 for ia,ib in ba.overlap(bb):
  aa=qa[list(ta[ia])];ab=qb[list(tb[ib])];points=[]
  for one,two in [(aa,ab),(ab,aa)]:
   for i in range(3):
    p=segment_triangle(one[i],one[(i+1)%3],two)
    if p is not None:points.append(p)
  if points:
   p=np.mean(points,axis=0);near=raw.find_nearest(Vector(p));fi=near[2]
   hits.append({'triangles':[ia,ib],'point':p.tolist(),'region':classify(p),'nearest_raw_face':fi})
 result={'count':len(hits),'region_histogram':{k:sum(h['region']==k for h in hits) for k in sorted({h['region'] for h in hits})},'points':hits}
 result['regional_cage_faces']={}
 for region in result['region_histogram']:
  subset=[h for h in hits if h['region']==region]
  ids=sorted({h['nearest_raw_face'] for h in subset});hist={i:sum(h['nearest_raw_face']==i for h in subset) for i in ids}
  tops=sorted(hist,key=hist.get,reverse=True)[:6]
  result['regional_cage_faces'][region]=[{'index':i,'pairs':hist[i],'vertices':list(a.data.polygons[i].vertices),'coords':[list(rawvs[j]) for j in a.data.polygons[i].vertices]} for i in tops]
 if hits:
  ps=np.array([h['point'] for h in hits]);result['bounds']=[ps.min(axis=0).tolist(),ps.max(axis=0).tolist()]
  ids=sorted({h['nearest_raw_face'] for h in hits});hist={i:sum(h['nearest_raw_face']==i for h in hits) for i in ids}
  tops=sorted(hist,key=hist.get,reverse=True)[:12]
  result['nearest_cage_faces']=[{'index':i,'pairs':hist[i],'vertices':list(a.data.polygons[i].vertices),'coords':[list(rawvs[j]) for j in a.data.polygons[i].vertices]} for i in tops]
 return result
coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];body=bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody']
out={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'frame':1,'scope':'Noncoplanar transverse triangle crossings, mean crossing points, nearest raw face is localization not exact subdivision provenance. Region tags use explicit world thresholds in script, not topology semantics.','pairs':{}}
for a,b in [(coat,body),(bpy.data.objects['BW6_NavyWaist'],coat)]+[(bpy.data.objects['BW6_SideEnclosure_'+str(side)],b) for side in [-1,1] for b in [body,coat]]:
 key=a.name+'__'+b.name;out['pairs'][key]=query(a,b)
 print(key,{k:v for k,v in out['pairs'][key].items() if k not in ['points','nearest_cage_faces','regional_cage_faces']},flush=True)
(R/'correction1_localized_crossings.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('No source blend saved')
