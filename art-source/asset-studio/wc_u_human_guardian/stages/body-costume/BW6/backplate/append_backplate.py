"""Append the scoped BW6 backplate into an already-open candidate; never save.

Call append_backplate() after loading the assembly. The caller owns the output.
No body, coat, front, collar, rig rest data or animation is replaced.
"""
import bpy,hashlib
from pathlib import Path
SOURCE=Path(__file__).parent/'ada_bw6_backplate_checkpoint_REVIEW.blend'
EXPECTED_SHA256='9081f10ab60f36b29d8400b33056efc4e1bfbfa881e42438683fa56db378ec75'
def append_backplate(rig_name='BW4_Armor_Independent_Rig'):
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED_SHA256
 targetrig=bpy.data.objects.get(rig_name)
 assert targetrig and targetrig.type=='ARMATURE' and 'spine01' in targetrig.data.bones
 assert not bpy.data.objects.get('BW6_BackPlate_Rebuilt'),'Already present; inspect before retry'
 before=set(bpy.data.objects)
 with bpy.data.libraries.load(str(SOURCE),link=False) as (available,request):request.objects=['BW6_BackPlate_Rebuilt']
 ob=request.objects[0];bpy.context.scene.collection.objects.link(ob)
 for m in ob.modifiers:
  if m.type=='ARMATURE':m.object=targetrig
 ob.hide_render=False;ob.hide_set(False)
 for name in ('BW6_BackPlate','BW6_Back_Neck_TurnedBorder','BW6_Back_Hem_TurnedBorder'):
  old=bpy.data.objects.get(name)
  if old:old.hide_render=True;old.hide_set(True)
 # Only unused dependency objects newly appended by this operation are removed.
 for extra in set(bpy.data.objects)-before-{ob}:
  if extra.type=='ARMATURE' and extra.users==0:bpy.data.objects.remove(extra)
 return {'owned':[ob.name],'hidden_baseline':['BW6_BackPlate','BW6_Back_Neck_TurnedBorder','BW6_Back_Hem_TurnedBorder'],'rig':targetrig.name,'source_sha256':EXPECTED_SHA256,'status':'LOCAL_REVIEW_CANDIDATE_NO_HUMAN_OR_RUNTIME_APPROVAL'}
