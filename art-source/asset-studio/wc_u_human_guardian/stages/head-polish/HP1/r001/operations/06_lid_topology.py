import bpy,bmesh,json,math
from mathutils import Vector
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
s=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=s
assert bpy.data.objects.get('HP1_HEAD_POLISH_Head_r007') is None
old=bpy.data.objects['HP1_HEAD_POLISH_Head_r006'];oldrings=json.loads(old['orbital_rings'])
verts=[tuple(v.co) for v in old.data.vertices];inner=set(oldrings[0][:80]+oldrings[1][:80])
faces=[tuple(p.vertices) for p in old.data.polygons if not any(i in inner for i in p.vertices)]
# Anatomical-right opening, ordered from lower-medial arc around outer
# canthus, upper arc and tear corner. These are explicit feature controls.
outline=[(.023,1.6837),(.028,1.6823),(.034,1.6821),(.040,1.6831),(.046,1.6851),(.0505,1.6878),(.053,1.6901),(.0535,1.6915),(.052,1.6941),(.0485,1.6970),(.044,1.6990),(.0385,1.7000),(.0325,1.6998),(.027,1.6985),(.0225,1.6962),(.019,1.6930),(.0168,1.6900),(.0162,1.6882),(.018,1.6863),(.020,1.6848)]
newrings=[]
def sphere(x,z):return .039+math.sqrt(max(.000001,.021**2-(x-.034)**2-(z-1.690)**2))
for oldring,sign in zip(oldrings,[1,-1]):
    transition=list(range(len(verts),len(verts)+20));verts.extend([(0,0,0)]*20)
    ring=oldring[:80]+transition+oldring[80:100];newrings.append(ring)
    for j in range(20):
        root=Vector(verts[ring[100+j]])
        if abs(root.x)<.017:
            w=max(0,1-abs(root.z-1.690)/.025)
            root.y-=.005*w
        verts[ring[100+j]]=tuple(root)
    for layer in range(5):
        for j,(x0,z0) in enumerate(outline):
            x=x0;z=z0
            if layer in [0,1]:
                y=sphere(x,z)+[-.0010,.00035][layer]
            elif layer==2:
                x=.034+(x-.034)*1.055;z=1.690+(z-1.690)*1.19
                y=sphere(x,z)+.0014
            elif layer==3:
                x=.034+(x-.034)*1.12;z=1.690+(z-1.690)*1.43
                y=sphere(x,z)+(.0006 if z>1.692 else .0013)
            else:
                a=Vector(verts[ring[60+j]]);b=Vector(verts[ring[100+j]])
                p=a.lerp(b,.53);x=abs(p.x);z=p.z;y=p.y
                rr=.021**2-(x-.034)**2-(z-1.690)**2
                if rr>0:y=max(y,.039+math.sqrt(rr)+.001)
            verts[ring[layer*20+j]]=(sign*x,y,z)
    for layer in range(5):
        for j in range(20):faces.append((ring[layer*20+j],ring[layer*20+(j+1)%20],ring[(layer+1)*20+(j+1)%20],ring[(layer+1)*20+j]))
m=bpy.data.meshes.new('HP1_Head_r007_LidFlow');m.from_pydata(verts,[],faces);m.update()
bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
h=old.copy();h.data=m;h.name='HP1_HEAD_POLISH_Head_r007';s.collection.objects.link(h);old.hide_render=True;old.hide_set(True)
for mat in old.data.materials:m.materials.append(mat)
for p in m.polygons:p.use_smooth=True
h['orbital_rings']=json.dumps(newrings)
h['revision_notes']='Changed lid topology: 20 authored opening controls, inset inner wall, margin, lid body, crease and independent socket transition. The rest of the connected mesh is retained.'
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
s['render_allowlist']=json.dumps([o.name for o in s.objects if not o.hide_render])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','portrait']:
    s.camera=bpy.data.objects[s.name+'_'+label];s.render.filepath=ROOT+'/captures/r007_'+label+'.png';bpy.ops.render.render(write_still=True)
print('HP1 r007 purpose-built eyelid topology executed and rendered.')
