import bpy,json,sys
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
uid='wc_u_dwarf_warrior'
bpy.ops.wm.open_mainfile(filepath=str(root/f'art-source/heroes/{uid}/{uid}.blend'))
arm=next(o for o in bpy.data.objects if o.type=='ARMATURE')
arm.animation_data.action=bpy.data.actions[f'AN_{uid}_Idle']
bpy.context.scene.frame_set(31);bpy.context.view_layer.update()
result={}
for side in ('l','r'):
 for part in ('upperarm','lowerarm','hand'):
  b=arm.pose.bones[part+'_'+side]
  result[b.name]={'head':list(b.head),'tail':list(b.tail),'matrix':list(map(list,b.matrix)),'euler':list(b.rotation_euler),'scale':list(b.scale),'rest_head':list(b.bone.head_local),'rest_tail':list(b.bone.tail_local)}
h=arm.pose.bones['hand_r'];source=h.bone.tail_local+Vector((0,0,.15*1.42))
result['grip']=list(h.matrix@h.bone.matrix_local.inverted()@source)
print('CONTACT_DIAGNOSTIC '+json.dumps(result))
