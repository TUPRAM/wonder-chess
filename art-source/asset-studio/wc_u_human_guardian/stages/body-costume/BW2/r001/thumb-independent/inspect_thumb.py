import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Matrix
import numpy as np
out=Path(__file__).parent;source=out.parent/'grip_correction1_input.blend';s=bpy.context.scene;r=bpy.data.objects['BW1_Temporary_Pose_Rig'];g=bpy.data.objects['BW1_Glove_Pair_SourceFit'];rec=json.loads(s['BW2_hand_contract']);Fi=Matrix(rec['frame_world']).inverted();C=np.array(rec['handle_center_hand_m']);axis=np.array(rec['handle_axis_hand']);R=rec['radius_m'];half=rec['endpoint_span_m']/2
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ge=g.evaluated_get(dg);raw=np.empty(len(ge.data.vertices)*3);ge.data.vertices.foreach_get('co',raw);raw=raw.reshape(-1,3);GW=np.array(Fi@ge.matrix_world);q=raw@GW[:3,:3].T+GW[:3,3]-C;ax=q@axis;rad=q-np.outer(ax,axis);gap=np.linalg.norm(rad,axis=1)-R
centroids={};patches={}
for d in ['1','2','3','4','5']:
    ids=rec['patches'][d]['indices'];rc=rad[ids].mean(axis=0);centroids[d]=(rc/np.linalg.norm(rc)).tolist();patches[d]={'indices':ids,'gaps_mm':(gap[ids]*1000).tolist(),'axial_mm':(ax[ids]*1000).tolist(),'radial_centroid_direction':centroids[d]}
report={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'current_thumb_scene_record':json.loads(s['BW2_thumb_correction1_cap_checked']),'contract':rec,'digit_patches':patches,'thumb_middle_radial_direction_dot':float(np.dot(centroids['1'],centroids['3'])),'thumb_euler_deg':{f'finger1-{j}.R':[math.degrees(v) for v in r.pose.bones[f'finger1-{j}.R'].rotation_euler] for j in [1,2,3]},'cameras':[o.name for o in s.objects if o.type=='CAMERA']}
(out/'initial_thumb_inspection.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
