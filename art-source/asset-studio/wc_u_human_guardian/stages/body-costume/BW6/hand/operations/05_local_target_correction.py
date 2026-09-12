"""BW6 local anatomical form target: original glove palm, rounded thenar and knuckle masses.

This is a sculpt/form study, not a finished glove or a new finger-ring generator.
"""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(__file__).resolve().parents[1];STAGE=OUT.parents[1];BW4=STAGE/'BW4/r001';BW5=STAGE/'BW5/hand'
bpy.ops.wm.open_mainfile(filepath=str(BW5/'ada_bw5_hand_checkpoint_ART_REVISE.blend'),load_ui=False,use_scripts=False)
s=bpy.context.scene
for o in s.objects:
 if o.type=='MESH' and not o.name.startswith('BW4_SelectedSword_'):o.hide_render=True;o.hide_set(True)
src=json.loads((BW4/'records/open_glove_geometry.json').read_text());verts=src['vertices_m']
# Preserve actual anatomical open-source palm topology for the form target.
# Digit surfaces are excluded semantically before the target is built.
# The cut/cap source target was rejected. A closed anatomical loft supplies
# independent palm thickness and a rounded cross arch, with named region masses.
v=[];f=[];segments=32
profiles=[(.008,.029,.015,.017),(.014,.030,.016,.017),(.032,.036,.017,.017),(.050,.043,.018,.016),(.070,.047,.014,.013),(.087,.046,.011,.010),(.098,.040,.010,.008),(.104,.034,.008,.006)]
for y,width,top,bottom in profiles:
 for k in range(segments):
  a=2*math.pi*k/segments;cs=math.cos(a);sn=math.sin(a)
  # A broad dorsal plane and rounded palmar arch, not a flattened two-panel fan.
  x=width*math.copysign(abs(cs)**.86,cs);z=(top if sn>=0 else bottom)*math.copysign(abs(sn)**.85,sn)
  v.append((x,y,z))
for j in range(len(profiles)-1):
 for k in range(segments):f.append([j*segments+k,j*segments+(k+1)%segments,(j+1)*segments+(k+1)%segments,(j+1)*segments+k])
f.append(list(reversed(range(segments))));f.append([(len(profiles)-1)*segments+k for k in range(segments)])
me=bpy.data.meshes.new('BW6_Closed_Anatomical_PalmCore');me.from_pydata(v,[],f);me.update()
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
palm=bpy.data.objects.new('BW6_Palm_Anatomical_FormTarget',me);s.collection.objects.link(palm)
faces=f
parts=[palm]
def mass(name,center,radii,rot=(0,0,0)):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=28,ring_count=18,location=center,rotation=rot)
 o=bpy.context.object;o.name=name;o.scale=radii;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);parts.append(o);return o
# Three deliberately separate anatomical masses follow the public Proko lesson:
# thenar, first dorsal interosseous/web and hypothenar. Dimensions are candidate
# art decisions informed by the source palm, not measurements copied from artwork.
mass('BW6_Thenar_Teardrop_Target',(.025,.048,.009),(.019,.024,.013),(0,math.radians(-12),math.radians(-22)))
mass('BW6_Hypothenar_Target',(-.030,.057,.002),(.013,.032,.015),(0,0,math.radians(-8)))
mass('BW6_First_Dorsal_Interosseous_Target',(.032,.076,.002),(.012,.020,.013),(0,math.radians(15),math.radians(15)))
# New opposing thumb volumes have independent silhouette and a broad root;
# they do not reuse BW5's hook or its loop interpolation.
mass('BW6_Thumb_Metacarpal_Target',(.039,.053,.012),(.013,.021,.017),(0,math.radians(-25),math.radians(-12)))
mass('BW6_Thumb_Proximal_Target',(.040,.058,.024),(.010,.012,.017),(math.radians(25),math.radians(-23),math.radians(-18)))
mass('BW6_Thumb_Distal_Pad_Target',(.027,.061,.029),(.014,.008,.0075),(0,math.radians(15),math.radians(-8)))
# Individual metacarpal/knuckle pad masses establish a descending arch and
# source-proportion differences before any finger detail is reconstructed.
for name,c,r in [('index',(.027,.099,.005),(.011,.011,.008)),('middle',(.003,.102,.003),(.012,.013,.009)),('ring',(-.019,.097,.002),(.011,.012,.008)),('little',(-.038,.099,.005),(.009,.011,.008))]:mass('BW6_'+name+'_MCP_Target',c,r)
# Explicit phalangeal gesture, using independently oriented broad form blocks.
# These are sculpt target masses, not a circular-strand loft or production cage.
gestures={
 'index':[(.027,.103,.006),(.029,.116,.040),(.027,.088,.061),(.023,.066,.043)],
 'middle':[(.003,.106,.002),(.003,.117,.039),(.002,.086,.063),(0,.063,.040)],
 'ring':[(-.019,.100,.002),(-.021,.113,.037),(-.020,.087,.059),(-.017,.066,.042)],
 'little':[(-.039,.102,.006),(-.041,.116,.036),(-.040,.092,.059),(-.035,.073,.044)]}
