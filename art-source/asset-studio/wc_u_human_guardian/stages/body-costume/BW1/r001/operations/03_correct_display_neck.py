import bpy,json
s=bpy.data.scenes['BW1_BODY_COSTUME'];body=bpy.data.objects['BW1_IndexedBody']
states=[(m,m.show_viewport) for m in body.modifiers]
for m,_ in states:m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get();dg.update();ev=body.evaluated_get(dg)
idx=[v.index for v in ev.data.vertices if (body.matrix_world@v.co).z<1.564904]
g=body.vertex_groups['BW1_Display_Body_Below_Neck'];g.remove(list(range(len(body.data.vertices))));g.add(idx,1.0,'REPLACE')
for m,state in states:m.show_viewport=state
dg.update()
bpy.data.lights['BW1_Key'].energy=170;bpy.data.lights['BW1_Fill'].energy=65;bpy.data.lights['BW1_Rim'].energy=100
s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/body_r000_corrected_display_front.png';bpy.ops.render.render(write_still=True)
print(json.dumps({'display_group_vertices':len(idx),'source_indices_or_coordinates_changed':False,'neck_interface_status':'Context only; evaluated-coordinate mask restored neck coverage, not welded integration'}))

