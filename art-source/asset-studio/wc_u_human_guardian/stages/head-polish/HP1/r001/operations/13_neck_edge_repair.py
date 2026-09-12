import bpy,bmesh,json,math
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
s=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=s
assert '/head-polish/HP1/r001/' in bpy.data.filepath.replace('\\','/')
assert bpy.context.object is None or bpy.context.object.mode=='OBJECT'
assert bpy.data.objects.get('HP1_HEAD_POLISH_Head_r013') is None
rejected=bpy.data.objects['HP1_HEAD_POLISH_Head_r012'];rejected.hide_render=True;rejected.hide_set(True)
old=bpy.data.objects['HP1_HEAD_POLISH_Head_r011'];h=old.copy();h.data=old.data.copy();h.name='HP1_HEAD_POLISH_Head_r013';s.collection.objects.link(h);h.hide_render=False;h.hide_set(False)
# Reject the r012 ear-base shelf. Rebuild only the two neck-edge arc rows
# which had nonmonotone back points, including a defect inherited from FH1.
# Boundary count and connectivity are retained; original files untouched.
for row,rear,back_z in [(0,-.054,1.563),(1,-.057,1.580)]:
    a=h.data.vertices[row*40].co.copy();b=h.data.vertices[row*40+24].co.copy()
    width=(abs(a.x)+abs(b.x))*.5;side_y=(a.y+b.y)*.5;side_z=(a.z+b.z)*.5
    for j in range(1,16):
        angle=math.pi*j/16
        h.data.vertices[row*40+24+j].co=(width*math.cos(angle),side_y+(rear-side_y)*math.sin(angle),side_z+(back_z-side_z)*math.sin(angle))
# A restrained mandibular body turn forward/below the ear, not a displacement
# of the lower ear attachment or a horizontal shelf at its base.
for v in h.data.vertices:
    p=v.co
    if v.index<764 and p.y>-.015 and p.z<1.634 and p.z>1.580:
        w=math.exp(-((abs(p.x)-.053)/.014)**2-((p.y-.012)/.028)**2-((p.z-1.609)/.012)**2)
        p.x+=(1 if p.x>0 else -1)*.0025*w;p.y-=.0013*w
h.data.update();bm=bmesh.new();bm.from_mesh(h.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(h.data);bm.free()
h['revision_notes']='Retains r011 facial work; rejects r012 ear-base shelf; repairs crossing neck arcs and places a restrained low mandibular turn.'
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
s['render_allowlist']=json.dumps([o.name for o in s.objects if not o.hide_render])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','primary_fit']:
    s.camera=bpy.data.objects[s.name+'_'+label];s.render.resolution_x=840 if label=='primary_fit' else 900;s.render.resolution_y=788 if label=='primary_fit' else 900
    s.render.filepath=ROOT+'/captures/r013_'+label+'.png';bpy.ops.render.render(write_still=True)
s.render.resolution_x=900;s.render.resolution_y=900
print('HP1 r013 repaired neck arcs and retained r011 likeness baseline.')
