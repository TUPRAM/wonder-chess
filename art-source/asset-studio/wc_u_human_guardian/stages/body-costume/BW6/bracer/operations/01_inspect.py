import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
SOURCE=R.parents[1]/'BW5/armor/ada_bw5_armor_checkpoint_r003_ART_REVISE.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
rig=bpy.data.objects['BW4_Armor_Independent_Rig']
out={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'bones':{},'objects':[]}
for b in rig.data.bones:
 if any(x in b.name.lower() for x in ['arm','hand','finger','thumb']):
  p=rig.pose.bones[b.name]
  out['bones'][b.name]={'head':list(rig.matrix_world@b.head_local),'tail':list(rig.matrix_world@b.tail_local),'pose_head':list(rig.matrix_world@p.head),'pose_tail':list(rig.matrix_world@p.tail),'matrix':[list(x) for x in rig.matrix_world@b.matrix_local]}
for o in s.objects:
 if o.type=='MESH' and any(x in o.name.lower() for x in ['bracer','glove','coat','sleeve','hand','body']):
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();co=[ev.matrix_world@v.co for v in me.vertices]
  out['objects'].append({'name':o.name,'visible':not o.hide_render,'verts':len(o.data.vertices),'matrix':[list(x) for x in o.matrix_world],'groups':[g.name for g in o.vertex_groups],'min':[min(p[i] for p in co) for i in range(3)],'max':[max(p[i] for p in co) for i in range(3)],'modifiers':[{'name':m.name,'type':m.type,'object':m.object.name if hasattr(m,'object') and m.object else None} for m in o.modifiers]});ev.to_mesh_clear()
(R/'records/source_inspection.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'bones':{k:v for k,v in out['bones'].items() if 'lowerarm' in k or 'hand' in k},'objects':out['objects']},indent=2))
