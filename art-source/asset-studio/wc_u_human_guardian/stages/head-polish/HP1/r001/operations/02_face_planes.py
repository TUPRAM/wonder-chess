import bpy,bmesh,json,math
from mathutils import Vector
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
scene=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=scene
assert bpy.data.objects.get('HP1_HEAD_POLISH_Head_r003') is None
old=bpy.data.objects['HP1_HEAD_POLISH_Head_r002'];h=old.copy();h.data=old.data.copy();h.name='HP1_HEAD_POLISH_Head_r003';scene.collection.objects.link(h)
old.hide_render=True;old.hide_set(True)
features=json.loads(h['feature_indices']);orbits=json.loads(h['orbital_rings'])
def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
# Reposition the diagnostic globes together with their anatomical lid cages.
for o in scene.objects:
    if 'Diagnostic_Eye' in o.name:o.location.y+=.010
# The surrounding cheek and outer socket use their own planes. These edits
# include the shared port roots so a displaced isolated patch cannot remain.
for v in h.data.vertices:
    p=v.co;x=abs(p.x)
    if v.index<764 and p.y>0 and .018<x<.072 and 1.640<p.z<1.730:
        weight=smooth((x-.018)/.020)*(1-smooth((x-.056)/.016))
        vertical=smooth((p.z-1.640)/.025)*(1-smooth((p.z-1.710)/.020))
        p.y+=.010*weight*vertical
# Purposeful nasal cross sections, with a broad root, separate bridge and tip.
nose=features['nose']
sections={3:(.020,.083,.064),4:(.019,.079,.062),5:(.018,.074,.060),6:(.019,.068,.061),7:(.020,.065,.064),8:(.021,.065,.064)}
for row,(width,center,edge) in sections.items():
    for j in range(9):
        q=(j-4)/4;p=h.data.vertices[nose[row*9+j]].co
        p.x=width*q;p.y=edge+(center-edge)*(1-abs(q)**1.6)
# Restore a broad, rounded upper-lid arc. The margin alone follows the globe;
# the socket ring is authored against independent face planes.
for ring,sign in zip(orbits,[1,-1]):
    outside=[h.data.vertices[i].co.copy() for i in ring[80:100]]
    for layer in range(4):
        for j in range(20):
            angle=math.radians(225+j*18);q=math.cos(angle);s=math.sin(angle)
            x=.034+.0194*q
            z=1.6894+.0020*q+(.0107 if s>=0 else .0080)*s
            if layer==1:
                x=.034+(x-.034)*1.024;z=1.6894+(z-1.6894)*1.09
            elif layer==2:
                x=.034+(x-.034)*1.13;z=1.6894+(z-1.6894)*1.40
            if layer<3:
                y=.042+math.sqrt(max(.000002,.023**2-(x-.034)**2-(z-1.690)**2))+[.0006,.0012,.0018][layer]
                p=Vector((sign*x,y,z))
            else:
                p=h.data.vertices[ring[40+j]].co*.50+outside[j]*.50
                # No abrupt medial-depth threshold. Interpolate continuously
                # into the shared nose and brow boundary instead.
            h.data.vertices[ring[layer*20+j]].co=p
# One shallow philtrum and quiet upper-muzzle transition. Lip body keeps
# independent volume; support rings no longer make a scalloped surface band.
mouth=features['mouth']
for local,i in enumerate(mouth):
    layer=local//34;p=h.data.vertices[i].co;q=min(1,abs(p.x)/.027)
    if layer<=3:p.y+=.0015*(1-q*q)
    elif layer==4:p.y+=.0025*(1-q*q)*(1 if p.z>1.6244 else .55)
    elif layer in [5,6,7] and p.z>1.627:
        base=[0,0,0,0,0,.0695,.0691,.0695][layer]
        p.y=base-.009*q*q
        if layer==6:
            a=h.data.vertices[mouth[5*34+local%34]].co
            b=h.data.vertices[mouth[7*34+local%34]].co
            p.z=a.z*.70+b.z*.30
for j in range(9):
    p=h.data.vertices[nose[j]].co;q=abs((j-4)/4);p.y=.070-.009*q*q
# Shape the bulb and nostril wings together; retain actual internal vaults.
for j in range(1,8):
    p=h.data.vertices[nose[18+j]].co
    if j==4:p.y=.089;p.z=1.660
    else:p.z+=.0022;p.y+=.002
for j in [1,2,3,5,6,7]:h.data.vertices[nose[9+j]].co.z+=.001
h.data.vertices[nose[13]].co.y=.079;h.data.vertices[nose[13]].co.z=1.650
# Continuous lower-cheek recession and a jaw angle behind the chin. Broad
# influence keeps the neck junction free of rectangular displacement edges.
ear_ids=set()
for g in h.vertex_groups:
    if 'Ear' in g.name:
        for v in h.data.vertices:
            if any(a.group==g.index for a in v.groups):ear_ids.add(v.index)
for v in h.data.vertices:
    p=v.co;x=abs(p.x)
    if v.index<764 and p.z<1.655:
        lower=1-smooth((p.z-1.610)/.045)
        side=smooth((x-.025)/.035)
        if p.y>.005:p.y-=.004*side*lower
        if p.y<-.045:
            p.y=-.045+(p.y+.045)*(1-.68*lower)
        if 1.567<p.z<1.610:
            p.z+=.009*side*(1-smooth((p.z-1.590)/.020))
h.data.update()
bm=bmesh.new();bm.from_mesh(h.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(h.data);bm.free()
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
scene['render_allowlist']=json.dumps([o.name for o in scene.objects if not o.hide_render])
h['revision_notes']='Re-established globe/socket depth, upper-lid arch, whole shared facial planes, continuous philtrum, rounded nasal tip and jaw angle; no hair, eyebrow or eyelash changes.'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','portrait']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/r003_'+label+'.png';bpy.ops.render.render(write_still=True)
print('HP1 r003 saved and rendered.')
