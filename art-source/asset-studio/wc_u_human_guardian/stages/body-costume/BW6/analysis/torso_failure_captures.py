import bpy,json,hashlib,math,bmesh,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).parent;source=R.parent/'armor/ada_bw6_upper_combined_r001.blend';sha=hashlib.sha256(source.read_bytes()).hexdigest();d=json.loads((R/'torso_failure_localization.json').read_text());folder=R/'torso_failure_captures';folder.mkdir(exist_ok=True);metadata=[]
def load():
 bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;return s
def setup(s,o,target,location,scale):
 for q in s.objects:
  if q.type=='MESH':q.hide_render=q!=o
 o.hide_render=False;o.hide_set(False);s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=960;s.render.resolution_y=960;s.render.resolution_percentage=100;s.display.shading.color_type='MATERIAL';s.display.shading.light='STUDIO';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.view_settings.view_transform='Standard';s.view_settings.look='None';s.use_nodes=False;s.render.use_sequencer=False
 cam=bpy.data.objects['BW4_Camera_shoulder'];cam.location=location;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.camera=cam;return cam
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
def capture(s,label,extra):
 s.render.filepath=str(folder/(label+'.png'));bpy.ops.render.render(write_still=True);metadata.append({'image':str(folder/(label+'.png')),'frame':s.frame_current,'camera_matrix':list(map(list,s.camera.matrix_world)),'scale':s.camera.data.ortho_scale,**extra})
s=load();s.frame_set(1);o=bpy.data.objects['BW6_PaddedCoat_Tailored'];original=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];rig=bpy.data.objects['BW4_Armor_Independent_Rig'];bones=set(rig.data.bones.keys());b=np.array([original.matrix_world@v.co for v in original.data.vertices]);same=[]
for v in o.data.vertices:
 p=o.matrix_world@v.co
 if abs(p.x)<.225:continue
 ds=np.linalg.norm(b-np.array(p),axis=1);j=int(np.argmin(ds))
 if ds[j]>1e-6:continue
 ga={o.vertex_groups[g.group].name:g.weight for g in v.groups if o.vertex_groups[g.group].name in bones};gb={original.vertex_groups[g.group].name:g.weight for g in original.data.vertices[j].groups if original.vertex_groups[g.group].name in bones};same.append(ga.keys()==gb.keys() and max([abs(ga[k]-gb[k]) for k in ga] or [0])<1e-6)
d['sleeve_source_correspondence']['coincident_same_bone_weights']=sum(same);d['sleeve_source_correspondence']['weight_comparison_note']='Original all-group comparison includes new non-skeletal thickness groups; use bone-only comparison for rig inheritance.';(R/'torso_failure_localization.json').write_text(json.dumps(d,indent=2))
for m in o.modifiers:
 if m.type in ['SUBSURF','SOLIDIFY']:m.show_render=False;m.show_viewport=False
colors=[(.65,.65,.65),(.8,.12,.08),(.95,.48,.08),(.55,.13,.68),(.02,.02,.02)];o.data.materials.clear()
for i,c in enumerate(colors):o.data.materials.append(material('Region_'+str(i),c))
regions={}
for hit in d['frames']['1']['full_self']['mapped_hits']:regions[hit['nearest_control_vertex']]={'collar_and_neck_saddle':1,'front_underplate':2,'armhole_axilla':3}.get(hit['region'],0)
for poly in o.data.polygons:poly.material_index=max([regions.get(i,0) for i in poly.vertices])
w=o.modifiers.new('Actual cage wire overlay','WIREFRAME');w.thickness=.00065;w.use_replace=False;w.use_even_offset=False;w.material_offset=4
setup(s,o,(0,-.01,1.34),(0,3,1.50),.64);capture(s,'rest_control_cage_region_map',{'meaning':'Actual posed cage, Subsurf and Solidify hidden for diagnostic only. Faces adjacent to nearest failing controls: red collar, orange front underplate, purple axilla. This is localized association, not exact raw/evaluated face correspondence.'})
for fr in [20,49]:
 for inherited in [False,True]:
  s=load();s.frame_set(fr);o=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous' if inherited else 'BW6_PaddedCoat_Tailored'];o.data.materials.clear();o.data.materials.append(material('DiagnosticGrey',(.62,.62,.62)));setup(s,o,(.31,.02,1.35),(2,3,1.85),.56);capture(s,('inherited' if inherited else 'current')+'_sleeve_'+str(fr),{'meaning':'Only the named actual garment evaluated through its existing rig at identical camera and authoring pose.','object':o.name})
s=load();s.frame_set(1);o=bpy.data.objects['BW6_PaddedCoat_Tailored'];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=bpy.data.meshes.new_from_object(ev);snapshot=bpy.data.objects.new('TEMP_Actual_Collar_Cutaway',mesh);s.collection.objects.link(snapshot);snapshot.matrix_world=o.matrix_world.copy();bm=bmesh.new();bm.from_mesh(mesh);cut=[f for f in bm.faces if f.calc_center_median().z<1.425 or f.calc_center_median().y>-.05];bmesh.ops.delete(bm,geom=cut,context='FACES');bm.to_mesh(mesh);bm.free();mesh.materials.clear();mesh.materials.append(material('ActualCollarGrey',(.58,.58,.58)));setup(s,snapshot,(0,-.08,1.50),(1.3,3,2.05),.36)
markers=bmesh.new();seen=set()
for h in d['frames']['1']['full_self']['mapped_hits']:
 p=Vector(h['point_world_m']);key=tuple(round(v/.004) for v in p)
 if h['region']!='collar_and_neck_saddle' or p.y>-.05 or key in seen:continue
 seen.add(key);made=bmesh.ops.create_icosphere(markers,subdivisions=1,radius=.0016);bmesh.ops.translate(markers,verts=made['verts'],vec=p)
mm=bpy.data.meshes.new('TEMP_actual_crossing_markers');markers.to_mesh(mm);markers.free();mark=bpy.data.objects.new('TEMP_self_crossing_points',mm);s.collection.objects.link(mark);mm.materials.append(material('ConfirmedSelfRed',(.95,.06,.03)));capture(s,'collar_inner_wall_cutaway',{'meaning':'Actual evaluated collar snapshot; front half and garment below1.425m removed only in temporary render scene. Red markers are spatially binned confirmed self-crossing means from the exact source,1.6mm radius. Not an edited garment candidate.'})
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha;(R/'torso_failure_capture_sources.json').write_text(json.dumps({'source':str(source),'sha256':sha,'source_unchanged':True,'captures':metadata},indent=2));print('READONLY_CAPTURES_COMPLETE',sum(same),len(same))
