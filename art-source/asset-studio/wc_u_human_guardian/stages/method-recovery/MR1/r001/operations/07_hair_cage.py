import bpy,bmesh,json
from mathutils import Vector
assert bpy.data.filepath.replace('\\','/').endswith('/method-recovery/MR1/r001/ada_method_proof_work.blend')
assert bpy.data.scenes.get('MR1_HAIR_PROOF') is None
root='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001'
scene=bpy.data.scenes.new('MR1_HAIR_PROOF');bpy.context.window.scene=scene
col=bpy.data.collections.new('MR1_HAIR_CANDIDATE_ALLOWLIST');scene.collection.children.link(col)
context_names=['ADA_Head_Continuous','ADA_Neck','ADA_Ear_Pinna_L','ADA_Ear_Helix_L','ADA_Ear_Pinna_R','ADA_Ear_Helix_R','ADA_Fitted_Eye_L','ADA_Fitted_Brow_L','ADA_Fitted_Eye_R','ADA_Fitted_Brow_R','ADA_Hair_Foundation']
context=[]
for name in context_names:
    src=bpy.data.objects[name];o=src.copy();o.data=src.data.copy();o.name='MR1_HAIR_CONTEXT_'+name;col.objects.link(o);o.hide_render=False;o.hide_viewport=False;o.hide_set(False);o['mr1_context_source']=name;context.append(o)
# Explicit stations measured relative to the preserved scalp; only local contacts
# were consulted. No vertex projection or whole-volume constraint is used.
centers=[(-.0245,.0064,1.8016),(-.0074,.0213,1.7975),(.0122,.0372,1.7817),(.0351,.0435,1.7614),(.0622,.0354,1.7428),(.0846,.0166,1.7209),(.0966,-.0172,1.6974),(.0931,-.0506,1.6830),(.0814,-.0616,1.6870)]
normals=[(-.306,.410,.859),(-.093,.619,.780),(.116,.774,.623),(.392,.810,.437),(.646,.692,.323),(.886,.428,.178),(.999,.035,.035),(.962,-.268,-.052),(.927,-.375,-.028)]
widths=[.005,.014,.024,.026,.023,.019,.015,.008,.002]
# Each five-sample top profile has independently authored crest position and depth.
top=[[-.001,-.0004,.0003,.0006,-.001],[-.001,.004,.008,.009,.0005],[0,.009,.016,.013,.0005],[.0005,.011,.018,.011,.0003],[.0002,.010,.016,.009,.0001],[0,.009,.012,.006,0],[-.0005,.006,.009,.003,-.0003],[-.0007,.003,.006,.004,-.0004],[-.0008,.0001,.001,.0003,-.0008]]
under=[[-.0025,-.002,-.0015,-.0018,-.0025],[-.0035,-.0015,-.0008,-.0017,-.0035],[-.0045,-.0015,-.0007,-.0015,-.0045],[-.005,-.002,-.0008,-.0018,-.0048],[-.0045,-.0018,-.0008,-.0015,-.004],[-.0035,-.0013,-.0007,-.0012,-.0032],[-.0025,-.0012,-.0008,-.0012,-.0025],[-.0018,-.0011,-.0008,-.001,-.0016],[-.0015,-.0012,-.001,-.0012,-.0015]]
fractions=[-1,-.55,0,.55,1]
verts=[];frames=[]
for i,c in enumerate(centers):
    c=Vector(c);n=Vector(normals[i]).normalized()
    tangent=Vector(centers[min(i+1,8)])-Vector(centers[max(i-1,0)])
    tangent=(tangent-n*tangent.dot(n)).normalized();across=n.cross(tangent).normalized();frames.append((list(tangent),list(across),list(n)))
    for heights in [top[i],under[i]]:
        for j,f in enumerate(fractions):verts.append(tuple(c+across*(widths[i]*f)+n*heights[j]))
