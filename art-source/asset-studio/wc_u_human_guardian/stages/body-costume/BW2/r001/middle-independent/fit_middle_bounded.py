import bpy,json,hashlib,math,time
import numpy as np
from pathlib import Path
from mathutils import Matrix
out=Path(__file__).parent;source=out.parent/'bw2_calibrated_open_handle.blend';sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha=='983311ca1c50a44779982b455ca17c2d3db346950a90d59c82b177f9aaeed3f4'
s=bpy.context.scene;r=bpy.data.objects['BW1_Temporary_Pose_Rig'];g=bpy.data.objects['BW1_Glove_Pair_SourceFit'];rec=json.loads(s['BW2_hand_contract']);contract_before=s['BW2_hand_contract'];F=Matrix(rec['frame_world']);Fi=F.inverted();axis=np.array(rec['handle_axis_hand']);C=np.array(rec['handle_center_hand_m']);R=rec['radius_m'];half=rec['endpoint_span_m']/2;usable=rec['usable_length_m']/2
bones=[r.pose.bones[f'finger3-{j}.R'] for j in [1,2,3]];prior=[b.matrix_basis.copy() for b in bones];handle=bpy.data.objects['BW2_Locked_Handle_28mm'];handle_before=handle.matrix_world.copy();ids=np.array(rec['patches']['3']['indices']);count=0;trace=[];best_feasible=None
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ge=g.evaluated_get(dg);GW=np.array(Fi@ge.matrix_world);WM=np.array(ge.matrix_world);lengths=[b.bone.length for b in bones]
raw=np.empty(len(ge.data.vertices)*3,dtype=np.float64);ge.data.vertices.foreach_get('co',raw);raw=raw.reshape(-1,3);hand=np.flatnonzero((raw@WM[:3,:3].T+WM[:3,3])[:,0]>.38)
def apply(p):
    for i,b in enumerate(bones):b.rotation_mode='XYZ';b.rotation_euler=(math.radians(p[i]),0,math.radians(p[3]) if i==0 else 0)
    bpy.context.view_layer.update()
def evaluate(p,keep=True):
    global count,best_feasible
    p=np.clip(p,[0,0,0,-10],[95,115,100,10]);apply(p);ge=g.evaluated_get(dg);raw=np.empty(len(ge.data.vertices)*3,dtype=np.float64);ge.data.vertices.foreach_get('co',raw);raw=raw.reshape(-1,3);assert len(raw)==s['BW2_patch_eval_count']==9130
    q=raw@GW[:3,:3].T+GW[:3,3];delta=q-C;ax=delta@axis;rad=np.linalg.norm(delta-np.outer(ax,axis),axis=1)-R;d=np.stack([rad,np.abs(ax)-half],axis=1);sd=np.minimum(np.max(d,axis=1),0)+np.linalg.norm(np.maximum(d,0),axis=1)
    pad=rad[ids]*1000;worstid=int(hand[np.argmin(sd[hand])]);worst=float(sd[worstid]*1000);pg=np.abs(ax[ids])<usable;contacts=(pad>=-.5)&(pad<=1)&pg
    score=float(np.mean((pad-.25)**2)+1000*max(0,-worst-.45)**2+1000*np.mean(np.maximum(np.abs(ax[ids])-usable,0)*1000)**2)
    data={'angles_X_deg':p[:3].tolist(),'root_Z_abduction_deg':float(p[3]),'score':score,'pad_gaps_mm':pad.tolist(),'pad_min_mm':float(min(pad)),'pad_max_mm':float(max(pad)),'pad_median_mm':float(np.median(pad)),'pad_p95_mm':float(np.percentile(pad,95)),'contacts_in_declared_band':int(sum(contacts)),'pad_count':len(ids),'all_pads_within_usable_span':bool(pg.all()),'whole_right_hand_vertex_min_sdf_mm':worst,'worst_evaluated_vertex':worstid,'worst_hand_point_m':q[worstid].tolist()}
    count+=1
    if keep:
        trace.append({'n':count,**data})
        if worst>=-.5 and (best_feasible is None or score<best_feasible['score']):best_feasible=data.copy()
    return score,data
def nelder(seed,steps,maxiter):
    points=[np.array(seed,dtype=float)]
    for i,step in enumerate(steps):q=np.array(seed,dtype=float);q[i]+=step;points.append(q)
    values=[evaluate(p)[0] for p in points]
    for iteration in range(maxiter):
        order=np.argsort(values);points=[points[i] for i in order];values=[values[i] for i in order]
        if max(np.linalg.norm(p-points[0]) for p in points)<.015:break
        centroid=np.mean(points[:-1],axis=0);ref=centroid+(centroid-points[-1]);rf=evaluate(ref)[0]
        if rf<values[0]:
            ex=centroid+2*(ref-centroid);ef=evaluate(ex)[0]
            points[-1],values[-1]=(ex,ef) if ef<rf else (ref,rf)
        elif rf<values[-2]:points[-1],values[-1]=ref,rf
        else:
            co=centroid+.5*((ref if rf<values[-1] else points[-1])-centroid);cf=evaluate(co)[0]
            if cf<min(rf,values[-1]):points[-1],values[-1]=co,cf
            else:
                for i in range(1,len(points)):points[i]=points[0]+.5*(points[i]-points[0]);values[i]=evaluate(points[i])[0]
    index=int(np.argmin(values));return evaluate(points[index])[1],iteration+1
initial=evaluate([15.2,59.4,56.8,0])[1];print('INITIAL',json.dumps(initial),flush=True)
attempts=[]
for seed,steps in [([15.2,59.4,56.8,0],[8,8,8,3]),([35,65,25,0],[8,8,8,3])]:
    result,it=nelder(seed,steps,260);attempts.append({'seed':seed,'iterations':it,'best':result});print('ATTEMPT',len(attempts),json.dumps(result),flush=True)
best=best_feasible or min((a['best'] for a in attempts),key=lambda a:a['score']);p=best['angles_X_deg']+[best['root_Z_abduction_deg']];evaluate(p,False)
assert s['BW2_hand_contract']==contract_before
assert max(abs(handle.matrix_world[i][j]-handle_before[i][j]) for i in range(4) for j in range(4))<1e-7
assert lengths==[b.bone.length for b in bones]
report={'source':str(source),'source_sha256':sha,'constraints':{'owned_bones':[b.name for b in bones],'all_X_nonnegative':True,'X_bounds_degrees':[[0,95],[0,115],[0,100]],'root_Z_bound_degrees':[-10,10],'no_other_rotations':True,'handle_unchanged':True,'patch_indices_unchanged':ids.tolist(),'no_skin_weight_or_length_edits':True,'save_blend':False},'initial':initial,'attempts':attempts,'best_feasible':best,'evaluations':count,'trace':trace,'limits':'Vertex-distance fit only; triangle interiors and visible geometry must also be reviewed. No grip acceptance.'}
(out/'bounded_fit.json').write_text(json.dumps(report,indent=2))
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.view_settings.view_transform='Standard'
for label,params in [('initial',[15.2,59.4,56.8,0]),('best',p)]:
    apply(params)
    for view in ['palm','side','oblique']:
        s.camera=bpy.data.objects['BW2_cam_'+view];s.render.filepath=str(out/(label+'_'+view+'.png'));bpy.ops.render.render(write_still=True)
for b,m in zip(bones,prior):b.matrix_basis=m
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
print('DONE',json.dumps(best),flush=True)
