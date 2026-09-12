"""Read-only BW5 surface query; exact existing BW2/BW4 query functions."""
import bpy,ast,json,sys,hashlib,bmesh
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1];BW4=OUT.parents[1]/'BW4/r001'
args=sys.argv[sys.argv.index('--')+1:];source=Path(args[0]);label=args[1]
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
before=hashlib.sha256(source.read_bytes()).hexdigest()
for p,names in [(BW4.parents[1]/'BW2/r001/integrated-independent/audit_integrated_geometry.py',('segment_triangle','self_audit')),(BW4/'reviews/hand_geometry/audit_fixed_geometry.py',('geometry','cross','convex_planes'))]:
 tree=ast.parse(p.read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];exec(compile(ast.Module(body=defs,type_ignores=[]),str(p),'exec'),globals())
o=next(o for o in bpy.context.scene.objects if o.name.startswith('BW5_ClosedGlove_'))
equipment={p:geometry(bpy.data.objects['BW4_SelectedSword_'+p],False) for p in ('handle','guard','blade')}
hq,ht,_,_=equipment['handle'];planes=convex_planes(hq,ht);hbvh=BVHTree.FromPolygons(hq.tolist(),[i for _,i in ht],all_triangles=True,epsilon=0)
report={'source':str(source),'source_sha256':before,'object':o.name,'query_basis':'Existing BW2 confirmed transverse triangle query and BW4 convex-hilt signed samples; no ideal cylinder','modes':{},'contact':'NOT_SCORED_LOCAL_CONSTRUCTION_FIRST; rebuilt anatomy correspondence is recorded before scores','limits':['Shared-vertex triangle pairs excluded','Coplanar and tangent cases not classified','Vertex SDF is a sample, not maximum full triangle depth','Intended wrist opening means glove is not a closed solid']}
bm=bmesh.new();bm.from_mesh(o.data);report['topology']={'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_nonboundary_edges':sum(not e.is_manifold and not e.is_boundary for e in bm.edges),'loose_vertices':sum(not v.link_faces for v in bm.verts),'zero_area_faces':sum(f.calc_area()<1e-13 for f in bm.faces)};bm.free()
for raw in (True,False):
 mode='raw' if raw else 'evaluated';q,tri,w,f=geometry(o,raw);own=self_audit(q,tri);checks={p:cross(q,tri,v,t) for p,(v,t,_,_) in equipment.items()}
 distances=[];inside=[]
 for point in q:
  ins=all(np.dot(n,point)-d<-1e-8 for n,d in planes);inside.append(ins);distances.append((-1 if ins else 1)*hbvh.find_nearest(Vector(point))[3]*1000)
 ds=np.array(distances);entry={'vertices':len(q),'triangles':len(tri),'self':own,'equipment':checks,'handle_vertex_distance':{'inside_vertices':sum(inside),'deeper_than_0_5mm':int((ds<-.5).sum()),'min_mm':float(ds.min()),'worst_vertex':int(ds.argmin()),'worst_point_m':q[ds.argmin()].tolist()},'triangles_fully_inside_handle':[i for i,ids in tri if all(inside[v] for v in ids)]};report['modes'][mode]=entry
 pads={}
 for name in ('index','middle','ring','little','thumb'):
  ids=[i for i,weight in enumerate(w) if weight.get('BW5_CONTACT_'+name,0)>.999]
  distances=ds[ids]
  pads[name]={'selection':'Predeclared construction-sector group, threshold > .999 after subdivision; no closest-vertex reselection','count':len(ids),'indices':ids,'points_m':q[ids].tolist(),'distance_mm':distances.tolist(),'summary_mm':{'min':float(distances.min()),'median':float(np.median(distances)),'max':float(distances.max())} if len(ids) else None,'count_in_minus0_5_plus1mm_band':int(((distances>=-.5)&(distances<=1)).sum())}
 entry['contact_regions']=pads
 print('BW5_CHECK',mode,'self',own['confirmed_nonadjacent_transverse_pairs'],'equipment',{p:r['confirmed_transverse_pairs'] for p,r in checks.items()},'min',float(ds.min()),flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
report['source_preserved']=True
(OUT/'records'/f'{label}_geometry.json').write_text(json.dumps(report,indent=2))
summary={'source':str(source),'source_sha256':before,'topology':report['topology'],'modes':{m:{'self_pairs':v['self']['confirmed_nonadjacent_transverse_pairs'],'equipment_pairs':{p:r['confirmed_transverse_pairs'] for p,r in v['equipment'].items()},'handle_samples':v['handle_vertex_distance'],'first_self_pairs':v['self']['pairs'][:12]} for m,v in report['modes'].items()}}
(OUT/'records'/f'{label}_summary.json').write_text(json.dumps(summary,indent=2));print('SUMMARY',json.dumps(summary),flush=True)
