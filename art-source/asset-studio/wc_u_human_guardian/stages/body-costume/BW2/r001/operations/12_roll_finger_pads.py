import bpy,json,math
from mathutils import Matrix,Vector
s=bpy.context.scene;r=bpy.data.objects['BW1_Temporary_Pose_Rig'];g=bpy.data.objects['BW1_Glove_Pair_SourceFit']
rec=json.loads(s['BW2_hand_contract']);Fi=Matrix(rec['frame_world']).inverted();axis=Vector(rec['handle_axis_hand']);C=Vector(rec['handle_center_hand_m']);R=rec['radius_m'];half=rec['endpoint_span_m']*.5;usable=half-.002
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ge=g.evaluated_get(dg);GW=Fi@ge.matrix_world
handids=[v.index for v in ge.data.vertices if (ge.matrix_world@v.co).x>.38]
bounds=[(0,95),(0,115),(0,100),(-10,10)]
def clamp(p):return [max(b[0],min(b[1],v)) for b,v in zip(bounds,p)]
def evaluate(p):
    p=clamp(p)
    for j,b in enumerate(bones):b.rotation_euler=(math.radians(p[j]),0,math.radians(p[3]) if j==0 else 0)
    bpy.context.view_layer.update();ge=g.evaluated_get(dg)
    pad=[];axials=[];worst=0
    for i in handids:
        q=GW@ge.data.vertices[i].co-C;ax=q.dot(axis);rad=(q-axis*ax).length-R;sd=max(rad,abs(ax)-half)
        worst=min(worst,sd*1000)
        if i in padids:pad.append(rad*1000);axials.append(ax)
    score=sum((v-.25)**2 for v in pad)/len(pad)+1000*max(0,-worst-.45)**2+1000*sum(max(0,abs(a)-usable)**2*1e6 for a in axials)/len(pad)
    return score,{'params_deg':p,'pad_gaps_mm':pad,'min_vertex_sdf_mm':worst,'contacts':sum(-.5<=v<=1 and abs(a)<=usable for v,a in zip(pad,axials)),'count':len(pad),'max_abs_axial_m':max(abs(a) for a in axials)}
def rank(item):return item[0][0]
def nelder(seed):
    points=[clamp(seed)]
    for i,step in enumerate([8,8,8,3]):
        q=seed[:];q[i]+=step;points.append(clamp(q))
    values=[evaluate(p) for p in points]
    for iteration in range(180):
        pairs=sorted(zip(values,points),key=rank);values=[v for v,p in pairs];points=[p for v,p in pairs]
        centroid=[sum(p[j] for p in points[:-1])/4 for j in range(4)]
        ref=clamp([2*c-p for c,p in zip(centroid,points[-1])]);rf=evaluate(ref)
        if rf[0]<values[0][0]:
            ex=clamp([c+2*(v-c) for c,v in zip(centroid,ref)]);ef=evaluate(ex)
            points[-1],values[-1]=(ex,ef) if ef[0]<rf[0] else (ref,rf)
        elif rf[0]<values[-2][0]:points[-1],values[-1]=ref,rf
        else:
            co=clamp([c+.5*(v-c) for c,v in zip(centroid,ref if rf[0]<values[-1][0] else points[-1])]);cf=evaluate(co)
            if cf[0]<min(rf[0],values[-1][0]):points[-1],values[-1]=co,cf
            else:
                for i in range(1,5):points[i]=clamp([(a+b)*.5 for a,b in zip(points[0],points[i])]);values[i]=evaluate(points[i])
    pairs=sorted(zip(values,points),key=rank)
    return pairs[0]
results={}
for digit,seeds in [(4,[[8.5,63.5,41.7,0],[32,45,50,8]]),(5,[[1,53,26,0],[25,40,45,8]])]:
    bones=[r.pose.bones['finger'+str(digit)+'-'+str(j)+'.R'] for j in [1,2,3]];padids=rec['patches'][str(digit)]['indices']
    candidates=[nelder(seed) for seed in seeds];candidates.sort(key=rank)
    value,params=candidates[0];value=evaluate(params);results[str(digit)]=value[1]
s['BW2_ring_little_correction1']=json.dumps(results)
for nm in ['palm','oblique','side','axial']:
    s.camera=bpy.data.objects['BW2_cam_'+nm];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/captures/finger_correction1_'+nm+'.png';bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['BW2_cam_oblique']
print(json.dumps(results))
