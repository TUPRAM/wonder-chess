import bpy,json,hashlib,math
import numpy as np
from pathlib import Path
from mathutils import Matrix
out=Path(__file__).parent;source=out.parent/'grip_correction1_input.blend';sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha=='71abf0c027695c17ff68544f305b49afc3c351b8f1bd7adfc2f641f1c2bc4b36'
s=bpy.context.scene;r=bpy.data.objects['BW1_Temporary_Pose_Rig'];g=bpy.data.objects['BW1_Glove_Pair_SourceFit'];rec=json.loads(s['BW2_hand_contract']);contract_before=s['BW2_hand_contract'];Fi=Matrix(rec['frame_world']).inverted();axis=np.array(rec['handle_axis_hand']);C=np.array(rec['handle_center_hand_m']);R=rec['radius_m'];half=rec['endpoint_span_m']/2;usable=half-.002
bones=[r.pose.bones[f'finger1-{j}.R'] for j in [1,2,3]];prior=[b.matrix_basis.copy() for b in bones];otherposes={p.name:p.matrix_basis.copy() for p in r.pose.bones if p not in bones};handle=bpy.data.objects['BW2_Locked_Handle_28mm'];handle_before=handle.matrix_world.copy();ids=np.array(rec['patches']['1']['indices']);midids=np.array(rec['patches']['3']['indices']);lengths=[b.bone.length for b in bones]
start=json.loads(s['BW2_thumb_correction1_cap_checked'])['params_deg'];count=0;trace=[];best_feasible=None
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ge=g.evaluated_get(dg);GW=np.array(Fi@ge.matrix_world);WM=np.array(ge.matrix_world)
raw=np.empty(len(ge.data.vertices)*3);ge.data.vertices.foreach_get('co',raw);raw=raw.reshape(-1,3);hand=np.flatnonzero((raw@WM[:3,:3].T+WM[:3,3])[:,0]>.38)
lower=np.array([-15,-85,-70,0,0,-20]);upper=np.array([80,85,40,85,80,20])
def apply(p):
    for b in bones:b.rotation_mode='XYZ'
    bones[0].rotation_euler=tuple(math.radians(v) for v in p[:3]);bones[1].rotation_euler=(math.radians(p[3]),0,0);bones[2].rotation_euler=(math.radians(p[4]),0,math.radians(p[5]));bpy.context.view_layer.update()
def evaluate(p,keep=True):
    global count,best_feasible
    p=np.clip(p,lower,upper);apply(p);ge=g.evaluated_get(dg);raw=np.empty(len(ge.data.vertices)*3);ge.data.vertices.foreach_get('co',raw);raw=raw.reshape(-1,3);assert len(raw)==9130
    q=raw@GW[:3,:3].T+GW[:3,3]-C;ax=q@axis;rv=q-np.outer(ax,axis);rad=np.linalg.norm(rv,axis=1)-R;d=np.stack([rad,np.abs(ax)-half],axis=1);sd=np.minimum(np.max(d,axis=1),0)+np.linalg.norm(np.maximum(d,0),axis=1)
    pad=rad[ids]*1000;worstid=int(hand[np.argmin(sd[hand])]);worst=float(sd[worstid]*1000);pg=np.abs(ax[ids])<=usable;contacts=(pad>=-.5)&(pad<=1)&pg
    thumbdir=rv[ids].mean(axis=0);thumbdir/=np.linalg.norm(thumbdir);middir=rv[midids].mean(axis=0);middir/=np.linalg.norm(middir);opposition=float(np.dot(thumbdir,middir));capexcess=np.maximum(np.abs(ax[ids])-usable,0)*1000
    # Preserve broad opposite-half-cylinder placement, not merely radial contact.
    score=float(np.mean((pad-.25)**2)+2000*max(0,-worst-.38)**2+2000*np.mean(capexcess**2)+4000*max(0,opposition+.5)**2)
    data={'params_deg':p.tolist(),'mapping':['CMC_X','CMC_Y','CMC_Z','MCP_X','IP_X','IP_Z'],'score':score,'pad_gaps_mm':pad.tolist(),'pad_axial_mm':(ax[ids]*1000).tolist(),'pad_min_mm':float(min(pad)),'pad_max_mm':float(max(pad)),'pad_median_mm':float(np.median(pad)),'pad_p95_mm':float(np.percentile(pad,95)),'contacts_in_declared_band':int(sum(contacts)),'pad_count':len(ids),'all_pads_within_usable_span':bool(pg.all()),'max_pad_axial_abs_mm':float(max(abs(ax[ids]))*1000),'thumb_middle_radial_dot':opposition,'whole_right_hand_vertex_min_sdf_mm':worst,'worst_evaluated_vertex':worstid,'worst_hand_point_m':(q[worstid]+C).tolist()}
    count+=1
    if keep:
        trace.append({'n':count,**data})
        if worst>=-.4 and pg.all() and opposition<=-.5 and (best_feasible is None or score<best_feasible['score']):best_feasible=data.copy()
    return score,data