widths={'index':.0175,'middle':.019,'ring':.0175,'little':.0145}
for name,points in gestures.items():
 for j,(aa,bb) in enumerate(zip(points,points[1:])):
  a=Vector(aa);b=Vector(bb);t=(b-a).normalized();u=Vector((1,0,0));u=(u-t*u.dot(t)).normalized();n=u.cross(t).normalized()
  bpy.ops.mesh.primitive_cube_add(size=1,location=(a+b)*.5);ob=bpy.context.object;ob.name='BW6_'+name+'_Phalanx'+str(j+1)+'_Form'
  ob.rotation_euler=Matrix((u,t,n)).transposed().to_euler();ob.scale=(widths[name]*(1-.12*j),(b-a).length+.004,.016-.002*j)
  bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  bevel=ob.modifiers.new('Sculpt form rounded edges','BEVEL');bevel.width=.0035;bevel.segments=3;bpy.ops.object.modifier_apply(modifier=bevel.name);parts.append(ob)
for o in bpy.data.objects:o.select_set(False)
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=palm;bpy.ops.object.join()
palm.name='BW6_Anatomical_PalmThenar_SculptTarget'
# Voxel union establishes one actual continuous target surface; no overlapping
# under-patch is retained. The target is explicitly separate from editable output.
palm.data.remesh_voxel_size=.0009;palm.data.remesh_voxel_adaptivity=0
bpy.ops.object.voxel_remesh()
smooth=palm.modifiers.new('Target local union cleanup','SMOOTH');smooth.factor=.45;smooth.iterations=8;bpy.context.view_layer.objects.active=palm;bpy.ops.object.modifier_apply(modifier=smooth.name)
for f in palm.data.polygons:f.use_smooth=True
palm.color=(.56,.53,.48,1);palm['scope']='LOCAL SCULPT FORM TARGET ONLY. No complete glove or topology/contact pass.'
palm['method']='Anatomically lofted closed palm core plus separately placed thenar, hypothenar, interosseous and MCP volumes; voxel-unified form target'
palm['source_license']='Original toigo glove CC0 adaptation; master and prior candidates unchanged'
s.name='BW6_ANATOMICAL_HAND_TARGET_CORRECTION2';s['BW6_scope']='Anatomical full-glove form target with independent phalangeal gesture; no completed-hand claim.'
for o in s.objects:
 if o.name.startswith('BW4_SelectedSword_'):o.hide_render=not o.name.endswith('handle')
s.camera=bpy.data.objects['BW4_oblique'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ada_bw6_hand_target_local_c1.blend'))
for view in ('palm','oblique'):
 s.camera=bpy.data.objects['BW4_'+view];s.render.filepath=str(OUT/'captures'/('target_local_c1_'+view+'.png'));bpy.ops.render.render(write_still=True)
 for o in s.objects:
  if o.name.startswith('BW4_SelectedSword_'):o.hide_render=True
 s.render.filepath=str(OUT/'captures'/('target_local_c1_'+view+'_isolated.png'));bpy.ops.render.render(write_still=True)
 for o in s.objects:
  if o.name.startswith('BW4_SelectedSword_'):o.hide_render=not o.name.endswith('handle')
(OUT/'records/target_local_c1.json').write_text(json.dumps({'status':'LOCAL_FORM_TARGET_REVIEW_REQUIRED','source':str(BW5/'ada_bw5_hand_checkpoint_ART_REVISE.blend'),'source_sha256':hashlib.sha256((BW5/'ada_bw5_hand_checkpoint_ART_REVISE.blend').read_bytes()).hexdigest(),'anatomical_palm_source':str(BW4/'records/open_glove_geometry.json'),'new_palm_loft_faces':len(faces),'original_palm_used_as_proportion_reference_only':True,'sculpt_vertices':len(palm.data.vertices),'sculpt_faces':len(palm.data.polygons),'voxel_m':.0009,'digit_gestures_m':gestures,'source_original_wrist_retained_for_later_editable_reconstruction':True,'sculpt_target_wrist_cap':'Temporary target cap; not claimed production opening','equipment_changed':False,'technical_scope':'Union cleanup only; no broad smoothing of BW5 mesh','anatomy_reference':'https://www.proko.com/course-lesson/how-to-draw-hands-muscle-anatomy-of-the-hand/','reference_access':'Primary author search-index excerpt inspected; direct page fetch timed out. No video-viewing claim.'},indent=2))
print('BW6_PALM_TARGET',len(palm.data.vertices),len(palm.data.polygons),flush=True)
