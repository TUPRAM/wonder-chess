import bpy,bmesh,json,math
from mathutils import Vector
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/features-head/FH1/r001'
assert bpy.data.objects.get('FH1_Nose_Control_Cage_r002') is None
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/features_initial_checkpoint.blend',copy=True)
scene=bpy.data.scenes['FH1_NOSE_STUDY'];bpy.context.window.scene=scene
old=bpy.data.objects['FH1_Nose_Control_Cage'];nose=old.copy();nose.data=old.data.copy();nose.name='FH1_Nose_Control_Cage_r002'
scene.collection.objects.link(nose);old.hide_render=True;old.hide_set(True)
margin=old.vertex_groups['Nostril_Margins'].index
ids=[v.index for v in old.data.vertices if any(g.group==margin for g in v.groups)]
for i in ids+list(range(81,105)):
    p=nose.data.vertices[i].co;side=1 if p.x>0 else -1
    p.x=side*.0108+(p.x-side*.0108)*.67
    p.y=.087+(p.y-.087)*.78-.003
    p.z=1.6505+(p.z-1.6505)*.44-.001
# Short columella beneath a compact tip, plus supported fleshy alar wings.
nose.data.vertices[13].co.y=.088;nose.data.vertices[13].co.z=1.647
for i in [10,16]:nose.data.vertices[i].co.y=.078
for i in [19,25]:nose.data.vertices[i].co.y=.089
nose.data.update();nose['correction']='Pass 1: smaller recessed downward nostrils, fleshy wings and short columella; unchanged head boundary.'
scene['render_allowlist']=json.dumps([o.name for o in scene.objects if not o.hide_render])
for label in ['front','profile','three_quarter','underside']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/nose_r002_'+label+'.png';bpy.ops.render.render(write_still=True)

scene=bpy.data.scenes['FH1_MOUTH_STUDY'];bpy.context.window.scene=scene
old=bpy.data.objects['FH1_Mouth_Control_Cage'];count=34
oldverts=[tuple(v.co) for v in old.data.vertices];verts=[]
# Add two short, purposeful contact support rows. This controls the lips'
# meeting edge under subdivision without thickening a painted slit.
for layer in range(9):
    source_layer=[0,1,1,1,2,3,4,5,6][layer]
    for j in range(count):
        x,y,z=oldverts[source_layer*count+j];q=min(1,abs(x)/.027)
        s=1 if z>=1.6213 else -1
        line=1.621+.0008*max(0,1-q*q)-.0004*math.exp(-(x/.0042)**2)
        if layer<=3:
            upper=oldverts[2*count+j][2]>oldverts[count+j][2];sign=1 if upper else -1
            y=oldverts[count+j][1]+[-.004,-.0008,0,.00025][layer]
            z=line+sign*[.00010,.00006,.000045,.00018][layer]
        if layer<7:
            x*=.94
            y=.057+(y-.057)*.73
            if layer>=4:z=line+(z-line)*(.92-.18*q*q)
        elif layer==7:
            x*=.98;y=.057+(y-.057)*.94
        verts.append((x,y,z))
faces=[(k*count+j,k*count+(j+1)%count,(k+1)*count+(j+1)%count,(k+1)*count+j) for k in range(8) for j in range(count)]
m=bpy.data.meshes.new('FH1_Mouth_r002_ControlMesh');m.from_pydata(verts,[],faces);m.update()
bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
mouth=bpy.data.objects.new('FH1_Mouth_Control_Cage_r002',m);scene.collection.objects.link(mouth);m.materials.append(bpy.data.materials['MR1_Uniform_Clay'])
for p in m.polygons:p.use_smooth=True
sub=mouth.modifiers.new('Editable cage preview','SUBSURF');sub.levels=2;sub.render_levels=2
root=mouth.vertex_groups.new(name='Matched_Head_Interface');root.add(list(range(272,306)),1,'REPLACE')
vg=mouth.vertex_groups.new(name='Lip_Contact_Support');vg.add(list(range(34,136)),1,'REPLACE')
mouth['interface_indices']=json.dumps(list(range(272,306)))
mouth['correction']='Pass 1: contact support loops, restrained lip projection, tapered lateral fullness; unchanged head boundary.'
old.hide_render=True;old.hide_set(True);scene['render_allowlist']=json.dumps([o.name for o in scene.objects if not o.hide_render])
bpy.context.view_layer.objects.active=mouth;mouth.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/mouth_r002_'+label+'.png';bpy.ops.render.render(write_still=True)
print('Nose and mouth correction pass 1 executed; original sources retained hidden.')
