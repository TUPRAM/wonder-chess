import bpy,bmesh,json,math
from mathutils.kdtree import KDTree
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-closure/ACB1'
assert bpy.data.filepath.replace('\\','/')==ROOT+'/ada_closure_work.blend'
oldscene=bpy.context.scene;src=bpy.context.view_layer.objects.active
assert src.type=='MESH' and len(src.data.vertices)==1670
assert len(src.modifiers)==1 and src.modifiers[0].type=='SUBSURF' and src.modifiers[0].levels==2
assert bpy.data.scenes.get('ACB1_HEAD') is None
scene=bpy.data.scenes.new('ACB1_HEAD');scene.world=oldscene.world
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
for o in oldscene.objects:
    if o.type in ['CAMERA','LIGHT'] or o.name in ['HP1_HEAD_POLISH_Eye_R','HP1_HEAD_POLISH_Eye_L']:
        c=o.copy();c.data=o.data.copy();c.name=o.name.replace('HP1_HEAD_POLISH','ACB1');scene.collection.objects.link(c)
baseline=src.copy();baseline.data=src.data.copy();baseline.name='ACB1_HEAD_BASELINE';scene.collection.objects.link(baseline);baseline.hide_render=True
dg=bpy.context.evaluated_depsgraph_get();ev=src.evaluated_get(dg)
mesh=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg)
target=bpy.data.objects.new('ACB1_FORM_TARGET',mesh);scene.collection.objects.link(target)
for p in mesh.polygons:p.use_smooth=True
# Masks protect actual boundary collars, nasal vault backs and unrelated skin.
bm=bmesh.new();bm.from_mesh(mesh);boundary=[v for v in bm.verts if v.is_boundary]
kd=KDTree(len(boundary))
for i,v in enumerate(boundary):kd.insert(v.co,i)
kd.balance();mask=mesh.attributes.new('.sculpt_mask','FLOAT','POINT')
openings=mesh.attributes.new('ACB1_protected_opening_collar','FLOAT','POINT')
active=[]
for v in mesh.vertices:
    p=v.co
    eye=((p.x-.029)/.033)**2+((p.z-1.689)/.027)**2
    cheek=((p.x-.033)/.032)**2+((p.z-1.667)/.026)**2
    muzzle=((p.x-.008)/.024)**2+((p.z-1.646)/.018)**2
    d=min(eye,cheek,muzzle)
    weight=max(0,min(1,(1.1-d)/.35)) if p.x>=-.0002 and p.y>.036 and v.normal.y>.12 else 0
    dist=kd.find(p)[2];protect=max(0,min(1,(.0025-dist)/.0012))
    weight*=1-protect;mask.data[v.index].value=1-weight;openings.data[v.index].value=protect
    if weight>.01:active.append(v.index)
bm.free()
target['role']='Disposable evaluated sculpt target, no extra subdivision; local right region + transition apron; protected openings.'
target['sculpt_target_status']='UNEDITED_EVALUATED_BASELINE'
target['mask_unlocked_vertices']=len(active)
origin=target.copy();origin.data=target.data.copy();origin.name='ACB1_SCULPT_ORIGIN';scene.collection.objects.link(origin);origin.hide_render=True
cage=baseline.copy();cage.data=baseline.data.copy();cage.name='ACB1_HEAD_CAGE';scene.collection.objects.link(cage);cage.hide_render=True;cage['role']='INPUT_CAGE_PENDING_RECONSTRUCTION, not new topology evidence'
scene['baseline_source']='Frozen HP1 r016 SHA256 775815688dc4aa30dce7085b78ef79bf9ff89f603f243af9110d8ef7b8d00b6b'
scene['render_allowlist']=json.dumps([o.name for o in scene.objects if not o.hide_render])
bpy.context.window.scene=scene;baseline.hide_set(True);cage.hide_set(True);origin.hide_set(True)
bpy.ops.object.select_all(action='DESELECT');target.select_set(True);bpy.context.view_layer.objects.active=target
scene.camera=bpy.data.objects['ACB1_front']
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        sp=area.spaces.active;sp.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion();sp.region_3d.view_location=(.015,.04,1.672);sp.region_3d.view_distance=.25;sp.region_3d.view_perspective='ORTHO'
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/ada_closure_work.blend')
bpy.ops.object.mode_set(mode='SCULPT')
print('ACB1_SETUP '+json.dumps({'source':src.name,'target_vertices':len(mesh.vertices),'target_faces':len(mesh.polygons),'unlocked_target_vertices':len(active),'brush':bpy.context.tool_settings.sculpt.brush.name if bpy.context.tool_settings.sculpt.brush else None,'target_modifiers':len(target.modifiers)}))
