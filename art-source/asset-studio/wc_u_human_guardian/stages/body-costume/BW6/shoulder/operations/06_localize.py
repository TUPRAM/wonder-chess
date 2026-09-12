import bpy,sys,json,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
ns=dict(ck.__dict__);exec(ck.__file__ and Path(ck.__file__).read_text().split("if __name__=='__main__':")[0].replace("'examples':out[:10]","'examples':out"),ns)
s=ck.load(R/(sys.argv[-1] if sys.argv[-1].endswith('.blend') else 'ada_bw6_shoulder_correction1.blend'));record=[]
for f,n in [(49,'Cap'),(54,'Cap'),(73,'Lame1')]:
 s.frame_set(f);bpy.context.view_layer.update();o=bpy.data.objects['BW6_Pauldron_R_'+n];r=ns['cross'](ck.geom(o),ck.geom(bpy.data.objects[s.get('BW6_SHOULDER_COAT','BW4_CONTEXT_BW1_CoatUpper_Continuous')]));pts=[Vector(p['point_world_m']) for p in r['examples']];inv=o.matrix_world.inverted();q=np.array([inv@p for p in pts]);base=np.array([v.co for v in o.data.vertices]);near=sorted(set(int(np.argmin(np.linalg.norm(base-p,axis=1))) for p in q));world=np.array(pts)
 item={'frame':f,'object':n,'count':r['count'],'world_bbox':[world.min(0).tolist(),world.max(0).tolist()],'local_bbox':[q.min(0).tolist(),q.max(0).tolist()],'nearest_control_indices':near,'all_points':world.tolist()};record.append(item);print({k:v for k,v in item.items() if k!='all_points'})
(R/'records'/('new_coat_collision_localization.json' if 'BW6_SHOULDER_COAT' in s else 'correction1_collision_localization.json')).write_text(json.dumps(record,indent=2))
