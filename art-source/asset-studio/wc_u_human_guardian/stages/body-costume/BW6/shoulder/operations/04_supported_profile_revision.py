import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_initial.blend');basis=json.loads((R/'records/initial_construction.json').read_text())['basis'];axis=Vector(basis['axis']);front=Vector(basis['front']);out=Vector(basis['out']);turn=Quaternion(front,math.radians(-20))
cap=bpy.data.objects['BW6_Pauldron_R_Cap'];rows=[(-.065,.092,.105,35),(-.05,.070,.105,40),(-.022,.090,.118,55),(.018,.104,.122,75),(.066,.096,.117,82),(.105,.075,.110,84),(.119,.063,.106,84)]
for i,(u,rw,rv,theta) in enumerate(rows):
 for j in range(13):
  t=(j/12*2-1)*math.radians(theta);v=rv*math.sin(t)*(1.04 if t<0 else .96);w=rw*math.cos(t);cap.data.vertices[i*13+j].co=turn@(axis*u+front*v+out*w)
cap.data.update();cap['revision']='Reconstructed proximal upturned lip and broad crown with ordered profile, compact distal eave. Local panel redesign, no inflated whole sleeve envelope.'
rig=bpy.data.objects['BW4_Armor_Independent_Rig']
for n,base,extra in [('Cap',.42,.54),('Lame1',.70,.28)]:
 h=bpy.data.objects['BW6_Pauldron_R_'+n+'_Suspension'];c=h.constraints['Partial arm roll, rigid plate suspension'];f=c.driver_add('influence');d=f.driver;d.type='SCRIPTED';v=d.variables.new();v.name='raise_z';v.type='TRANSFORMS';t=v.targets[0];t.id=rig;t.bone_target='upperarm01.R';t.transform_type='ROT_Z';t.transform_space='LOCAL_SPACE';t.rotation_mode='XYZ';d.expression=f'{base}+{extra}*min(1,max(0,-raise_z/0.48))';h['BW6_suspension_range']='Support-led lowered pose; transitions to arm-following through negative local-Z authoring raise, bounded .42-.96 cap/.70-.98 first lame. Must audit other actions.'
s.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_shoulder_correction1.blend'))
record={}
for fr in [1,25,49,54,73,97]:
 s.frame_set(fr);bpy.context.view_layer.update();record[fr]={n:bpy.data.objects['BW6_Pauldron_R_'+n+'_Suspension'].constraints['Partial arm roll, rigid plate suspension'].influence for n in ['Cap','Lame1']}
(R/'records/correction1_articulation.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
