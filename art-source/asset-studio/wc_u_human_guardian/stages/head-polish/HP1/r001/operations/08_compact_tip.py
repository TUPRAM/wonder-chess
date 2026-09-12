import bpy,bmesh,json,math
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
s=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=s
assert bpy.data.objects.get('HP1_HEAD_POLISH_Head_r009') is None
old=bpy.data.objects['HP1_HEAD_POLISH_Head_r008'];h=old.copy();h.data=old.data.copy();h.name='HP1_HEAD_POLISH_Head_r009';s.collection.objects.link(h);old.hide_render=True;old.hide_set(True)
f=json.loads(h['feature_indices']);nose=f['nose'];bulb=json.loads(h['nasal_bulb_section'])
for j in range(1,8):
    p=h.data.vertices[bulb[j]].co
    p.y=[0,.079,.084,.087,.088,.087,.084,.079,0][j]
    p.z=[0,1.658,1.660,1.662,1.663,1.662,1.660,1.658,0][j]
h.data.vertices[nose[22]].co=(0,.0865,1.6585)
h.data.vertices[nose[31]].co=(0,.0835,1.670)
h.data.vertices[nose[13]].co=(0,.0785,1.651)
# A short columella-to-philtrum turn; preserve the nostril vaults and lip join.
for j in range(1,8):
    p=h.data.vertices[nose[j]].co;q=abs(j-4)/4
    p.y=.0718-.0108*q*q
    p.z=1.6442-.0012*q*q
orbits=json.loads(h['orbital_rings'])
for ring in orbits:
    for layer in [2,3]:
        for j in [4,5,6,7,8,9]:h.data.vertices[ring[layer*20+j]].co.y+=.0006
h.data.update();bm=bmesh.new();bm.from_mesh(h.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(h.data);bm.free()
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
h['revision_notes']='Compact rounded nasal bulb correction, shortened columella-to-philtrum turn and local outer lid clearance.'
s['render_allowlist']=json.dumps([o.name for o in s.objects if not o.hide_render])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','portrait']:
    s.camera=bpy.data.objects[s.name+'_'+label];s.render.filepath=ROOT+'/captures/r009_'+label+'.png';bpy.ops.render.render(write_still=True)
print('HP1 r009 compact tip correction saved and rendered.')
