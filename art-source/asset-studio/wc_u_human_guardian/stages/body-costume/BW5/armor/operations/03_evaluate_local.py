import bpy,json,ast,sys,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:];src=Path(args[0]);tag=args[1]
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s
old=R.parents[1]/'BW4/r001/armor/operations/08_verify_and_motion.py'
t=ast.parse(old.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in ['geom','crossing']],type_ignores=[]),str(old),'exec'),globals())
q=R.parents[1]/'BW2/r001/integrated-independent/audit_integrated_geometry.py';t=ast.parse(q.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='segment_triangle'],type_ignores=[]),str(q),'exec'),globals())
coat='BW4_CONTEXT_BW1_CoatUpper_Continuous';body='BW4_CONTEXT_BW1_IndexedBody';F='BW4_Breastplate_ControlSurface';B='BW4_Backplate_ControlSurface';navy='BW5_Navy_Waist_Enclosure';collar='BW5_Tailored_Collar'
pairs=[(F,coat),(B,coat),(F,body),(B,body),(navy,coat),(collar,coat),(collar,body),(navy,'BW4_CONTEXT_BW1_WaistBelt')]
for side in [-1,1]:
    pairs += [('BW4_Thorax_SideReturn_'+str(side),coat),('BW4_ShoulderBridge_'+str(side),coat)]
frames=range(1,98) if 'all' in tag else [1,20,28,29,49,54,73,97]
records=[]
for fr in frames:
    s.frame_set(fr);bpy.context.view_layer.update();gs={n:geom(bpy.data.objects[n]) for n in set(n for p in pairs for n in p)}
    row={'frame':fr,'pairs':{a+'__'+b:crossing(gs[a],gs[b]) for a,b in pairs}};records.append(row)
    print('FRAME',fr,{k:v['confirmed_transverse_pairs'] for k,v in row['pairs'].items()},flush=True)
summary={k:{'first':next((f['frame'] for f in records if f['pairs'][k]['confirmed_transverse_pairs']),None),'max':max(f['pairs'][k]['confirmed_transverse_pairs'] for f in records)} for k in records[0]['pairs']}
(R/'records'/f'{tag}_crossings.json').write_text(json.dumps({'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'scope':'Discrete evaluated transverse triangle confirmation; no continuous/coplanar/containment guarantee','summary':summary,'frames':records},indent=2))
