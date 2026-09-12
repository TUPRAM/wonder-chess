import bpy,json
from mathutils import Vector
s=bpy.data.scenes['BW1_BODY_COSTUME'];s.frame_set(1);s.render.engine='CYCLES';s.cycles.samples=24
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.resolution_x=850;s.render.resolution_y=1100
meshes=[o for o in s.objects if o.type=='MESH'];flags={o.name:o.hide_get() for o in meshes};records=[]
def capture(name,cam):
    s.camera=bpy.data.objects[cam];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/'+name+'.png'
    record={'file':s.render.filepath,'camera':cam,'matrix_world':[list(row) for row in s.camera.matrix_world],'ortho_scale':s.camera.data.ortho_scale,'resolution':[s.render.resolution_x,s.render.resolution_y],'frame':s.frame_current,'mesh_allowlist':[o.name for o in meshes if not o.hide_render],'contextual_head':'MP1 ART_REVISE; exact geometry preserved, neck interface unjoined'}
    bpy.ops.render.render(write_still=True);records.append(record)
for o in meshes:o.hide_render=flags[o.name] or not (o.name=='BW1_IndexedBody' or o.name.startswith('BW1_Context'))
print('Context object names: '+str([o.name for o in bpy.data.collections['BW1_CONTEXT_HEAD'].objects]))
# Use collection membership explicitly rather than relying on name spelling.
for o in meshes:o.hide_render=flags[o.name] or not (o.name=='BW1_IndexedBody' or o in bpy.data.collections['BW1_CONTEXT_HEAD'].objects[:])
for view in ['front','profile','back','three_quarter','other_three_quarter']:capture('body_context_'+view,'BW1_Camera_'+view)
for o in meshes:o.hide_render=flags[o.name]
for view in ['front','profile','back','three_quarter','other_three_quarter']:capture('candidate_context_'+view,'BW1_Camera_'+view)
key=bpy.data.objects['BW1_Key'];oldkey=key.location.copy();oldrot=key.rotation_euler.copy();key.location.x=-key.location.x;key.rotation_euler=(Vector((0,0,1))-key.location).to_track_quat('-Z','Y').to_euler()
capture('candidate_context_reversed_key','BW1_Camera_three_quarter')
key.location=oldkey;key.rotation_euler=oldrot
for o in meshes:o.hide_render=flags[o.name] or o in bpy.data.collections['BW1_ARMOR'].objects[:] or o in bpy.data.collections['BW1_EQUIPMENT'].objects[:]
capture('cloth_layer_context','BW1_Camera_three_quarter')
for o in meshes:o.hide_render=flags[o.name]
s['BW1_final_capture_records']=json.dumps(records)
s['BW1_candidate_status']='ART_REVISE';s['BW1_human_forms_approval']=False
s.camera=bpy.data.objects['BW1_Camera_three_quarter']
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps({'captured':len(records),'files':[r['file'] for r in records]}))
