import bpy,bmesh,json
s=bpy.context.scene;source=bpy.data.objects['MP1_MpfbFoundation_Source'];source.hide_set(False)
for ob in s.objects:ob.select_set(False)
source.select_set(True);bpy.context.view_layer.objects.active=source
s.MPFB_MDP_symmetry=True;s.MPFB_MDP_refit=False
params={"mouth_mouth_upperlip_middle_down_up":-0.18,"mouth_mouth_lowerlip_middle_down_up":0.45,"mouth_mouth_upperlip_volume_decr_incr":-0.25,"mouth_mouth_lowerlip_volume_decr_incr":-0.1}
s.mouth_mouth_upperlip_middle_down_up=-0.18
s.mouth_mouth_lowerlip_middle_down_up=0.45
s.mouth_mouth_upperlip_volume_decr_incr=-0.25
s.mouth_mouth_lowerlip_volume_decr_incr=-0.1
bpy.context.view_layer.update()
mesh=bpy.data.meshes.new_from_object(source.evaluated_get(bpy.context.evaluated_depsgraph_get()),preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get());mesh.name='MP1_Head_Cage_r002';bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=(0,0,1.368),plane_no=(0,0,1),clear_inner=True);bm.to_mesh(mesh);bm.free()
head=bpy.data.objects.new('MP1_Head_r002',mesh);s.collection.objects.link(head);head.matrix_world=source.matrix_world.copy();mesh.materials.clear();mesh.materials.append(bpy.data.materials['MP1_Uniform_Clay'])
for f in mesh.polygons:f.use_smooth=True;f.material_index=0
mod=head.modifiers.new('Editable cage subdivision','SUBSURF');mod.levels=2;mod.render_levels=2
for ob in s.objects:
    if ob.type=='MESH':ob.hide_render=ob.name not in {'MP1_Head_r002','MP1_Eye_R','MP1_Eye_L'};ob.hide_set(ob.hide_render);ob.select_set(False)
head.select_set(True);bpy.context.view_layer.objects.active=head
s['mpfb_params_r002']=json.dumps(params);print('Applied MPFB target controls',json.dumps(params));print('source_keys',len(source.data.shape_keys.key_blocks));s.camera=bpy.data.objects['HP1_HEAD_POLISH_three_quarter'];bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/mpfb-pilot/MP1/captures/r002_three_quarter.png';bpy.ops.render.render(write_still=True)
