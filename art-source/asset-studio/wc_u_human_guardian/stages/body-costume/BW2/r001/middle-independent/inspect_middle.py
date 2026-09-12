import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
import numpy as np
out=Path(__file__).parent;source=out.parent/'bw2_calibrated_open_handle.blend';s=bpy.context.scene
r=bpy.data.objects['BW1_Temporary_Pose_Rig'];g=bpy.data.objects['BW1_Glove_Pair_SourceFit'];rec=json.loads(s['BW2_hand_contract']);F=Matrix(rec['frame_world']);Fi=F.inverted();C=np.array(rec['handle_center_hand_m']);axis=np.array(rec['handle_axis_hand']);R=rec['radius_m'];half=rec['endpoint_span_m']/2;ids=rec['patches']['3']['indices']
bones=[r.pose.bones[f'finger3-{j}.R'] for j in [1,2,3]]
for b,a in zip(bones,[15.2,59.4,56.8]):b.rotation_mode='XYZ';b.rotation_euler=(math.radians(a),0,0)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ge=g.evaluated_get(dg);me=ge.to_mesh()
raw=np.empty(len(me.vertices)*3);me.vertices.foreach_get('co',raw);raw=raw.reshape(-1,3);GW=np.array(Fi@ge.matrix_world);q=raw@GW[:3,:3].T+GW[:3,3];delta=q-C;ax=delta@axis;rad=np.linalg.norm(delta-np.outer(ax,axis),axis=1)-R;d=np.stack([rad,np.abs(ax)-half],axis=1);sdf=np.minimum(np.max(d,axis=1),0)+np.linalg.norm(np.maximum(d,0),axis=1)
worldmat=np.array(ge.matrix_world);world=raw@worldmat[:3,:3].T+worldmat[:3,3];hand=np.flatnonzero(world[:,0]>.38)
re=r.evaluated_get(dg);jointrecords={}
for pb in re.pose.bones:
    if pb.name.endswith('.R') and any(t in pb.name for t in ('finger','metacarpal','wrist')):
        h=np.array(Fi@(re.matrix_world@pb.head));t=np.array(Fi@(re.matrix_world@pb.tail));jointrecords[pb.name]={'head_hand':h.tolist(),'tail_hand':t.tolist()}
def classify(index):
    point=q[index];best=None
    for n,v in jointrecords.items():
        h=np.array(v['head_hand']);t=np.array(v['tail_hand']);v=t-h;f=float(np.clip(np.dot(point-h,v)/np.dot(v,v),0,1));dist=float(np.linalg.norm(point-(h+v*f)))
        if best is None or dist<best['distance_to_segment_m']:best={'nearest_bone':n,'fraction_along':f,'distance_to_segment_m':dist}
    return {'evaluated_index':int(index),'sdf_mm':float(sdf[index]*1000),'side_gap_mm':float(rad[index]*1000),'axial_m':float(ax[index]),'hand_point_m':q[index].tolist(),**best}
worst=hand[np.argsort(sdf[hand])[:30]]
report={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'contract':rec,'eval_count':len(raw),'expected_eval_count':s.get('BW2_patch_eval_count'),'glove_modifiers':[{'name':m.name,'type':m.type,'levels':getattr(m,'levels',None),'render_levels':getattr(m,'render_levels',None)} for m in g.modifiers],'pose_X_degrees':[15.2,59.4,56.8],'middle_pads':[classify(i) for i in ids],'worst_whole_right_hand_vertices':[classify(i) for i in worst],'joints_hand':jointrecords}
ge.to_mesh_clear();(out/'initial_diagnosis.json').write_text(json.dumps(report,indent=2));print(json.dumps({'eval_count':len(raw),'expected_eval_count':s.get('BW2_patch_eval_count'),'pad':report['middle_pads'],'worst':report['worst_whole_right_hand_vertices'][:8]}),flush=True)
