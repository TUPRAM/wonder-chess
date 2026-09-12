import bpy,json
from mathutils import Matrix
src=bpy.context.scene
assert src.name=='BW2_RIGHT_GRIP'
assert 'BW3_COLLISION_FIRST' not in bpy.data.scenes
s=bpy.data.scenes.new('BW3_COLLISION_FIRST')
s.world=src.world.copy()
s.render.engine='CYCLES';s.cycles.samples=24
s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.render.film_transparent=False
s.view_settings.view_transform=src.view_settings.view_transform;s.view_settings.look=src.view_settings.look
s.view_settings.exposure=src.view_settings.exposure;s.view_settings.gamma=src.view_settings.gamma
s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
s.frame_start=1;s.frame_end=145;s.render.fps=24;s.render.fps_base=1
coll=bpy.data.collections.new('BW3_DERIVED_HAND');s.collection.children.link(coll)
presentation=bpy.data.collections.new('BW3_REVIEW');s.collection.children.link(presentation)
mapping={}
names={'BW1_Temporary_Pose_Rig':'BW3_Derived_Rig','BW1_IndexedBody':'BW3_Derived_Body','BW1_Glove_Pair_SourceFit':'BW3_Derived_Glove','BW2_FixedHandFrame_R':'BW3_FixedHandFrame_R','BW2_Locked_Handle_28mm':'BW3_Locked_Handle_28mm'}
for oldnm,newnm in names.items():
    old=bpy.data.objects[oldnm];o=old.copy()
    if old.data:o.data=old.data.copy()
    o.name=newnm;coll.objects.link(o);mapping[old]=o
    if old.animation_data and old.animation_data.action:
        o.animation_data.action=old.animation_data.action.copy();o.animation_data.action.name='BW3_OriginalRoute_Derived'
    o['BW3_source_object']=oldnm
for old,o in mapping.items():
    if old.parent:o.parent=mapping[old.parent]
    for mod in o.modifiers:
        if mod.type=='ARMATURE':mod.object=mapping[mod.object]
    assert len(o.constraints)==0
    assert not o.animation_data or (len(o.animation_data.drivers)==0 and len(o.animation_data.nla_tracks)==0)
    o.matrix_parent_inverse=old.matrix_parent_inverse.copy();o.matrix_basis=old.matrix_basis.copy()
for old in list(src.objects):
    if old.name.startswith('BW2_cam_') or old.name.startswith('BW2_light_'):
        o=old.copy();o.data=old.data.copy();o.name=old.name.replace('BW2_','BW3_',1);presentation.objects.link(o)
        if old.animation_data and old.animation_data.action:
            o.animation_data.action=old.animation_data.action.copy();o.animation_data.action.name='BW3_CarryCamera_Derived'
        o.hide_render=False;o.hide_viewport=False
for k in ['BW2_frame_world','BW2_hand_contract','BW2_contact_patches_open','BW2_patch_eval_level','BW2_patch_eval_count','BW2_retained_grip_pose','BW2_carry_spec','BW2_hand_frame_in_posebone']:
    s[k]=src[k]
s['BW3_scope']='Independent derived body/glove/rig/action; collision-first right hand only; original master objects retained in prior scenes.'
s['BW3_method_status']='DIAGNOSIS'
s['BW3_human_approval']='NOT_ISSUED'
s['BW3_fixture_revision']='BW2 fixed28mm diameter109mm total105mm usable; unchanged'
bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
r=bpy.data.objects['BW3_Derived_Rig'];g=bpy.data.objects['BW3_Derived_Glove'];b=bpy.data.objects['BW3_Derived_Body']
g.hide_render=False;g.hide_viewport=False;g.hide_set(False);b.hide_render=True;b.hide_set(True)
r.hide_render=True;r.hide_set(False)
h=bpy.data.objects['BW3_Locked_Handle_28mm'];h.hide_render=False;h.hide_set(False)
s.camera=bpy.data.objects['BW3_cam_oblique']
checks={'body_mesh_independent':b.data!=bpy.data.objects['BW1_IndexedBody'].data,'body_keys_independent':b.data.shape_keys!=bpy.data.objects['BW1_IndexedBody'].data.shape_keys,'glove_mesh_independent':g.data!=bpy.data.objects['BW1_Glove_Pair_SourceFit'].data,'rig_data_independent':r.data!=bpy.data.objects['BW1_Temporary_Pose_Rig'].data,'rig_action_independent':r.animation_data.action!=bpy.data.objects['BW1_Temporary_Pose_Rig'].animation_data.action,'shape_keys':len(b.data.shape_keys.key_blocks),'body_vertices':len(b.data.vertices),'glove_vertices':len(g.data.vertices),'armature_targets':[(o.name,m.object.name) for o in [b,g] for m in o.modifiers if m.type=='ARMATURE'],'holder_parent':bpy.data.objects['BW3_FixedHandFrame_R'].parent.name,'handle_parent':h.parent.name}
assert all(checks[k] for k in ['body_mesh_independent','body_keys_independent','glove_mesh_independent','rig_data_independent','rig_action_independent'])
s['BW3_independence']=json.dumps(checks)
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW3/r001/ada_bw3_grip_work.blend')
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW3/r001/bw3_independent_open_input.blend',copy=True)
print(json.dumps(checks))

