import bpy,json,ast,sys,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];B=R.parents[1];args=sys.argv[sys.argv.index('--')+1:];source=R/args[0];label=args[1]
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s
for p,names in [(B/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(R.parent/'analysis/inspect_outside_work.py',['geom','screen'])]:
 t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
owned=json.loads(s['BW6_knee_owned']);others=['BW4_CONTEXT_BW1_IndexedBody','BW4_CONTEXT_BW1_Leggings','BW4_CONTEXT_BW1_Greave_R','BW4_CONTEXT_BW1_Boot_Pair_SourceFit','BW4_CONTEXT_BW1_FootprintSole_R'];others=[n for n in others if not bpy.data.objects[n].hide_render];frames=range(1,82) if len(args)>2 else [1,11,21,31,41]
out={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'frames':{},'raw_self':{},'scope':'Nonadjacent noncoplanar transverse triangle screen; not containment, tangency or mathematically continuous collision proof.'}
for f in frames:
 s.frame_set(f);bpy.context.view_layer.update();g={n:geom(bpy.data.objects[n]) for n in owned+others};checks={}
 for n in owned:
  checks[n+'__SELF']=screen(g[n],g[n],True)
  for o in others:checks[n+'__'+o]=screen(g[n],g[o])
 for i,n in enumerate(owned):
  for o in owned[i+1:]:checks[n+'__'+o]=screen(g[n],g[o])
 if f==1:
  for n in owned:a=geom(bpy.data.objects[n],True);out['raw_self'][n]=screen(a,a,True)
 out['frames'][str(f)]=checks;(R/'records'/(label+'_audit.json')).write_text(json.dumps(out,indent=2));print('KNEE',f,{k:v['pairs'] for k,v in checks.items() if v['pairs']},flush=True)
out['sha256_after']=hashlib.sha256(source.read_bytes()).hexdigest();assert out['sha256_after']==out['sha256'];(R/'records'/(label+'_audit.json')).write_text(json.dumps(out,indent=2))
