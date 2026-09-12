"""Read-only localized fit and existing transverse self screen on outside work."""
import bpy, ast, hashlib, json, sys
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent;BASE=R.parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
SOURCE=R.parent/'armor'/(args[0] if args else 'ada_bw6_torso_outside_work.blend')
PREFIX=args[1] if len(args)>1 else 'outside'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
p=BASE/'BW2/r001/integrated-independent/audit_integrated_geometry.py';t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='segment_triangle'],type_ignores=[]),str(p),'exec'),globals())
def geom(o,raw=False):
 if raw:m=o.data.copy();w=o.matrix_world
 else:e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();w=e.matrix_world
 m.calc_loop_triangles();q=np.array([w@v.co for v in m.vertices]);tri=[tuple(t.vertices) for t in m.loop_triangles]
 sw=next((md for md in o.modifiers if md.type=='SHRINKWRAP'),None)
 vg=o.vertex_groups.get(sw.vertex_group) if sw and sw.vertex_group else None
 gi=vg.index if vg else -1
 groups=[1.0 if sw and not sw.vertex_group else next((g.weight for g in v.groups if g.group==gi),0) for v in m.vertices]
 if raw:bpy.data.meshes.remove(m)
 else:e.to_mesh_clear()
 return q,tri,BVHTree.FromPolygons([Vector(v) for v in q],tri,all_triangles=True),groups
def screen(a,b,self_query=False):
 qa,ta,ba,ga=a;qb,tb,bb,gb=b;hits=[]
 for ia,ib in ba.overlap(bb):
  if self_query and (ia>=ib or set(ta[ia])&set(tb[ib])):continue
  aa=qa[list(ta[ia])];ab=qb[list(tb[ib])];points=[]
  for one,two in [(aa,ab),(ab,aa)]:
   for i in range(3):
    p=segment_triangle(one[i],one[(i+1)%3],two)
    if p is not None:points.append(p)
  if points:hits.append({'triangles':[ia,ib],'point':np.mean(points,axis=0).tolist(),'a_vertices':list(ta[ia]),'a_positions':aa.tolist(),'a_clearance_weights':[ga[i] for i in ta[ia]]})
 out={'pairs':len(hits),'hits':hits}
 if hits:
  points=np.array([h['point'] for h in hits]);weights=[w for h in hits for w in h['a_clearance_weights']]
  out.update(bounds=[points.min(axis=0).tolist(),points.max(axis=0).tolist()],weight_range=[min(weights),max(weights)],zero_weight_vertices=sum(w==0 for w in weights),partial_weight_vertices=sum(0<w<.9999 for w in weights))
 return out
def brief(x):return {k:v for k,v in x.items() if k!='hits'}
coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];body=bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody'];navy=bpy.data.objects['BW6_NavyWaist']
wrap=next(m for m in coat.modifiers if m.type=='SHRINKWRAP');solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY')
out={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_saved':False,'modifier_order':[m.type for m in coat.modifiers],'wrap':{'method':wrap.wrap_method,'mode':wrap.wrap_mode,'offset':wrap.offset,'group':wrap.vertex_group},'poses':{},'self_screen':{}}
for frame in [1,20,49]:
 s.frame_set(frame);bpy.context.view_layer.update();gb=geom(body);gc=geom(coat)
 row={'coat_body':screen(gc,gb),'navy_coat':screen(geom(navy),gc),'navy_front':screen(geom(navy),geom(bpy.data.objects['BW6_FrontPlate']))}
 for label,n in [('front','BW6_FrontPlate'),('back','BW6_BackPlate')]:
  gp=geom(bpy.data.objects[n]);row[label+'_body']=screen(gp,gb);row[label+'_coat']=screen(gp,gc)
 for label in ['outer_no_wall','no_wrap_no_wall']:
  solid.show_viewport=False
  if label=='no_wrap_no_wall':wrap.show_viewport=False
  bpy.context.view_layer.update();variant=geom(coat);row[label]=screen(variant,gb)
  if frame==1:row[label+'_self']=screen(variant,variant,True)
 if frame==1:
  solid.show_viewport=True;wrap.show_viewport=False;bpy.context.view_layer.update()
  variant=geom(coat);row['no_wrap_with_wall']=screen(variant,gb);row['no_wrap_with_wall_self']=screen(variant,variant,True)
 solid.show_viewport=True;wrap.show_viewport=True;bpy.context.view_layer.update()
 out['poses'][str(frame)]=row
 print('FRAME',frame,{k:brief(v) for k,v in row.items()},flush=True)
 (R/(PREFIX+'_localized_interim.json')).write_text(json.dumps(out,indent=2),encoding='utf8')
for frame in [1,20,49]:
 s.frame_set(frame);bpy.context.view_layer.update();row={}
 names=json.loads(s['BW6_owned_visible_parts']) if frame==1 else [coat.name]
 for n in names:
  o=bpy.data.objects[n];r={}
  for raw in ([True,False] if frame==1 else [False]):
   g=geom(o,raw);r['raw' if raw else 'evaluated']=screen(g,g,True)
  row[n]=r;print('SELF',frame,n,{k:brief(v) for k,v in r.items()},flush=True)
 out['self_screen'][str(frame)]=row
out['scope']='Nonadjacent noncoplanar transverse triangle screen; mean crossing points. Not coplanar overlap, tangency, containment or continuous-time proof. Raw cage is undeformed; evaluated is sampled pose. No art approval.'
out['sha256_after']=hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert out['sha256_after']==out['sha256']
(R/(PREFIX+'_localized_and_self.json')).write_text(json.dumps(out,indent=2),encoding='utf8')
print('DONE source unchanged')
