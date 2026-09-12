import bpy, json
from mathutils import Matrix
expected = r'C:\Users\iputu\Documents\Wonder Chess\art-source\asset-studio\wc_u_human_guardian\live\ada_live_mcp_r001.blend'
assert bpy.data.filepath == expected, 'Wrong scene; no edit performed'
assert 'AS1_LIVE_MCP_TEST' not in bpy.data.objects, 'Inspect prior operation before retry'
curve = bpy.data.curves.new('AS1_LIVE_MCP_TEST_TEXT', 'FONT')
curve.body = 'LIVE MCP\nCONNECTED\n\nReference setup only'
curve.size = 0.07
curve.space_line = 1.15
ob = bpy.data.objects.new('AS1_LIVE_MCP_TEST', curve)
bpy.context.scene.collection.objects.link(ob)
ob.matrix_world = bpy.data.objects['AS1_REF_body_front'].matrix_world.copy()
ob.location = (-0.60, 0.76, 1.25)
ob['purpose'] = 'Visible live-session connectivity test, not hero geometry or art approval'
ob.hide_render = True
for item in bpy.context.selected_objects: item.select_set(False)
ob.select_set(True)
bpy.context.view_layer.objects.active = ob
bpy.context.scene['as1_live_session_status'] = 'MCP edit verified; owner reference approval still pending'
bpy.context.view_layer.update()
for area in bpy.context.screen.areas: area.tag_redraw()
print(json.dumps({'operation_id':'AS1-LIVE-MCP-ADD-LABEL-001','file':bpy.data.filepath,'added':ob.name,'location':list(ob.location),'character_mesh_count':sum(o.type=='MESH' for o in bpy.context.scene.objects)}))
