import bpy,bmesh,json,math
from mathutils import Vector
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
s=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=s
assert '/head-polish/HP1/r001/' in bpy.data.filepath.replace('\\','/')
assert bpy.data.objects.get('HP1_HEAD_POLISH_Head_r014') is None
old=bpy.data.objects['HP1_HEAD_POLISH_Head_r013'];h=old.copy();h.data=old.data.copy();h.name='HP1_HEAD_POLISH_Head_r014';s.collection.objects.link(h);old.hide_render=True;old.hide_set(True)
rings=json.loads(h['orbital_rings'])
weights={7:0,8:.12,9:.38,10:.70,11:.95,12:1,13:.90,14:.65,15:.25,16:0}
for ring in rings:
    for layer,amount in [(0,1),(1,1),(2,.88),(3,.58),(4,.2)]:
        for j,w in weights.items():
            p=h.data.vertices[ring[layer*20+j]].co;x=abs(p.x);old_z=p.z
            p.z-=.0022*w*amount
            if layer<3:
                a=math.sqrt(max(.000001,.021**2-(x-.034)**2-(old_z-1.690)**2))
                b=math.sqrt(max(.000001,.021**2-(x-.034)**2-(p.z-1.690)**2))
                p.y+=b-a
h.data.update();bm=bmesh.new();bm.from_mesh(h.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(h.data);bm.free()
h['revision_notes']='Retained r013 geometry and increased upper-lid coverage with an oblique convex arc. Diagnostic eye material unchanged; no hair/brow/lash edits.'
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
s['render_allowlist']=json.dumps([o.name for o in s.objects if not o.hide_render])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','primary_fit','other_three_quarter','back']:
    s.camera=bpy.data.objects[s.name+'_'+label];s.render.resolution_x=840 if label=='primary_fit' else 900;s.render.resolution_y=788 if label=='primary_fit' else 900
    s.render.filepath=ROOT+'/captures/r014_'+label+'.png';bpy.ops.render.render(write_still=True)
s.render.resolution_x=900;s.render.resolution_y=900
# Reverse the key and fill positions while retaining energy and camera.
key=bpy.data.objects[s.name+'_Key'];fill=bpy.data.objects[s.name+'_Fill'];km=key.matrix_world.copy();fm=fill.matrix_world.copy()
key.location.x=-key.location.x;fill.location.x=-fill.location.x
target=Vector((0,-.008,1.680));key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler();fill.rotation_euler=(target-fill.location).to_track_quat('-Z','Y').to_euler()
s.camera=bpy.data.objects[s.name+'_three_quarter'];s.render.filepath=ROOT+'/captures/r014_reverse_key.png';bpy.ops.render.render(write_still=True)
key.matrix_world=km;fill.matrix_world=fm
# Inspect the actual openings without diagnostic globes underneath them.
for side in ['R','L']:bpy.data.objects[s.name+'_Eye_'+side].hide_render=True
s.camera=bpy.data.objects[s.name+'_front'];s.render.filepath=ROOT+'/captures/r014_openings.png';bpy.ops.render.render(write_still=True)
for side in ['R','L']:bpy.data.objects[s.name+'_Eye_'+side].hide_render=False
s.camera=bpy.data.objects[s.name+'_primary_fit']
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        sp=a.spaces.active;sp.region_3d.view_rotation=s.camera.rotation_euler.to_quaternion();sp.region_3d.view_location=(0,.01,1.678);sp.region_3d.view_distance=.35;sp.region_3d.view_perspective='ORTHO'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('HP1 r014 lid coverage, six views, reversed lighting and open-lid evidence rendered.')
