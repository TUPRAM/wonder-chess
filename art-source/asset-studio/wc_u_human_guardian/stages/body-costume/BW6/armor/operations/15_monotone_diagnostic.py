import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_monotone_coat.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];rows=[]
for ob in [coat,bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous']]:
 rows.append({'object':ob.name,'world':[list(x) for x in ob.matrix_world],'modifiers':[{'type':m.type,'target':getattr(getattr(m,'target',None),'name',None),'thickness':getattr(m,'thickness',None),'offset':getattr(m,'offset',None)} for m in ob.modifiers],'base_bounds':[[min((ob.matrix_world@v.co)[a] for v in ob.data.vertices),max((ob.matrix_world@v.co)[a] for v in ob.data.vertices)] for a in range(3)]})
(R/'records/monotone_diagnostic.json').write_text(json.dumps(rows,indent=2))
for m in coat.modifiers:
 if m.type=='SHRINKWRAP':m.show_viewport=False;m.show_render=False
s.camera=bpy.data.objects['BW4_Camera_three_quarter'];s.cycles.samples=8;s.render.threads=4;s.render.filepath=str(R/'captures/monotone_no_wrap.png');bpy.ops.render.render(write_still=True)
for o in s.objects:
 if o.type=='MESH':o.hide_render=o!=coat
s.render.filepath=str(R/'captures/monotone_coat_only_no_wrap.png');bpy.ops.render.render(write_still=True)
