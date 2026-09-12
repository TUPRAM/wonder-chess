import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
SOURCE=R.parents[1]/'BW5/armor/ada_bw5_armor_checkpoint_r003_ART_REVISE.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False)
original=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=original;original.frame_set(1)
# Native isolated scene: only copied context, independently owned rig/action and new bracer parts.
s=bpy.data.scenes.new('BW6_RIGHT_BRACER_AUTHORING_ONLY');bpy.context.window.scene=s
s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.engine='CYCLES';s.cycles.samples=20
s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.threads_mode='FIXED';s.render.threads=3;s.render.fps=24;s.frame_start=1;s.frame_end=97
s.world=original.world.copy() if original.world else bpy.data.worlds.new('BW6_Bracer_Studio')
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
col=bpy.data.collections.new('BW6_BRACER_NEW_CONSTRUCTION');s.collection.children.link(col)
ctx=bpy.data.collections.new('BW6_BRACER_UNCHANGED_CONTEXT');s.collection.children.link(ctx)
oldrig=bpy.data.objects['BW4_Armor_Independent_Rig'];rig=oldrig.copy();rig.data=oldrig.data.copy();rig.name='BW6_Bracer_Independent_Rig';ctx.objects.link(rig)
rig.animation_data.action=oldrig.animation_data.action.copy();rig.animation_data.action.name='BW6_Bracer_Preserved97_Authoring_ONLY'
assert rig.data!=oldrig.data and rig.animation_data.action!=oldrig.animation_data.action
contexts={}
for nm in ['BW4_CONTEXT_BW1_IndexedBody','BW4_CONTEXT_BW1_CoatUpper_Continuous','BW4_CONTEXT_BW1_Glove_Pair_SourceFit']:
 old=bpy.data.objects[nm];o=old.copy();o.data=old.data.copy();o.name='BW6_Bracer_CONTEXT_'+nm.removeprefix('BW4_CONTEXT_BW1_');ctx.objects.link(o)
 for m in o.modifiers:
  if m.type=='ARMATURE':m.object=rig
 if o.parent==oldrig:o.parent=rig
 o.hide_set(False);o.hide_render=False;contexts[nm]=o
 assert o.data!=old.data
 if old.data.shape_keys:assert o.data.shape_keys!=old.data.shape_keys
s.frame_set(1);bpy.context.view_layer.update()
coat=contexts['BW4_CONTEXT_BW1_CoatUpper_Continuous'];body=contexts['BW4_CONTEXT_BW1_IndexedBody'];glove=contexts['BW4_CONTEXT_BW1_Glove_Pair_SourceFit']
W=rig.matrix_world@rig.data.bones['wrist.R'].head_local;E=rig.matrix_world@rig.data.bones['lowerarm01.R'].head_local
A=(E-W).normalized();D=Vector((.7502737045,.0453408845,.6595708132));D=(D-A*D.dot(A)).normalized();T=A.cross(D).normalized()
def bvh(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(p.vertices) for p in me.polygons];ev.to_mesh_clear();return BVHTree.FromPolygons(v,f)
bvs={'body':bvh(body),'padded_sleeve':bvh(coat),'unchanged_glove':bvh(glove)}
def radial(t,a):
 q=W+A*t;d=D*math.cos(a)+T*math.sin(a);vals={}
 for nm,bv in bvs.items():
  hit=bv.ray_cast(q+d*.16,-d,.20)
  if hit[0] is not None:
   rad=(hit[0]-q).dot(d)
   if .002<rad<.13:vals[nm]=rad
 return vals
records=[]
for t in [0,.012,.025,.04,.06,.09,.12,.15,.18,.20]:
 records.append({'distance_proximal_from_wrist_m':t,'rays':[{'angle_degrees':a,'layer_radius_m':radial(t,math.radians(a))} for a in range(-180,180,15)]})
def mat(n,c,metal=0,rough=.45):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
steel=mat('BW6_Bracer_Steel_Preview',(.26,.29,.33),.65,.32);leather=mat('BW6_Bracer_Leather_Preview',(.065,.043,.032),0,.55);edge=mat('BW6_Bracer_Edge_Preview',(.38,.40,.43),.65,.32)
clay=mat('BW6_Bracer_Context_Clay',(.22,.205,.19),0,.68)
for o in contexts.values():o.data.materials.clear();o.data.materials.append(clay)
owned=[]
def create(n,vs,fs,material,wall=.002,bevel=.001,subd=0):
 me=bpy.data.meshes.new(n+'_EditableSurface');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 # An open sleeve can be oriented either way by recalc: assert its dominant normals face radially out.
 score=sum(f.normal.dot((f.calc_center_median()-W)-A*(f.calc_center_median()-W).dot(A))*f.calc_area() for f in bm.faces)
 if score<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(me);bm.free();me.materials.append(material)
 o=bpy.data.objects.new(n,me);col.objects.link(o)
 for p in me.polygons:p.use_smooth=True
 if subd:m=o.modifiers.new('Section continuity','SUBSURF');m.levels=subd;m.render_levels=subd
 if wall:m=o.modifiers.new('Outward construction wall','SOLIDIFY');m.thickness=wall;m.offset=1;m.use_even_offset=False
 if bevel:m=o.modifiers.new('Selected edge highlight','BEVEL');m.width=bevel;m.segments=2;m.limit_method='ANGLE';m.angle_limit=.55
 g=o.vertex_groups.new(name='lowerarm02.R');g.add(list(range(len(vs))),1,'REPLACE');m=o.modifiers.new('Single rigid forearm owner','ARMATURE');m.object=rig
 o['owner_bone']='lowerarm02.R';o['runtime_status']='AUTHORING_ONLY';owned.append(o);return o
