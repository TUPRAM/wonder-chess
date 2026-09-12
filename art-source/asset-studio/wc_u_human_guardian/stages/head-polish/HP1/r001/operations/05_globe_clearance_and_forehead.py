import bpy,bmesh,json,math
from mathutils import Vector
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
s=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=s
assert bpy.data.objects.get('HP1_HEAD_POLISH_Head_r006') is None
old=bpy.data.objects['HP1_HEAD_POLISH_Head_r005'];h=old.copy();h.data=old.data.copy();h.name='HP1_HEAD_POLISH_Head_r006';s.collection.objects.link(h);old.hide_render=True;old.hide_set(True)
f=json.loads(h['feature_indices']);orbits=json.loads(h['orbital_rings'])
def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
# Seat a smaller globe in the narrowed head. The side of the former globe
# penetrated the outer canthus after the lateral proportion edit.
for side,sign in [('R',1),('L',-1)]:
    eye=bpy.data.objects['HP1_HEAD_POLISH_Eye_'+side]
    eye.location=(sign*.034,.039,1.690);eye.scale=(.021/.0245,)*3
for ring,sign in zip(orbits,[1,-1]):
    for layer in [0,1]:
        for j in range(20):
            p=h.data.vertices[ring[layer*20+j]].co
            radius=.021
            p.y=.039+math.sqrt(max(.000001,radius*radius-(abs(p.x)-.034)**2-(p.z-1.690)**2))+[.00035,.0010][layer]
    for j in range(20):
        root=h.data.vertices[ring[80+j]].co
        if root.z<1.677:root.y-=.0017
    for layer,t in [(2,.18),(3,.57)]:
        for j in range(20):
            inner=h.data.vertices[ring[20+j]].co.copy();outer=h.data.vertices[ring[80+j]].co.copy();p=inner.lerp(outer,t)
            # Only these two orbital transition rings use a minimum globe
            # clearance. The cheek is not projected onto a sphere.
            rr=.021**2-(abs(p.x)-.034)**2-(p.z-1.690)**2
            if rr>0:p.y=max(p.y,.039+math.sqrt(rr)+.001)
            h.data.vertices[ring[layer*20+j]].co=p
# Replace inherited brow humps with a broad continuous frontal bone plane.
# This spans both temples and the glabella; no rectangular smoothing region.
orbital_interior=set(orbits[0][:60]+orbits[1][:60])
for v in h.data.vertices:
    p=v.co;x=abs(p.x)
    if p.y>.006 and p.z>1.704 and p.z<1.751 and v.index not in orbital_interior:
        weight=smooth((p.z-1.704)/.011)*(1-smooth((p.z-1.730)/.021))
        surface=.062-.037*(min(1,x/.073)**2.7)-.005*smooth((p.z-1.718)/.020)
        p.y=p.y*(1-weight)+surface*weight
# Tame the under-eye pad without erasing the cheek's lateral plane.
for v in h.data.vertices:
    p=v.co;x=abs(p.x)
    if p.y>.015 and v.index not in orbital_interior:
        p.y-=.0015*math.exp(-((x-.045)/.023)**2-((p.z-1.669)/.009)**2)
h.data.update();bm=bmesh.new();bm.from_mesh(h.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(h.data);bm.free()
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
h['revision_notes']='Smaller seated globe, localized lid/socket clearance, continuous glabella and forehead plane, reduced under-eye pad.'
s['render_allowlist']=json.dumps([o.name for o in s.objects if not o.hide_render])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','portrait']:
    s.camera=bpy.data.objects[s.name+'_'+label];s.render.filepath=ROOT+'/captures/r006_'+label+'.png';bpy.ops.render.render(write_still=True)
print('HP1 r006 globe clearance and forehead rendered.')
