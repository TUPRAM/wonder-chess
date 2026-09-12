import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
R=Path(__file__).resolve().parents[1];B=R.parents[1];source=B/'BW5/armor/ada_bw5_armor_checkpoint_r003_ART_REVISE.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
rig=bpy.data.objects['BW4_Armor_Independent_Rig'];rig.data=rig.data.copy();oldaction=rig.animation_data.action;oldaction.use_fake_user=True;rig.animation_data_clear();rig.name='BW6_Knee_Independent_Rig'
for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update();knee=rig.matrix_world@rig.pose.bones['lowerleg01.R'].head;rest=(rig.matrix_world@rig.pose.bones['upperleg02.R'].matrix).copy();axis=Vector((-.9968269,.0145336,-.078262)).normalized()
collection=bpy.data.collections.new('BW6_RIGID_KNEE_AUTHORING_ONLY');s.collection.children.link(collection)
owned=[];controls={}
def shell(name,rows):
 u=[-1,-.96,-.72,-.34,-.06,0,.06,.34,.72,.96,1];vs=[];fs=[]
 for z,w,y in rows:
  for a in u:vs.append((-.010+w*a,y-.018*a-.026*a*a+.003*(1-abs(a)),z))
 for r in range(len(rows)-1):
  for j in range(len(u)-1):a=r*len(u)+j;fs.append((a,a+len(u),a+len(u)+1,a+1))
 me=bpy.data.meshes.new(name+'_ControlSurface');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(name,me);collection.objects.link(o);o.color=(.52,.56,.6,1)
 for p in me.polygons:p.use_smooth=True
 md=o.modifiers.new('Controlled broad curvature','SUBSURF');md.levels=1;md.render_levels=1
 md=o.modifiers.new('Rigid plate wall','SOLIDIFY');md.thickness=.0035;md.offset=-1;md.use_even_offset=False
 c=bpy.data.objects.new(name+'_RigidControl',None);collection.objects.link(c);c.empty_display_type='ARROWS';c.empty_display_size=.06;o.parent=c;c.rotation_mode='QUATERNION';controls[name]=c;owned.append(name);return o
cup=shell('BW6_KneeCup_R', [(-.070,.018,.071),(-.065,.036,.075),(-.047,.055,.084),(0,.070,.096),(.045,.060,.101),(.063,.041,.103),(.067,.025,.103)])
upper=shell('BW6_KneeUpperLame_R',[(.045,.055,.109),(.05,.06,.109),(.091,.062,.114),(.098,.059,.114)])
lower=shell('BW6_KneeLowerLame_R',[(-.103,.035,.061),(-.098,.045,.063),(-.063,.054,.080),(-.058,.054,.082)])
replaces=['BW4_CONTEXT_BW1_KneeCup_R_ThighAttachment','BW4_CONTEXT_BW1_KneeCup_ThighStrap_R']
for name in replaces:bpy.data.objects[name].hide_render=True;bpy.data.objects[name].hide_set(True)
# Deliberate local placement samples against measured body/leggings rays. Not a claim of anatomical patella tracking.
table=[(0,0,0,0,0),(30,12,3,20,-.008),(60,25,8,42,-.019),(90,40,14,68,-.031),(120,56,22,94,-.043)]
record={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'knee_world_rest':list(knee),'verified_world_bend_axis':list(axis),'table':table,'samples':{},'owned':owned,'replaces':replaces,'scope':'Authoring-only deliberately placed rigid caps/lames. New 81-frame isolated bend and return, not game animation or BW1 source motion.'}
for f,deg in [(1,0),(11,30),(21,60),(31,90),(41,120),(51,90),(61,60),(71,30),(81,0)]:
 row=next(r for r in table if r[0]==deg);s.frame_set(f)
 for p in rig.pose.bones:p.rotation_mode='XYZ';p.rotation_euler=(0,0,0);p.location=(0,0,0)
 rig.pose.bones['lowerleg01.R'].rotation_euler.x=math.radians(deg)
 for p in rig.pose.bones:p.keyframe_insert('rotation_euler',frame=f,group=p.name)
 for name,ang in zip(owned,row[1:4]):
  q=Quaternion(axis,math.radians(ang));c=controls[name];c.location=knee+q@Vector((0,row[4],0));c.rotation_quaternion=q;c.keyframe_insert('location',frame=f);c.keyframe_insert('rotation_quaternion',frame=f)
 record['samples'][f]={'bend_degrees':deg,'control':{n:{'location':list(controls[n].location),'quaternion':list(controls[n].rotation_quaternion)} for n in owned}}
rig.animation_data.action.name='BW6_Knee_Deliberate_Bend_AUTHORING_ONLY'
for act in bpy.data.actions:
 if act.name.startswith('BW6_'):
  for layer in act.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      for k in fc.keyframe_points:k.interpolation='LINEAR'
for o in s.objects:
 if o.type=='MESH':
  o.hide_render=o.name not in owned+['BW4_CONTEXT_BW1_IndexedBody','BW4_CONTEXT_BW1_Leggings','BW4_CONTEXT_BW1_Boot_Pair_SourceFit','BW4_CONTEXT_BW1_FootprintSole_R','BW4_CONTEXT_BW1_Greave_R','BW4_CONTEXT_BW1_BootVampStrap_R']
  if o.name not in owned:o.color=(.24,.25,.26,1)
s.frame_start=1;s.frame_end=81;s.render.fps=24;s.frame_set(1);s['BW6_knee_owned']=json.dumps(owned);s['BW6_knee_record']=json.dumps(record);s['BW6_knee_status']='AUTHORING_ONLY_ART_REVISE_UNTIL_REVIEW';s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=850;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.display.shading.light='STUDIO';s.display.shading.color_type='OBJECT';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world.color=(.07,.07,.07);s.view_settings.view_transform='Standard'
for view,loc in [('front',(.17,2,.52)),('profile',(2,.05,.50)),('three_quarter',(1.35,1.8,.88))]:
 d=bpy.data.cameras.new('BW6_KneeCamera_'+view);cam=bpy.data.objects.new(d.name,d);collection.objects.link(cam);cam.location=loc;target=Vector((.155,-.03,.47));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=.62
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_knee_initial.blend'))
for f in [1,11,21,31,41]:
 s.frame_set(f)
 for view in ['front','profile','three_quarter']:
  s.camera=bpy.data.objects['BW6_KneeCamera_'+view];s.render.filepath=str(R/'captures'/f'initial_{view}_{f}.png');bpy.ops.render.render(write_still=True)
(R/'records/initial_construction.json').write_text(json.dumps(record,indent=2));print('INITIAL_KNEE_SAVED')
