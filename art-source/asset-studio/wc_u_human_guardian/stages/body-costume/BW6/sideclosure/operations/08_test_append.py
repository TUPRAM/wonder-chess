import bpy,json,importlib.util,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];source=R.parent/'armor/ada_bw6_upper_integrated_r002.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;rig=bpy.data.objects['BW4_Armor_Independent_Rig'];s.frame_set(1)
before=rig.animation_data.action
spec=importlib.util.spec_from_file_location('bw6_side_append',R/'append_side_return.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
result=mod.append_side_return(rig,s)
assert rig.animation_data.action==before
rec=json.loads((R/'records/verification.json').read_text());result['verified_signatures']={}
for n in result['objects']:
 o=bpy.data.objects[n]
 sig=hashlib.sha256(str(([(tuple(v.co),[(o.vertex_groups[g.group].name,round(g.weight,8)) for g in v.groups]) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[(m.name,m.type,m.show_viewport,m.show_render) for m in o.modifiers])).encode()).hexdigest()
 assert sig==rec['save_reopen_signatures'][n];result['verified_signatures'][n]=sig
(R/'records/append_verification.json').write_text(json.dumps(result,indent=2));print('APPEND_ONLY_VERIFIED_NO_SAVE')
