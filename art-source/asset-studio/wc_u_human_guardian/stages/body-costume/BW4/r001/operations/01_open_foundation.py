import bpy, json, hashlib, bmesh
from pathlib import Path
from mathutils import Matrix, Vector
OUT=Path(__file__).resolve().parents[1]
SOURCE=OUT.parents[1]/'BW3/r001/bw3_independent_open_input.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
s=bpy.data.scenes['BW3_COLLISION_FIRST'];bpy.context.window.scene=s;s.frame_set(1)
r=bpy.data.objects['BW3_Derived_Rig'];g=bpy.data.objects['BW3_Derived_Glove']
for m in g.modifiers:
 if m.type=='SUBSURF':m.show_viewport=False;m.show_render=False
bpy.context.view_layer.update()
F=Matrix(json.loads(s['BW2_frame_world']));inv=F.inverted()
deps=bpy.context.evaluated_depsgraph_get();eg=g.evaluated_get(deps);me=eg.to_mesh()
allv=[inv @ (g.matrix_world @ v.co) for v in me.vertices]
ids=[i for i,v in enumerate(allv) if abs(v.x)<.16 and -.13<v.y<.32 and abs(v.z)<.14]
index={old:i for i,old in enumerate(ids)}
verts=[tuple(allv[i]) for i in ids];faces=[[index[v] for v in p.vertices] for p in me.polygons if all(v in index for v in p.vertices)]
weights=[{g.vertex_groups[q.group].name:q.weight for q in g.data.vertices[i].groups} for i in ids]
joints={pb.name:{'head':list(inv @ (r.matrix_world @ pb.head)),'tail':list(inv @ (r.matrix_world @ pb.tail)),'matrix':[list(x) for x in pb.matrix]} for pb in r.pose.bones if pb.name.endswith('.R') and ('finger' in pb.name or pb.name in ['wrist.R','lowerarm01.R'])}
eg.to_mesh_clear()
record={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_object':g.name,'source_vertex_ids':ids,'vertices_m':verts,'faces':faces,'weights':weights,'joints':joints,'metric_frame_world':[list(x) for x in F],'license':'CC0 toigo_gloves_short adaptation; original retained','status':'OPEN_REFERENCE_ONLY'}
(OUT/'records').mkdir(exist_ok=True);(OUT/'captures').mkdir(exist_ok=True)
(OUT/'records/open_glove_geometry.json').write_text(json.dumps(record,indent=2))
# Independent visible editing reference in metric hand coordinates. No copied finger rig.
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.name='BW4_OPEN_FOUNDATION'
mesh=bpy.data.meshes.new('BW4_OpenGlove_Cage');mesh.from_pydata(verts,[],faces);mesh.update()
ob=bpy.data.objects.new('BW4_OpenGlove_CC0_Reference',mesh);s.collection.objects.link(ob)
for p in mesh.polygons:p.use_smooth=True
sub=ob.modifiers.new('Source subdivision unchanged','SUBSURF');sub.levels=1;sub.render_levels=1
for k in sorted({k for w in weights for k in w}):
 vg=ob.vertex_groups.new(name=k)
 for i,w in enumerate(weights):
  if k in w:vg.add([i],w[k],'REPLACE')
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.55,.53,.5);s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH'
s.world=bpy.data.worlds.new('BW4_ReviewWorld');s.world.color=(.065,.065,.065)
s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100
s.view_settings.view_transform='Standard';s.view_settings.look='None'
for name,pos in [('palm',(.05,.07,.55)),('dorsal',(-.03,.09,-.55)),('side',(.55,.08,.08)),('oblique',(.33,.35,.5))]:
 cd=bpy.data.cameras.new('BW4_Open_'+name);c=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector((.004,.085,.018))-c.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=.34;s.camera=c;s.render.filepath=str(OUT/'captures'/('open_'+name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'open_glove_reference.blend'))
print('OPEN_FOUNDATION',len(verts),len(faces),list(joints))
