import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];source=R/'ada_bw6_bracer_correction2.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW6_RIGHT_BRACER_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
owned=[bpy.data.objects[n] for n in json.loads(s['BW6_bracer_owned'])];ctx=[bpy.data.objects[n] for n in json.loads(s['BW6_bracer_context'])];rig=bpy.data.objects['BW6_Bracer_Independent_Rig']
def sig(o):
 v={'co':[list(v.co) for v in o.data.vertices],'faces':[list(f.vertices) for f in o.data.polygons],'weights':[[[o.vertex_groups[g.group].name,g.weight] for g in v.groups] for v in o.data.vertices]}
 return hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()
def action_sig(a):
 curves=[c for l in a.layers for st in l.strips for bag in st.channelbags for c in bag.fcurves]
 rows=[{'path':c.data_path,'index':c.array_index,'keys':[[list(p.co),p.interpolation,list(p.handle_left),list(p.handle_right)] for p in c.keyframe_points]} for c in curves]
 return hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()
oldrig=bpy.data.objects['BW4_Armor_Independent_Rig'];assert action_sig(rig.animation_data.action)==action_sig(oldrig.animation_data.action)
signature={o.name:sig(o) for o in owned+ctx};s['review_status']='LOCAL_REVIEW_CANDIDATE_NOT_HUMAN_APPROVED';s['runtime_status']='AUTHORING_ONLY_NOT_SEVEN_GAME_CLIPS'
s['bounded_edits']='One initial construction, two substantive corrections; no further geometry revision in this assignment.'
s.camera=bpy.data.objects['BW6_Bracer_Camera_ThreeQuarter'];s.frame_set(1)
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  area.spaces.active.region_3d.view_location=Vector(json.loads(s['BW6_bracer_frame'])['wrist']);area.spaces.active.region_3d.view_distance=.7
work=R/'ada_bw6_bracer_work.blend';frozen=R/'ada_bw6_bracer_checkpoint_r002_REVIEW_CANDIDATE.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(work));bpy.ops.wm.save_as_mainfile(filepath=str(frozen));frozenhash=hashlib.sha256(frozen.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(frozen),use_scripts=False);s=bpy.data.scenes['BW6_RIGHT_BRACER_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
assert {n:sig(bpy.data.objects[n]) for n in signature}==signature
owned=[bpy.data.objects[n] for n in json.loads(s['BW6_bracer_owned'])];ctx=[bpy.data.objects[n] for n in json.loads(s['BW6_bracer_context'])];rig=bpy.data.objects['BW6_Bracer_Independent_Rig']
F=json.loads(s['BW6_bracer_frame']);W=Vector(F['wrist']);A=Vector(F['proximal']);D=Vector(F['dorsal']);T=Vector(F['transverse']);target=W+A*.085
report={'source':str(source),'work':str(work),'checkpoint':str(frozen),'sha256':frozenhash,'work_sha256':hashlib.sha256(work.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'save_reopen_mesh_signatures':signature,'mesh_weight_records_match_reopen':True,'copied_action_matches_original':True,'copied_rig_data_independent':rig.data!=bpy.data.objects['BW4_Armor_Independent_Rig'].data,'clip_scope':'97-frame MPFB authoring action; canonical seven game animations unrun','parts':[],'captures':[]}
for o in owned:
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();report['parts'].append({'name':o.name,'cage_vertices':len(o.data.vertices),'evaluated_triangles':len(me.loop_triangles),'degenerate_polygons':sum(p.area<1e-12 for p in me.polygons),'owner':o.get('owner_bone'),'modifiers':[(m.name,m.type) for m in o.modifiers]});ev.to_mesh_clear()
(R/'records/verification.json').write_text(json.dumps(report,indent=2))
# The following changes are render-only and happen after frozen/reopen verification.
def isolate():
 masks=[]
 for o in ctx:
  vg=o.vertex_groups.new(name='BW6_DIAGNOSTIC_FOREARM_VIEW_ONLY')
  for v in o.data.vertices:
   q=o.matrix_world@v.co-W;t=q.dot(A);r=(q-A*t).length
   if -.22<t<.29 and r<.145:vg.add([v.index],1,'REPLACE')
  m=o.modifiers.new('Temporary forearm image isolation; not saved','MASK');m.vertex_group=vg.name;masks.append(m)
 return masks
masks=isolate();s.cycles.samples=16
def shot(label,cam):
 s.camera=bpy.data.objects['BW6_Bracer_Camera_'+cam];s.render.filepath=str(R/'captures'/(label+'.png'));bpy.ops.render.render(write_still=True);report['captures'].append({'path':s.render.filepath,'frame':s.frame_current,'camera':s.camera.name,'source_checkpoint_sha256':frozenhash,'context':'Unchanged context geometry with temporary forearm-only display mask'});(R/'records/verification.json').write_text(json.dumps(report,indent=2))
shot('r002_isolated_three_quarter','ThreeQuarter')
# Clay comparison uses the exact same source-bound camera and material setup.
clay=bpy.data.materials.new('BW6_Bracer_UniformReviewClay');clay.diffuse_color=(.30,.30,.30,1);clay.use_nodes=True;clay.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.30,.30,.30,1);clay.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.62
s.view_layers[0].material_override=clay
for label,cam in [('r002_clay_dorsal','Dorsal'),('r002_clay_volar','Volar'),('r002_clay_side','Side'),('r002_clay_axial','Axial')]:shot(label,cam)
key=bpy.data.objects['BW6_Bracer_Key'];fill=bpy.data.objects['BW6_Bracer_Fill'];oldenergy=(key.data.energy,fill.data.energy);key.data.energy,fill.data.energy=fill.data.energy,key.data.energy;key.location,targetkey=target-D*.55-T*.3+A*.2,key.location.copy();key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler();shot('r002_reversed_clay','ThreeQuarter');key.location=targetkey;key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler();key.data.energy,fill.data.energy=oldenergy
# Actual new cage: subdivision/wall/bevel disabled, wireframe reads the existing source edges.
states=[]
for o in ctx:o.hide_render=True
for o in owned:
 for m in o.modifiers:
  if m.type!='ARMATURE':states.append((m,m.show_render));m.show_render=False
 wire=o.modifiers.new('Actual control cage edges; unsaved capture','WIREFRAME');wire.thickness=.00065;wire.use_replace=False;wire.use_even_offset=False
