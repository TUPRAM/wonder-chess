import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
old=R.parents[1]/'BW4/r001/armor/ada_armor_checkpoint_FINAL_ART_REVISE.blend'
bpy.ops.wm.open_mainfile(filepath=str(old), use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY']; bpy.context.window.scene=s; s.frame_set(1)
assert bpy.app.version[:2]==(5,1)
parts=json.loads(s['armor_parts']); context=json.loads(s['context_parts'])
inventory={}
for o in s.objects:
    if o.type=='MESH':
        ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh(); v=[ev.matrix_world@x.co for x in me.vertices]
        inventory[o.name]={'vertices':len(o.data.vertices),'hidden':o.hide_render,'bounds_m':[[min(x[k] for x in v),max(x[k] for x in v)] for k in range(3)],'modifiers':[{'name':m.name,'type':m.type,'thickness':getattr(m,'thickness',None),'offset':getattr(m,'offset',None),'even_offset':getattr(m,'use_even_offset',None),'rig':getattr(getattr(m,'object',None),'name',None)} for m in o.modifiers]}
        ev.to_mesh_clear()
cameras={o.name:{'matrix_world':[list(r) for r in o.matrix_world],'type':o.data.type,'ortho_scale':o.data.ortho_scale} for o in s.objects if o.type=='CAMERA'}
(R/'records/preflight.json').write_text(json.dumps({'source':str(old),'sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'version':bpy.app.version_string,'scene':s.name,'parts':parts,'context':context,'objects':inventory,'cameras':cameras,'action':bpy.data.objects['BW4_Armor_Independent_Rig'].animation_data.action.name},indent=2))
s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.samples=16
for view in ['front','back','profile','three_quarter','rear_three_quarter']:
    s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('baseline_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('BW5_BASELINE_RENDERS_COMPLETE',flush=True)
