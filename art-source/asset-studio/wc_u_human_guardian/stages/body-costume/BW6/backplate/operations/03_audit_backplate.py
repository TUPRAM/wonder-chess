import bpy,json,ast,sys,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];BASE=R.parents[1];args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
source=R/(args[0] if args else 'ada_bw6_backplate_initial.blend');label=args[1] if len(args)>1 else 'initial';all97=len(args)>2 and args[2]=='all97'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s
for p,names in [(BASE/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(R.parent/'analysis/inspect_outside_work.py',['geom','screen'])]:
 t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
owned=json.loads(s['BW6_backplate_owned']);cloth='BW6_PaddedCoat_Tailored';body='BW6_BodyFit_Candidate';others=['BW6_FrontPlate','BW6_NavyWaist','BW6_SideEnclosure_-1','BW6_SideEnclosure_1']
if not bpy.data.objects['BW6_Back_Hem_TurnedBorder'].hide_render:others.append('BW6_Back_Hem_TurnedBorder')
record={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'97 integer authoring poses when selected; nonadjacent noncoplanar transverse triangle screen, not containment/tangency/continuous-time or game proof','frames':{},'raw_self':{}}
frames=list(range(1,98)) if all97 else [1,20,49,73,97]
for fr in frames:
 s.frame_set(fr);bpy.context.view_layer.update();g={n:geom(bpy.data.objects[n]) for n in owned+[cloth,body]+others}
 checks={}
 for name in owned:
  checks[name+'__SELF']=screen(g[name],g[name],True)
  for other in [cloth,body]+others:checks[name+'__'+other]=screen(g[name],g[other])
 for i,a in enumerate(owned):
  for b in owned[i+1:]:checks[a+'__'+b]=screen(g[a],g[b])
 if fr==1:
  for name in owned:
   raw=geom(bpy.data.objects[name],True);record['raw_self'][name]=screen(raw,raw,True)
 record['frames'][str(fr)]=checks
 (R/'records'/(label+'_audit.json')).write_text(json.dumps(record,indent=2))
 print('BACKPLATE_FRAME',fr,{k:v['pairs'] for k,v in checks.items()},flush=True)
record['sha256_after']=hashlib.sha256(source.read_bytes()).hexdigest();assert record['sha256_after']==record['sha256'];record['frame_count']=len(frames)
(R/'records'/(label+'_audit.json')).write_text(json.dumps(record,indent=2));print('BACKPLATE_AUDIT_COMPLETE',len(frames))
