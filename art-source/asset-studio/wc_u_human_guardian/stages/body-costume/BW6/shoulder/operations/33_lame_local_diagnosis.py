import bpy,sys,json,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_shared_lame_support.blend');s.frame_set(73);bpy.context.view_layer.update();o=bpy.data.objects['BW6_Pauldron_R_Lame2'];coat=bpy.data.objects[s['BW6_SHOULDER_COAT']];g=ck.geom(o);c=ck.geom(coat);base=np.array([o.matrix_world@v.co for v in o.data.vertices]);r=ck.cross(g,c);data=[]
for pair in g[2].overlap(c[2]):
 a,b=pair;aa=g[0][list(g[1][a])];bb=c[0][list(c[1][b])];points=[]
 for one,two in [(aa,bb),(bb,aa)]:
  for i in range(3):
   point=ck.segment_triangle(one[i],one[(i+1)%3],two)
   if point is not None:points.append(point)
 if points:
  p=np.mean(points,axis=0);index=int(np.argmin(np.linalg.norm(base-p,axis=1)));data.append({'near_cage':[index//13,index%13],'point':p.tolist()})
from collections import Counter
print('NEAREST_CAGE',Counter(tuple(x['near_cage']) for x in data));(R/'records/shared_lame_first_conflict_local.json').write_text(json.dumps(data,indent=2))
