import bpy,bmesh,json,math
from mathutils import Vector
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
s=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=s
assert bpy.data.filepath.replace('\\','/')==ROOT+'/ada_head_polish_work.blend'
assert bpy.context.mode=='OBJECT'
assert bpy.data.objects.get('HP1_HEAD_POLISH_Head_r015') is None
old=bpy.data.objects['HP1_HEAD_POLISH_Head_r014']
h=old.copy();h.data=old.data.copy();h.name='HP1_HEAD_POLISH_Head_r015';s.collection.objects.link(h)
before=[v.co.copy() for v in h.data.vertices]
ring=json.loads(h['orbital_rings'])[0]
# Twenty explicit aperture controls in millimetres. Nasal peak and firmer
# lateral segment replace the uniformly arced lid. The other eye is fixed.
opening=[(23,1685.0),(28,1683.7),(34,1683.4),(40,1684.2),(46,1686.2),(50.5,1688.5),(53,1690.4),(53.5,1691.5),(52,1692.8),(48.5,1693.9),(44,1694.8),(38.5,1695.5),(32.5,1695.8),(27,1695.0),(22.5,1693.4),(19,1691.2),(16.8,1689.1),(16.2,1688.2),(18,1687.0),(20,1685.9)]
def globe_y(x,z):
    return .039+math.sqrt(max(.0000001,.0207**2-(x-.034)**2-(z-1.690)**2))
for j,(xm,zm) in enumerate(opening):
    x=xm*.001;z=zm*.001
    for layer,depth in [(0,.00005),(1,.00115)]:
        h.data.vertices[ring[layer*20+j]].co=(x,globe_y(x,z)+depth,z)
# Independently authored lid-body and crease depth. No full-face projection
# or smoothing. Only the two margin rows use the unchanged globe as a guide.
body_y=[58.4,60.1,60.9,60.5,58.2,54.0,49.1,47.8,50.8,55.7,59.1,60.7,61.2,60.4,58.5,55.7,53.0,51.8,54.2,56.6]
crease_y=[57.3,59.2,60.0,59.5,57.2,52.5,46.7,45.2,47.0,52.0,55.9,57.8,58.8,58.7,57.4,55.8,54.0,52.3,54.2,55.8]
for j in range(20):
    delta=Vector((opening[j][0]*.001-before[ring[j]].x,0,opening[j][1]*.001-before[ring[j]].z))
    for layer,amount,depths in [(2,.95,body_y),(3,.68,crease_y)]:
        p=h.data.vertices[ring[layer*20+j]].co;p+=delta*amount;p.y=depths[j]*.001
    # Local connector row follows the new lid without dragging the boundary.
    p=h.data.vertices[ring[80+j]].co;p+=delta*.22
    if j in [0,1,2,3,4]:p.y+=[.0018,.0017,.0011,.0005,0][j]
    if j in [14,15,16,17,18,19]:p.y+=[.0003,.0006,.001,.0018,.0024,.0022][j-14]
# Sparse, named cross-sections shape the nasal sidewall and independent
# upper cheek. Outer cheek, jaw, ear and lower mouth remain bitwise fixed.
depth_targets={341:63.5,342:61.3,343:60.0,344:57.0,362:62.0,379:60.0,398:58.9,
784:70.8,791:66.8,798:63.3,805:60.8,
316:67.0,285:64.0,252:64.7,251:68.2,250:71.0,249:72.0}
for i,ym in depth_targets.items():h.data.vertices[i].co.y=ym*.001
# Columella right flank: move its connected nostril vault with the local
# attachment. Midline and opposite-side controls remain fixed in this proof.
for i in [768,775,825,830,831,836]:
    h.data.vertices[i].co.y+=.0008
    h.data.vertices[i].co.z-=.0006
# Bring right upper-lip support into a short shallow philtral transition;
# existing contact line, lower lip, center seam and commissure are retained.
support={1024:65.0,1025:67.1,1026:69.0,1027:70.8,1028:71.6,1029:69.5,
1059:66.0,1060:68.0,1061:70.0,1062:71.3,1063:70.0,
1094:66.2,1095:68.3,1096:70.9,1097:70.2}
for i,ym in support.items():h.data.vertices[i].co.y=ym*.001
h.data.update()
changed=[v.index for v in h.data.vertices if (v.co-before[v.index]).length>1e-8]
assert all(before[i].x>0 and before[i].y>.038 and 1.632<before[i].z<1.713 for i in changed)
assert all(tuple(v.co)==tuple(before[v.index]) for v in h.data.vertices if before[v.index].x<=0)
bm=bmesh.new();bm.from_mesh(h.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(h.data);bm.free()
vg=h.vertex_groups.new(name='LC1_Anatomical_Right_Correction');vg.add(changed,1,'REPLACE')
h['local_correction_indices']=json.dumps(changed)
h['local_correction_method']='Attempt 1: explicit aperture arc; independent lid-body/crease depths; nasal sidewall and upper-muzzle cross-section controls. No smoothing, no mirror, no center-seam move.'
h['local_baseline']='HP1_HEAD_POLISH_Head_r014';h['art_status']='REVISE'
old.hide_render=True;old.hide_set(True)
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
s['render_allowlist']=json.dumps([o.name for o in s.objects if not o.hide_render])
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/ada_head_polish_work.blend')
print('LOCAL_ATTEMPT_1 '+json.dumps({'object':h.name,'changed_vertices':len(changed),'indices':changed,'center_and_left_fixed':True}))
