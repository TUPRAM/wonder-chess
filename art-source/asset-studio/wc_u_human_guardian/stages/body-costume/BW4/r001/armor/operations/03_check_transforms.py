import bpy,json
from mathutils import Vector
from pathlib import Path
R=Path('C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW4/r001/armor')
res={}
for sn in ['BW1_BODY_COSTUME','BW4_ARMOR_LOCAL_AUTHORING_ONLY']:
 s=bpy.data.scenes[sn];bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 names=['BW1_Temporary_Pose_Rig','BW1_IndexedBody','BW1_CoatUpper_Continuous'] if sn.startswith('BW1') else ['BW4_Armor_Independent_Rig','BW4_CONTEXT_BW1_IndexedBody','BW4_CONTEXT_BW1_CoatUpper_Continuous','BW4_Breastplate_ControlSurface']
 res[sn]={}
 for nm in names:
  o=bpy.data.objects[nm];ob=o.evaluated_get(dg);d={'matrix':list(map(list,o.matrix_world)),'parent':getattr(o.parent,'name',None),'basis':list(map(list,o.matrix_basis)),'parentinverse':list(map(list,o.matrix_parent_inverse))}
  if o.type=='MESH':
   me=ob.to_mesh();v=[ob.matrix_world@v.co for v in me.vertices];d['evalmin']=[min(a[i] for a in v) for i in range(3)];d['evalmax']=[max(a[i] for a in v) for i in range(3)];ob.to_mesh_clear()
  if o.type=='ARMATURE':d['pose']={p.name:list(map(list,p.matrix_basis)) for p in o.pose.bones if any(abs(p.matrix_basis[i][j]-(1 if i==j else 0))>1e-5 for i in range(4) for j in range(4))}
  res[sn][nm]=d
(R/'records/transform_check.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
