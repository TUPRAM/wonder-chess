import bpy,ast,json,hashlib,math,sys
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];BASE=R.parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
SOURCE=R/(args[0] if args else 'ada_bw6_bracer_correction1.blend');LABEL=args[1] if len(args)>1 else 'r001'
for p,names in [(BASE/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(R.parent/'analysis/inspect_outside_work.py',['geom','screen'])]:
 t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
left=SOURCE.parent.name=='left'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False);s=bpy.data.scenes['BW6_LEFT_BRACER_AUTHORING_ONLY' if left else 'BW6_RIGHT_BRACER_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
rig=bpy.data.objects['BW6_LeftBracer_Independent_Rig' if left else 'BW6_Bracer_Independent_Rig'];wrist=rig.pose.bones['wrist.L' if left else 'wrist.R'];saved=wrist.matrix_basis.copy();action=rig.animation_data.action;rig.animation_data.action=None
owned=[bpy.data.objects[n] for n in json.loads(s['BW6_bracer_owned'])];ctx=[bpy.data.objects[n] for n in json.loads(s['BW6_bracer_context'])]
out={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'scope':'Reversible additive wrist-local matrix rotations at frame1. These are explicit local stress probes, not game animation or validated anatomical ranges. Frozen glove/body mesh and weights unchanged.','probes':[]}
def brief(r):return {k:v for k,v in r.items() if k!='hits'}|{'examples':r['hits'][:3]}
for axis,deg in [('X',-15),('X',15),('Z',-15),('Z',15),('X',-25),('X',25),('Z',-25),('Z',25)]:
 wrist.matrix_basis=saved@Matrix.Rotation(math.radians(deg),4,axis);bpy.context.view_layer.update();geoms={o.name:geom(o) for o in owned+ctx}
 row={'wrist_local_axis':axis,'degrees':deg,'parts':{}}
 for o in owned:row['parts'][o.name]={'self':brief(screen(geoms[o.name],geoms[o.name],True)),'context':{c.name:brief(screen(geoms[o.name],geoms[c.name])) for c in ctx}}
 row['interpart']={}
 for i,o in enumerate(owned):
  for p in owned[i+1:]:
   q=screen(geoms[o.name],geoms[p.name]);
   if q['pairs']:row['interpart'][o.name+' / '+p.name]=brief(q)
 out['probes'].append(row);print('PROBE',axis,deg,{o:{'self':v['self']['pairs'],'context':{n:r['pairs'] for n,r in v['context'].items()}} for o,v in row['parts'].items()},'between',{k:r['pairs'] for k,r in row['interpart'].items()},flush=True)
wrist.matrix_basis=saved;rig.animation_data.action=action;bpy.context.view_layer.update();out['restored_exact_basis']=max(abs(wrist.matrix_basis[i][j]-saved[i][j]) for i in range(4) for j in range(4))<1e-7
out['source_sha256_after']=hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert out['source_sha256_after']==out['source_sha256']
(SOURCE.parent/'records'/(LABEL+'_wrist_stress_probes.json')).write_text(json.dumps(out,indent=2));print('NO_SAVE_EXACT_RESTORE')
