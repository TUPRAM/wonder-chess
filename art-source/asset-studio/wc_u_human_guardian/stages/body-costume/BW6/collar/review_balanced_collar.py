import bpy,ast,json,hashlib,numpy as np,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent;B=R.parent
tag=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'initial'
src=R/('ada_bw6_balanced_collar_'+tag+'.blend');sha=hashlib.sha256(src.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s
for p,names in [(B.parent/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(B/'analysis/inspect_outside_work.py',['geom','screen'])]:
    t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
o=bpy.data.objects['BW6_CollarBalanced_CoatCandidate'];old=bpy.data.objects['BW6_PaddedCoat_Tailored'];body=bpy.data.objects['BW6_BodyFit_Candidate']
out={'source':str(src),'sha256':sha,'candidate_object':o.name,'baseline_object':old.name,'frames':{},'tested_metal_objects':[]}
owned=json.loads(s.get('BW6_owned_visible_parts','[]'))
metal=[q for q in s.objects if q.type=='MESH' and not q.hide_render and q.name.startswith('BW6_') and any(w in q.name for w in ['FrontPlate','BackPlate','Back_','Pauldron'])]
out['tested_metal_objects']=[q.name for q in metal]
def localized(result,raw):
    counts={};hits=[]
    for h in result['hits']:
        pt=np.array(h['point']);i=int(np.argmin(np.linalg.norm(raw[0]-pt,axis=1)));rest=o.matrix_world@o.data.vertices[i].co
        region='collar_aperture' if rest.z>=1.435 and abs(rest.x)<.19 else 'protected_other_coat'
        counts[region]=counts.get(region,0)+1
        hits.append({'point':h['point'],'region':region,'triangles':h['triangles'],'nearest_control':i,'control_rest':list(rest)})
    return {'pairs':result['pairs'],'region_counts':counts,'hits':hits}
for frame in [1,20,49,73,86]:
    s.frame_set(frame);bpy.context.view_layer.update();wall=next(m for m in o.modifiers if m.type=='SOLIDIFY');sub=next(m for m in o.modifiers if m.type=='SUBSURF')
    full=geom(o);wall.show_viewport=False;bpy.context.view_layer.update();outer=geom(o);sub.show_viewport=False;bpy.context.view_layer.update();raw=geom(o);wall.show_viewport=sub.show_viewport=True;bpy.context.view_layer.update();gb=geom(body)
    row={'self':localized(screen(full,full,True),raw),'body':localized(screen(full,gb),raw),'outer_self':localized(screen(outer,outer,True),raw),'cage_self':localized(screen(raw,raw,True),raw),'metal':{}}
    for q in metal:row['metal'][q.name]=localized(screen(full,geom(q)),raw)
    out['frames'][str(frame)]=row
    (R/'records'/('balanced_'+tag+'_queries.json')).write_text(json.dumps(out,indent=2))
    print('FRAME',frame,{k:({a:b['pairs'] for a,b in v.items()} if k=='metal' else {'pairs':v['pairs'],'regions':v['region_counts']}) for k,v in row.items()},flush=True)
assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
out['source_unchanged']=True;out['limits']='Finite transverse noncoplanar triangle screen at five authoring poses. Shared-vertex self triangles omitted; no coplanar/tangent/containment/continuous-time proof. No game-clip or engine result.'
(R/'records'/('balanced_'+tag+'_queries.json')).write_text(json.dumps(out,indent=2));print('COLLAR_QUERY_COMPLETE')
