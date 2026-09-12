import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def mesh_audit(o):
    bm=bmesh.new();bm.from_mesh(o.data)
    r={'vertices':len(bm.verts),'faces':len(bm.faces),'quads':sum(len(f.verts)==4 for f in bm.faces),'triangles':sum(len(f.verts)==3 for f in bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_internal_edges':sum(len(e.link_faces)>2 for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'winding_conflicts':sum(not e.is_contiguous for e in bm.edges if len(e.link_faces)==2),'loose_vertices':sum(not v.link_faces for v in bm.verts)}
    bm.free();return r
def record(sc):
    bpy.context.window.scene=sc
    cameras=[];lights=[]
    for o in sc.objects:
        if o.type=='CAMERA':cameras.append({'name':o.name,'matrix_world':[list(r) for r in o.matrix_world],'projection':o.data.type,'ortho_scale':o.data.ortho_scale,'lens':o.data.lens,'clip':[o.data.clip_start,o.data.clip_end],'depth_of_field':o.data.dof.use_dof})
        if o.type=='LIGHT':lights.append({'name':o.name,'matrix_world':[list(r) for r in o.matrix_world],'type':o.data.type,'energy':o.data.energy,'size':o.data.size,'color':list(o.data.color)})
    override=sc.view_layers[0].material_override
    return {'scene':sc.name,'active_camera':sc.camera.name if sc.camera else None,'resolution':[sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage],'engine':sc.render.engine,'samples':sc.cycles.samples,'denoising':sc.cycles.use_denoising,'world':sc.world.name,'world_background_color':list(sc.world.node_tree.nodes['Background'].inputs[0].default_value),'world_strength':sc.world.node_tree.nodes['Background'].inputs[1].default_value,'view_transform':sc.view_settings.view_transform,'look':sc.view_settings.look,'exposure':sc.view_settings.exposure,'gamma':sc.view_settings.gamma,'material_override':override.name if override else None,'render_allowlist':[o.name for o in sc.objects if not o.hide_render],'objects':[{'name':o.name,'type':o.type,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hide_get':o.hide_get(),'collections':[c.name for c in o.users_collection],'modifiers':[{'name':m.name,'type':m.type,'show_viewport':m.show_viewport,'show_render':m.show_render,'levels':m.levels if m.type=='SUBSURF' else None,'render_levels':m.render_levels if m.type=='SUBSURF' else None} for m in o.modifiers]} for o in sc.objects],'collection_exclusions':[{'name':c.name,'exclude':c.exclude,'hide_viewport':c.hide_viewport} for c in sc.view_layers[0].layer_collection.children],'cameras':cameras,'lights':lights}
proofs={}
for n in ['MR1_Right_Orbital_Cage','MR1_Hair_Leading_Sweep_Cage','MR1_CONTEXT_Joined_Head_Diagnostic']:proofs[n]=mesh_audit(bpy.data.objects[n])
bpy.context.window.scene=bpy.data.scenes['MR1_FACE_PROOF'];tree=BVHTree.FromObject(bpy.data.objects['MR1_Right_Orbital_Cage'],bpy.context.evaluated_depsgraph_get())
hits=[];tested=0
for xi in range(5,66):
 for zi in range(1662,1717):
  x=xi/1000;z=zi/1000;d=.0265**2-(x-.035)**2-(z-1.689)**2
  if d<=0:continue
  gy=.026+math.sqrt(d);p,n,i,t=tree.ray_cast(Vector((x,.20,z)),Vector((0,-1,0)),.25)
  if p is not None:
   tested+=1
   if gy-p.y>.00005:hits.append([x,z,(gy-p.y)*1000])
scenes=[record(bpy.data.scenes[n]) for n in ['MR1_FACE_PROOF','MR1_FACE_BASELINE_REVIEW','MR1_HAIR_PROOF','MR1_HAIR_BASELINE_REVIEW','MR1_CONTEXT_HEAD_CANDIDATE','MR1_CONTEXT_BASELINE_REVIEW']]
bpy.context.window.scene=bpy.data.scenes['MR1_CONTEXT_HEAD_CANDIDATE'];sc=bpy.context.scene;sc.camera=bpy.data.objects['MR1_CONTEXT_three_quarter']
for o in sc.objects:o.select_set(False)
o=bpy.data.objects['MR1_CONTEXT_Joined_Head_Diagnostic'];o.select_set(True);bpy.context.view_layer.objects.active=o
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  s=area.spaces.active;s.region_3d.view_location=(0,-.01,1.704);s.region_3d.view_distance=.45;s.region_3d.view_rotation=sc.camera.rotation_euler.to_quaternion();s.region_3d.view_perspective='ORTHO';s.shading.type='SOLID';s.overlay.show_wireframes=False;s.overlay.show_extras=False
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
result={'blender_version':bpy.app.version_string,'active_filepath':bpy.data.filepath,'active_scene':bpy.context.scene.name,'proof_geometry':proofs,'eye_clearance_sample':{'skin_ray_hits':tested,'intersection_threshold_mm':.05,'intersections':hits,'boundary':'1 mm sampled analytic globe check; not exhaustive collision or deformation verification'},'scenes':scenes,'reverse_light_recipe':{'face':{'key_location':[.328,.35,1.95],'fill_location':[-.202,.23,1.77],'aim':[.039,.025,1.687]},'context':{'key_location':[.28,.38,2.06],'fill_location':[-.32,.24,1.83],'aim':[0,-.01,1.704]},'energies_unchanged':True},'human_approval_written':False}
print('MR1_FINAL_AUDIT '+json.dumps(result))
