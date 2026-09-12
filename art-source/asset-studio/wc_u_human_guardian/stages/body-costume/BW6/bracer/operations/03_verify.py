import bpy,json,hashlib,ast,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];BASE=R.parents[1]
argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
source=R/(argv[0] if argv else 'ada_bw6_bracer_initial.blend');label=argv[1] if len(argv)>1 else 'initial'
for p,names in [(BASE/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(R.parent/'analysis/inspect_outside_work.py',['geom','screen'])]:
 tree=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW6_LEFT_BRACER_AUTHORING_ONLY' if source.parent.name=='left' else 'BW6_RIGHT_BRACER_AUTHORING_ONLY'];bpy.context.window.scene=s
owned=[bpy.data.objects[n] for n in json.loads(s['BW6_bracer_owned'])];ctx=[bpy.data.objects[n] for n in json.loads(s['BW6_bracer_context'])]
out={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'Source-bound 97-frame MPFB authoring diagnostic, not canonical game actions. Non-adjacent transverse triangle crossings; no tangency/copolanarity or continuous guarantee.','raw_self':{},'frames':[]}
def compact(r):return {k:v for k,v in r.items() if k!='hits'}|{'examples':r['hits'][:5]}
s.frame_set(1)
for o in owned:out['raw_self'][o.name]=compact(screen(geom(o,True),geom(o,True),True))
frames=list(range(1,98)) if 'all' in argv else [1,20,49,73,97]
for f in frames:
 s.frame_set(f);bpy.context.view_layer.update();gs={o.name:geom(o) for o in owned+ctx};row={'frame':f,'parts':{},'between_parts':{}}
 for o in owned:
  row['parts'][o.name]={'self':compact(screen(gs[o.name],gs[o.name],True)),'context':{c.name:compact(screen(gs[o.name],gs[c.name])) for c in ctx}}
 for i,o in enumerate(owned):
  for p in owned[i+1:]:
   r=screen(gs[o.name],gs[p.name]);
   if r['pairs']:row['between_parts'][o.name+' / '+p.name]=compact(r)
 out['frames'].append(row)
 print('BRACER',f,{o:{'self':v['self']['pairs'],'context':{c:r['pairs'] for c,r in v['context'].items()}} for o,v in row['parts'].items()},'between', {k:v['pairs'] for k,v in row['between_parts'].items()},flush=True)
 (source.parent/'records'/(label+'_surface_checks.json')).write_text(json.dumps(out,indent=2))
assert out['sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
print('DONE_NO_BLEND_SAVE')