def nelder(seed,steps,maxiter):
    points=[np.array(seed,dtype=float)]
    for i,step in enumerate(steps):q=np.array(seed,dtype=float);q[i]+=step;points.append(q)
    values=[evaluate(p)[0] for p in points]
    for iteration in range(maxiter):
        order=np.argsort(values);points=[points[i] for i in order];values=[values[i] for i in order]
        if max(np.linalg.norm(np.clip(p,lower,upper)-np.clip(points[0],lower,upper)) for p in points)<.015:break
        centroid=np.mean(points[:-1],axis=0);ref=centroid+(centroid-points[-1]);rf=evaluate(ref)[0]
        if rf<values[0]:
            ex=centroid+2*(ref-centroid);ef=evaluate(ex)[0];points[-1],values[-1]=(ex,ef) if ef<rf else (ref,rf)
        elif rf<values[-2]:points[-1],values[-1]=ref,rf
        else:
            co=centroid+.5*((ref if rf<values[-1] else points[-1])-centroid);cf=evaluate(co)[0]
            if cf<min(rf,values[-1]):points[-1],values[-1]=co,cf
            else:
                for i in range(1,len(points)):points[i]=points[0]+.5*(points[i]-points[0]);values[i]=evaluate(points[i])[0]
    return evaluate(points[int(np.argmin(values))])[1],iteration+1
initial=evaluate(start)[1];print('INITIAL',json.dumps(initial),flush=True);attempts=[]
for seed,steps in [(start,[6,6,6,8,-8,5]),([30,-50,-5,40,45,0],[6,6,6,8,8,5])]:
    result,it=nelder(seed,steps,340);attempts.append({'seed':seed,'iterations':it,'best':result});print('ATTEMPT',len(attempts),json.dumps(result),flush=True)
best=best_feasible or min((a['best'] for a in attempts),key=lambda a:a['score']);evaluate(best['params_deg'],False)
assert s['BW2_hand_contract']==contract_before
assert max(abs(handle.matrix_world[i][j]-handle_before[i][j]) for i in range(4) for j in range(4))<1e-7
assert lengths==[b.bone.length for b in bones]
assert max(abs(r.pose.bones[n].matrix_basis[i][j]-m[i][j]) for n,m in otherposes.items() for i in range(4) for j in range(4))<1e-7
report={'source':str(source),'source_sha256':sha,'constraints':{'owned_bones':[b.name for b in bones],'bounds':list(zip(lower.tolist(),upper.tolist())),'bounds_basis':'Inherited root guardrails; MCP/IP flexion kept nonnegative. These Euler limits are not a measured biomechanical validation.','handle_unchanged':True,'patch_indices_unchanged':ids.tolist(),'pad_usable_halfspan_mm':usable*1000,'opposition_radial_dot_max':-.5,'no_skin_weight_or_length_edits':True,'no_other_pose_changes':True,'save_blend':False},'initial':initial,'attempts':attempts,'best_feasible':best,'evaluations':count,'trace':trace,'limits':'Vertex-based fit candidate; triangle interiors and visible geometry reviewed separately. No full-grip or human acceptance.'}
(out/'bounded_thumb_fit.json').write_text(json.dumps(report,indent=2))
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.view_settings.view_transform='Standard'
for label,params in [('initial',start),('best',best['params_deg'])]:
    apply(params)
    for view in ['palm','side','oblique','axial']:
        s.camera=bpy.data.objects['BW2_cam_'+view];s.render.filepath=str(out/(label+'_'+view+'.png'));bpy.ops.render.render(write_still=True)
for b,m in zip(bones,prior):b.matrix_basis=m
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
print('DONE',json.dumps(best),flush=True)
