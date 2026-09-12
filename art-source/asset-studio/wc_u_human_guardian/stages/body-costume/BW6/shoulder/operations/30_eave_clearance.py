import bpy,sys,json,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_checkpoint_r002_LOCAL_REVIEW.blend');records=[]
for fr in [1,49,73,78,'lowered']:
 if fr=='lowered':ck.lowered(s)
 else:s.frame_set(fr);bpy.context.view_layer.update()
 cap=bpy.data.objects['BW6_Pauldron_R_Cap'];lame=bpy.data.objects['BW6_Pauldron_R_Lame1'];g=ck.geom(lame);base=np.array([lame.matrix_world@v.co for v in lame.data.vertices]);row=[]
 for j in range(13):
  v=cap.data.vertices[78+j];p=cap.matrix_world@v.co;n=(cap.matrix_world.to_3x3()@v.normal).normalized();inner=p-n*.003;hit,normal,tri,distance=g[2].find_nearest(inner);nearest=int(np.argmin(np.linalg.norm(base-np.array(hit),axis=1)));row.append({'cap_eave_column':j,'nearest_lame_cage_row_column':[nearest//13,nearest%13],'distance_mm':distance*1000,'cap_inner_m':list(inner),'lame_nearest_m':list(hit)})
 records.append({'frame':fr,'eave':row});print(fr,[round(x['distance_mm'],1) for x in row])
(R/'records/r002_eave_clearance.json').write_text(json.dumps(records,indent=2))
