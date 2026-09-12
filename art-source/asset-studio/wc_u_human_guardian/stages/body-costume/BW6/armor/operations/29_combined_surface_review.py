import bpy,json,ast,sys,hashlib,itertools
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:]
source=R/args[0];prefix=args[1]
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s
for p,names in [(R.parents[1]/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(R.parent/'analysis/inspect_outside_work.py',['geom','screen'])]:
 tree=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
owned=[n for n in json.loads(s['BW6_owned_visible_parts']) if not bpy.data.objects[n].hide_render]
cloth='BW6_PaddedCoat_Tailored';body='BW6_BodyFit_Candidate';metal=[n for n in owned if n!=cloth]
pairs=[(cloth,body)]+[(n,body) for n in metal]+[(n,cloth) for n in metal]+list(itertools.combinations(metal,2))
out={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'owned':owned,'body':body,'frames':{},'worst':{},'raw_self':{},'scope':'Evaluated noncoplanar transverse triangle screen. Excludes adjacent shared-vertex self pairs, coplanar/tangent cases and containment. All97 authoring integers plus selected halves; not seven canonical game actions or continuous-time proof.'}
frames=list(range(1,98))+[19.5,20.5,48.5,49.5,72.5,73.5,85.5,86.5]
for index,frame in enumerate(frames):
 s.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update();gs={n:geom(bpy.data.objects[n]) for n in owned+[body]};row={}
 for a,b in pairs+[(n,n) for n in owned]:
  key=a+'__'+b;r=screen(gs[a],gs[b],a==b);row[key]=r['pairs']
  if r['pairs']>out['worst'].get(key,{}).get('pairs',0):out['worst'][key]={'frame':frame,**r}
 out['frames'][str(frame)]=row
 if frame==1:
  for n in owned:
   g=geom(bpy.data.objects[n],True);r=screen(g,g,True);out['raw_self'][n]={'pairs':r['pairs'],'hits':r['hits']}
 if index%12==0:print('CHECKED',index+1,'/',len(frames),'frame',frame,'nonzero',sum(v>0 for v in row.values()),flush=True)
 (R/'records'/(prefix+'_surface_progress.json')).write_text(json.dumps({'source':str(source),'completed':index+1,'total':len(frames),'last_frame':frame}))
out['sha256_after']=hashlib.sha256(source.read_bytes()).hexdigest();assert out['sha256_after']==out['sha256']
(R/'records'/(prefix+'_surfaces.json')).write_text(json.dumps(out,indent=2))
print('BW6_ALL_SURFACE_REVIEW_COMPLETE',json.dumps({k:{'frame':v['frame'],'pairs':v['pairs']} for k,v in out['worst'].items()}),flush=True)
