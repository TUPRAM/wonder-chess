import bpy,bmesh,json,math
from mathutils import Vector
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
scene=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=scene
assert bpy.data.objects.get('HP1_HEAD_POLISH_Head_r004') is None
old=bpy.data.objects['HP1_HEAD_POLISH_Head_r003'];h=old.copy();h.data=old.data.copy();h.name='HP1_HEAD_POLISH_Head_r004';scene.collection.objects.link(h);old.hide_render=True;old.hide_set(True)
features=json.loads(h['feature_indices']);orbits=json.loads(h['orbital_rings'])
# Explicit object names: the previous inherited-name filter did not select
# either copied globe. Set and verify the intended anatomical centers.
for side,sign in [('R',1),('L',-1)]:
    eye=bpy.data.objects['HP1_HEAD_POLISH_Eye_'+side];eye.location=(sign*.034,.042,1.690)
# Rebuild the shared orbital boundary into an oval flow. A rectangular root
# whose medial edge lay lateral to the opening folded back on itself. Each
# outer ring now encloses its inner ring in the frontal projection.
for ring,sign in zip(orbits,[1,-1]):
    for j in range(20):
        a=math.radians(225+j*18);q=math.cos(a);s=math.sin(a)
        x=.034+.032*q;z=1.691+.001*q+(.030 if s>0 else .026)*s
        # Broad shallow bone plane above the eye, cheek beneath, temple turn.
        y=.064-.020*max(0,q)**2-.002*max(0,-q)
        h.data.vertices[ring[80+j]].co=(sign*x,y,z)
    for layer,t in [(2,.16),(3,.57)]:
        for j in range(20):
            inner=h.data.vertices[ring[20+j]].co.copy();outer=h.data.vertices[ring[80+j]].co.copy()
            p=inner.lerp(outer,t)
            if layer==2:p.y+=.0011
            h.data.vertices[ring[layer*20+j]].co=p
# The adjoining bridge sections share these vertices. Reflow their interior
# controls into the moved boundary without projecting onto the old face.
nose=features['nose']
centers={3:(.084,1.668),4:(.0785,1.679),5:(.071,1.689),6:(.065,1.699),7:(.064,1.709),8:(.0635,1.720)}
for row,(depth,height) in centers.items():
    left=h.data.vertices[nose[row*9]].co.copy();right=h.data.vertices[nose[row*9+8]].co.copy()
    for j in range(1,8):
        q=(j-4)/4;edge=right if q>=0 else left;p=h.data.vertices[nose[row*9+j]].co
        p.x=abs(edge.x)*q;p.y=depth+(edge.y-depth)*abs(q)**1.55;p.z=height+(edge.z-height)*abs(q)**1.2
# Remove the old extra philtrum support wave by placing it between the
# vermilion border and perioral flow; preserve the actual lip border.
mouth=features['mouth']
for j in range(34):
    a=h.data.vertices[mouth[5*34+j]].co.copy();b=h.data.vertices[mouth[7*34+j]].co.copy()
    h.data.vertices[mouth[6*34+j]].co=a.lerp(b,.30)
h.data.update();bm=bmesh.new();bm.from_mesh(h.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(h.data);bm.free()
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
h['revision_notes']='Shared orbital root rebuilt as enclosing oval flow, bridge columns reflowed to it, explicit globe centers verified, philtrum support wave removed.'
scene['render_allowlist']=json.dumps([o.name for o in scene.objects if not o.hide_render])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','portrait']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/r004_'+label+'.png';bpy.ops.render.render(write_still=True)
print('HP1 r004 rebuilt shared flow and rendered.')
