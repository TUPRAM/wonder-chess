import bpy,json,math
from mathutils import Matrix,Vector
s=bpy.context.scene;r=bpy.data.objects['BW1_Temporary_Pose_Rig'];g=bpy.data.objects['BW1_Glove_Pair_SourceFit']
rec=json.loads(s['BW2_hand_contract']);F=Matrix(rec['frame_world']);Fi=F.inverted();axis=Vector(rec['handle_axis_hand']);C=Vector(rec['handle_center_hand_m']);R=rec['radius_m'];half=rec['endpoint_span_m']*.5
digit=2
bones=[r.pose.bones['finger'+str(digit)+'-'+str(j)+'.R'] for j in [1,2,3]]
padids=rec['patches'][str(digit)]['indices']
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
ge=g.evaluated_get(dg);GW=Fi@ge.matrix_world
handids=[v.index for v in ge.data.vertices if (ge.matrix_world@v.co).x>.38]
def evaluate(angles):
    for b,a in zip(bones,angles):b.rotation_euler.x=math.radians(a)
    bpy.context.view_layer.update()
    ge=g.evaluated_get(dg)
    pad=[]
    worst=0
    for i in handids:
        q=GW@ge.data.vertices[i].co-C;ax=q.dot(axis);rad=(q-axis*ax).length-R
        sd=max(rad,abs(ax)-half)
        worst=min(worst,sd*1000)
        if i in padids:pad.append(rad*1000)
    err=sum((v-.3)**2 for v in pad)/len(pad)+35*max(0,-worst-.35)**2
    return err,pad,worst
best=[25.,65.,40.];score,pad,worst=evaluate(best);count=1
for step in [12,6,3,1,.3]:
    for sweep in range(6):
        improved=False
        for j in range(3):
            for sign in [-1,1]:
                trial=best[:];trial[j]=max(0,min([95,115,100][j],trial[j]+sign*step))
                result=evaluate(trial);count+=1
                if result[0]<score:
                    best=trial;score,pad,worst=result;improved=True
        if not improved:break
score,pad,worst=evaluate(best)
s['BW2_index_construction']=json.dumps({'angles':best,'pad_gaps_mm':pad,'whole_hand_min_sdf_mm':worst,'evaluations':count,'objective':score})
s.camera=bpy.data.objects['BW2_cam_oblique'];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/captures/index_fitted_initial.png';bpy.ops.render.render(write_still=True)
print(s['BW2_index_construction'])
