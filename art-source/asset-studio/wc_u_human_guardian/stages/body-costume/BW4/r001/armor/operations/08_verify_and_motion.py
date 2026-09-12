import bpy,json,hashlib,ast
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW4/r001/armor')
frozen=R/'ada_armor_checkpoint_FINAL_ART_REVISE.blend';work=R/'ada_armor_work.blend';src=R.parents[2]/'BW1/r001/ada_body_costume_checkpoint_r003_ART_REVISE.blend'
def meshhash(o):
 h=hashlib.sha256();a=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',a);h.update(a.tobytes());h.update(str([tuple(p.vertices) for p in o.data.polygons]).encode());h.update(str([[(g.group,round(g.weight,8)) for g in v.groups] for v in o.data.vertices]).encode())
 if o.data.shape_keys:
  for key in o.data.shape_keys.key_blocks:key.data.foreach_get('co',a);h.update(key.name.encode());h.update(a.tobytes())
 return h.hexdigest()
def signatures():
 return {o.name:meshhash(o) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('BW4_')}
expected=signatures();bpy.ops.wm.open_mainfile(filepath=str(frozen),use_scripts=False);assert signatures()==expected
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;rig=bpy.data.objects['BW4_Armor_Independent_Rig'];s.frame_set(1)
source_originals={o.name:meshhash(o) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('BW1_')}
assert rig.data!=bpy.data.objects['BW1_Temporary_Pose_Rig'].data
assert rig.animation_data.action!=bpy.data.objects['BW1_Temporary_Pose_Rig'].animation_data.action
independent=[]
for o in s.objects:
 if o.name.startswith('BW4_CONTEXT_'):
  original=bpy.data.objects.get(o.name[len('BW4_CONTEXT_'):]);assert original is not None and o.data!=original.data
  if original.data.shape_keys:assert o.data.shape_keys!=original.data.shape_keys
  independent.append(o.name)
solidify_records=[]
for nm,th in [('BW4_CONTEXT_BW1_CoatUpper_Continuous',.006),('BW4_CONTEXT_BW1_Leggings',.002)]:
 m=next(m for m in bpy.data.objects[nm].modifiers if m.type=='SOLIDIFY');orig=next(m for m in bpy.data.objects[nm[len('BW4_CONTEXT_'):]].modifiers if m.type=='SOLIDIFY')
 assert not m.use_even_offset and abs(abs(m.thickness)-th)<1e-6 and m.thickness==orig.thickness and m.offset==orig.offset
 solidify_records.append({'name':nm,'thickness_m':m.thickness,'offset':m.offset,'use_even_offset':m.use_even_offset,'matches_source':True})
query=R.parents[2]/'BW2/r001/integrated-independent/audit_integrated_geometry.py'
tree=ast.parse(query.read_text());defs=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='segment_triangle'],type_ignores=[]);exec(compile(defs,str(query),'exec'),globals())
def geom(o):
 dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();co=[ev.matrix_world@v.co for v in me.vertices];tri=[tuple(t.vertices) for t in me.loop_triangles];ev.to_mesh_clear();q=np.array(co);return q,tri,BVHTree.FromPolygons(co,tri,all_triangles=True)
def crossing(a,b):
 qa,ta,ba=a;qb,tb,bb=b;pairs=ba.overlap(bb);hits=[]
 for ia,ib in pairs:
  aa=qa[list(ta[ia])];ab=qb[list(tb[ib])];points=[]
  for one,two in [(aa,ab),(ab,aa)]:
   for i in range(3):
    p=segment_triangle(one[i],one[(i+1)%3],two)
    if p is not None:points.append(p)
  if points:hits.append({'triangles':[ia,ib],'world_point_m':np.mean(points,axis=0).tolist()})
 return {'broad_pairs':len(pairs),'confirmed_transverse_pairs':len(hits),'examples':hits[:4]}
parts=[bpy.data.objects[n] for n in json.loads(s['armor_parts'])];coat=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];frames=[]
targets=['BW4_Breastplate_ControlSurface','BW4_Backplate_ControlSurface','BW4_Pauldron_R_Cap','BW4_Pauldron_R_Lame1','BW4_Pauldron_R_Lame2']
for fr in range(1,98):
 s.frame_set(fr);bpy.context.view_layer.update();gcoat=geom(coat);entry={'frame':fr,'vs_coat':{}}
 for nm in targets:
  ga=geom(bpy.data.objects[nm]);assert np.isfinite(ga[0]).all();entry['vs_coat'][nm]=crossing(ga,gcoat)
 frames.append(entry)
 if fr%12==1:print('AUDIT_FRAME',fr,flush=True)
summary={nm:{'first_detected_frame':next((x['frame'] for x in frames if x['vs_coat'][nm]['confirmed_transverse_pairs']),None),'max_pairs':max(x['vs_coat'][nm]['confirmed_transverse_pairs'] for x in frames)} for nm in targets}
s.frame_set(1);struct=[]
for ob in parts:
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();struct.append({'name':ob.name,'cage_vertices':len(ob.data.vertices),'evaluated_vertices':len(me.vertices),'triangles':len(me.loop_triangles),'degenerate_polygons':sum(p.area<1e-12 for p in me.polygons),'owner':ob.get('owner_bone')});ev.to_mesh_clear()
(R/'records/all97_authoring_frame_surfaces.json').write_text(json.dumps({'source':str(frozen),'sha256':hashlib.sha256(frozen.read_bytes()).hexdigest(),'scope':'Every integer frame of 97-frame local MPFB diagnostic; not canonical seven actions. Noncoplanar transverse triangle crossing only; tangencies, coplanar overlap and containment not certified.','frames':frames,'summary':summary},indent=2))
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False)
master_after={o.name:meshhash(o) for o in bpy.data.objects if o.name in source_originals}
assert master_after==source_originals
report={'work':str(work),'work_sha256':hashlib.sha256(work.read_bytes()).hexdigest(),'checkpoint':str(frozen),'checkpoint_sha256':hashlib.sha256(frozen.read_bytes()).hexdigest(),'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'candidate_mesh_signatures_match_reopen':True,'unchanged_original_BW1_mesh_records':len(master_after),'independent_context_meshes':len(independent),'independent_rig_action':True,'preserved_coat_and_leggings_solidify':solidify_records,'parts':struct,'collision_summary':summary,'not_run':['Canonical seven game clips','Unreal import and gameplay','Recipe replay and second body','Human approval'],'status':'ART_REVISE'}
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(summary,indent=2))
