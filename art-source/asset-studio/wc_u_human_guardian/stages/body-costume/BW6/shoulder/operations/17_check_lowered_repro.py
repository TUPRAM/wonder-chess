import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
records=[]
for name in ['ada_bw6_shoulder_checkpoint_ART_REVISE.blend','ada_bw6_shoulder_underlap_candidate.blend']:
 s=ck.load(R/name);ck.lowered(s)
 for n in range(3):
  bpy.context.view_layer.update();cap=bpy.data.objects['BW6_Pauldron_R_Cap'];g=ck.geom(cap);coat=ck.geom(bpy.data.objects[s['BW6_SHOULDER_COAT']]);r={'source':name,'iteration':n,'capcoat':ck.cross(g,coat)['count'],'cap_hash':hashlib.sha256(g[0].tobytes()).hexdigest(),'coat_hash':hashlib.sha256(coat[0].tobytes()).hexdigest(),'influence':cap.parent.constraints['Partial arm roll, rigid plate suspension'].influence,'capmatrix':[list(x) for x in cap.matrix_world]};records.append(r)
print(json.dumps(records,indent=2));(R/'records/lowered_repro_check.json').write_text(json.dumps(records,indent=2))
