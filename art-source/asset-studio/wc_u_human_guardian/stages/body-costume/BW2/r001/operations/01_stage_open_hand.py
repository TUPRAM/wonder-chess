import bpy,json
s=bpy.context.scene
assert s.name=='BW1_BODY_COSTUME' and bpy.context.mode=='OBJECT'
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW2/r001/ada_bw2_grip_work.blend')
s.name='BW2_RIGHT_GRIP'
s['BW2_scope']='Anatomical-right grip only; AUTHORING_ONLY; no human approval'
c=bpy.data.collections.new('BW2_CONTACT_STUDY')
s.collection.children.link(c)
r=bpy.data.objects['BW1_Temporary_Pose_Rig']
r.animation_data.action.use_fake_user=True
r.animation_data.action=None
for pb in r.pose.bones:
    pb.matrix_basis.identity()
s.frame_set(1)
bpy.context.view_layer.update()
print(json.dumps({'file':bpy.data.filepath,'rig_world':[list(x) for x in r.matrix_world],'bones':[{'name':b.name,'head':list(r.matrix_world@b.head),'tail':list(r.matrix_world@b.tail),'mode':b.rotation_mode,'basis':[list(x) for x in b.matrix_basis]} for b in r.pose.bones if b.name.endswith('.R') and ('finger' in b.name or 'wrist' in b.name)],'mods':[{'object':n,'mods':[(m.name,m.type) for m in bpy.data.objects[n].modifiers]} for n in ['BW1_Glove_Pair_SourceFit','BW1_IndexedBody']]}))