def grid_surface(n,ts,angles,radius,material,wall=.002,bevel=.001,subd=0):
 vs=[];fs=[]
 for j,t in enumerate(ts):
  for a in angles:
   aa=math.radians(a);r=radius(t,aa);z=t
   # Proximal dorsal crest and shallow wrist dip give the shell intentional end profiles.
   if n.endswith('DorsalShell'):
    f=(j/(len(ts)-1))**5;z+=f*.009*max(0,math.cos(aa))
   vs.append(tuple(W+A*z+(D*math.cos(aa)+T*math.sin(aa))*r))
 N=len(angles)
 for j in range(len(ts)-1):
  for i in range(N-1):a=j*N+i;fs.append((a,a+1,a+N+1,a+N))
 return create(n,vs,fs,material,wall,bevel,subd)
def underlying(t,a):
 vals=radial(t,a);return max(vals.values(),default=.027)
def field(t,a):
 # Ring envelope is fitted from actual rest sleeve/body; crest and sidewalls remain independent planes.
 candidates=[underlying(t+dt,a+da) for dt in [-.004,0,.004] for da in [-.09,0,.09]]
 return max(candidates)+.006+.0025*max(0,math.cos(a))**6
angles=[-118,-116,-101,-83,-61,-37,-15,-4,0,4,15,37,61,83,101,116,118]
shell=grid_surface('BW6_R_Bracer_DorsalShell',[.026,.028,.054,.095,.139,.174,.177],angles,field,steel,.0024,.0008,1)
# A supple volar closure lies below the metal edges with controlled seam margins.
inner_angles=list(range(110,251,10))
closure=grid_surface('BW6_R_Bracer_VolarLeather',[.026,.028,.07,.13,.175,.177],inner_angles,lambda t,a:underlying(t,a)+.004,leather,.0018,.0005,1)
# Cuff is separate from glove; soft overlap can follow the wrist only on its distal edge.
cuff_angles=list(range(-180,181,12))
cuff=grid_surface('BW6_R_Bracer_WristCuff',[.004,.006,.017,.036,.038],cuff_angles,lambda t,a:underlying(t,a)+.004,leather,.0015,.0004,1)
# Two leather closure bands cross the inner opening, with folded ends sitting outside the shell.
for k,t in enumerate([.060,.145]):
 grid_surface('BW6_R_Bracer_ClosureStrap_'+str(k+1),[t-.007,t-.006,t+.006,t+.007],list(range(94,267,8)),lambda u,a:field(u,a)+.0036,leather,.0017,.00045,1)
# Turned borders along shell top and bottom share its fit rather than floating arbitrary rings.
for label,t in [('Wrist',.028),('Elbow',.174)]:
 grid_surface('BW6_R_Bracer_'+label+'Rim',[t-.0015,t-.0007,t+.0013,t+.0021],angles,lambda u,a:field(u,a)+.0025,edge,.0014,.0005,1)
# Camera frame is metric and fixed in the candidate, not adjusted per comparison.
target=W+A*.085
def camera(n,offset,scale=.39):
 data=bpy.data.cameras.new(n);data.type='ORTHO';data.ortho_scale=scale;o=bpy.data.objects.new(n,data);s.collection.objects.link(o);o.location=target+offset;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();return o
cams={
 'dorsal':camera('BW6_Bracer_Camera_Dorsal',D*.65+A*.07),
 'volar':camera('BW6_Bracer_Camera_Volar',-D*.65+A*.03),
 'side':camera('BW6_Bracer_Camera_Side',T*.65+A*.06),
 'three_quarter':camera('BW6_Bracer_Camera_ThreeQuarter',D*.52+T*.35-A*.09),
 'axial':camera('BW6_Bracer_Camera_Axial',-A*.65+D*.05,.20)}
for nm,loc,power,size in [('Key',target+D*.55+T*.3+A*.2,35,.42),('Fill',target-D*.4-T*.3,18,.5),('Rim',target+T*.6+A*.15,25,.4)]:
 d=bpy.data.lights.new('BW6_Bracer_'+nm,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler()
s.camera=cams['three_quarter'];s['BW6_bracer_owned']=json.dumps([o.name for o in owned]);s['BW6_bracer_context']=json.dumps([o.name for o in contexts.values()]);s['BW6_bracer_frame']=json.dumps({'wrist':list(W),'proximal':list(A),'dorsal':list(D),'transverse':list(T)})
out={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'frame':json.loads(s['BW6_bracer_frame']),'sections':records,'owned':[o.name for o in owned],'rig':rig.name,'independent_meshes_and_rig_action':True,'method':'New sectioned dorsal shell, separate volar leather closure, overlapping cuff and closure straps. Derived body/glove unchanged. Fitted from actual sleeve/body/glove rest surfaces. Single lowerarm02.R rigid owner.','representation':'Ada-specific bracer authoring candidate, no fixed hand or runtime claim'}
(R/'records/initial_construction.json').write_text(json.dumps(out,indent=2))
path=R/'ada_bw6_bracer_initial.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path))
for label in ['dorsal','volar','side','three_quarter','axial']:
 s.camera=cams[label];s.render.filepath=str(R/'captures'/('initial_'+label+'.png'));bpy.ops.render.render(write_still=True)
print('BRACER_INITIAL_DONE',path)
