import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_underlap_candidate.blend');src=R.parent/'armor/ada_bw6_torso_interface_work.blend';rig=bpy.data.objects['BW4_Armor_Independent_Rig'];body=bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody'];old=bpy.data.objects['BW6_PaddedCoat_Tailored'];old.name='BW6_Context_PriorCoat_NotActive';old.hide_render=True;old.hide_set(True)
with bpy.data.libraries.load(str(src),link=False) as (a,b):b.objects=['BW6_PaddedCoat_Tailored']
o=b.objects[0];s.collection.objects.link(o);mods=[]
for m in o.modifiers:
 if m.type=='ARMATURE':m.object=rig
 if m.type=='SHRINKWRAP':
  assert m.target.name.startswith('BW4_CONTEXT_BW1_IndexedBody'),m.target.name
  m.target=body
 mods.append({'name':m.name,'type':m.type,'target':m.target.name if hasattr(m,'target') and m.target else None,'object':m.object.name if hasattr(m,'object') and m.object else None})
o.hide_render=False;o.hide_set(False);s['BW6_SHOULDER_COAT']=o.name;s['BW6_COAT_CONTEXT_SOURCE']=str(src);s['BW6_COAT_CONTEXT_SHA256']=hashlib.sha256(src.read_bytes()).hexdigest();s['BW6_SHOULDER_STATUS']='NEW_INTERFACE_PENDING_REVIEW';bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_shoulder_interface_candidate.blend'))
(R/'records/stable_coat_interface.json').write_text(json.dumps({'source':str(src),'sha256':s['BW6_COAT_CONTEXT_SHA256'],'object':o.name,'remapped_modifiers':mods,'lowered_diagnostic':'Explicit frame1 then main rig action cleared/restored into temporary lowered pose; supersedes prior loop-end scene-time lowered samples.'},indent=2))
