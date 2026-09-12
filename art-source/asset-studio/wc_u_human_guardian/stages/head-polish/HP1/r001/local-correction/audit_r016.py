import bpy,bmesh,json
from mathutils.bvhtree import BVHTree
s=bpy.data.scenes['HP1_HEAD_POLISH'];h=bpy.data.objects['HP1_HEAD_POLISH_Head_r016'];old=bpy.data.objects['HP1_HEAD_POLISH_Head_r014']
bm=bmesh.new();bm.from_mesh(h.data)
a={'object':h.name,'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'internal_nonmanifold':sum(not e.is_manifold and not e.is_boundary for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-12 for f in bm.faces)}
bm.free()
ev=h.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();vs=[tuple(v.co) for v in m.vertices];fs=[tuple(p.vertices) for p in m.polygons];tree=BVHTree.FromPolygons(vs,fs,epsilon=0)
hits=[(i,j) for i,j in tree.overlap(tree) if i<j and not set(fs[i]).intersection(fs[j])]
a['nonadjacent_self_overlap_pairs']=len(hits);a['examples']=hits[:15];ev.to_mesh_clear()
a['changed_indices']=[v.index for v in h.data.vertices if (v.co-old.data.vertices[v.index].co).length>1e-8]
a['negative_x_changed']=[i for i in a['changed_indices'] if old.data.vertices[i].co.x<-.000001]
a['shared_midline_changed']=[i for i in a['changed_indices'] if abs(old.data.vertices[i].co.x)<.000001]
a['neck_changed']=[i for i in a['changed_indices'] if old.data.vertices[i].co.z<1.630]
a['topology_unchanged']=len(old.data.vertices)==len(h.data.vertices) and [tuple(p.vertices) for p in old.data.polygons]==[tuple(p.vertices) for p in h.data.polygons]
print('LOCAL_AUDIT '+json.dumps(a))
