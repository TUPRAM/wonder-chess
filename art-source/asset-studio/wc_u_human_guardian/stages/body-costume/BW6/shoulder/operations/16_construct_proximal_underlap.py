import bpy,sys,json,math,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_checkpoint_ART_REVISE.blend');basis=json.loads((R/'records/initial_construction.json').read_text())['basis'];axis=Vector(basis['axis']);front=Vector(basis['front']);out=Vector(basis['out']);o=bpy.data.objects['BW6_Pauldron_R_Lame1'];old=o.data;vs=[];faces=[]
rows=[(.045,.089,.098,62),(.065,.090,.099,66),(.083,.090,.101,70),(.092,.091,.099,71),(.119,.096,.093,69),(.150,.091,.087,63)]
for i,(u,rw,rv,theta) in enumerate(rows):
 for j in range(13):
  t=(j/12*2-1)*math.radians(theta);vs.append(tuple(axis*u+front*(rv*math.sin(t)*(1.04 if t<0 else .96))+out*(rw*math.cos(t))))
for i in range(5):
 for j in range(12):a=i*13+j;faces.append((a,a+1,a+14,a+13))
me=bpy.data.meshes.new('BW6_Lame1_ExplicitProximalUnderlap');me.from_pydata(vs,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
if sum(p.normal.dot(out) for p in me.polygons)<0:
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.reverse_faces(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
for mat in old.materials:me.materials.append(mat)
for p in me.polygons:p.use_smooth=True
o.data=me;o['BW6_underlap']='Two new proximal strips extend first lame 38mm under the supported cap. Distal boundary/radius retained; no exterior cap growth or endpoint reattachment.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_shoulder_underlap_candidate.blend'))
