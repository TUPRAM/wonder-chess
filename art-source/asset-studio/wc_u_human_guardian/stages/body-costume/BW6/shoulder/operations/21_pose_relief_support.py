import bpy,sys,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_underlap_fitted.blend');rig=bpy.data.objects['BW4_Armor_Independent_Rig'];cap=bpy.data.objects['BW6_Pauldron_R_Cap'];col=bpy.data.collections['BW6_SHOULDER_SUPPORTED_PANELS_AUTHORING_ONLY']
h=bpy.data.objects.new('BW6_R_Cap_SecondaryHinge',None);col.objects.link(h);h.rotation_mode='ZYX';h.empty_display_type='ARROWS';h.empty_display_size=.06
for index in [0,1]:
 d=h.driver_add('rotation_euler',index).driver;d.type='SCRIPTED'
 for name,channel in [('rx','ROT_X'),('rz','ROT_Z')]:
  v=d.variables.new();v.name=name;v.type='TRANSFORMS';t=v.targets[0];t.id=rig;t.bone_target='upperarm01.R';t.transform_type=channel;t.transform_space='LOCAL_SPACE';t.rotation_mode='XYZ'
 forward='min(1,max(0,(rx-0.34906585)/0.43633231))';lowered='min(1,max(0,rz/0.55850536))'
 d.expression=f'-0.17453293*({forward})' if index==0 else f'-0.20943951*({forward})-0.13962634*({lowered})'
c=cap.constraints.new('COPY_ROTATION');c.name='Secondary rigid hinge before supported cap rotation';c.target=h;c.mix_mode='BEFORE';c.owner_space='WORLD';c.target_space='WORLD'
h['BW6_method']='Collision-tested secondary rigid hinge about cap strap pivot: forward raise ramps posterior relief to -10deg X/-12deg Y; lowered pose to -8deg Y. No positional slack or mesh deformation.'
h['BW6_limitation']='World-aligned hinge axes calibrated to this unchanged torso orientation and exact 97-frame authoring diagnostic. Torso rotation/general rig/game-animation compatibility remains unverified.'
names=json.loads(s['BW6_SHOULDER_HELPERS']);names.append(h.name);s['BW6_SHOULDER_HELPERS']=json.dumps(names);s['BW6_SHOULDER_STATUS']='SECONDARY_HINGE_PENDING_REVIEW';bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_shoulder_supported_hinge.blend'))
record={}
for fr in [1,49,56,65,71,73,97]:
 s.frame_set(fr);bpy.context.view_layer.update();record[str(fr)]=[math.degrees(a) for a in h.rotation_euler]
ck.lowered(s);record['lowered']=[math.degrees(a) for a in h.rotation_euler];(R/'records/secondary_hinge_channels.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
