import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R.parents[1]
for d in ['records','captures','motion']:(R/d).mkdir(exist_ok=True,parents=True)
p=B/'BW5/armor/ada_bw5_armor_checkpoint_r003_ART_REVISE.blend'
bpy.ops.wm.open_mainfile(filepath=str(p),use_scripts=False,load_ui=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s
out={'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'objects':{},'rigs':{}}
for o in s.objects:
 if o.type=='MESH' and any(x in o.name.lower() for x in ['knee','leg','boot','sole','greave','body']):
  out['objects'][o.name]={'visible':not o.hide_render,'verts':len(o.data.vertices),'modifiers':[{'type':m.type,'name':m.name,'object':m.object.name if m.type=='ARMATURE' and m.object else None} for m in o.modifiers],'groups':[g.name for g in o.vertex_groups],'parent':o.parent.name if o.parent else None,'constraints':[c.name for c in o.constraints],'bounds':[[min((o.matrix_world@v.co)[i] for v in o.data.vertices),max((o.matrix_world@v.co)[i] for v in o.data.vertices)] for i in range(3)]}
 if o.type=='ARMATURE':
  out['rigs'][o.name]={'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None,'legs':{b.name:{'head':list(o.matrix_world@b.head_local),'tail':list(o.matrix_world@b.tail_local),'matrix':[list(r) for r in b.matrix_local]} for b in o.data.bones if any(x in b.name.lower() for x in ['thigh','calf','shin','foot','toe'])},'poses':{}}
  for f in [1,20,25,49,73,97]:
   s.frame_set(f);out['rigs'][o.name]['poses'][f]={b.name:list(b.rotation_quaternion) if b.rotation_mode=='QUATERNION' else list(b.rotation_euler) for b in o.pose.bones if any(x in b.name.lower() for x in ['thigh','calf','shin','foot'])}
(R/'records/source_inspection.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
