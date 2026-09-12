import bpy,bmesh,json
s=bpy.context.scene;source=bpy.data.objects['MP1_MpfbFoundation_Source'];source.hide_set(False)
for ob in s.objects:ob.select_set(False)
source.select_set(True);bpy.context.view_layer.objects.active=source
s.MPFB_MDP_symmetry=True;s.MPFB_MDP_refit=False
params={'head_head_invertedtriangular':.12,'head_head_back_scale_depth_decr_incr':-.12,'chin_chin_height_decr_incr':.16,'chin_chin_prominent_decr_incr':.12,'chin_chin_width_decr_incr':-.08,'cheek_r_cheek_bones_decr_incr':.10,'cheek_r_cheek_inner_decr_incr':-.08,'nose_nose_scale_vert_decr_incr':-.10,'nose_nose_scale_depth_decr_incr':-.08,'nose_nose_point_width_decr_incr':.06,'mouth_mouth_trans_backward_forward':-.18,'mouth_mouth_philtrum_volume_decr_incr':.10,'mouth_mouth_upperlip_height_decr_incr':-.10,'mouth_mouth_lowerlip_height_decr_incr':-.12,'mouth_mouth_lowerlip_middle_down_up':.12,'mouth_mouth_cupidsbow_decr_incr':.10,'eyes_r_eye_scale_decr_incr':.20,'eyes_r_eye_corner2_down_up':.15,'eyes_r_eye_height1_decr_incr':-.10,'eyes_r_eye_height2_decr_incr':.05,'eyes_r_eye_height3_decr_incr':-.08}
s.head_head_invertedtriangular=0.12
s.head_head_back_scale_depth_decr_incr=-0.12
s.chin_chin_height_decr_incr=0.16
s.chin_chin_prominent_decr_incr=0.12
s.chin_chin_width_decr_incr=-0.08
s.cheek_r_cheek_bones_decr_incr=0.1
s.cheek_r_cheek_inner_decr_incr=-0.08
s.nose_nose_scale_vert_decr_incr=-0.1
s.nose_nose_scale_depth_decr_incr=-0.08
s.nose_nose_point_width_decr_incr=0.06
s.mouth_mouth_trans_backward_forward=-0.18
s.mouth_mouth_philtrum_volume_decr_incr=0.1
s.mouth_mouth_upperlip_height_decr_incr=-0.1
s.mouth_mouth_lowerlip_height_decr_incr=-0.12
s.mouth_mouth_lowerlip_middle_down_up=0.12
s.mouth_mouth_cupidsbow_decr_incr=0.1
s.eyes_r_eye_scale_decr_incr=0.2
s.eyes_r_eye_corner2_down_up=0.15
s.eyes_r_eye_height1_decr_incr=-0.1
s.eyes_r_eye_height2_decr_incr=0.05
s.eyes_r_eye_height3_decr_incr=-0.08
bpy.context.view_layer.update()
mesh=bpy.data.meshes.new_from_object(source.evaluated_get(bpy.context.evaluated_depsgraph_get()),preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get());mesh.name='MP1_Head_Cage_r001';bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=(0,0,1.368),plane_no=(0,0,1),clear_inner=True);bm.to_mesh(mesh);bm.free()
head=bpy.data.objects.new('MP1_Head_r001',mesh);s.collection.objects.link(head);head.matrix_world=source.matrix_world.copy();mesh.materials.clear();mesh.materials.append(bpy.data.materials['MP1_Uniform_Clay'])
for f in mesh.polygons:f.use_smooth=True;f.material_index=0
mod=head.modifiers.new('Editable cage subdivision','SUBSURF');mod.levels=2;mod.render_levels=2
for ob in s.objects:
    if ob.type=='MESH':ob.hide_render=ob.name not in {'MP1_Head_r001','MP1_Eye_R','MP1_Eye_L'};ob.hide_set(ob.hide_render);ob.select_set(False)
head.select_set(True);bpy.context.view_layer.objects.active=head
s['mpfb_params_r001']=json.dumps(params);print('Applied MPFB target controls',json.dumps(params));print('source_keys',len(source.data.shape_keys.key_blocks));s.camera=bpy.data.objects['HP1_HEAD_POLISH_three_quarter'];bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/mpfb-pilot/MP1/captures/r001_three_quarter.png';bpy.ops.render.render(write_still=True)
