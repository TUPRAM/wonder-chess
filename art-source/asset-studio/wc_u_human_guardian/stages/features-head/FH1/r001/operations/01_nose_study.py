import bpy,bmesh,json
from mathutils import Vector
assert '/features-head/FH1/r001/' in bpy.data.filepath.replace('\\','/')
assert bpy.data.scenes.get('FH1_NOSE_STUDY') is None
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/features-head/FH1/r001'

def fh_mesh(name,data,collection):
    m=bpy.data.meshes.new(name+'_ControlMesh');m.from_pydata(data['vertices'],[],data['faces']);m.update()
    bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
    o=bpy.data.objects.new(name,m);collection.objects.link(o)
    m.materials.append(bpy.data.materials['MR1_Uniform_Clay'])
    for p in m.polygons:p.use_smooth=True
    for name,ids in data.get('named_vertex_groups',{}).items():
        vg=o.vertex_groups.new(name=name);vg.add(ids,1,'REPLACE')
    root=o.vertex_groups.new(name='Matched_Head_Interface');root.add(data['root_loop'],1,'REPLACE')
    sub=o.modifiers.new('Editable cage preview','SUBSURF');sub.levels=2;sub.render_levels=2
    o['construction_notes']=data['design_notes'];o['interface_indices']=json.dumps(data['root_loop'])
    return o

def fh_scene(name,target,scale):
    scene=bpy.data.scenes.new(name);bpy.context.window.scene=scene
    col=bpy.data.collections.new(name+'_EXPLICIT_ALLOWLIST');scene.collection.children.link(col)
    scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
    scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.world=bpy.data.worlds['MR1_Neutral_World']
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
    target=Vector(target)
    for label,offset in [('front',(0,.5,0)),('profile',(.5,0,0)),('three_quarter',(.32,.43,.025)),('underside',(.18,.42,-.27))]:
        d=bpy.data.cameras.new(name+'_'+label);o=bpy.data.objects.new(d.name,d);col.objects.link(o)
        o.location=target+Vector(offset);o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
        d.type='ORTHO';d.ortho_scale=scale;d.clip_start=.001;d.clip_end=20
    for label,offset,energy in [('Key',(-.23,.30,.24),2.5),('Fill',(.26,.22,.03),.65)]:
        d=bpy.data.lights.new(name+'_'+label,'AREA');o=bpy.data.objects.new(d.name,d);col.objects.link(o)
        o.location=target+Vector(offset);o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
        d.energy=energy;d.shape='DISK';d.size=.23
    scene.camera=bpy.data.objects[name+'_three_quarter']
    for a in bpy.context.screen.areas:
        if a.type=='VIEW_3D':
            s=a.spaces.active;s.region_3d.view_location=target;s.region_3d.view_distance=scale*1.4
            s.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion();s.region_3d.view_perspective='ORTHO'
            s.shading.type='SOLID';s.shading.color_type='MATERIAL';s.overlay.show_floor=False;s.overlay.show_extras=False
    return scene,col

scene,col=fh_scene('FH1_NOSE_STUDY',(0,.070,1.679),.104)
nose=fh_mesh('FH1_Nose_Control_Cage',build_nose(),col)
bpy.context.view_layer.objects.active=nose;nose.select_set(True)
scene['render_allowlist']=json.dumps([o.name for o in col.objects])
scene['status']='Isolated original nose construction; incomplete head; no human forms approval'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','underside']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/nose_initial_'+label+'.png'
    bpy.ops.render.render(write_still=True)
print('FH1_NOSE_CREATED '+json.dumps({'vertices':len(nose.data.vertices),'faces':len(nose.data.polygons),'interface':len(build_nose()['root_loop'])}))
