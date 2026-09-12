import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_shared_support_recut.blend');source=R.parent/'armor/ada_bw6_torso_simple_clamped.blend';rig=bpy.data.objects['BW4_Armor_Independent_Rig'];old=bpy.data.objects.get('BW6_PaddedCoat_Tailored')
if old:bpy.data.objects.remove(old,do_unlink=True)
with bpy.data.libraries.load(str(source),link=False) as (a,b):
 b.objects=['BW6_PaddedCoat_Tailored','BW6_BodyFit_Candidate']
for o in b.objects:
 assert o is not None
 s.collection.objects.link(o)
 for m in o.modifiers:
  if m.type=='ARMATURE':m.object=rig
 o.hide_render=False;o.hide_set(False)
for n in ['BW4_CONTEXT_BW1_IndexedBody','BW4_CONTEXT_BW1_CoatUpper_Continuous']:
 o=bpy.data.objects.get(n)
 if o:o.hide_render=True;o.hide_set(True)
s['BW6_SHOULDER_COAT']='BW6_PaddedCoat_Tailored';s['BW6_SHOULDER_COAT_SOURCE']=str(source);s['BW6_SHOULDER_COAT_SOURCE_SHA256']=hashlib.sha256(source.read_bytes()).hexdigest();s['BW6_GARMENT_LIMIT']='Root supplied garment remains ART_REVISE for known self/body crossings. This shoulder check only evaluates armor against its current outer/inner evaluated surfaces.';bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_shoulder_final_interface.blend'))
