import bpy,json
from pathlib import Path
from mathutils import Vector,Matrix
out=Path(__file__).parent;rig=bpy.data.objects['BW1_Temporary_Pose_Rig'];w=rig.matrix_world
report={'status':'READ_ONLY_GEOMETRIC_FRAME_NOT_EXECUTED_AS_ATTACHMENT_OR_GRIP','method':'Anatomical hand-width axis from index MCP minus little MCP; forward from mean distal endpoint minus MCP using explicit armature-space head_local/tail_local; palmar sign aligned with positive local-X curl derived from matrix_local column 2. All transformed through rig.matrix_world.','limits':'This fixes a coordinate-frame error only. Proposed handle centers have not been constructed or visually fitted. Grip contact remains ART_REVISE. No scene edits or pose changes were made.','handles':{}}
for side,diameter,length in [('R',.032,.13),('L',.030,.12)]:
    roots=[w@rig.data.bones[f'finger{i}-1.{side}'].head_local for i in range(2,6)]
    tips=[w@rig.data.bones[f'finger{i}-3.{side}'].tail_local for i in range(2,6)]
    center_mcp=sum(roots,Vector())/4
    axis=(roots[0]-roots[-1]).normalized()
    forward=sum(((tip-root).normalized() for root,tip in zip(roots,tips)),Vector()).normalized()
    forward=(forward-axis*forward.dot(axis)).normalized()
    reference=sum(((w.to_3x3()@Vector(rig.data.bones[f'finger{i}-1.{side}'].matrix_local.col[2][:3])).normalized() for i in range(2,6)),Vector()).normalized()
    palmar=axis.cross(forward).normalized()
    if palmar.dot(reference)<0:palmar.negate()
    center=center_mcp+forward*.012+palmar*.022
    local_x=forward;local_y=axis.cross(local_x).normalized();matrix=Matrix(((local_x.x,local_y.x,axis.x,center.x),(local_x.y,local_y.y,axis.y,center.y),(local_x.z,local_y.z,axis.z,center.z),(0,0,0,1)))
    wrist=w@rig.data.bones['wrist.'+side].matrix_local
    report['handles'][side]={'mcp_center_world':list(center_mcp),'axis_world':list(axis),'forward_world':list(forward),'palmar_world':list(palmar),'center_world_proposed':list(center),'center_offsets_m':{'finger_forward':.012,'palmar':.022},'diameter_m':diameter,'length_m':length,'matrix_world_proposed':[list(row) for row in matrix],'matrix_relative_to_wrist_rest_proposed':[list(row) for row in wrist.inverted()@matrix],'axis_validation':{'forward_dot_mean_mcp_to_tip':float(forward.dot(sum(((tip-root).normalized() for root,tip in zip(roots,tips)),Vector()).normalized())),'palmar_dot_positive_local_x_curl':float(palmar.dot(reference))}}
(out/'corrected_handle_frame_UNTESTED.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
