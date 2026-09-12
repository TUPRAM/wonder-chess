import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_shared_lame_support.blend');bas=json.loads((R/'records/initial_construction.json').read_text())['basis'];axis=Vector(bas['axis']);front=Vector(bas['front']);out=Vector(bas['out']);o=bpy.data.objects['BW6_Pauldron_R_Lame2'];changes=[]
for i,(u,rw,rv,oldend,newend) in enumerate([(.139,.081,.087,64,62),(.149,.082,.085,64,54),(.170,.078,.081,66,46),(.191,.073,.076,66,46)]):
 for j in range(9,13):
  old=o.data.vertices[i*13+j].co.copy();w=((j-8)/4)**2;theta=math.radians((j/12*2-1)*oldend-(oldend-newend)*w);new=axis*u+front*(rv*math.sin(theta)*.96)+out*(rw*math.cos(theta));o.data.vertices[i*13+j].co=new;changes.append({'vertex':i*13+j,'before':list(old),'after':list(new)})
o.data.update();o['BW6_local_reconstruction']='Anterior return recut after shared suspension exposed front-corner sleeve crossings at 71-73. Retains crest, rear silhouette, proximal attachment and rigid motion; progressively shortens distal front quarter.'
s['BW6_SHOULDER_STATUS']='SHARED_SUPPORT_LOCAL_RETURN_PENDING_REVIEW';p=R/'ada_bw6_shoulder_shared_support_recut.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p));(R/'records/shared_support_front_return_recut.json').write_text(json.dumps({'changes':changes,'diagnosis':'shared_lame_first_conflict_local.json; nearest cage rows1-3 columns11-12'},indent=2))
