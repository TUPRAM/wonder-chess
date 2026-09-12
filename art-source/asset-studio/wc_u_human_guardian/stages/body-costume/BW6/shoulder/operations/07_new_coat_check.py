import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_correction1.blend');src=R.parent/'armor/ada_bw6_torso_correction1.blend';rig=bpy.data.objects['BW4_Armor_Independent_Rig']
with bpy.data.libraries.load(str(src),link=False) as (a,b):
 print('NEW_OBJECTS',[n for n in a.objects if n.startswith('BW6_')]);b.objects=['BW6_PaddedCoat_Tailored']
for o in b.objects:
 s.collection.objects.link(o)
 for m in o.modifiers:
  if m.type=='ARMATURE':m.object=rig
 o.hide_render=False;o.hide_set(False)
old=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];old.hide_render=True;old.hide_set(True)
s['BW6_SHOULDER_COAT']='BW6_PaddedCoat_Tailored';s['BW6_COAT_CONTEXT_SOURCE']=str(src);s['BW6_COAT_CONTEXT_SHA256']=hashlib.sha256(src.read_bytes()).hexdigest()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_shoulder_new_coat_context.blend'))
