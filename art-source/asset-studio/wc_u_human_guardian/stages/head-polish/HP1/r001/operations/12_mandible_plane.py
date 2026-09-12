import bpy,bmesh,json,math
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
s=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=s
assert '/head-polish/HP1/r001/' in bpy.data.filepath.replace('\\','/')
assert bpy.data.objects.get('HP1_HEAD_POLISH_Head_r012') is None
old=bpy.data.objects['HP1_HEAD_POLISH_Head_r011'];h=old.copy();h.data=old.data.copy();h.name='HP1_HEAD_POLISH_Head_r012';s.collection.objects.link(h);old.hide_render=True;old.hide_set(True)
initial=bpy.data.objects['FH1_Combined_Head_Control_Cage']
def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
# Explicit jaw section: the lowest face row formerly remained almost level
# all the way around the skull, creating a conical face/neck. Raise its rear
# into the mandibular angle, retaining the front chin and open neck boundary.
sections=[(1.577,.038,.30),(1.590,.032,.14),(1.606,.022,.06),(1.617,.016,0),(1.624,.012,0),(1.632,.008,0),(1.643,.004,0)]
for v in h.data.vertices:
    if v.index>=764:continue
    original=initial.data.vertices[v.index].co
    if original.z<=1.565 or original.z>=1.650:continue
    chosen=None;best=10
    for z,raise_by,spread in sections:
        error=abs(original.z-z)
        if error<best:best=error;chosen=(z,raise_by,spread)
    if best>.006:continue
    p=v.co;rear=smooth((.050-p.y)/.095)
    p.z+=chosen[1]*rear
    p.x*=1+chosen[2]*rear
# Restore a small amount of chin projection for the primary portrait after
# the compact-chin correction; the jaw itself now provides the lower turn.
for v in h.data.vertices:
    p=v.co
    if v.index<764 and p.y>.041 and 1.570<p.z<1.612:
        w=math.exp(-((p.z-1.585)/.012)**2)*math.exp(-(p.x/.035)**4)
        p.y+=.0025*w;p.z-=.0015*w
h['revision_notes']='Reconstructed mandibular sections from chin to rear jaw angle, preserving open neck base. No head width rescale or hair-family change.'
h.data.update();bm=bmesh.new();bm.from_mesh(h.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(h.data);bm.free()
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
s['render_allowlist']=json.dumps([o.name for o in s.objects if not o.hide_render])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','primary_fit']:
    s.camera=bpy.data.objects[s.name+'_'+label];s.render.resolution_x=840 if label=='primary_fit' else 900;s.render.resolution_y=788 if label=='primary_fit' else 900
    s.render.filepath=ROOT+'/captures/r012_'+label+'.png';bpy.ops.render.render(write_still=True)
s.render.resolution_x=900;s.render.resolution_y=900
print('HP1 r012 mandible sections executed and rendered.')
