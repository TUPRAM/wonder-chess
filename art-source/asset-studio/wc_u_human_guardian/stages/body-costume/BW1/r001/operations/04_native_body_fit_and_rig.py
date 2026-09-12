import bpy,json
from mathutils import Matrix,Vector
s=bpy.data.scenes['BW1_BODY_COSTUME'];body=bpy.data.objects['BW1_IndexedBody']
for o in s.objects:o.select_set(False)
body.select_set(True);bpy.context.view_layer.objects.active=body
s.MPFB_MDP_prune=False;s.MPFB_MDP_symmetry=True;s.MPFB_MDP_refit=False
s.torso_measure_shoulder_dist_decr_incr=.12
s.torso_torso_vshape_decr_incr=.08
s.arms_r_upperarm_shoulder_muscle_decr_incr=.12
s.hands_r_hand_scale_decr_incr=.03
s['body_target_settings']=json.dumps({'torso_measure_shoulder_dist_decr_incr':.12,'torso_torso_vshape_decr_incr':.08,'arms_r_upperarm_shoulder_muscle_decr_incr':.12,'hands_r_hand_scale_decr_incr':.03,'symmetry':True,'units':'dimensionless MPFB target amounts'})
states=[(m,m.show_viewport) for m in body.modifiers]
for m,_ in states:m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get();dg.update();before=[body.matrix_world@v.co for v in body.evaluated_get(dg).data.vertices];world=body.matrix_world.copy()
body.matrix_world=Matrix.Identity(4)
s.MPFB_ADR_standard_rig='default';s.MPFB_ADR_import_weights=True
result=bpy.ops.mpfb.add_standard_rig()
rig=body.parent;rig.name='BW1_Temporary_Pose_Rig';rig['export_status']='LOCAL_ARTICULATION_PROOF_ONLY_NOT_RUNTIME_COMPATIBLE';rig.matrix_world=world;body.matrix_parent_inverse=Matrix.Identity(4);body.matrix_basis=Matrix.Identity(4)
for coll in list(rig.users_collection):coll.objects.unlink(rig)
bpy.data.collections['BW1_RIG'].objects.link(rig)
dg.update();after=[body.matrix_world@v.co for v in body.evaluated_get(dg).data.vertices]
error=max((a-b).length for a,b in zip(before,after))
for m,state in states:m.show_viewport=state
bpy.context.view_layer.objects.active=body
arm=next(m for m in body.modifiers if m.type=='ARMATURE')
bpy.ops.object.modifier_move_up(modifier=arm.name)
for ob in bpy.data.collections['BW1_CONTEXT_HEAD'].objects:
    mat=ob.matrix_world.copy();ob.parent=rig;ob.parent_type='BONE';ob.parent_bone='head';ob.matrix_world=mat
rig.show_in_front=True;rig.hide_render=True
dg.update()
print(json.dumps({'rig_operator':list(result),'rig_bones':len(rig.data.bones),'preserved_world_max_vertex_delta_m':error,'raw_vertices':len(body.data.vertices),'keys':len(body.data.shape_keys.key_blocks),'armature_matrix':[list(r) for r in rig.matrix_world],'bone_examples':[(b.name,list(rig.matrix_world@b.head_local),list(rig.matrix_world@b.tail_local)) for b in rig.data.bones if b.name in {'upperarm01.R','lowerarm01.R','wrist.R','upperleg01.R','lowerleg01.R','foot.R','head'}]},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
s.camera=bpy.data.objects['BW1_Camera_three_quarter'];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/body_r001_three_quarter.png';bpy.ops.render.render(write_still=True)

