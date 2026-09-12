import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_coupled_support.blend')
h=bpy.data.objects['BW6_Pauldron_R_Lame2_Suspension'];h.constraints['Coupled rigid cap/arm suspension'].influence=.85;h['BW6_cap_follow']=.85
bpy.context.view_layer.update();out=R/'ada_bw6_shoulder_shared_lame_support.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
r=ck.audit(s,[1,25,49,65,68,71,73,78,86,97,'lowered']);(R/'records/shared_lame_probe.json').write_text(json.dumps({'source':str(out),'frames':r},indent=2))
for fr in [49,73,'lowered']:
 s=ck.load(out);ck.render(s,'shared_lame_shoulder_'+str(fr),pose=fr)
