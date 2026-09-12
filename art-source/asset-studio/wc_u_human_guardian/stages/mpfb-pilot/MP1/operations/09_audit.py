import bpy,bmesh,json
from mathutils.bvhtree import BVHTree
s=bpy.data.scenes['MP1_ADA_HEAD'];head=bpy.data.objects['MP1_Head_r002'];results={}
for label,mesh in [('control',head.data),('evaluated',head.evaluated_get(bpy.context.evaluated_depsgraph_get()).data)]:
    bm=bmesh.new();bm.from_mesh(mesh);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table();bm.normal_update();boundary=[e for e in bm.edges if e.is_boundary];todo=set(v for e in boundary for v in e.verts);loops=[]
    while todo:
        seed=todo.pop();comp={seed};stack=[seed]
        while stack:
            v=stack.pop()
            for e in v.link_edges:
                if e.is_boundary:
                    w=e.other_vert(v)
                    if w in todo:todo.remove(w);comp.add(w);stack.append(w)
        loops.append({'vertices':len(comp),'world_z_min':min((head.matrix_world@v.co).z for v in comp),'world_z_max':max((head.matrix_world@v.co).z for v in comp)})
    bvh=BVHTree.FromBMesh(bm,epsilon=1e-8);pairs=bvh.overlap(bvh);sets=[set(v.index for v in f.verts) for f in bm.faces];overlaps=[(a,b) for a,b in pairs if a<b and not sets[a]&sets[b]]
    results[label]={'vertices':len(bm.verts),'faces':len(bm.faces),'triangles':sum(len(f.verts)-2 for f in bm.faces),'quads':sum(len(f.verts)==4 for f in bm.faces),'edges_with_more_than_two_faces':sum(len(e.link_faces)>2 for e in bm.edges),'loose_edges':sum(not e.link_faces for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'boundary_loops':loops,'raw_nonadjacent_bvh_overlap_count':len(overlaps),'overlap_examples':overlaps[:12]};bm.free()
results['cameras_lights']={o.name:{'type':o.type,'matrix':[list(row) for row in o.matrix_world],'data':{'lens':o.data.lens,'ortho_scale':o.data.ortho_scale,'type':o.data.type} if o.type=='CAMERA' else {'type':o.data.type,'energy':o.data.energy}} for o in s.objects if o.type in {'CAMERA','LIGHT'}}
results['source']={'vertices':len(bpy.data.objects['MP1_MpfbFoundation_Source'].data.vertices),'shape_keys':[(k.name,k.value) for k in bpy.data.objects['MP1_MpfbFoundation_Source'].data.shape_keys.key_blocks]};results['visible_meshes']=[o.name for o in s.objects if o.type=='MESH' and not o.hide_render];results['texture_images']=[im.name for im in bpy.data.images if im.users>0];results['human_approval']=False
print(json.dumps(results,indent=2))
