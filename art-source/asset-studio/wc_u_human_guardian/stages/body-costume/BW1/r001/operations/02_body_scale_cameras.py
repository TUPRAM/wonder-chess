import bpy,json,math
from mathutils import Vector
s=bpy.data.scenes['BW1_BODY_COSTUME'];bpy.context.window.scene=s;body=bpy.data.objects['BW1_IndexedBody']
scale=1.82/(1.7992445230484009-0.1285039186477661)*1.05
body.scale=(scale,scale,scale);body.location=(0,-.07,0)
s['body_height_target_m']=1.82;s['fitting_scale']=scale;s['rest_pose']='MPFB native A-pose; measure before local articulation; +Y forward, +X anatomical right'
clay=bpy.data.materials.new('BW1_Uniform_Clay');clay.use_nodes=True;p=clay.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.48,.48,.48,1);p.inputs['Roughness'].default_value=.68
body.data.materials.clear();body.data.materials.append(clay)
for f in body.data.polygons:f.material_index=0;f.use_smooth=True
sub=body.modifiers.new('Study subdivision','SUBSURF');sub.levels=1;sub.render_levels=1
for ob in bpy.data.collections['BW1_CONTEXT_HEAD'].objects:
    ob.data.materials.clear();ob.data.materials.append(clay)
    for f in ob.data.polygons:f.material_index=0
s.world=bpy.data.worlds['MR1_Neutral_World'].copy();s.world.name='BW1_Neutral_World'
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=850;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
for name,pos in [('front',(0,4,.93)),('profile',(4,0,.93)),('back',(0,-4,.93)),('three_quarter',(3.3,4.4,1.45)),('other_three_quarter',(-3.3,4.4,1.45))]:
    data=bpy.data.cameras.new('BW1_Camera_'+name);cam=bpy.data.objects.new('BW1_Camera_'+name,data);bpy.data.collections['BW1_PRESENTATION'].objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector((0,0,.93))-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=2.1
for name,pos,energy,size in [('Key',(-2.4,3.5,3.4),420,3.2),('Fill',(2.8,1.6,2.2),160,2.8),('Rim',(0,-3,2.8),260,2.5)]:
    data=bpy.data.lights.new('BW1_'+name,'AREA');ob=bpy.data.objects.new('BW1_'+name,data);bpy.data.collections['BW1_PRESENTATION'].objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler();data.energy=energy;data.shape='DISK';data.size=size
s.camera=bpy.data.objects['BW1_Camera_front']
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.overlay.show_overlays=False
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get();body.modifiers['BW1 display cut; master indices retained'].show_viewport=False
body.modifiers['Hide helpers'].show_viewport=False;body.modifiers['Study subdivision'].show_viewport=False;dg.update();ev=body.evaluated_get(dg)
landmarks={}
for name in ['joint-r-shoulder','joint-l-shoulder','joint-r-elbow','joint-r-hand','joint-r-finger-3-1','joint-r-finger-2-1','joint-r-finger-5-1','joint-r-upper-leg','joint-r-knee','joint-r-ankle','joint-r-foot-1','joint-r-foot-2','joint-ground','joint-pelvis','joint-spine-2']:
    idx=body.vertex_groups[name].index;vs=[v for v in ev.data.vertices if any(g.group==idx and g.weight>.5 for g in v.groups)]
    co=sum((v.co for v in vs),Vector())/len(vs);landmarks[name]=list(body.matrix_world@co)
body.modifiers['BW1 display cut; master indices retained'].show_viewport=True;body.modifiers['Hide helpers'].show_viewport=True;body.modifiers['Study subdivision'].show_viewport=True;dg.update()
s['body_landmarks_initial']=json.dumps(landmarks)
print(json.dumps({'scale':scale,'landmarks':landmarks},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/body_r000_front.png';bpy.ops.render.render(write_still=True)

