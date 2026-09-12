import bpy,bmesh,json
from mathutils.bvhtree import BVHTree
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-closure/ACB1'
s=bpy.data.scenes['ACB1_HEAD'];t=bpy.data.objects['ACB1_FORM_TARGET'];base=bpy.data.objects['ACB1_HEAD_BASELINE'];orig=bpy.data.objects['ACB1_SCULPT_ORIGIN'];c=bpy.data.objects['ACB1_HEAD_CAGE']
def audit(o):
 bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
 edges=[e for e in bm.edges if e.is_boundary];unseen=set(v.index for e in edges for v in e.verts);sizes=[]
 while unseen:
  q=[unseen.pop()];n=0
  while q:
   k=q.pop();n+=1
   for e in bm.verts[k].link_edges:
    if e.is_boundary:
     v=e.other_vert(bm.verts[k]).index
     if v in unseen:unseen.remove(v);q.append(v)
  sizes.append(n)
 tree=BVHTree.FromBMesh(bm);pairs=tree.overlap(tree);cross=[]
 for i,j in pairs:
  if i<j and not set(v.index for v in bm.faces[i].verts).intersection(v.index for v in bm.faces[j].verts):cross.append([i,j])
 r={'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_loop_sizes':sorted(sizes),'edges_with_over_two_faces':sum(len(e.link_faces)>2 for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'nonadjacent_bvh_overlaps':len(cross)}
 bm.free();return r
ds=[(v.co-orig.data.vertices[v.index].co).length for v in t.data.vertices]
mask=t.data.attributes['.sculpt_mask'];coll=t.data.attributes['ACB1_protected_opening_collar']
r={'outcome':'PARKED_ART_REVISE','target':audit(t),'input_cage_pending_reconstruction':audit(c),'changed_target_vertices':sum(d>1e-9 for d in ds),'max_target_delta_mm':max(ds)*1000,'fully_masked_changed':sum(d>1e-9 and mask.data[i].value>=.99999 for i,d in enumerate(ds)),'fully_protected_opening_collar_changed':sum(d>1e-9 and coll.data[i].value>=.99999 for i,d in enumerate(ds)),'input_cage_coordinates_unchanged':all((v.co-base.data.vertices[v.index].co).length==0 for v in c.data.vertices),'input_cage_faces_unchanged':all(tuple(p.vertices)==tuple(base.data.polygons[p.index].vertices) for p in c.data.polygons),'camera_matrices_unchanged':{}}
for o in s.objects:
 if o.type in ['CAMERA','LIGHT']:
  old=bpy.data.objects.get(o.name.replace('ACB1','HP1_HEAD_POLISH'))
  if old:r['camera_matrices_unchanged'][o.name]=all(abs(o.matrix_world[i][j]-old.matrix_world[i][j])<1e-7 for i in range(4) for j in range(4))
s['closure_outcome']='PARKED_ART_REVISE';s['reconstruction_status']='NOT_RUN: sculpt target failed visual gate';s['human_approval']='NOT_ISSUED'
s['render_allowlist']=json.dumps([o.name for o in s.objects if not o.hide_render])
print('ACB1_AUDIT '+json.dumps(r))
wire=c.copy();wire.data=c.data.copy();wire.name='ACB1_INPUT_CAGE_DIAGNOSTIC_ONLY';s.collection.objects.link(wire);wire.hide_set(False);wire.hide_render=False;wire.modifiers.clear()
w=wire.modifiers.new('Actual input cage edges - reconstruction not performed','WIREFRAME');w.thickness=.00015;w.use_replace=True
t.hide_render=True
for side in ['R','L']:bpy.data.objects['ACB1_Eye_'+side].hide_render=True
for view in ['front','three_quarter']:
 s.camera=bpy.data.objects['ACB1_'+view];s.render.resolution_x=900;s.render.resolution_y=900;s.render.filepath=ROOT+'/captures/input_cage_PENDING_'+view+'.png';bpy.ops.render.render(write_still=True)
wire.hide_render=True;wire.hide_set(True);t.hide_render=False
for side in ['R','L']:bpy.data.objects['ACB1_Eye_'+side].hide_render=False
s.camera=bpy.data.objects['ACB1_primary_fit']
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/ada_closure_work.blend')
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/ada_closure_checkpoint_ACB1_ART_REVISE.blend',copy=True)

