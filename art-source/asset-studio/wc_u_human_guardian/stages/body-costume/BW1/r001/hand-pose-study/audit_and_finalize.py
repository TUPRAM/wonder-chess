import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector,Euler
out=Path(__file__).parent;rig=bpy.data.objects['BW1_Temporary_Pose_Rig'];glove=bpy.data.objects['BW1_Glove_Pair_SourceFit'];world=rig.matrix_world.copy()
record=json.loads((out/'poses_correction2.json').read_text())
record['status']='ART_REVISE_STOPPED_AFTER_TWO_CORRECTIONS'
record['correction']='Initial candidate plus two bounded corrections. The second used one documented fixed-handle placement correction. No further grip corrections authorized in this child assignment.'
record['pose_acceptance']={'open':'useful static diagnostic; no human approval','relaxed':'useful mild-flexion diagnostic; no human approval','sword_grip':'REJECTED: no coherent power grip; visible joint/web deformation','shield_grip':'REJECTED: no coherent power grip; unclear thumb contact'}
record['method']='Unchanged glove/body source geometry; native FK finger rotations chosen by constrained centerline fitting to cylinders; image review rejected the grip outcomes.'
record['limits']='Do not promote rejected grip poses to approved local proof. Vertex-level contact screening does not establish surface clearance, complete contact or animation compatibility.'
audit={'method':'Actual Blender evaluated control vertices with subdivision temporarily disabled, grouped by summed finger-bone weight >= 0.25. Signed radial distance to finite cylinder measured only where within its axial length. No scene geometry altered.','poses':{}}
saved_mods=[]
for mod in glove.modifiers:
    if mod.type=='SUBSURF':saved_mods.append((mod,mod.show_viewport));mod.show_viewport=False
for side,key in [('R','sword_grip'),('L','shield_grip')]:
    for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
    for name,vals in record['poses'][key].items():rig.pose.bones[name].rotation_euler=vals
    bpy.context.view_layer.update()
    h=record['handles'][side];c=Vector(h['center_world']);axis=Vector(h['axis_world']);radius=h['radius_m'];half=h['length_m']/2
    mesh=glove.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    per={}
    for f in range(1,6):
        names=[f'finger{f}-{j}.{side}' for j in (1,2,3)];gids={g.index for g in glove.vertex_groups if g.name in names}
        selected=[v.index for v in glove.data.vertices if sum(g.weight for g in v.groups if g.group in gids)>=.25]
        distances=[]
        for i in selected:
            p=glove.matrix_world@mesh.vertices[i].co;d=p-c;axial=d.dot(axis)
            if abs(axial)<=half:distances.append((d-axis*axial).length-radius)
        per[str(f)]={'sampled_vertices':len(distances),'min_radial_clearance_mm':round(min(distances)*1000,3) if distances else None,'vertices_inside_cylinder_beyond_1mm':sum(d<-.001 for d in distances),'vertices_within_2mm_of_cylinder':sum(abs(d)<=.002 for d in distances),'bone_heads_world':[list(world@rig.pose.bones[n].head) for n in names],'bone_tip_world':list(world@rig.pose.bones[names[-1]].tail)}
    glove.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
    audit['poses'][key]=per
    bpy.context.view_layer.update()
    obj=bpy.data.objects['STUDY_FIXED_HANDLE_'+side]
    h['matrix_world']=[list(row) for row in obj.matrix_world]
    h['wrist_rest_matrix_world']=[list(row) for row in (world@rig.data.bones['wrist.'+side].matrix_local)]
    h['matrix_relative_to_wrist_rest']=[list(row) for row in ((world@rig.data.bones['wrist.'+side].matrix_local).inverted()@obj.matrix_world)]
for mod,value in saved_mods:mod.show_viewport=value
for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
for name,vals in {**record['poses']['sword_grip'],**record['poses']['shield_grip']}.items():rig.pose.bones[name].rotation_euler=vals
bpy.context.view_layer.update()
record['input_sha256']=hashlib.sha256((out.parent/'bw1_hand_pose_input.blend').read_bytes()).hexdigest()
record['numerical_observations']=audit
(out/'poses.json').write_text(json.dumps(record,indent=2))
(out/'contact_observations.json').write_text(json.dumps(audit,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out/'hand_pose_study_ART_REVISE.blend'))
print(json.dumps(audit,indent=2))
