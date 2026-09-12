import bpy,json
s=bpy.context.scene;s.frame_set(37)
g=bpy.data.objects['BW1_Glove_Pair_SourceFit'];h=bpy.data.objects['BW2_Locked_Handle_28mm']
key=bpy.data.objects['BW2_light_key'];fill=bpy.data.objects['BW2_light_fill']
key_mat=key.matrix_world.copy();fill_mat=fill.matrix_world.copy()
key.matrix_world=fill_mat;fill.matrix_world=key_mat
s.camera=bpy.data.objects['BW2_cam_oblique'];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/captures/grip_retained_reversed_light.png';bpy.ops.render.render(write_still=True)
key.matrix_world=key_mat;fill.matrix_world=fill_mat
cage=g.copy();cage.data=g.data.copy();cage.name='BW2_DIAG_ActualPosedControlCage';bpy.data.collections['BW2_CONTACT_STUDY'].objects.link(cage)
for mod in cage.modifiers:
    if mod.type=='SUBSURF':mod.levels=0;mod.render_levels=0
wire=bpy.data.materials.new('BW2_DIAG_CageLines');wire.diffuse_color=(.025,.008,.002,1);wire.use_nodes=True
bs=wire.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.025,.008,.002,1);bs.inputs['Roughness'].default_value=.8
cage.data.materials.clear();cage.data.materials.append(g.data.materials[0]);cage.data.materials.append(wire)
mod=cage.modifiers.new('Actual base topology edges','WIREFRAME');mod.thickness=.00016;mod.use_replace=False;mod.offset=1;mod.material_offset=1
g.hide_render=True;cage.hide_render=False;cage.hide_set(False);h.hide_render=True
for nm in ['axial','back']:
    s.camera=bpy.data.objects['BW2_cam_'+nm];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/captures/actual_posed_cage_'+nm+'.png';bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(cage,do_unlink=True)
g.hide_render=False;h.hide_render=False
s.camera=bpy.data.objects['BW2_cam_oblique']
bpy.data.objects['BW2_cam_carry_close'].data.ortho_scale=.32
s['BW2_candidate_status']='ART_REVISE'
s['BW2_human_approval']='NOT_ISSUED'
s['BW2_stop_reason']='Retained calibrated contact improvement fails anatomical enclosure: confirmed nonadjacent hand self intersections and severe thumb-web fold. Stop pose search; no actual sword adaptation.'
s['BW2_runtime_path']='AUTHORING_ONLY; proposed fixed posed grip in derived hand export requires rest-space conversion and wrist seam checks; no game skeleton changes or import.'
s['BW2_recipe_status']='NOT_PROMOTED; replay and second body NOT_RUN'
s['BW2_capture_note']='Matched captures grip_initial versus grip_integrated use unchanged cameras and clay. Actual posed cage uses original editable glove base with armature, subdivision disabled and wire overlay; handle hidden. Reversed lighting swaps key/fill locations only.'
s.frame_set(37)
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/ada_bw2_grip_work.blend')
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/ada_bw2_grip_checkpoint_r001_ART_REVISE.blend',copy=True)
print(json.dumps({'status':s['BW2_candidate_status'],'file':bpy.data.filepath,'scene':s.name,'frame':37,'new_checkpoint':'ada_bw2_grip_checkpoint_r001_ART_REVISE.blend'}))

