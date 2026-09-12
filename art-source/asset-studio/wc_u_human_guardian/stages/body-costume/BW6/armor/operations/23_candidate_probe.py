import bpy,json,ast,sys,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
source=R/(args[0] if args else 'ada_bw6_torso_recut_neck.blend');prefix=args[1] if len(args)>1 else 'recut'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
base=R.parents[1]
for p,names in [(base/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(R.parent/'analysis/inspect_outside_work.py',['geom','screen'])]:
 t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
owned=json.loads(s['BW6_owned_visible_parts']);cloth='BW6_PaddedCoat_Tailored';body='BW6_BodyFit_Candidate' if bpy.data.objects.get('BW6_BodyFit_Candidate') else 'BW4_CONTEXT_BW1_IndexedBody'
pairs=[(cloth,body)]+[(n,body) for n in owned if n!=cloth]+[(n,cloth) for n in owned if n!=cloth]+[('BW6_NavyWaist','BW6_FrontPlate'),('BW6_NavyWaist','BW6_BackPlate'),('BW6_NavyWaist','BW6_LeatherBelt')]
pairs=[(a,b) for a,b in pairs if a in owned+[body] and b in owned+[body]]
out={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'frames':{}}
for fr in [1,20,49,73,97]:
 s.frame_set(fr);bpy.context.view_layer.update();gs={n:geom(bpy.data.objects[n]) for n in set(owned+[body])};row={a+'__'+b:screen(gs[a],gs[b]) for a,b in pairs};row['coat_self']=screen(gs[cloth],gs[cloth],True)
 if fr==1:
  for n in owned:
   if n!=cloth:row[n+'__SELF']=screen(gs[n],gs[n],True)
  c=bpy.data.objects[cloth];wall=next(m for m in c.modifiers if m.type=='SOLIDIFY');wall.show_viewport=False;bpy.context.view_layer.update();g=geom(c);row['coat_outer_body']=screen(g,gs[body]);row['coat_outer_self']=screen(g,g,True);wall.show_viewport=True
 out['frames'][str(fr)]=row;print('FRAME',fr,{k:v['pairs'] for k,v in row.items()},flush=True)
(R/'records'/(prefix+'_candidate_probe.json')).write_text(json.dumps(out,indent=2));print('BW6_PROBE_COMPLETE')
