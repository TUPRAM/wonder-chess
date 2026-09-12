import bpy,sys,json,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
ns=dict(ck.__dict__);exec(Path(ck.__file__).read_text().split("if __name__=='__main__':")[0].replace("'examples':out[:10]","'examples':out"),ns)
s=ck.load(R/'ada_bw6_shoulder_checkpoint_ART_REVISE.blend');cap=bpy.data.objects['BW6_Pauldron_R_Cap'];coat=bpy.data.objects[s['BW6_SHOULDER_COAT']];records=[]
for fr in [56,60,65,73,80]:
 s.frame_set(fr);bpy.context.view_layer.update();pairs=ns['cross'](ck.geom(cap),ck.geom(coat));pts=[Vector(p['point_world_m']) for p in pairs['examples']]
 if not pts:continue
 inv=cap.matrix_world.inverted();base=np.array([v.co for v in cap.data.vertices]);q=np.array([inv@p for p in pts]);world=np.array(pts);near=sorted(set(int(np.argmin(np.linalg.norm(base-p,axis=1))) for p in q));record={'frame':fr,'count':len(pts),'nearest_cage_indices':near,'cage_rows_and_columns':sorted(set((i//13,i%13) for i in near)),'local_bounds':[q.min(0).tolist(),q.max(0).tolist()],'world_bounds':[world.min(0).tolist(),world.max(0).tolist()],'cap_matrix_world':[list(x) for x in cap.matrix_world],'cap_influence':cap.parent.constraints['Partial arm roll, rigid plate suspension'].influence,'all_crossing_points':world.tolist()};records.append(record)
(R/'records/retained_cap_local_failure.json').write_text(json.dumps(records,indent=2));print(json.dumps([{k:v for k,v in r.items() if k not in ['all_crossing_points','cap_matrix_world']} for r in records],indent=2))
for fr in [56,73]:
 s=ck.load(R/'ada_bw6_shoulder_checkpoint_ART_REVISE.blend');ck.render(s,f'retained_failure_f{fr}','rear_three_quarter',fr)
