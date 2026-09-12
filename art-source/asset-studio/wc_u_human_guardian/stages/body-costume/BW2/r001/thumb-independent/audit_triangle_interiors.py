import bpy,json,hashlib,math
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
out=Path(__file__).parent;record=json.loads((out/'bounded_thumb_fit.json').read_text());source=Path(record['source']);assert hashlib.sha256(source.read_bytes()).hexdigest()==record['source_sha256']
s=bpy.context.scene;r=bpy.data.objects['BW1_Temporary_Pose_Rig'];g=bpy.data.objects['BW1_Glove_Pair_SourceFit'];rec=json.loads(s['BW2_hand_contract']);Fi=Matrix(rec['frame_world']).inverted();C=np.array(rec['handle_center_hand_m']);axis=np.array(rec['handle_axis_hand']);R=rec['radius_m'];half=rec['endpoint_span_m']/2
U=np.array([0.,0.,1.]);V=np.cross(axis,U);V/=np.linalg.norm(V)
def clip(poly,limit,positive):
    result=[]
    for i,b in enumerate(poly):
        a=poly[i-1];fa=(np.dot(a,axis)-limit)*(1 if positive else -1);fb=(np.dot(b,axis)-limit)*(1 if positive else -1)
        ia=fa<=0;ib=fb<=0
        if ia!=ib:result.append(a+(b-a)*(fa/(fa-fb)))
        if ib:result.append(b)
    return result
def closest_projected(poly):
    xy=np.array([[np.dot(p,U),np.dot(p,V)] for p in poly]);cross=[]
    best=(1e9,None)
    for i,b in enumerate(xy):
        a=xy[i-1];d=b-a;cross.append(a[0]*b[1]-a[1]*b[0]);den=np.dot(d,d);t=float(np.clip(-np.dot(a,d)/den,0,1)) if den>1e-20 else 0.;p=a+t*d;radius=float(np.linalg.norm(p))
        if radius<best[0]:best=(radius,poly[i-1]+t*(poly[i]-poly[i-1]))
    if len(xy)>=3 and (all(c>=-1e-14 for c in cross) or all(c<=1e-14 for c in cross)) and abs(sum(cross))>1e-14:return 0.,None
    return best
def has_depth(tri,depth):
    p=clip(list(tri),half-depth,True)
    if len(p)<2:return False,None,None
    p=clip(p,-half+depth,False)
    if len(p)<2:return False,None,None
    radius,loc=closest_projected(p)
    return radius<R-depth,radius,loc
results=[]
for label,params in [('initial',record['initial']['params_deg']),('best',record['best_feasible']['params_deg'])]:
    r.pose.bones['finger1-1.R'].rotation_euler=tuple(math.radians(v) for v in params[:3]);r.pose.bones['finger1-2.R'].rotation_euler=(math.radians(params[3]),0,0);r.pose.bones['finger1-3.R'].rotation_euler=(math.radians(params[4]),0,math.radians(params[5]))
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ge=g.evaluated_get(dg);me=ge.to_mesh();me.calc_loop_triangles();raw=np.empty(len(me.vertices)*3);me.vertices.foreach_get('co',raw);raw=raw.reshape(-1,3);GW=np.array(Fi@ge.matrix_world);q=raw@GW[:3,:3].T+GW[:3,3]-C;WM=np.array(ge.matrix_world);world=raw@WM[:3,:3].T+WM[:3,3]
    tris=[(ti.index,list(ti.vertices),q[list(ti.vertices)]) for ti in me.loop_triangles if np.max(world[list(ti.vertices),0])>.38]
    candidates=[]
    for index,ids,tri in tris:
        if has_depth(tri,0)[0]:candidates.append((index,ids,tri))
    deep=[]
    for index,ids,tri in candidates:
        hit,rad,point=has_depth(tri,.0005)
        if hit:deep.append({'evaluated_triangle':index,'vertices':ids,'radius_m_at_depth_clip':rad,'point_hand_m':(point+C).tolist() if point is not None else None})
    lo=0.;hi=R;worst=None
    for _ in range(18):
        mid=(lo+hi)/2;found=None
        for index,ids,tri in candidates:
            hit,rad,p=has_depth(tri,mid)
            if hit:found=(index,ids,rad,p);break
        if found:lo=mid;worst=found
        else:hi=mid
    result={'label':label,'triangle_count_right_hand_screened':len(tris),'triangles_intersecting_cylinder_solid':len(candidates),'triangles_penetrating_deeper_than_0_5mm':len(deep),'deep_triangles':deep,'maximum_triangle_penetration_depth_mm_interval':[lo*1000,hi*1000],'worst_triangle':{'index':worst[0],'vertices':worst[1],'point_hand_m':(worst[3]+C).tolist() if worst[3] is not None else None} if worst else None}
    results.append(result);ge.to_mesh_clear();print(json.dumps(result),flush=True)
report={'source_sha256':record['source_sha256'],'method':'Evaluated glove triangles clipped against capped cylinder axial slabs; minimum radial distance of the resulting projected convex polygon. Bisection tests intersection with an inward-offset cylinder, bounding the deepest signed-cylinder penetration over triangle interiors, not only vertices.','numerical_depth_interval_width_m':R/(2**18),'proxy':'Locked ideal circular cylinder radius0.014m, span0.109m. Actual96-sided proxy differs radially by <=0.0075mm.','results':results,'not_tested':'Glove self-intersection, other posed fingers, moving grip, bone length change, skin changes; no changes were made to these.','source_sha256_after':hashlib.sha256(source.read_bytes()).hexdigest()}
assert report['source_sha256_after']==record['source_sha256'];(out/'triangle_interior_audit.json').write_text(json.dumps(report,indent=2))
