import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
source=R.parents[1]/'BW5/armor/ada_bw5_armor_checkpoint_r003_ART_REVISE.blend';sha=hashlib.sha256(source.read_bytes()).hexdigest()
for cam,pose in [('shoulder','lowered'),('rear_three_quarter',73),('shoulder',1)]:s=ck.load(source);ck.render(s,f'baseline_bw5r003_{cam}_{pose}',cam,pose)
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha;(R/'records/baseline_capture_source.json').write_text(json.dumps({'source':str(source),'sha256':sha,'poses':['explicit frame1 lowered diagnostic','authoring frame73','authoring frame1'],'comparison_scope':'Same saved cameras and fixed resolution/Workbench rendering; BW5 torso/coat versus BW6 combined torso/coat context is separately labeled and not asserted to be unchanged.'},indent=2))
