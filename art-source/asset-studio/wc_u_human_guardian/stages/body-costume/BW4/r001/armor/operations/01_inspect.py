import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW4/r001/armor')
s=bpy.data.scenes['BW1_BODY_COSTUME']; bpy.context.window.scene=s;s.frame_set(1)
rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
info={'source':bpy.data.filepath,'version':bpy.app.version_string,'scene':s.name,'frame':s.frame_current,'rig_world':[list(r) for r in rig.matrix_world],'action':rig.animation_data.action.name,'bones':{},'objects':[]}
for b in rig.data.bones:
 if any(x in b.name for x in ['spine','arm','clav','shoulder','neck']):info['bones'][b.name]={'head':list(rig.matrix_world@b.head_local),'tail':list(rig.matrix_world@b.tail_local)}
for o in s.objects:
 if o.type=='MESH':
  co=[o.matrix_world@Vector(v) for v in o.bound_box]
  info['objects'].append({'name':o.name,'hide':o.hide_render,'verts':len(o.data.vertices),'min':[min(v[i] for v in co) for i in range(3)],'max':[max(v[i] for v in co) for i in range(3)],'modifiers':[{'name':m.name,'type':m.type,'target':getattr(getattr(m,'object',None),'name',None)} for m in o.modifiers]})
(R/'records/source_inspection.json').write_text(json.dumps(info,indent=2))
print(json.dumps(info['bones'],indent=2))
