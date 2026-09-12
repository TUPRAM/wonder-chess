import bpy,bmesh,json,math
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
s=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=s
assert bpy.data.filepath.replace('\\','/')==ROOT+'/ada_head_polish_work.blend'
assert bpy.data.objects.get('HP1_HEAD_POLISH_Head_r016') is None
old=bpy.data.objects['HP1_HEAD_POLISH_Head_r015'];baseline=bpy.data.objects['HP1_HEAD_POLISH_Head_r014']
h=old.copy();h.data=old.data.copy();h.name='HP1_HEAD_POLISH_Head_r016';s.collection.objects.link(h)
ring=json.loads(h['orbital_rings'])[0]
# Restore a small designed nasal-half convex peak; no uniform lid shift.
for j,dz in [(10,.0004),(11,.0009),(12,.00115),(13,.0009),(14,.00035)]:
    for layer,factor in [(0,1),(1,1),(2,.95),(3,.65),(4,.15)]:
        p=h.data.vertices[ring[layer*20+j]].co;z0=p.z;p.z+=dz*factor
        if layer<2:
            a=math.sqrt(max(.0000001,.0207**2-(p.x-.034)**2-(z0-1.690)**2))
            b=math.sqrt(max(.0000001,.0207**2-(p.x-.034)**2-(p.z-1.690)**2))
            p.y+=b-a
# Explicit local profile chain: base of columella, subnasale, philtrum,
# upper-lip support. Shared midline controls stay on X=0. Their adjacent
# subdivided faces on both sides respond; this is not zero surface spillover.
profile={767:(78.1,1650.7),248:(73.8,1644.2),1098:(71.2,1639.48),1064:(69.1,1636.29),1030:(69.0,1635.46)}
for i,(ym,zm) in profile.items():
    p=h.data.vertices[i].co;p.y=ym*.001;p.z=zm*.001
# Retain right philtral-column support but remove the abrupt over-full peak
# introduced by attempt 1. Vermilion, mouth contact and commissure untouched.
targets={249:73.2,250:71.5,
1025:66.9,1026:68.2,1027:69.5,1028:70.2,1029:69.6,
1060:67.7,1061:69.0,1062:70.2,1063:69.9,
1095:68.2,1096:70.6,1097:71.4}
for i,ym in targets.items():h.data.vertices[i].co.y=ym*.001
h.data.update();changed=[v.index for v in h.data.vertices if (v.co-baseline.data.vertices[v.index].co).length>1e-8]
assert all(baseline.data.vertices[i].co.x>=-1e-8 and baseline.data.vertices[i].co.y>.038 and 1.632<baseline.data.vertices[i].co.z<1.713 for i in changed)
assert all(tuple(v.co)==tuple(baseline.data.vertices[v.index].co) for v in h.data.vertices if baseline.data.vertices[v.index].co.x<-.000001)
bm=bmesh.new();bm.from_mesh(h.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(h.data);bm.free()
vg=h.vertex_groups.new(name='LC2_Local_Region_Including_Profile_Seam');vg.add(changed,1,'REPLACE')
h['local_correction_indices']=json.dumps(changed)
h['local_correction_method']='Attempt 2: authored nasal-half lid peak and five shared-midline profile controls within columella/philtrum/upper-lip support; corrected right philtral gradient. No smoothing or mirror. Negative-X cage controls fixed; nearby subdivision responds to shared midline.'
h['midline_profile_indices']=json.dumps(list(profile))
h['art_status']='REVISE'
old.hide_render=True;old.hide_set(True)
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
s['render_allowlist']=json.dumps([o.name for o in s.objects if not o.hide_render])
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/ada_head_polish_work.blend')
print('LOCAL_ATTEMPT_2 '+json.dumps({'object':h.name,'changed_vertices_from_r014':len(changed),'midline_controls':list(profile),'negative_x_controls_fixed':True,'neighboring_surface_responds_to_midline':True}))