shot('r002_actual_control_cage','ThreeQuarter')
for o in owned:o.modifiers.remove(o.modifiers['Actual control cage edges; unsaved capture'])
for m,state in states:m.show_render=state
for o in ctx:o.hide_render=False
# Matched BW5 before image, source bracer itself remains untouched.
for o in owned:o.hide_render=True
before=bpy.data.objects['BW4_CONTEXT_BW1_Bracer_R'].copy();before.data=before.data.copy();s.collection.objects.link(before);before.hide_render=False;before.hide_set(False);shot('bw5_baseline_same_camera_dorsal','Dorsal');before.hide_render=True
for o in owned:o.hide_render=False
# Actual extra wrist bend, using the stress-tested local correction.
wrist=rig.pose.bones['wrist.R'];basis=wrist.matrix_basis.copy();action=rig.animation_data.action;rig.animation_data.action=None;wrist.matrix_basis=basis@Matrix.Rotation(math.radians(25),4,'X');bpy.context.view_layer.update();shot('r002_wrist_Xplus25_stress','ThreeQuarter');wrist.matrix_basis=basis;rig.animation_data.action=action
report['sha256_after_captures']=hashlib.sha256(frozen.read_bytes()).hexdigest();assert report['sha256_after_captures']==frozenhash
(R/'records/verification.json').write_text(json.dumps(report,indent=2));print('FROZEN_REOPEN_CAPTURES_DONE')
