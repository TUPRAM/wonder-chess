import bpy,bmesh,json
from mathutils.bvhtree import BVHTree
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
s=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=s;h=bpy.data.objects['HP1_HEAD_POLISH_Head_r014']
assert '/head-polish/HP1/r001/' in bpy.data.filepath.replace('\\','/')
assert bpy.data.scenes.get('HP1_CAGE_REVIEW') is None
cs=bpy.data.scenes.new('HP1_CAGE_REVIEW');cs.world=s.world;cs.render.engine='CYCLES';cs.cycles.samples=24;cs.cycles.use_denoising=True;cs.render.resolution_x=900;cs.render.resolution_y=900;cs.render.resolution_percentage=100;cs.render.image_settings.file_format='PNG';cs.view_settings.view_transform='Standard';cs.view_settings.look='None'
for src in s.objects:
    if src.type in ['CAMERA','LIGHT']:
        c=src.copy();c.data=src.data.copy();c.name=cs.name+src.name.replace(s.name,'');cs.collection.objects.link(c)
body=h.copy();body.data=h.data.copy();body.name='HP1_CAGE_REVIEW_Base';cs.collection.objects.link(body)
for mod in body.modifiers:mod.show_render=False;mod.show_viewport=False
for p in body.data.polygons:p.use_smooth=False
wire=body.copy();wire.data=body.data.copy();wire.name='HP1_CAGE_REVIEW_ActualEdges';cs.collection.objects.link(wire);wire.modifiers.clear()
mat=bpy.data.materials.new('HP1_Cage_Diagnostic_Ink');mat.diffuse_color=(.012,.023,.030,1);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.012,.023,.030,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8
wire.data.materials.clear();wire.data.materials.append(mat)
wf=wire.modifiers.new('Actual source cage edges','WIREFRAME');wf.thickness=.00018;wf.use_replace=True;wf.offset=1
cs['render_allowlist']=json.dumps([o.name for o in cs.objects]);bpy.context.window.scene=cs
for label in ['front','three_quarter']:
    cs.camera=bpy.data.objects[cs.name+'_'+label];cs.render.filepath=ROOT+'/captures/r014_cage_'+label+'.png';bpy.ops.render.render(write_still=True)
bpy.context.window.scene=s
bm=bmesh.new();bm.from_mesh(h.data);bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table()
remaining=set(e for e in bm.edges if e.is_boundary);loops=[]
while remaining:
    stack=[remaining.pop()];es=[]
    while stack:
        e=stack.pop();es.append(e)
        for v in e.verts:
            for n in v.link_edges:
                if n in remaining:remaining.remove(n);stack.append(n)
    vs=set(v for e in es for v in e.verts)
    loops.append({'edges':len(es),'bounds':[[min(v.co[k] for v in vs),max(v.co[k] for v in vs)] for k in range(3)]})
seen=set();components=[]
for v in bm.verts:
    if v.index in seen:continue
    todo=[v];seen.add(v.index);count=0
    while todo:
        n=todo.pop();count+=1
        for e in n.link_edges:
            other=e.other_vert(n)
            if other.index not in seen:seen.add(other.index);todo.append(other)
    components.append(count)
audit={'source':bpy.data.filepath,'object':h.name,'vertices':len(bm.verts),'edges':len(bm.edges),'faces':len(bm.faces),'components':components,'boundary_loops':loops,'nonmanifold_internal_edges':[e.index for e in bm.edges if not e.is_manifold and not e.is_boundary],'degenerate_faces':[f.index for f in bm.faces if f.calc_area()<1e-12],'face_sizes':{str(k):sum(len(f.verts)==k for f in bm.faces) for k in [3,4,5,6]},'human_forms_approval':False,'art_status':'REVISE'}
bm.free();ev=h.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();v=[tuple(p.co) for p in m.vertices];faces=[tuple(p.vertices) for p in m.polygons];tree=BVHTree.FromPolygons(v,faces,epsilon=0)
hits=[(a,b) for a,b in tree.overlap(tree) if a<b and not set(faces[a]).intersection(faces[b])]
audit['evaluated']={'vertices':len(v),'faces':len(faces),'triangles':sum(len(f)-2 for f in faces),'nonadjacent_self_overlap_pairs':len(hits),'method':'Blender BVHTree overlap, epsilon 0, pairs sharing mesh vertices excluded. One neutral pose only.'};ev.to_mesh_clear()
audit['visible_meshes']=[o.name for o in s.objects if o.type=='MESH' and not o.hide_render]
audit['hair_family_linked_to_active_scene']=[o.name for o in s.objects if any(x in o.name.lower() for x in ['hair','braid','brow','lash'])]
audit['cameras']=[{'name':o.name,'matrix':[list(row) for row in o.matrix_world],'ortho_scale':o.data.ortho_scale} for o in s.objects if o.type=='CAMERA']
audit['render']={'engine':s.render.engine,'samples':s.cycles.samples,'view_transform':s.view_settings.view_transform,'exposure':s.view_settings.exposure}
audit['not_run']=['Deformation or animation tests','UVs and production materials','Rigging','Unreal import','Packaged game','Protected human approval service']
s['status']='HP1 r014 executed head shape candidate; REVISE, no human forms approval.'
s['render_allowlist']=json.dumps([o.name for o in s.objects if not o.hide_render])
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/ada_head_polish_work.blend')
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/ada_head_polish_checkpoint_r014.blend',copy=True)
print('HP1_AUDIT_JSON '+json.dumps(audit))
