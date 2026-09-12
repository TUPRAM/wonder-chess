import bpy,bmesh,json,math
from mathutils import Vector
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
assert '/head-polish/HP1/r001/' in bpy.data.filepath.replace('\\','/')
assert bpy.data.scenes.get('HP1_HEAD_POLISH') is None
source_scene=bpy.data.scenes['FH1_COMBINED_HEAD']
source_names=['FH1_Combined_Head_Control_Cage_r004','FH1_Diagnostic_Eye_R','FH1_Diagnostic_Eye_L']
for name in ['HP1_BASELINE','HP1_HEAD_POLISH']:
    sc=bpy.data.scenes.new(name);sc.world=source_scene.world
    col=bpy.data.collections.new(name+'_ALLOWLIST');sc.collection.children.link(col)
    sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True
    sc.render.resolution_x=900;sc.render.resolution_y=900;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG'
    sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.view_settings.exposure=0;sc.view_settings.gamma=1
    for o in source_scene.objects:
        if o.type not in ['CAMERA','LIGHT'] and o.name not in source_names:continue
        copy=o.copy();copy.data=o.data.copy();col.objects.link(copy);copy.hide_render=False;copy.hide_viewport=False
        if o.name==source_names[0]:copy.name=name+'_Head_r001'
        elif o.name in source_names[1:]:copy.name=name+'_Eye_'+o.name[-1]
        else:copy.name=name+o.name.replace('FH1_COMBINED_HEAD','')
    sc.camera=bpy.data.objects[name+'_three_quarter']
    sc['render_allowlist']=json.dumps([o.name for o in col.objects]);sc['scope']='Head skin and diagnostic globes only. No hair, eyebrows, or eyelashes.'
    # Dedicated head-and-face framing for the main illustration comparison.
    target=Vector((0,.020,1.665))
    for label,offset in [('portrait',(.38,.43,.075)),('back',(0,-.5,0)),('other_three_quarter',(-.32,.43,.025))]:
        d=bpy.data.cameras.new(name+'_'+label);cam=bpy.data.objects.new(d.name,d);col.objects.link(cam)
        cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        d.type='ORTHO';d.ortho_scale=.245 if label=='portrait' else .290;d.clip_start=.001;d.clip_end=20
    sc['render_allowlist']=json.dumps([o.name for o in col.objects])
sc=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=sc
head=bpy.data.objects['HP1_HEAD_POLISH_Head_r001']
# Record stable component index order from the untouched FH1 assembly.
initial=bpy.data.objects['FH1_Combined_Head_Control_Cage'];lookup={tuple(round(c,6) for c in v.co):v.index for v in initial.data.vertices}
feature_indices={}
for part,objname in [('nose','FH1_Nose_Control_Cage_r002'),('mouth','FH1_Mouth_Control_Cage_r002')]:
    feature_indices[part]=[lookup[tuple(round(c,6) for c in v.co)] for v in bpy.data.objects[objname].data.vertices]
for side in ['L','R']:
    gi=head.vertex_groups['Orbital_'+side].index;ri=head.vertex_groups['Orbital_'+side+'_Joined_Interface'].index
    inner=[];root=[]
    for v in head.data.vertices:
        memberships={g.group for g in v.groups}
        if ri in memberships:root.append(v.index)
        elif gi in memberships:inner.append(v.index)
    feature_indices['orbit_'+side]=inner;feature_indices['orbit_root_'+side]=root
head['feature_indices']=json.dumps(feature_indices)
bpy.ops.object.select_all(action='DESELECT');head.select_set(True);bpy.context.view_layer.objects.active=head
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        s=a.spaces.active;s.region_3d.view_location=(0,-.008,1.680);s.region_3d.view_distance=.36
        s.region_3d.view_rotation=sc.camera.rotation_euler.to_quaternion();s.region_3d.view_perspective='ORTHO'
        s.shading.type='SOLID';s.shading.color_type='MATERIAL';s.overlay.show_floor=False;s.overlay.show_extras=False
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
baseline=bpy.data.scenes['HP1_BASELINE'];bpy.context.window.scene=baseline
for label in ['front','profile','three_quarter','portrait']:
    baseline.camera=bpy.data.objects[baseline.name+'_'+label];baseline.render.filepath=ROOT+'/captures/baseline_'+label+'.png';bpy.ops.render.render(write_still=True)
bpy.context.window.scene=sc
print('HP1 baseline and head-only candidate established. No hair objects linked or edited. '+json.dumps({k:len(v) for k,v in feature_indices.items()}))
