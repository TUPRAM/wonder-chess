import bpy,json,math
from mathutils import Matrix,Vector
s=bpy.context.scene;r=bpy.data.objects['BW1_Temporary_Pose_Rig'];g=bpy.data.objects['BW1_Glove_Pair_SourceFit']
rec=json.loads(s['BW2_hand_contract']);Fi=Matrix(rec['frame_world']).inverted();axis=Vector(rec['handle_axis_hand']);C=Vector(rec['handle_center_hand_m']);R=rec['radius_m'];half=rec['endpoint_span_m']*.5
bones=[r.pose.bones['finger1-'+str(j)+'.R'] for j in [1,2,3]]
padids=rec['patches']['1']['indices']
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ge=g.evaluated_get(dg);GW=Fi@ge.matrix_world
handids=[v.index for v in ge.data.vertices if (ge.matrix_world@v.co).x>.38]
def evaluate(params):
    bones[0].rotation_euler=(math.radians(params[0]),math.radians(params[1]),math.radians(params[2]))
    bones[1].rotation_euler=(math.radians(params[3]),0,0)
    bones[2].rotation_euler=(math.radians(params[4]),0,math.radians(params[5]))
    bpy.context.view_layer.update();ge=g.evaluated_get(dg)
    pad=[];coords=[];worst=0
    for i in handids:
        q=GW@ge.data.vertices[i].co-C;ax=q.dot(axis);rad=(q-axis*ax).length-R;sd=max(rad,abs(ax)-half)
        worst=min(worst,sd*1000)
        if i in padids:pad.append(rad*1000);coords.append(q)
    center=sum(coords,Vector())/len(coords)
    err=sum((v-.3)**2 for v in pad)/len(pad)+45*max(0,-worst-.35)**2
    # Thumb should meet the proximal side of the cylinder, opposing distal fingers.
    perp=Vector((-axis.y,axis.x,0))
    err+=2*max(0,center.dot(perp)*1000+3)**2
    err+=60*sum(max(0,abs(q.dot(axis))-(half-.002))**2*1e6 for q in coords)/len(coords)
    err+=40*sum(max(0,-v-.35)**2 for v in pad)/len(pad)
    return err,pad,worst,list(center)
bounds=[(-15,80),(-85,85),(-70,40),(-10,85),(-10,80),(-20,20)]
starts=[]
for bx in [0,30,60]:
    for by in [-60,0,60]:
        for bz in [-40,0]:
            trial=[bx,by,bz,20,20,0];result=evaluate(trial);starts.append((result[0],trial))
starts.sort()
best_overall=None;evalcount=len(starts)
for initial_error,initial in starts[:3]:
    best=initial[:];score,pad,worst,position=evaluate(best)
    for step in [12,5,2,.6]:
        for sweep in range(6):
            improved=False
            for j in range(6):
                for sign in [-1,1]:
                    trial=best[:];trial[j]=max(bounds[j][0],min(bounds[j][1],trial[j]+sign*step))
                    result=evaluate(trial);evalcount+=1
                    if result[0]<score:
                        best=trial;score,pad,worst,position=result;improved=True
            if not improved:break
    if best_overall is None or score<best_overall[0]:best_overall=(score,best[:],pad[:],worst,position[:])
score,best,pad,worst,position=best_overall
evaluate(best)
s['BW2_thumb_correction1_cap_checked']=json.dumps({'params_deg':best,'mapping':['CMC_X','CMC_Y','CMC_Z','MCP_X','IP_X','IP_Z'],'pad_gaps_mm':pad,'whole_hand_min_sdf_mm':worst,'centroid_relative_handle':position,'evaluations':evalcount,'objective':score,'method':'bounded base opposition/axial-rotation search; fixed handle and all original pad samples retained'})
for nm in ['palm','oblique','axial']:
    s.camera=bpy.data.objects['BW2_cam_'+nm];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/captures/grip_correction1_cap_checked_'+nm+'.png';bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['BW2_cam_oblique']
print(s['BW2_thumb_correction1_cap_checked'])
