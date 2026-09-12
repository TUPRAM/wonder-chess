import bpy,json,hashlib,ast,math
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
out=Path(__file__).parent;source=out.parent/'grip_integrated_contact_r001.blend';sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha=='9509750f833cec0c8cac90cd866215a732baed67571d1d444c7b718f441f877d'
s=bpy.context.scene;r=bpy.data.objects['BW1_Temporary_Pose_Rig'];glove=bpy.data.objects['BW1_Glove_Pair_SourceFit'];body=bpy.data.objects['BW1_IndexedBody'];rec=json.loads(s['BW2_hand_contract']);Fi=Matrix(rec['frame_world']).inverted();axis=np.array(rec['handle_axis_hand']);C=np.array(rec['handle_center_hand_m']);R=rec['radius_m'];half=rec['endpoint_span_m']/2;U=np.array([0.,0.,1.]);V=np.cross(axis,U);V/=np.linalg.norm(V)
# Reuse only three already-executed read-only geometric query functions; no fitting code is run.
query_source=out.parent/'middle-independent/audit_triangle_interiors.py';tree=ast.parse(query_source.read_text());query_defs=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('clip','closest_projected','has_depth')],type_ignores=[]);exec(compile(query_defs,str(query_source),'exec'),globals())
def data_for(ob):
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();raw=np.empty(len(me.vertices)*3);me.vertices.foreach_get('co',raw);raw=raw.reshape(-1,3);GW=np.array(Fi@ev.matrix_world);q=raw@GW[:3,:3].T+GW[:3,3]
    triangles=[(t.index,tuple(t.vertices)) for t in me.loop_triangles if all(-.025<q[i,1]<.24 and abs(q[i,0])<.135 and abs(q[i,2])<.14 for i in t.vertices)]
    ev.to_mesh_clear();return q,triangles
def cylinder_audit(q,triangles):
    shifted=q-C;ax=shifted@axis;radial=shifted-np.outer(ax,axis);rad=np.linalg.norm(radial,axis=1)-R;d=np.stack([rad,np.abs(ax)-half],axis=1);sd=np.minimum(np.max(d,axis=1),0)+np.linalg.norm(np.maximum(d,0),axis=1)
    candidates=[]
    for index,ids in triangles:
        tri=shifted[list(ids)]
        if has_depth(tri,0)[0]:candidates.append((index,ids,tri))
    deep=[]
    for index,ids,tri in candidates:
        hit,ra,pt=has_depth(tri,.0005)
        if hit:deep.append({'triangle':index,'vertices':ids,'point_hand_m':(pt+C).tolist() if pt is not None else None})
    lo=0.;hi=R;worst=None
    for _ in range(18):
        m=(lo+hi)/2;found=None
        for index,ids,tri in candidates:
            hit,ra,pt=has_depth(tri,m)
            if hit:found=(index,ids,pt);break
        if found:lo=m;worst=found
        else:hi=m
    ids_hand=sorted({i for _,ids in triangles for i in ids});minimum=int(ids_hand[int(np.argmin(sd[ids_hand]))]);patches={}
    for digit,p in rec['patches'].items():
        ids=p['indices'];gaps=rad[ids]*1000;axial=np.abs(ax[ids]);patches[digit]={'gaps_mm':gaps.tolist(),'within_band':int(np.sum((gaps>=-.5)&(gaps<=1)&(axial<=half-.002))),'count':len(ids),'max_abs_axial_mm':float(max(axial)*1000)}
    return {'triangle_count':len(triangles),'solid_intersection_triangles':len(candidates),'deeper_than_0_5mm':len(deep),'deep_triangles':deep,'max_triangle_depth_mm_interval':[lo*1000,hi*1000],'worst_triangle':{'index':worst[0],'vertices':worst[1],'point_hand_m':(worst[2]+C).tolist() if worst[2] is not None else None} if worst else None,'minimum_vertex_sdf_mm':float(sd[minimum]*1000),'minimum_vertex_index':minimum,'patches':patches}
def segment_triangle(a,b,tri):
    direction=b-a;e1=tri[1]-tri[0];e2=tri[2]-tri[0];p=np.cross(direction,e2);det=float(np.dot(e1,p))
    if abs(det)<1e-16:return None
    inv=1/det;tvec=a-tri[0];u=float(np.dot(tvec,p)*inv)
    if u<-1e-8 or u>1+1e-8:return None
    qq=np.cross(tvec,e1);v=float(np.dot(direction,qq)*inv)
    if v<-1e-8 or u+v>1+1e-8:return None
    t=float(np.dot(e2,qq)*inv)
    if t<=1e-8 or t>=1-1e-8:return None
    return a+t*direction
def self_audit(q,triangles):
    tri_indices=[ids for _,ids in triangles];bvh=BVHTree.FromPolygons(q.tolist(),tri_indices,all_triangles=True,epsilon=0.)
    broad={(min(a,b),max(a,b)) for a,b in bvh.overlap(bvh) if a!=b};pairs=[]
    for a,b in sorted(broad):
        ia=tri_indices[a];ib=tri_indices[b]
        if set(ia)&set(ib):continue
        ta=q[list(ia)];tb=q[list(ib)];hits=[]
        for seg,other in [(ta,tb),(tb,ta)]:
            for i in range(3):
                point=segment_triangle(seg[i],seg[(i+1)%3],other)
                if point is not None:hits.append(point)
        if hits:
            center=np.mean(hits,axis=0);pairs.append({'triangles':[triangles[a][0],triangles[b][0]],'vertices':[ia,ib],'intersection_hand_m':center.tolist(),'intersection_point_count':len(hits)})
    return {'broad_pairs':len(broad),'confirmed_nonadjacent_transverse_pairs':len(pairs),'pairs':pairs,'limits':'Topologically shared-vertex triangle pairs excluded. Nonadjacent transverse segment/triangle intersections confirmed; coplanar overlap and tangential contacts not classified.'}
report={'source':str(source),'source_sha256':sha,'method':'Fixed input pose. Active evaluated hand surfaces, same contract/patches. Ideal capped-cylinder triangle-interior query and independent nonadjacent triangle crossing confirmation. DQ is an unsaved modifier-only diagnostic.','variants':[]}
mods={o.name:next(m for m in o.modifiers if m.type=='ARMATURE') for o in [glove,body]};prior={n:m.use_deform_preserve_volume for n,m in mods.items()}
for mode in ['linear','dq']:
    for m in mods.values():m.use_deform_preserve_volume=mode=='dq'
    for ob in [glove,body]:
        q,tris=data_for(ob);selfcheck=self_audit(q,tris);entry={'mode':mode,'object':ob.name,'evaluated_vertices':len(q),'self_intersections':selfcheck}
        if ob==glove:entry['cylinder']=cylinder_audit(q,tris)
        report['variants'].append(entry);print('VARIANT',mode,ob.name,'self_pairs',selfcheck['confirmed_nonadjacent_transverse_pairs'],'cylinder',entry.get('cylinder',{}).get('max_triangle_depth_mm_interval'),flush=True)
for n,m in mods.items():m.use_deform_preserve_volume=prior[n]
report['source_sha256_after']=hashlib.sha256(source.read_bytes()).hexdigest();assert report['source_sha256_after']==sha;(out/'integrated_geometry_audit.json').write_text(json.dumps(report,indent=2))
