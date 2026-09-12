import bpy,sys,json,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
src=R/'ada_bw6_shoulder_work.blend';shutil.copy2(src,R/'ada_bw6_shoulder_forward_raise_rejected.blend');s=ck.load(src)
h=bpy.data.objects['BW6_Pauldron_R_Cap_Suspension'];d=h.animation_data.drivers[0].driver;d.expression='.42+.54*min(1,max(0,-raise_z/.48))'
for v in list(d.variables):
 if v.name=='raise_x':d.variables.remove(v)
h['BW6_axis_completion']='Forward-axis extension tested and rejected after larger cap/coat crossings. Retained Z-driven support still fails forward raising and remains ART_REVISE.'
s['BW6_SHOULDER_STATUS']='ART_REVISE';s['BW6_SHOULDER_FAILURE']='Cap intersects tailored coat/collar during forward raise; no human approval, runtime compatibility or mirrored extension.'
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(src));frozen=R/'ada_bw6_shoulder_checkpoint_ART_REVISE.blend';bpy.ops.wm.save_as_mainfile(filepath=str(frozen))
(R/'records/freeze.json').write_text(json.dumps({'work':str(src),'work_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'frozen':str(frozen),'frozen_sha256':hashlib.sha256(frozen.read_bytes()).hexdigest(),'status':'ART_REVISE','retained':'New independent three-panel cages, native shoulder strap suspension, anatomically located pivot, clean nested lame openings and corrected proximal underlap. Forward-raise driver extension rejected.','context_source':s['BW6_COAT_CONTEXT_SOURCE'],'context_sha256':s['BW6_COAT_CONTEXT_SHA256']},indent=2))
