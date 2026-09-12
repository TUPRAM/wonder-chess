import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck;from append_bw6_shoulder_r003 import apply_lowered_support_pose
source=R/'ada_bw6_shoulder_r003_combined_review.blend';s=ck.load(source);saved=apply_lowered_support_pose();assert saved is not None;h=bpy.data.objects['BW6_R_Cap_SecondaryHinge'];assert abs(h.rotation_euler.y+__import__('math').radians(8))<1e-6;print('LOWERED_HELPER_OK');s=ck.load(source);records=[];names=json.loads(s['BW6_SHOULDER_ACTIVE'])
for f in list(range(1,98))+['lowered']:
 if f=='lowered':ck.lowered(s)
 else:s.frame_set(f);bpy.context.view_layer.update()
 body=ck.geom(bpy.data.objects['BW6_BodyFit_Candidate']);records.append({'frame':f,'body_crossings':{n:ck.cross(ck.geom(bpy.data.objects[n]),body) for n in names}})
(R/'records/r003_body_and_lowered_helper.json').write_text(json.dumps({'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'helper_verified':True,'frames':records},indent=2));print('BODY_QUERY_DONE')
