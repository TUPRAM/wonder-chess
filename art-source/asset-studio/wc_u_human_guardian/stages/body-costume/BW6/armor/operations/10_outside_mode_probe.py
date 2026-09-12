import bpy,json,ast,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_saddle_clearance.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];bpy.context.view_layer.objects.active=coat
solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY')
original=[m.type for m in coat.modifiers]
wrap=next(m for m in coat.modifiers if m.type=='SHRINKWRAP')
print('WRAP_ENUMS',[(x.identifier,x.description) for x in wrap.bl_rna.properties['wrap_mode'].enum_items],flush=True)
wrap.wrap_mode='OUTSIDE'
bpy.ops.object.modifier_move_to_index(modifier=solid.name,index=len(coat.modifiers)-1)
assert [m.type for m in coat.modifiers].index('SHRINKWRAP')<[m.type for m in coat.modifiers].index('SOLIDIFY')
coat['BW6_wall_order']='Pose and constrain outer cloth surface before final6mm inward thickness; prevents projecting both walls onto the same target.'
src=R/'ada_bw6_torso_outside_work.blend';bpy.ops.wm.save_as_mainfile(filepath=str(src))
base=R.parents[1]
for p,names in [(base/'BW4/r001/armor/operations/08_verify_and_motion.py',['geom','crossing']),(base/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle'])]:
 t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
owned=json.loads(s['BW6_owned_visible_parts']);body='BW4_CONTEXT_BW1_IndexedBody';cloth=coat.name
pairs=[(cloth,body)]+[(n,body) for n in owned if n!=cloth]+[(n,cloth) for n in owned if n!=cloth]+[('BW6_NavyWaist','BW6_LeatherBelt')]
records=[]
for frame in [1,20,49,73,97]:
 s.frame_set(frame);bpy.context.view_layer.update();gs={n:geom(bpy.data.objects[n]) for n in {x for p in pairs for x in p}}
 row={'frame':frame,'pairs':{a+'__'+b:crossing(gs[a],gs[b]) for a,b in pairs}};records.append(row)
 print('FRAME',frame,{k:v['confirmed_transverse_pairs'] for k,v in row['pairs'].items()},flush=True)
(R/'records/outside_pose_probe.json').write_text(json.dumps({'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'modifier_order_before':original,'modifier_order_after':[m.type for m in coat.modifiers],'frames':records},indent=2))
s.cycles.samples=12;s.render.threads=4;s.frame_set(1)
for view in ['front','profile','three_quarter']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('outside_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('BW6_CLEARANCE_PROBE_COMPLETE')
