"""Read-only fixed-grip local query, reusing BW2's transverse triangle test."""
import bpy
import ast
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
SOURCE=Path(bpy.data.filepath)
before=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['BW4_ClosedGlove_Correction1','correction1']
glove=bpy.data.objects[args[0]]
label=args[1]
bw2=ROOT.parents[1]/'BW2/r001/integrated-independent/audit_integrated_geometry.py'
tree=ast.parse(bw2.read_text())
defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('segment_triangle','self_audit')]
exec(compile(ast.Module(body=defs,type_ignores=[]),str(bw2),'exec'),globals())

def geometry(obj,raw):
    if raw:
        mesh=obj.data
        matrix=obj.matrix_world
    else:
        ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh=ev.to_mesh();matrix=ev.matrix_world
    mesh.calc_loop_triangles()
    pts=np.array([list(matrix@v.co) for v in mesh.vertices])
    tris=[(t.index,tuple(t.vertices)) for t in mesh.loop_triangles]
    groups={g.index:g.name for g in obj.vertex_groups}
    weights=[{groups[g.group]:g.weight for g in v.groups if g.group in groups} for v in mesh.vertices]
    faces=[tuple(p.vertices) for p in mesh.polygons]
    if not raw:ev.to_mesh_clear()
    return pts,tris,weights,faces

def cross(q,triangles,p,other):
    ai=[t[1] for t in triangles];bi=[t[1] for t in other]
    av=BVHTree.FromPolygons(q.tolist(),ai,all_triangles=True,epsilon=0)
    bv=BVHTree.FromPolygons(p.tolist(),bi,all_triangles=True,epsilon=0)
    broad=av.overlap(bv);pairs=[]
    for a,b in broad:
        ta=q[list(ai[a])];tb=p[list(bi[b])];hits=[]
        for seg,othertri in [(ta,tb),(tb,ta)]:
            for i in range(3):
                point=segment_triangle(seg[i],seg[(i+1)%3],othertri)
                if point is not None:hits.append(point)
        if hits:pairs.append({'glove_triangle':triangles[a][0],'equipment_triangle':other[b][0],
            'glove_vertices':ai[a],'equipment_vertices':bi[b],
            'intersection_world_m':np.mean(hits,axis=0).tolist(),
            'glove_triangle_points_m':ta.tolist(),'equipment_triangle_points_m':tb.tolist()})
    return {'broad_pairs':len(broad),'confirmed_transverse_pairs':len(pairs),'pairs':pairs}

equipment={}
for part in ['handle','guard','blade']:
    obj=bpy.data.objects['BW4_SelectedSword_'+part]
    equipment[part]=geometry(obj,False)

def convex_planes(q,triangles):
    center=q.mean(axis=0);planes=[]
    for _,ids in triangles:
        a,b,c=q[list(ids)];normal=np.cross(b-a,c-a);ln=np.linalg.norm(normal)
        if ln<1e-13:continue
        normal/=ln
        if np.dot(normal,center-a)>0:normal=-normal
        d=np.dot(normal,a)
        if not any(np.linalg.norm(normal-n)<1e-6 and abs(d-t)<1e-6 for n,t in planes):planes.append((normal,d))
    return planes

hq,ht,_,hf=equipment['handle']
planes=convex_planes(hq,ht)
handle_bvh=BVHTree.FromPolygons(hq.tolist(),[i for _,i in ht],all_triangles=True,epsilon=0)
records=json.loads((ROOT/'records/correction1.json').read_text())
declared=records['predeclared_contact_source_vertices']
report={'source':str(SOURCE),'source_sha256_before':before,'glove':glove.name,
 'status':'READ_ONLY_GEOMETRY_SCREEN_NOT_ART_APPROVAL','space':'world metres, BW4 local metric hand scene',
 'source_query':str(bw2),'modes':{},'pommel':'No separate pommel object; handle includes end cap.',
 'method':'BVH candidate pairs followed by BW2 nonadjacent transverse segment-triangle intersection; actual selected equipment mesh triangles, no ideal cylinder substitute.',
 'limits':['Shared-vertex self triangle pairs excluded. Coplanar and tangent overlaps not classified.',
           'No mathematical certification of collision-free volume. Glove wrist is intentionally open.',
           'Signed distances are sampled glove vertices to convex actual handle surfaces, not a complete deepest-penetration solution.',
           'Contact selection follows existing predeclared vertex groups, not nearest post-fit vertices. Semantic remap is assessed by recorded source IDs and preserved group assignment.']}
for raw in [True,False]:
    mode='raw' if raw else 'evaluated'
    q,tris,weights,faces=geometry(glove,raw)
    own=self_audit(q,tris)
    for pair in own['pairs']:
        pair['triangle_points_m']=[q[list(v)].tolist() for v in pair['vertices']]
    distances=[];inside=[]
    for point in q:
        isinside=all(np.dot(n,point)-d < -1e-8 for n,d in planes)
        near=handle_bvh.find_nearest(Vector(point))
        distances.append((-1 if isinside else 1)*near[3]*1000)
        inside.append(isinside)
    distances=np.array(distances)
    contact={}
    for digit,ids in declared.items():
        name='CONTACT_'+digit+'_source_pad'
        current=[i for i,w in enumerate(weights) if w.get(name,0)>.999]
        ds=distances[current]
        contact[digit]={'group':name,'predeclared_source_ids':ids,'queried_ids':current,
          'raw_ids_match_predeclared':current==ids if raw else None,
          'threshold':'>0.999 inherited group weight','count':len(current),
          'distance_mm':ds.tolist(),'summary_mm':{'min':float(ds.min()),'median':float(np.median(ds)),'max':float(ds.max())} if len(ds) else None,
          'inside_minus0_5_plus1_0_band':int(((ds>=-.5)&(ds<=1)).sum()),
          'points_m':q[current].tolist()}
    entry={'vertices':len(q),'triangles':len(tris),'self':own,
      'equipment':{part:cross(q,tris,p,t) for part,(p,t,_,_) in equipment.items()},
      'handle_vertex_distance':{'inside_vertices':int(sum(inside)),'deeper_than_0_5mm':int((distances<-.5).sum()),
       'min_mm':float(distances.min()),'worst_vertex':int(distances.argmin()),'worst_point_m':q[distances.argmin()].tolist()},
      'contact':contact,
      'triangles_all_vertices_inside_handle':[i for i,ids in tris if all(inside[v] for v in ids)]}
    report['modes'][mode]=entry
    print('BW4_GEOMETRY',mode,'self',own['confirmed_nonadjacent_transverse_pairs'],
          'equipment',{p:r['confirmed_transverse_pairs'] for p,r in entry['equipment'].items()},
          'min_handle_mm',entry['handle_vertex_distance']['min_mm'],flush=True)
report['source_sha256_after']=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert report['source_sha256_after']==before
report['source_preserved']=True
(OUT/(label+'_geometry.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
summary={'status':report['status'],'source':str(SOURCE),'source_sha256':before,
 'modes':{m:{'self_pairs':v['self']['confirmed_nonadjacent_transverse_pairs'],
 'equipment_pairs':{p:r['confirmed_transverse_pairs'] for p,r in v['equipment'].items()},
 'worst_handle_vertex':v['handle_vertex_distance'],
 'contacts':{d:{k:p[k] for k in ['count','raw_ids_match_predeclared','summary_mm','inside_minus0_5_plus1_0_band']} for d,p in v['contact'].items()},
 'first_self_pairs':v['self']['pairs'][:8]} for m,v in report['modes'].items()}}
(OUT/(label+'_summary.json')).write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
