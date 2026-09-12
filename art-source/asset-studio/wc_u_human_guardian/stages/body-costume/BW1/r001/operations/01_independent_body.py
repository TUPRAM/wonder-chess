import bpy,json
assert bpy.data.filepath.replace('\\','/').endswith('/mpfb-pilot/MP1/ada_mpfb_work.blend')
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/ada_bw1_preedit_live.blend',copy=True)
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/ada_body_costume_work.blend')
src=bpy.data.objects['MP1_MpfbFoundation_Source']
s=bpy.data.scenes.new('BW1_BODY_COSTUME');s.use_fake_user=True;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1.0
bpy.context.window.scene=s
for name in ['BW1_BODY','BW1_CLOTH','BW1_ARMOR','BW1_EQUIPMENT','BW1_RIG','BW1_CONTEXT_HEAD','BW1_PRESENTATION']:
    c=bpy.data.collections.new(name);s.collection.children.link(c)
body=src.copy();body.data=src.data.copy();body.name='BW1_IndexedBody';body.data.name='BW1_IndexedBody_Mesh'
bpy.data.collections['BW1_BODY'].objects.link(body);body.hide_render=False;body.hide_set(False)
for m in list(body.modifiers):
    if m.name=='Head preview; full source indices preserved':body.modifiers.remove(m)
body['source_method']='Independent MPFB MP1 indexed body copy, native targets only on full source';body['human_approval']=False
bpy.context.view_layer.objects.active=body;body.select_set(True)
dg=bpy.context.evaluated_depsgraph_get();dg.update();ev=body.evaluated_get(dg)
coords=[body.matrix_world@v.co for v in ev.data.vertices]
for srcname,newname in [('MP1_Head_r002','BW1_Context_Head_ART_REVISE'),('MP1_Eye_R','BW1_Context_Eye_R'),('MP1_Eye_L','BW1_Context_Eye_L')]:
    old=bpy.data.objects[srcname];o=old.copy();o.data=old.data.copy();o.name=newname;bpy.data.collections['BW1_CONTEXT_HEAD'].objects.link(o);o.hide_render=False;o.hide_set(False);o['context_only']=True
preview=body.vertex_groups.new(name='BW1_Display_Body_Below_Neck')
preview.add([v.index for v in body.data.vertices if v.co.z<1.368],1.0,'REPLACE')
m=body.modifiers.new('BW1 display cut; master indices retained','MASK');m.vertex_group=preview.name
for sc in bpy.data.scenes:sc.use_fake_user=True
print(json.dumps({'source_independent_mesh':body.data!=src.data,'keys_independent':body.data.shape_keys!=src.data.shape_keys,'raw_vertices':len(body.data.vertices),'shape_keys':len(body.data.shape_keys.key_blocks),'full_skin_vertices':len(coords),'full_skin_bounds':[[min(v[k] for v in coords),max(v[k] for v in coords)] for k in range(3)],'matrix':[list(row) for row in body.matrix_world],'modifiers':[(m.name,m.type,m.vertex_group if m.type=='MASK' else '') for m in body.modifiers],'groups':[g.name for g in body.vertex_groups]},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

