import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).parent;source=R.parent/'armor/ada_bw5_armor_correction1.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
ob=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table()
edges=[e for e in bm.edges if e.is_boundary];adj={}
for e in edges:
 a,b=e.verts;adj.setdefault(a.index,[]).append(b.index);adj.setdefault(b.index,[]).append(a.index)
seen=set();loops=[]
for seed in adj:
 if seed in seen:continue
 loop=[seed];seen.add(seed);prev=-1;cur=seed
 while True:
  opts=[x for x in adj[cur] if x!=prev]
  nex=next((x for x in opts if x not in seen),None)
  if nex is None:break
  prev,cur=cur,nex;seen.add(cur);loop.append(cur)
 pts=[ob.matrix_world@ob.data.vertices[i].co for i in loop];loops.append({'indices':loop,'vertices_world_m':[list(p) for p in pts],'zmin':min(p.z for p in pts),'zmax':max(p.z for p in pts),'mean_z':sum(p.z for p in pts)/len(pts),'xrange':[min(p.x for p in pts),max(p.x for p in pts)],'yrange':[min(p.y for p in pts),max(p.y for p in pts)],'closed':seed in adj[cur]})
loops.sort(key=lambda x:x['mean_z'],reverse=True)
bm.free();(R/'coat_neck_boundary.json').write_text(json.dumps({'source':str(source),'object':ob.name,'vertices':len(ob.data.vertices),'object_matrix':[list(r) for r in ob.matrix_world],'shape_keys':list(ob.data.shape_keys.key_blocks.keys()) if ob.data.shape_keys else [],'boundary_loops':loops},indent=2))
print(json.dumps(loops[:2],indent=2))
