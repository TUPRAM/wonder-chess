import bpy,bmesh,math,json
from mathutils import Vector
s=bpy.context.scene;o=bpy.data.objects['MP1_MpfbFoundation_Source'];bpy.context.view_layer.objects.active=o;o.hide_set(False)
o.rotation_euler.z=math.pi;o.scale=(1.05,1.05,1.05);o.location=(0,-0.07,1.69-1.487139105796814*1.05);bpy.context.view_layer.update()
s['source_to_review_scale']=1.05;s['source_to_review_translation']=list(o.location);s['neck_cut_local_z']=1.368
mesh=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()),preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get())
mesh.name='MP1_Head_Cage_r000';bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=0.000001,plane_co=(0,0,1.368),plane_no=(0,0,1),clear_inner=True,clear_outer=False);bm.to_mesh(mesh);bm.free()
head=bpy.data.objects.new('MP1_Head_r000',mesh);s.collection.objects.link(head);head.matrix_world=o.matrix_world.copy()
clay=bpy.data.materials.new('MP1_Uniform_Clay');clay.diffuse_color=(.5,.5,.5,1);clay.use_nodes=True;p=clay.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.5,.5,.5,1);p.inputs['Roughness'].default_value=.65
mesh.materials.clear();mesh.materials.append(clay)
for f in mesh.polygons:f.use_smooth=True;f.material_index=0
sub=head.modifiers.new('Editable cage subdivision','SUBSURF');sub.levels=2;sub.render_levels=2
for side,x in [('R',-.0284753926),('L',.0284753926)]:
    pos=o.matrix_world @ Vector((x,-.1100633144,1.4871391058));bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=.0126,location=pos);eye=bpy.context.object;eye.name='MP1_Eye_'+side;eye.data.materials.append(clay)
    for f in eye.data.polygons:f.use_smooth=True
o.hide_render=True;o.hide_set(True)
for ob in s.objects:ob.select_set(False)
head.select_set(True);bpy.context.view_layer.objects.active=head
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.overlay.show_overlays=False
s.camera=bpy.data.objects['HP1_HEAD_POLISH_three_quarter'];s.render.resolution_percentage=100;s.render.resolution_x=900;s.render.resolution_y=900
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps({'head_vertices':len(mesh.vertices),'head_faces':len(mesh.polygons),'visible_meshes':[v.name for v in s.objects if v.type=='MESH' and not v.hide_render]},indent=2))
