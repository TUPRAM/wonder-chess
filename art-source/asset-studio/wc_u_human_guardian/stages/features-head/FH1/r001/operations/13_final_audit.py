import bpy,bmesh,json
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/features-head/FH1/r001'
scene=bpy.data.scenes['FH1_COMBINED_HEAD'];bpy.context.window.scene=scene
head=bpy.data.objects['FH1_Combined_Head_Control_Cage_r004']
bm=bmesh.new();bm.from_mesh(head.data)
boundary=[e for e in bm.edges if e.is_boundary];remaining=set(boundary);loops=[]
while remaining:
    stack=[remaining.pop()];edges=[]
    while stack:
        edge=stack.pop();edges.append(edge)
        for v in edge.verts:
            for e in v.link_edges:
                if e in remaining:remaining.remove(e);stack.append(e)
    vs={v for e in edges for v in e.verts}
    loops.append({'edge_count':len(edges),'bounds':[[min(v.co[k] for v in vs),max(v.co[k] for v in vs)] for k in range(3)]})
seen=set();components=[]
for v in bm.verts:
    if v.index in seen:continue
    stack=[v];seen.add(v.index);count=0
    while stack:
        node=stack.pop();count+=1
        for edge in node.link_edges:
            other=edge.other_vert(node)
            if other.index not in seen:seen.add(other.index);stack.append(other)
    components.append(count)
audit={'vertices':len(bm.verts),'edges':len(bm.edges),'faces':len(bm.faces),'connected_components':components,'boundary_loops':loops,'unexpected_nonmanifold_edges':[e.index for e in bm.edges if not e.is_manifold and not e.is_boundary],'degenerate_faces':[f.index for f in bm.faces if f.calc_area()<1e-12],'quad_faces':sum(1 for f in bm.faces if len(f.verts)==4),'six_sided_nostril_vault_caps':sum(1 for f in bm.faces if len(f.verts)==6),'subdivision_preview':2,'deformation_and_self_intersection_certification':'NOT_RUN','visual_status':'REVISE; technical checks do not certify likeness or surface quality'}
bm.free()
audit['source_file_hash']='Recorded by the external file-verification helper after Blender saves the checkpoint.'
records={}
for sc in bpy.data.scenes:
    if not sc.name.startswith('FH1_'):continue
    records[sc.name]={'objects':[{'name':o.name,'type':o.type,'hidden_render':o.hide_render,'mesh_vertices':len(o.data.vertices) if o.type=='MESH' else None,'mesh_faces':len(o.data.polygons) if o.type=='MESH' else None} for o in sc.objects],'cameras':[{'name':o.name,'matrix_world':[list(row) for row in o.matrix_world],'ortho_scale':o.data.ortho_scale,'dof':o.data.dof.use_dof} for o in sc.objects if o.type=='CAMERA'],'render':{'engine':sc.render.engine,'samples':sc.cycles.samples,'resolution':[sc.render.resolution_x,sc.render.resolution_y],'view_transform':sc.view_settings.view_transform,'exposure':sc.view_settings.exposure},'declared_render_allowlist':json.loads(sc.get('render_allowlist','[]'))}
scene.camera=bpy.data.objects['FH1_COMBINED_HEAD_three_quarter']
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        s=a.spaces.active;s.region_3d.view_location=(0,-.008,1.680);s.region_3d.view_distance=.36
        s.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion();s.region_3d.view_perspective='ORTHO'
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/ada_features_work.blend')
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/ada_features_checkpoint_r004.blend',copy=True)
print('FH1_FINAL_AUDIT '+json.dumps({'source':bpy.data.filepath,'active_scene':scene.name,'active_object':head.name,'audit':audit,'scenes':records}))
