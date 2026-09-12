import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_correction2.blend');rig=bpy.data.objects['BW4_Armor_Independent_Rig'];h=bpy.data.objects['BW6_Pauldron_R_Cap_Suspension'];d=h.animation_data.drivers[0].driver
v=d.variables.new();v.name='raise_x';v.type='TRANSFORMS';t=v.targets[0];t.id=rig;t.bone_target='upperarm01.R';t.transform_type='ROT_X';t.transform_space='LOCAL_SPACE';t.rotation_mode='XYZ'
d.expression='.42+.54*min(1,max(0,max(-raise_z,.75*abs(raise_x))/.48))';h['BW6_axis_completion']='Both observed sideways and forward raises drive the same bounded strap suspension. This is finite authoring support, not collision response.'
basis=json.loads((R/'records/initial_construction.json').read_text())['basis'];axis=Vector(basis['axis']);front=Vector(basis['front']);out=Vector(basis['out']);o=bpy.data.objects['BW6_Pauldron_R_Lame1']
for i in [0,1]:
 for j in range(13):
  t=(j/12*2-1)*math.radians(70 if i==0 else 71)
  o.data.vertices[i*13+j].co-=out*(.008*math.cos(t))
o.data.update();o['BW6_underlap']='Proximal two rows 8mm deeper at crest, tapering by section angle, to fit 3mm cap and 3mm lame shells without their former 2mm-only space; distal surface preserved.'
s.frame_set(1);bpy.context.view_layer.update();s['BW6_SHOULDER_STATUS']='LOCAL_CORRECTED_PENDING_REVIEW';bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_shoulder_work.blend'))
