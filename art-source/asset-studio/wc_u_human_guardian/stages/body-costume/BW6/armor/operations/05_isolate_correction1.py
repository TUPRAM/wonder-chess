import bpy,json,ast,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];src=R/'ada_bw6_torso_correction1.blend'
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
base=R.parents[1]
for p,names in [(base/'BW4/r001/armor/operations/08_verify_and_motion.py',['geom','crossing']),(base/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle'])]:
 t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
owned=json.loads(s['BW6_owned_visible_parts']);names=owned+['BW4_CONTEXT_BW1_IndexedBody'];gs={n:geom(bpy.data.objects[n]) for n in names}
out={'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'pairs':{n:{'body':crossing(gs[n],gs['BW4_CONTEXT_BW1_IndexedBody']),'coat':crossing(gs[n],gs['BW6_PaddedCoat_Tailored']) if n!='BW6_PaddedCoat_Tailored' else None} for n in owned},'visible':[o.name for o in s.objects if o.type=='MESH' and not o.hide_render]}
(R/'records/correction1_queries.json').write_text(json.dumps(out,indent=2))
s.camera=bpy.data.objects['BW4_Camera_three_quarter'];s.cycles.samples=8;s.render.threads=3
vis={o:o.hide_render for o in s.objects if o.type=='MESH'}
for tag,keep in [('armor_only',[n for n in owned if n!='BW6_PaddedCoat_Tailored']),('coat_only',['BW6_PaddedCoat_Tailored']),('body_only',['BW4_CONTEXT_BW1_IndexedBody'])]:
 for o in vis:o.hide_render=o.name not in keep
 s.render.filepath=str(R/'captures'/('correction1_'+tag+'.png'));bpy.ops.render.render(write_still=True)
for o,h in vis.items():o.hide_render=h
print('INITIAL_DIAGNOSTICS_COMPLETE')
