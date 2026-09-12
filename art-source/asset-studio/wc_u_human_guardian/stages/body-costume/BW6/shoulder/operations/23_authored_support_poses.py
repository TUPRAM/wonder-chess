import bpy,sys,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_supported_hinge.blend');h=bpy.data.objects['BW6_R_Cap_SecondaryHinge'];cap=bpy.data.objects['BW6_Pauldron_R_Cap']
for i in [0,1]:h.driver_remove('rotation_euler',i)
c=cap.constraints.new('COPY_LOCATION');c.name='Bounded shoulder strap allowance';c.target=h;c.use_offset=True;c.owner_space='WORLD';c.target_space='WORLD'
poses={1:(0,0,0),25:(0,0,0),49:(0,0,0),56:(-4.031434,-4.837721,0),65:(-8.407407,-10.088888,0),71:(-9.88918,-11.867015,0),73:(-10,-12,0),78:(0,-12,.003),86:(0,-6,0),97:(0,0,0)}
for fr,(x,y,z) in poses.items():
 h.rotation_euler=(math.radians(x),math.radians(y),0);h.location=(0,0,z);h.keyframe_insert('rotation_euler',frame=fr);h.keyframe_insert('location',frame=fr)
action=h.animation_data.action;action.name='BW6_Cap_Authored_Support_97_NOT_GAME_CLIPS'
for layer in action.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:
   for fc in bag.fcurves:
    for key in fc.keyframe_points:key.interpolation='LINEAR'
s['BW6_Relief_Representation']='AUTHORED_97_FRAME_ACTION';s['BW6_LOWERED_SUPPORT_POSE']=json.dumps({'secondary_hinge_degrees':[0,-8,0],'strap_allowance_m':0,'context':'Separately authored lowered reference pose; not automatic generalization of timeline support.'})
h['BW6_method']='Deliberately authored support poses selected using actual cap/coat/lame collision checks; max tested 3mm strap allowance. Interpolation must pass its own sample audit.'
h['BW6_limitation']='Finite 97-frame authoring action only. Existing game clips/torso variation/new poses require their own support calibration or runtime integration decision.'
s.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_shoulder_authored_support.blend'));(R/'records/authored_support_keyposes.json').write_text(json.dumps({'pose_degrees_x_y_and_upward_strap_m':poses,'source_tests':['stable_coat_f73_rigid_probe.json','stable_coat_f78_rigid_probe.json','stable_coat_f86_rigid_probe.json','stable_coat_lowered_rigid_probe.json'],'scope':'Explicit candidate authoring poses; no runtime or physics-simulation claim.'},indent=2))
