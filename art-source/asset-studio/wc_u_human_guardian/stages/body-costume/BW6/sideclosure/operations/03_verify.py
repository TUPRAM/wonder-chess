import bpy,ast,json,hashlib,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];BASE=R.parents[1];args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];SOURCE=R/(args[0] if args else 'ada_bw6_side_return_initial.blend');LABEL=args[1] if len(args)>1 else 'initial'
for p,names in [(BASE/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(R.parent/'analysis/inspect_outside_work.py',['geom','screen'])]:
 t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
owned=[bpy.data.objects[n] for n in json.loads(s['BW6_side_return_owned'])];ctx=[bpy.data.objects[n] for n in ['BW4_CONTEXT_BW1_IndexedBody','BW6_PaddedCoat_Tailored','BW6_FrontPlate','BW6_BackPlate','BW6_NavyWaist']]
out={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'raw_self':{},'frames':[]}
def brief(r):return {k:v for k,v in r.items() if k!='hits'}|{'examples':r['hits'][:4]}
for o in owned:out['raw_self'][o.name]=brief(screen(geom(o,True),geom(o,True),True))
for f in (range(1,98) if 'all' in args else [1,20,49,73,97]):
 s.frame_set(f);bpy.context.view_layer.update();gs={o.name:geom(o) for o in owned+ctx};row={'frame':f,'parts':{},'interpart':{}}
 for o in owned:row['parts'][o.name]={'self':brief(screen(gs[o.name],gs[o.name],True)),'context':{c.name:brief(screen(gs[o.name],gs[c.name])) for c in ctx}}
 for i,o in enumerate(owned):
  for p in owned[i+1:]:
   r=screen(gs[o.name],gs[p.name]);
   if r['pairs']:row['interpart'][o.name+' / '+p.name]=brief(r)
 out['frames'].append(row);print('SIDE',f,{o:{'self':v['self']['pairs'],'context':{c:q['pairs'] for c,q in v['context'].items()}} for o,v in row['parts'].items()},'between',{p:r['pairs'] for p,r in row['interpart'].items()},flush=True)
 (R/'records'/(LABEL+'_surface_checks.json')).write_text(json.dumps(out,indent=2))
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==out['sha256'];print('NO_SAVE_DONE')
