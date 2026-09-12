import bpy,json,math
from mathutils import Vector,Matrix
s=bpy.data.scenes['BW1_BODY_COSTUME'];s.frame_set(1);body=bpy.data.objects['BW1_IndexedBody'];rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
# Read the full indexed shape-key surface with topology-changing display modifiers temporarily disabled.
flags=[m.show_viewport for m in body.modifiers]
for m in body.modifiers:m.show_viewport=False
bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());coords=[v.co.copy() for v in ev.data.vertices]
assert len(coords)==19158
for m,flag in zip(body.modifiers,flags):m.show_viewport=flag
bpy.context.view_layer.update()
skin=body.vertex_groups['body'].index
candidates=[v.index for v in body.data.vertices if any(g.group==skin for g in v.groups)]
targets=[Vector((.125,.066,.501)),Vector((.178,.066,.501)),Vector((.151,.071,.538))]
indices=[]
for target in targets:
    best=-1;distance=100
    for i in candidates:
        p=body.matrix_world@coords[i];d=(p-target).length
        if d<distance and i not in indices:best=i;distance=d
    indices.append(best)
assert len(set(indices))==3
me=bpy.data.meshes.new('BW1_KneeSurfaceAnchor_R_Mesh');me.from_pydata([coords[i] for i in indices],[],[(0,1,2)]);me.update()
anchor=bpy.data.objects.new('BW1_KneeSurfaceAnchor_R',me);bpy.data.collections['BW1_RIG'].objects.link(anchor)
anchor.parent=rig;anchor.matrix_world=body.matrix_world.copy();anchor.hide_render=True;anchor.display_type='WIRE'
for g in body.vertex_groups:
    if g.name in rig.data.bones:
        vg=anchor.vertex_groups.new(name=g.name)
        for j,i in enumerate(indices):
            for weight in body.data.vertices[i].groups:
                if weight.group==g.index:vg.add([j],weight.weight,'REPLACE')
m=anchor.modifiers.new('Source knee deformation correspondence','ARMATURE');m.object=rig
anchor['source_vertex_indices']=indices;anchor['status']='TEMPORARY_RIGID_ATTACHMENT_PROXY'
cup=bpy.data.objects['BW1_KneeCup_R_ThighAttachment'];world=cup.matrix_world.copy();bpy.context.view_layer.update()
cup.parent=anchor;cup.parent_type='VERTEX_3';cup.parent_vertices=(0,1,2);cup.matrix_world=world
cup['attachment_policy']='Rigid three-vertex parent on source-corresponding weighted knee proxy; local authoring only, runtime bake untested'
s.camera=bpy.data.objects['BW1_Camera_leg_proof'];s.render.resolution_x=900;s.render.resolution_y=900
for frame,name in [(1,'stance'),(121,'bend')]:
 s.frame_set(frame);s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/knee_surface_'+name+'.png';bpy.ops.render.render(write_still=True)
s.frame_set(145);s.camera=bpy.data.objects['BW1_Camera_three_quarter'];s.render.resolution_x=850;s.render.resolution_y=1100;s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/knee_surface_kneel.png';bpy.ops.render.render(write_still=True)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);print(json.dumps({'knee_attachment_corrective_attempt':2,'indices':indices,'no_further_corrections_this_run':True}))