faces=[]
for i in range(8):
    for j in range(4):
        faces.append((i*10+j,i*10+j+1,(i+1)*10+j+1,(i+1)*10+j))
        faces.append((i*10+5+j,(i+1)*10+5+j,(i+1)*10+6+j,i*10+6+j))
    faces.extend([(i*10,(i+1)*10,(i+1)*10+5,i*10+5),(i*10+4,i*10+9,(i+1)*10+9,(i+1)*10+4)])
for i in [0,8]:
    for j in range(4):faces.append((i*10+j,i*10+5+j,i*10+6+j,i*10+j+1))
me=bpy.data.meshes.new('MR1_Hair_Leading_Sweep_ControlMesh');me.from_pydata(verts,[],faces);me.update()
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
hair=bpy.data.objects.new('MR1_Hair_Leading_Sweep_Cage',me);col.objects.link(hair)
me.materials.append(bpy.data.materials['MR1_Uniform_Clay'])
for p in me.polygons:p.use_smooth=True
sub=hair.modifiers.new('One subdivision level proof','SUBSURF');sub.levels=1;sub.render_levels=1
hair['mr1_method']='Nine individually shaped stations; five top and five underside samples; flat fitted underside and independent asymmetric crest; finite quad-capped taper'
hair['mr1_station_spec']=json.dumps({'centers':centers,'normals':normals,'half_widths':widths,'top':top,'underside':under,'frames':frames})
hair['mr1_scope']='Single leading sweep method proof; incomplete hairstyle'
vg=hair.vertex_groups.new(name='Root_And_Selected_Underside');vg.add(list(range(10)),1,'REPLACE');vg.add([15,16,17,18,19],.5,'REPLACE');vg.add([55,56,57,58,59,65,66,67,68,69],.5,'REPLACE')
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.world=bpy.data.worlds['MR1_Neutral_World']
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
scene.view_layers[0].material_override=bpy.data.materials['MR1_Uniform_Clay']
target=Vector((0,-.020,1.737))
def camera(name,pos,aim=target,scale=.275):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);col.objects.link(o);o.location=pos;o.rotation_euler=(Vector(aim)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;d.clip_start=.001;d.clip_end=20;d.dof.use_dof=False;return o
for n,p in [('front',(0,.65,1.737)),('profile',(.65,-.020,1.737)),('three_quarter',(.42,.52,1.80)),('rear',(0,-.65,1.737)),('top',(0,-.02,2.38))]:camera('MR1_HAIR_'+n,p)
camera('MR1_HAIR_root',(-.08,.20,2.1),(-.008,.025,1.797),.085)
for n,p,e,sz in [('Key',(-.28,.38,2.06),3.4,.35),('Fill',(.32,.24,1.83),.8,.35)]:
    d=bpy.data.lights.new('MR1_HAIR_'+n,'AREA');o=bpy.data.objects.new('MR1_HAIR_'+n,d);col.objects.link(o);o.location=p;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();d.energy=e;d.shape='DISK';d.size=sz
scene.camera=bpy.data.objects['MR1_HAIR_three_quarter']
scene['mr1_operation']='hair_initial_shaped_wedge';scene['mr1_hair_corrections']=0;scene['mr1_render_allowlist']=json.dumps([o.name for o in col.objects])
for o in scene.objects:o.select_set(False)
hair.select_set(True);bpy.context.view_layer.objects.active=hair
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        s=a.spaces.active;s.region_3d.view_location=target;s.region_3d.view_distance=.38;s.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion();s.region_3d.view_perspective='ORTHO';s.shading.type='SOLID';s.shading.color_type='MATERIAL';s.overlay.show_extras=False;s.overlay.show_floor=False
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for v in ['front','profile','three_quarter','rear','top','root']:
    scene.camera=bpy.data.objects['MR1_HAIR_'+v];scene.render.filepath=root+'/captures/hair_r001_clay_'+v+'.png';bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects['MR1_HAIR_three_quarter']
print(json.dumps({'hair_vertices':len(me.vertices),'hair_faces':len(me.polygons),'scene':scene.name,'allowlist':json.loads(scene['mr1_render_allowlist'])}))
