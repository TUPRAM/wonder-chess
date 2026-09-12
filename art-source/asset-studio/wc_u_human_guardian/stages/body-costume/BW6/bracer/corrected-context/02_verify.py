import bpy,ast,json,hashlib,sys,math
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parent;BW6=R.parents[1];BASE=BW6.parent;args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];SOURCE=R/(args[0] if args else 'ada_bw6_bracers_actual_sleeve_initial.blend');LABEL=args[1] if len(args)>1 else 'initial'
for p,names in [(BASE/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(BW6/'analysis/inspect_outside_work.py',['geom','screen'])]:
 t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
owned=[bpy.data.objects[n] for n in json.loads(s['BW6_correct_context_bracer_owned'])];ctx=[bpy.data.objects[n] for n in ['BW4_CONTEXT_BW1_IndexedBody','BW6_PaddedCoat_Tailored','BW4_CONTEXT_BW1_Glove_Pair_SourceFit']];rig=bpy.data.objects['BW4_Armor_Independent_Rig']
out={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'raw_self':{},'samples':[]}
def brief(r):return {k:v for k,v in r.items() if k!='hits'}|{'examples':r['hits'][:4]}
for o in owned:out['raw_self'][o.name]=brief(screen(geom(o,True),geom(o,True),True))
def check(label):
 bpy.context.view_layer.update();gs={o.name:geom(o) for o in owned+ctx};row={'sample':label,'parts':{},'interpart':{}}
 for o in owned:row['parts'][o.name]={'self':brief(screen(gs[o.name],gs[o.name],True)),'context':{c.name:brief(screen(gs[o.name],gs[c.name])) for c in ctx}}
 for i,o in enumerate(owned):
  for p in owned[i+1:]:
   r=screen(gs[o.name],gs[p.name])
   if r['pairs']:row['interpart'][o.name+' / '+p.name]=brief(r)
 out['samples'].append(row);summary={o:{'self':v['self']['pairs'],'context':{c:q['pairs'] for c,q in v['context'].items() if q['pairs']}} for o,v in row['parts'].items() if v['self']['pairs'] or any(q['pairs'] for q in v['context'].values())};print('BRACER',label,summary,'between',{p:r['pairs'] for p,r in row['interpart'].items()},flush=True);(R/'records'/(LABEL+'_surface_checks.json')).write_text(json.dumps(out,indent=2))
for f in (range(1,98) if 'all' in args else [1,20,49,73,97]):s.frame_set(f);check('frame'+str(f))
if 'stress' in args:
 s.frame_set(1);action=rig.animation_data.action;rig.animation_data.action=None
 for side in ['R','L']:
  p=rig.pose.bones['wrist.'+side];saved=p.matrix_basis.copy()
  for axis in ['X','Z']:
   for angle in [-25,-15,15,25]:p.matrix_basis=saved@Matrix.Rotation(math.radians(angle),4,axis);check(side+'_'+axis+str(angle))
  p.matrix_basis=saved
 rig.animation_data.action=action
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==out['sha256'];print('NO_SAVE_DONE')
