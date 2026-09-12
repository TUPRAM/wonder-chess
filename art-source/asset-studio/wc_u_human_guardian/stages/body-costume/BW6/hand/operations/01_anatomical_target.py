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
faces=[]
for f in src['faces']:
 c=Vector(tuple(sum(verts[i][j] for i in f)/len(f) for j in range(3)))
 if c.y<.101 and not(c.x>.039 and c.y>.044):faces.append(f)
used=sorted({i for f in faces for i in f});index={old:i for i,old in enumerate(used)}
me=bpy.data.meshes.new('BW6_Original_Palm_Target_Source');me.from_pydata([verts[i] for i in used],[],[[index[i] for i in f] for f in faces]);me.update()
bm=bmesh.new();bm.from_mesh(me);bound=[e for e in bm.edges if e.is_boundary];bmesh.ops.holes_fill(bm,edges=bound,sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
palm=bpy.data.objects.new('BW6_Palm_Anatomical_FormTarget',me);s.collection.objects.link(palm)
parts=[palm]
def mass(name,center,radii,rot=(0,0,0)):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=28,ring_count=18,location=center,rotation=rot)
 o=bpy.context.object;o.name=name;o.scale=radii;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);parts.append(o);return o
# Three deliberately separate anatomical masses follow the public Proko lesson:
# thenar, first dorsal interosseous/web and hypothenar. Dimensions are candidate
# art decisions informed by the source palm, not measurements copied from artwork.
mass('BW6_Thenar_Teardrop_Target',(.026,.051,.011),(.020,.028,.018),(0,math.radians(-12),math.radians(-22)))
mass('BW6_Hypothenar_Target',(-.030,.057,.002),(.013,.032,.015),(0,0,math.radians(-8)))
mass('BW6_First_Dorsal_Interosseous_Target',(.031,.079,.006),(.015,.020,.015),(0,math.radians(15),math.radians(15)))
# New opposing thumb volumes have independent silhouette and a broad root;
# they do not reuse BW5's hook or its loop interpolation.
mass('BW6_Thumb_Metacarpal_Target',(.039,.053,.012),(.013,.021,.017),(0,math.radians(-25),math.radians(-12)))
mass('BW6_Thumb_Proximal_Target',(.042,.059,.026),(.009,.012,.020),(math.radians(25),math.radians(-23),math.radians(-18)))
mass('BW6_Thumb_Distal_Pad_Target',(.030,.063,.039),(.014,.0075,.010),(0,math.radians(15),math.radians(-8)))
# Individual metacarpal/knuckle pad masses establish a descending arch and
# source-proportion differences before any finger detail is reconstructed.
for name,c,r in [('index',(.027,.096,.007),(.011,.015,.012)),('middle',(.003,.099,.003),(.012,.017,.013)),('ring',(-.019,.094,.002),(.011,.016,.012)),('little',(-.038,.085,.006),(.009,.013,.011))]:mass('BW6_'+name+'_MCP_Target',c,r)
for o in bpy.context.selected_objects:o.select_set(False)
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=palm;bpy.ops.object.join()
palm.name='BW6_Anatomical_PalmThenar_SculptTarget'
# Voxel union establishes one actual continuous target surface; no overlapping
# under-patch is retained. The target is explicitly separate from editable output.
palm.data.remesh_voxel_size=.0013;palm.data.remesh_voxel_adaptivity=0
bpy.ops.object.voxel_remesh()
smooth=palm.modifiers.new('Target local union cleanup','SMOOTH');smooth.factor=.45;smooth.iterations=2;bpy.context.view_layer.objects.active=palm;bpy.ops.object.modifier_apply(modifier=smooth.name)
for f in palm.data.polygons:f.use_smooth=True
palm.color=(.56,.53,.48,1);palm['scope']='LOCAL SCULPT FORM TARGET ONLY. No complete glove or topology/contact pass.'
palm['method']='Original anatomical glove palm plus separately placed thenar, hypothenar, interosseous and MCP volumes; voxel-unified form target'
palm['source_license']='Original toigo glove CC0 adaptation; master and prior candidates unchanged'
s.name='BW6_ANATOMICAL_PALM_TARGET_INITIAL';s['BW6_scope']='Anatomical palm/thenar/knuckle local target. Fingers absent; no completed-hand claim.'
for o in s.objects:
 if o.name.startswith('BW4_SelectedSword_'):o.hide_render=not o.name.endswith('handle')
s.camera=bpy.data.objects['BW4_oblique'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ada_bw6_palm_target_initial.blend'))
for view in ('palm','dorsal','side','oblique','axial'):
 s.camera=bpy.data.objects['BW4_'+view];s.render.filepath=str(OUT/'captures'/('target_initial_'+view+'.png'));bpy.ops.render.render(write_still=True)
 for o in s.objects:
  if o.name.startswith('BW4_SelectedSword_'):o.hide_render=True
 s.render.filepath=str(OUT/'captures'/('target_initial_'+view+'_isolated.png'));bpy.ops.render.render(write_still=True)
 for o in s.objects:
  if o.name.startswith('BW4_SelectedSword_'):o.hide_render=not o.name.endswith('handle')
(OUT/'records/target_initial.json').write_text(json.dumps({'status':'LOCAL_FORM_TARGET_REVIEW_REQUIRED','source':str(BW5/'ada_bw5_hand_checkpoint_ART_REVISE.blend'),'source_sha256':hashlib.sha256((BW5/'ada_bw5_hand_checkpoint_ART_REVISE.blend').read_bytes()).hexdigest(),'anatomical_palm_source':str(BW4/'records/open_glove_geometry.json'),'original_palm_faces':len(faces),'sculpt_vertices':len(palm.data.vertices),'sculpt_faces':len(palm.data.polygons),'voxel_m':.0013,'source_original_wrist_retained_for_later_editable_reconstruction':True,'sculpt_target_wrist_cap':'Temporary target cap; not claimed production opening','equipment_changed':False,'technical_scope':'Union cleanup only; no broad smoothing of BW5 mesh','anatomy_reference':'https://www.proko.com/course-lesson/how-to-draw-hands-muscle-anatomy-of-the-hand/','reference_access':'Primary author search-index excerpt inspected; direct page fetch timed out. No video-viewing claim.'},indent=2))
print('BW6_PALM_TARGET',len(palm.data.vertices),len(palm.data.polygons),flush=True)
