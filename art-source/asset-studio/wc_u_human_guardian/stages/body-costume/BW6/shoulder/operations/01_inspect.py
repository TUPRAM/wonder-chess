import bpy, json, numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1]
for x in ['records','captures','operations']: (R/x).mkdir(parents=True,exist_ok=True)
src=R.parents[1]/'BW5/armor/ada_bw5_armor_checkpoint_r003_ART_REVISE.blend'
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
rig=bpy.data.objects['BW4_Armor_Independent_Rig']
bones={b.name:{'head_world':list(rig.matrix_world@b.head_local),'tail_world':list(rig.matrix_world@b.tail_local),'parent':b.parent.name if b.parent else None} for b in rig.data.bones if any(t in b.name for t in ['clav','should','upperarm','spine'])}
out={'bones':bones,'rig_world':[list(x) for x in rig.matrix_world],'rig_action':rig.animation_data.action.name,'plate_cages':{}}
for o in s.objects:
 if o.type=='MESH' and o.name.startswith('BW4_Pauldron_R'):
  out['plate_cages'][o.name]={'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'modifiers':[(m.name,m.type) for m in o.modifiers]}
coat=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];ev=coat.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();q=np.array([ev.matrix_world@v.co for v in me.vertices]);q=q[(q[:,0]>.12)&(q[:,2]>1.20)];out['coat_shoulder_points']=q.tolist();ev.to_mesh_clear()
(R/'records/source_inspection.json').write_text(json.dumps(out,indent=2));print(json.dumps({'bones':bones,'rig_action':out['rig_action']},indent=2))
