import bpy,json
from pathlib import Path
from mathutils import Vector
out=Path(__file__).parent;rig=bpy.data.objects['BW1_Temporary_Pose_Rig'];report={}
for side in ('R','L'):
    report[side]={}
    for f in range(2,6):
        b=rig.data.bones[f'finger{f}-1.{side}']
        report[side][str(f)]={'endpoint_direction_world':list((rig.matrix_world.to_3x3()@(b.tail_local-b.head_local)).normalized()),'y_axis_property_world':list((rig.matrix_world.to_3x3()@b.y_axis).normalized()),'matrix_local_y_world':list((rig.matrix_world.to_3x3()@Vector(b.matrix_local.col[1][:3])).normalized())}
(out/'frame_diagnosis.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
