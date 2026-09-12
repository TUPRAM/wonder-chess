"""Independent editable surface reconstructed from the BW6 anatomical form target."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from collections import Counter,defaultdict
OUT=Path(__file__).resolve().parents[1];BW4=OUT.parents[1]/'BW4/r001'
source=OUT/'ada_bw6_hand_target_local_c1.blend';bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
s=bpy.context.scene;target=bpy.data.objects['BW6_Anatomical_PalmThenar_SculptTarget']
for ob in bpy.data.objects:ob.select_set(False)
o=bpy.data.objects.new('BW6_ClosedGlove_Reconstructed',target.data.copy());s.collection.objects.link(o);o.select_set(True);bpy.context.view_layer.objects.active=o;target.hide_render=True;target.hide_set(True)
print('QUADRIFLOW_START',len(o.data.vertices),flush=True)
bpy.ops.object.quadriflow_remesh(target_faces=2200,use_mesh_symmetry=False,use_preserve_sharp=False,use_preserve_boundary=False)
print('QUADRIFLOW_END',len(o.data.vertices),len(o.data.polygons),flush=True)
# Replace the temporary form-target cuff cap with a real preserved opening.
bm=bmesh.new();bm.from_mesh(o.data)
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=(0,.025,0),plane_no=(0,1,0),clear_inner=True,clear_outer=False)
for v in list(bm.verts):
 if not v.link_faces:bm.verts.remove(v)
edges=[e for e in bm.edges if e.is_boundary];adj=defaultdict(list)
for e in edges:
 a,b=e.verts;adj[a].append(b);adj[b].append(a)
start=next(iter(adj));a=start;prev=None;bound=[]
for _ in range(500):
 bound.append(a);nxt=next(v for v in adj[a] if v!=prev);prev,a=a,nxt
 if a==start:break
assert len(bound)==len(adj),'Expected one proximal boundary only'
bound.sort(key=lambda v:math.atan2(v.co.z,v.co.x)%(2*math.pi))
d=json.loads((BW4/'records/open_glove_geometry.json').read_text());counts=Counter(tuple(sorted((a,b))) for f in d['faces'] for a,b in zip(f,f[1:]+f[:1]));ids=sorted({i for e,c in counts.items() if c==1 for i in e});wrist=[Vector(d['vertices_m'][i]) for i in ids];wrist.sort(key=lambda p:math.atan2(p.z,p.x)%(2*math.pi));wr=[bm.verts.new(p) for p in wrist]
pa=[math.atan2(v.co.z,v.co.x)%(2*math.pi) for v in wr];pb=[math.atan2(v.co.z,v.co.x)%(2*math.pi) for v in bound];ia=ib=0;na=len(wr);nb=len(bound)
while ia<na or ib<nb:
 ta=pa[(ia+1)%na]+(2*math.pi if ia+1>=na else 0) if ia<na else 20
 tb=pb[(ib+1)%nb]+(2*math.pi if ib+1>=nb else 0) if ib<nb else 20
 if ta<tb:bm.faces.new([wr[ia%na],wr[(ia+1)%na],bound[ib%nb]]);ia+=1
 else:bm.faces.new([wr[ia%na],bound[(ib+1)%nb],bound[ib%nb]]);ib+=1
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
for f in o.data.polygons:f.use_smooth=True
sub=o.modifiers.new('Editable surface review subdivision','SUBSURF');sub.levels=1;sub.render_levels=1;o.color=(.55,.53,.49,1)
o['method']='New quadriflow editable surface reconstructed against anatomical volume target; exact source wrist reconstructed after target cap removal.'
o['scope']='LOCAL_FIXED_GLOVE_REVIEW_REQUIRED; no game bind/action or art acceptance'
s.name='BW6_RECONSTRUCTED_ANATOMICAL_GLOVE'
for ob in s.objects:
 if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=not ob.name.endswith('handle')
s.camera=bpy.data.objects['BW4_oblique'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ada_bw6_hand_reconstructed_correction1.blend'))
for name in ('palm','dorsal','side','oblique','axial','underside'):
 s.camera=bpy.data.objects['BW4_'+name];s.render.filepath=str(OUT/'captures'/('reconstructed_correction1_'+name+'.png'));bpy.ops.render.render(write_still=True)
 if name in ('palm','oblique','side'):
  for ob in s.objects:
   if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=True
  s.render.filepath=str(OUT/'captures'/('reconstructed_correction1_'+name+'_isolated.png'));bpy.ops.render.render(write_still=True)
  for ob in s.objects:
   if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=not ob.name.endswith('handle')
(OUT/'records/reconstructed_correction1.json').write_text(json.dumps({'target_source':str(source),'target_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'new_cage_vertices':len(o.data.vertices),'new_cage_faces':len(o.data.polygons),'target_faces_requested':2200,'source_wrist_vertices':20,'boundary_reconstruction':'One cut loop at Y25 mm, angular correspondence bridge to exact source wrist','topology_correspondence_to_old_BW5':False,'human_approval':False,'rig_runtime':'NOT_RUN'},indent=2))
