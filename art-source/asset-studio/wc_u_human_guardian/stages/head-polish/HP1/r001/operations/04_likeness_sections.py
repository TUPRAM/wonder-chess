import bpy,bmesh,json,math
from mathutils import Vector
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
scene=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=scene
assert bpy.data.objects.get('HP1_HEAD_POLISH_Head_r005') is None
old=bpy.data.objects['HP1_HEAD_POLISH_Head_r004'];h=old.copy();h.data=old.data.copy();h.name='HP1_HEAD_POLISH_Head_r005';scene.collection.objects.link(h);old.hide_render=True;old.hide_set(True)
f=json.loads(h['feature_indices']);orbits=json.loads(h['orbital_rings'])
def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
# The inner corner flow encloses the aperture without crushing the nasal
# control columns into a central ridge. This changes both sides of the join.
for ring,sign in zip(orbits,[1,-1]):
    for j in range(20):
        p=h.data.vertices[ring[80+j]].co
        if abs(p.x)<.012:p.x=sign*(.008+(abs(p.x)-.0024)*.42)
        if p.z>1.701:p.y-=.003*smooth((p.z-1.701)/.014)
    for layer,t in [(2,.16),(3,.57)]:
        for j in range(20):
            inner=h.data.vertices[ring[20+j]].co.copy();outer=h.data.vertices[ring[80+j]].co.copy()
            p=inner.lerp(outer,t)
            if layer==2:p.y+=.0007
            h.data.vertices[ring[layer*20+j]].co=p
nose=f['nose'];centers={3:(.084,1.668),4:(.0755,1.679),5:(.0655,1.689),6:(.0605,1.699),7:(.0607,1.709),8:(.0615,1.720)}
for row,(depth,height) in centers.items():
    left=h.data.vertices[nose[row*9]].co.copy();right=h.data.vertices[nose[row*9+8]].co.copy()
    for j in range(1,8):
        q=(j-4)/4;edge=right if q>=0 else left;p=h.data.vertices[nose[row*9+j]].co
        p.x=abs(edge.x)*q;p.y=depth+(edge.y-depth)*abs(q)**1.4;p.z=height+(edge.z-height)*abs(q)**1.2
# The head was wider relative to pupil spacing than the visible cheeks in
# the supplied front study. Keep central features and reduce lateral breadth
# continuously through cheeks, temples and ears.
for v in h.data.vertices:
    p=v.co;x=abs(p.x);sign=1 if p.x>=0 else -1
    lateral=smooth((x-.043)/.026)
    p.x=sign*(x-.0115*lateral)
    # High cheek and lower cheek are different planes, not one inflated oval.
    if .025<x<.076 and p.y>.012:
        cheek=math.exp(-((x-.052)/.020)**2)
        p.y+=.0025*cheek*math.exp(-((p.z-1.673)/.011)**2)
        p.y-=.0028*cheek*math.exp(-((p.z-1.636)/.019)**2)
# Skin-only expression: bring the upper central lid down slightly, preserving
# the outer canthus and a convex arch rather than recreating the flat slit.
for ring in orbits:
    for layer in range(3):
        for j in range(20):
            p=h.data.vertices[ring[layer*20+j]].co
            if p.z>1.693:
                w=math.exp(-((abs(p.x)-.035)/.010)**2)
                p.z-=.0015*w
# Fuller lower lip and a restrained cupid's bow. The surrounding skin stays
# quiet; this is geometric volume with no color or cosmetic hair additions.
mouth=f['mouth']
for local,i in enumerate(mouth):
    layer=local//34;p=h.data.vertices[i].co;q=min(1,abs(p.x)/.025)
    if layer==4 and p.z<1.6244:p.z-=.0010*(1-q*q);p.y+=.0007*(1-q*q)
    if layer in [5,6] and p.z>1.628:p.z-=.00065*math.exp(-((abs(p.x)-.008)/.005)**2)
h.data.update();bm=bmesh.new();bm.from_mesh(h.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(h.data);bm.free()
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
h['revision_notes']='Broadened nasal root columns, shallow nasion, lateral head proportion correction, high-cheek and lower-cheek planes, upper-lid expression and restrained lip volumes.'
scene['render_allowlist']=json.dumps([o.name for o in scene.objects if not o.hide_render])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','portrait']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/r005_'+label+'.png';bpy.ops.render.render(write_still=True)
print('HP1 r005 likeness sections saved and rendered.')
