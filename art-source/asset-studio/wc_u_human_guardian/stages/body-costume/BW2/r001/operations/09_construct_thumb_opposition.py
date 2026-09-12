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
    return err,pad,worst,list(center)
best=[35.,0.,-15.,25.,25.,0.]
bounds=[(-15,75),(-30,30),(-65,25),(-10,85),(-10,80),(-25,25)]
score,pad,worst,position=evaluate(best);count=1
for step in [15,7,3,1,.3]:
    for sweep in range(7):
        improved=False
        for j in range(6):
            for sign in [-1,1]:
                trial=best[:];trial[j]=max(bounds[j][0],min(bounds[j][1],trial[j]+sign*step))
                result=evaluate(trial);count+=1
                if result[0]<score:
                    best=trial;score,pad,worst,position=result;improved=True
        if not improved:break
score,pad,worst,position=evaluate(best)
s['BW2_thumb_construction']=json.dumps({'params_deg':best,'mapping':['CMC_X','CMC_Y','CMC_Z','MCP_X','IP_X','IP_Z'],'pad_gaps_mm':pad,'whole_hand_min_sdf_mm':worst,'centroid_relative_handle':position,'evaluations':count,'objective':score})
for nm in ['palm','oblique','side','back','axial']:
    s.camera=bpy.data.objects['BW2_cam_'+nm];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/captures/grip_initial_'+nm+'.png';bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['BW2_cam_oblique']
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/ada_bw2_grip_work.blend')
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/grip_initial_art_review.blend',copy=True)
print(s['BW2_thumb_construction'])

