import bpy,ast,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent;B=R.parent;source=B/'armor/ada_bw6_upper_combined_r001.blend';sha=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s
for p,names in [(B.parent/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(R/'inspect_outside_work.py',['geom','screen'])]:
 tree=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];old=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];body=bpy.data.objects['BW6_BodyFit_Candidate'];out={'source':str(source),'sha256':sha,'source_saved':False,'objects':{},'frames':{}}
for o in [coat,old,body]:out['objects'][o.name]={'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'matrix_world':list(map(list,o.matrix_world)),'modifiers':[{'name':m.name,'type':m.type,'target':m.object.name if hasattr(m,'object') and m.object else None,'visible':m.show_viewport} for m in o.modifiers]}
def compact_map(result,raw,n_outer,full):
 q=raw[0];groups={};mapped=[]
 for hit in result['hits']:
  p=np.array(hit['point']);i=int(np.argmin(np.linalg.norm(q-p,axis=1)));v=coat.data.vertices[i];rest=coat.matrix_world@v.co
  if rest.z>=1.435 and abs(rest.x)<.19:region='collar_and_neck_saddle'
  elif abs(rest.x)>=.225:region='sleeve'
  elif abs(rest.x)>=.155:region='armhole_axilla'
  elif rest.y>.025:region='front_underplate'
  else:region='back_or_side_torso'
  a,b=hit['triangles'];layers=[]
  for tri in [full[1][a],full[1][b]] if full is not None else []:
   layers.append('outer' if all(k<n_outer for k in tri) else ('inner' if all(n_outer<=k<2*n_outer for k in tri) else 'rim'))
  key=region+(' / '+'-'.join(layers) if layers else '');groups[key]=groups.get(key,0)+1;mapped.append({'region':region,'layers':layers,'point_world_m':p.tolist(),'nearest_control_vertex':i,'control_rest_world_m':list(rest),'weights':{coat.vertex_groups[g.group].name:g.weight for g in v.groups}})
 return {'pairs':result['pairs'],'region_layer_counts':groups,'mapped_hits':mapped}
for frame in [1,20,49,73]:
 s.frame_set(frame);bpy.context.view_layer.update();gb=geom(body);rows={};wall=next(m for m in coat.modifiers if m.type=='SOLIDIFY');sub=next(m for m in coat.modifiers if m.type=='SUBSURF');full=geom(coat);wall.show_viewport=False;bpy.context.view_layer.update();outer=geom(coat);sub.show_viewport=False;bpy.context.view_layer.update();raw=geom(coat);sub.show_viewport=True;wall.show_viewport=True;bpy.context.view_layer.update()
 for label,g in [('full',full),('outer',outer),('posed_cage',raw)]:
  result=screen(g,g,True);rows[label+'_self']=compact_map(result,raw,len(outer[0]),g if label=='full' else None);r=screen(g,gb);rows[label+'_body']=compact_map(r,raw,len(outer[0]),None)
 inherited=geom(old);rows['inherited_original_coat_self']=screen(inherited,inherited,True);rows['inherited_original_coat_body']=screen(inherited,gb);rows['evaluated_vertex_counts']={'full':len(full[0]),'outer':len(outer[0]),'cage':len(raw[0])};out['frames'][str(frame)]=rows;print('FRAME',frame,{k:v['pairs'] for k,v in rows.items() if 'pairs' in v},flush=True)
s.frame_set(1);bpy.context.view_layer.update();a=np.array([coat.matrix_world@v.co for v in coat.data.vertices]);b=np.array([old.matrix_world@v.co for v in old.data.vertices]);preserved=[];new=[]
for i,p in enumerate(a):
 if abs(p[0])<.225:continue
 dist=np.linalg.norm(b-p,axis=1);j=int(np.argmin(dist));target=old.data.vertices[j];v=coat.data.vertices[i];ga={coat.vertex_groups[g.group].name:g.weight for g in v.groups};gb={old.vertex_groups[g.group].name:g.weight for g in target.groups};item={'current_control':i,'source_control':j,'distance_m':float(dist[j]),'weights_equal':ga.keys()==gb.keys() and max([abs(ga[k]-gb[k]) for k in ga] or [0])<1e-6}
 (preserved if dist[j]<1e-6 else new).append(item)
out['sleeve_source_correspondence']={'region':'abs world x >= .225 at rest','coincident_source_vertices':len(preserved),'inserted_or_changed_vertices':len(new),'coincident_same_weights':sum(x['weights_equal'] for x in preserved),'records':preserved+new};assert hashlib.sha256(source.read_bytes()).hexdigest()==sha;out['sha256_after']=sha;out['limits']='Read-only native finite transverse query. No source save. Nearest posed cage localization is diagnostic, not retopology correspondence. Original hidden coat comparison uses actual source object and modifiers; no generalized baseline pass.';(R/'torso_failure_localization.json').write_text(json.dumps(out,indent=2));print('READONLY_COMPLETE')
