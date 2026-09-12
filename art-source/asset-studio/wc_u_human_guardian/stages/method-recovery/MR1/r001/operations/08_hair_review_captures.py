import bpy,bmesh,json
from mathutils import Vector
root='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001'
sc=bpy.data.scenes['MR1_HAIR_PROOF'];bpy.context.window.scene=sc;col=bpy.data.collections['MR1_HAIR_CANDIDATE_ALLOWLIST']
h=bpy.data.objects['MR1_Hair_Leading_Sweep_Cage']
# Matched original context and visible r003 hair; named failed experiments stay excluded.
baseline=bpy.data.scenes.new('MR1_HAIR_BASELINE_REVIEW')
bc=bpy.data.collections.new('MR1_HAIR_BASELINE_ALLOWLIST');baseline.collection.children.link(bc)
names=[o.get('mr1_context_source') for o in sc.objects if o.get('mr1_context_source')]
names += [o.name for o in bpy.data.scenes['Scene'].objects if o.type=='MESH' and not o.hide_render and (o.name.startswith('ADA_Overlapping_Lock_') or o.name.startswith('ADA_Temporal_Sweep_') or o.name in ['ADA_Temple_Loose_Lock','ADA_Braid_Strand_0','ADA_Braid_Strand_1','ADA_Braid_Strand_2','ADA_Braid_Tail'])]
for n in names:
    src=bpy.data.objects[n];o=src.copy();o.data=src.data.copy();o.name='MR1_HAIR_BASE_'+n;bc.objects.link(o);o.hide_render=False;o.hide_viewport=False
for o in sc.objects:
    if o.type in {'CAMERA','LIGHT'}:bc.objects.link(o)
baseline.world=sc.world;baseline.render.engine='CYCLES';baseline.cycles.samples=16;baseline.cycles.use_denoising=True
baseline.render.resolution_x=900;baseline.render.resolution_y=900;baseline.render.resolution_percentage=100;baseline.render.film_transparent=False
baseline.render.image_settings.file_format='PNG'
baseline.view_settings.view_transform='Standard';baseline.view_settings.look='None';baseline.view_settings.exposure=0;baseline.view_settings.gamma=1
baseline.view_layers[0].material_override=bpy.data.materials['MR1_Uniform_Clay']
baseline['mr1_render_allowlist']=json.dumps([o.name for o in bc.objects])
wire=bpy.data.objects.new('MR1_HAIR_Control_Cage_Wire',h.data.copy());col.objects.link(wire)
wire.data.materials.clear();wire.data.materials.append(bpy.data.materials['MR1_Cage_Dark'])
mod=wire.modifiers.new('Visible control edges','WIREFRAME');mod.thickness=.00028;mod.offset=1;mod.use_replace=True
wire.hide_render=True;wire.hide_set(True)
for label,p in [('PART_GUIDE',(-.0245,.0064,1.8016)),('FRONTAL_HAIRLINE_GUIDE',(.0351,.0435,1.7614)),('TEMPLE_TRANSITION_GUIDE',(.0846,.0166,1.7209)),('REAR_GATHERING_GUIDE',(.025,-.100,1.705))]:
    o=bpy.data.objects.new('MR1_HAIR_'+label,None);col.objects.link(o);o.location=p;o.empty_display_type='PLAIN_AXES';o.empty_display_size=.008;o.hide_render=True;o['scope']='Candidate construction guide, interpreted from approved reference; not new approval'
def cap(scene,name,view):
    bpy.context.window.scene=scene;scene.camera=bpy.data.objects['MR1_HAIR_'+view];scene.render.filepath=root+'/captures/'+name+'_'+view+'.png';bpy.ops.render.render(write_still=True)
for view in ['front','profile','three_quarter','rear','top','root']:cap(baseline,'hair_baseline_clay',view)
bpy.context.window.scene=sc
sc.view_layers[0].material_override=None;wire.hide_render=False;h.modifiers[0].show_render=False
for view in ['three_quarter','top']:cap(sc,'hair_r001_cage',view)
wire.hide_render=True;h.modifiers[0].show_render=True;sc.view_layers[0].material_override=bpy.data.materials['MR1_Uniform_Clay']
contexts=[o for o in sc.objects if o.get('mr1_context_source')]
for o in contexts:o.hide_render=True
cap(sc,'hair_r001_isolated','three_quarter');cap(sc,'hair_r001_isolated','top')
# Cross-section from a temporary evaluated duplicate, never cut the source.
deps=bpy.context.evaluated_depsgraph_get();ev=h.evaluated_get(deps);me=bpy.data.meshes.new_from_object(ev);section=bpy.data.objects.new('MR1_HAIR_SECTION_DIAGNOSTIC_ONLY',me);col.objects.link(section)
spec=json.loads(h['mr1_station_spec']);c=Vector(spec['centers'][3]);t=Vector(spec['frames'][3][0])
bm=bmesh.new();bm.from_mesh(me)
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=c+t*.0008,plane_no=t,clear_outer=True,dist=1e-7)
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=c-t*.0008,plane_no=t,clear_inner=True,dist=1e-7)
bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
for f in me.polygons:f.use_smooth=False
section['scope']='Temporary closed review section of evaluated duplicate; excluded from candidate'
d=bpy.data.cameras.new('MR1_HAIR_section');cam=bpy.data.objects.new('MR1_HAIR_section',d);col.objects.link(cam)
cam.location=c-t*.5;cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=.067;d.clip_start=.001;d.clip_end=20
h.hide_render=True;cap(sc,'hair_r001_cross','section');h.hide_render=False;section.hide_render=True;section.hide_set(True)
for o in contexts:o.hide_render=False
sc.camera=bpy.data.objects['MR1_HAIR_three_quarter'];sc['mr1_render_allowlist']=json.dumps([o.name for o in sc.objects if not o.hide_render])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);bpy.ops.wm.save_as_mainfile(filepath=root+'/hair_mass_proof_r001.blend',copy=True)
print(json.dumps({'baseline_names':names,'hair_control_vertices':len(h.data.vertices),'hair_control_faces':len(h.data.polygons),'cross_section_source_unchanged':True}))
