"""Retain correction 1, reject correction 2; inspect source-bound surfaces."""
import bpy,bmesh,json,hashlib,math
import numpy as np
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
OUT=Path(__file__).resolve().parents[1];BW4=OUT.parents[1]/'BW4/r001'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
baseline=BW4/'ada_fixed_hand_checkpoint_ART_REVISE.blend'
source=OUT/'ada_bw5_hand_correction1.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
s=bpy.context.scene;o=bpy.data.objects['BW5_ClosedGlove_Correction1'];o.name='BW5_ClosedGlove_Retained'
s.name='BW5_FIXED_HAND_ART_REVISE';s['BW5_status']='ART_REVISE: retain correction1; correction2 worsened palm/web topology'
s['BW5_visual_blockers']='Repeated ring-like fingers, flat stretched palm flow, hook-like thumb/thenar, incomplete distributed contact'
s['BW5_runtime']='NOT_RUN_LOCAL_ART_GATE_NOT_MET';s['BW5_human_approval']='NOT_ISSUED'
s['BW5_study_allowlist']=json.dumps([o.name]+['BW4_SelectedSword_'+n for n in ('handle','guard','blade')])
s['BW5_export_allowlist']='[]'
o['status']='ART_REVISE; local transverse surface screen clear, visual construction/contact incomplete'
o['representation']='New fixed glove derivative based on CC0 source dimensions and exact wrist opening; old BW4 source retained hidden independently'
record=json.loads((OUT/'records/correction1_construction.json').read_text());regions=record['anatomical_digit_construction']
declared={}
for n in (2,3,4,5):
 ids=regions[f'{n}_new_digit'];chosen=[ids[station*16+k] for station in (5,6) for k in (2,3,4,5,6)]
 name={2:'index',3:'middle',4:'ring',5:'little'}[n]
 declared[name]={'region':'Distal palmar surface; stations 5 and 6; profile sector 2 3 4 5 6','ids':chosen,'declared_without_nearest_vertex_selection':True}
 vg=o.vertex_groups.new(name='BW5_CONTACT_'+name);vg.add(chosen,1,'REPLACE')
ids=regions['thumb_new_surface'];chosen=[ids[station*16+k] for station in (3,4) for k in (14,15,0,1,2)]
declared['thumb']={'region':'Opposing distal thumb surface; stations 3 and 4; sector 14 15 0 1 2','ids':chosen,'declared_without_nearest_vertex_selection':True}
vg=o.vertex_groups.new(name='BW5_CONTACT_thumb');vg.add(chosen,1,'REPLACE')
(OUT/'records/retained_pad_mapping_before_scoring.json').write_text(json.dumps(declared,indent=2))
for ob in s.objects:
 if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=False
s.camera=bpy.data.objects['BW4_oblique'];s.render.filepath=''
work=OUT/'ada_bw5_hand_work.blend';frozen=OUT/'ada_bw5_hand_checkpoint_ART_REVISE.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(work));bpy.ops.wm.save_as_mainfile(filepath=str(frozen),copy=True)
frozenhash=sha(frozen)
manifest={'retained_source':str(source),'retained_source_sha256':sha(source),'work':str(work),'work_sha256':sha(work),'frozen':str(frozen),'frozen_sha256':frozenhash,'BW4_preserved':{'file':str(baseline),'sha256':sha(baseline)},'rejected_candidate':str(OUT/'ada_bw5_hand_correction2.blend'),'rejected_sha256':sha(OUT/'ada_bw5_hand_correction2.blend'),'no_geometry_change_in_capture':True,'cameras':{},'captures':[],'scope':'Static authoring construction; no source/action/game skeleton modification or seven game clip validation'}
def render(name):
 path=OUT/'captures'/name;s.render.filepath=str(path);bpy.ops.render.render(write_still=True);manifest['captures'].append({'path':str(path),'sha256':sha(path),'camera':s.camera.name,'matrix_world':[list(r) for r in s.camera.matrix_world],'source_sha256':frozenhash})
def equipment(mode):
 for ob in s.objects:
  if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=mode=='hidden' or (mode=='hilt' and not ob.name.endswith('handle'))
for name in ('palm','dorsal','side','underside','oblique','axial'):
 s.camera=bpy.data.objects['BW4_'+name];manifest['cameras'][name]={'matrix_world':[list(r) for r in s.camera.matrix_world],'ortho_scale':s.camera.data.ortho_scale}
 equipment('full');render('retained_full_'+name+'.png')
 equipment('hilt');render('retained_hilt_only_'+name+'.png')
 if name in ('palm','oblique','underside','side'):
  equipment('hidden');render('retained_equipment_hidden_'+name+'.png')
# Anatomy markers are projected from actual construction landmarks; labels are
# composited later without altering rendered anatomy.
s.camera=bpy.data.objects['BW4_palm'];labels=[]
for name,x in [('index',.027),('middle',.003),('ring',-.019),('little',-.039)]:
 p=Vector((x,.088,.060));uv=world_to_camera_view(s,s.camera,p);labels.append({'label':name,'world_m':list(p),'image_xy':[uv.x*1000,(1-uv.y)*1000]})
p=Vector((.034,.056,.032));uv=world_to_camera_view(s,s.camera,p);labels.append({'label':'thumb / index side','world_m':list(p),'image_xy':[uv.x*1000,(1-uv.y)*1000]})
(OUT/'records/anatomical_label_projection.json').write_text(json.dumps({'source':str(frozen),'sha256':frozenhash,'camera':'BW4_palm','labels':labels,'guard_starts_x_m':.059,'handle_axis_guard_to_end':[-1,0,0]},indent=2))
# Actual raw cage: a separate unsaved overlay copy has wireframe geometry only.
equipment('hidden');sub=o.modifiers[0];sub.show_render=False;sub.show_viewport=False
wire=bpy.data.objects.new('BW5_Actual_Cage_Overlay',o.data.copy());s.collection.objects.link(wire);wire.color=(.015,.02,.025,1)
w=wire.modifiers.new('Actual source edges','WIREFRAME');w.thickness=.00022;w.use_replace=True
for name in ('palm','oblique','side','underside'):
 s.camera=bpy.data.objects['BW4_'+name];render('retained_actual_cage_'+name+'.png')
bpy.data.objects.remove(wire,do_unlink=True);sub.show_render=True;sub.show_viewport=True
# Balanced and reversed area key: same source, exposure, material and camera.
s.camera=bpy.data.objects['BW4_oblique'];s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=4
mat=bpy.data.materials.new('BW5_Neutral_Clay_Diagnostic');mat.diffuse_color=(.34,.32,.29,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.34,.32,.29,1);bs.inputs['Roughness'].default_value=.7;o.data.materials.clear();o.data.materials.append(mat)
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.12,.12,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.3
target=Vector((0,.065,.025))
def area(name,pos,power,size):
 d=bpy.data.lights.new(name,'AREA');ob=bpy.data.objects.new(name,d);s.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();d.energy=power;d.shape='DISK';d.size=size;return ob
key=area('BW5_Diagnostic_Key',(.16,.06,.30),1.3,.22);fill=area('BW5_Diagnostic_Fill',(-.22,.05,.18),.20,.25)
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
render('retained_uniform_clay_key.png');key.location=(-.16,.06,.30);key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler();render('retained_uniform_clay_reversed_key.png')
for ob in (key,fill):bpy.data.objects.remove(ob,do_unlink=True)
s.render.engine='BLENDER_WORKBENCH';s.view_settings.view_transform='Standard';s.view_settings.look='None'
# Actual evaluated plane intersections, not drawn estimates of cross sections.
def geo(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();pts=[ev.matrix_world@v.co for v in me.vertices];tri=[tuple(t.vertices) for t in me.loop_triangles];ev.to_mesh_clear();return pts,tri
def section_segments(ob,x):
 pts,tri=geo(ob);segments=[]
 for ids in tri:
  hits=[]
  for a,b in zip(ids,ids[1:]+ids[:1]):
   va,vb=pts[a],pts[b];da=va.x-x;db=vb.x-x
   if da*db<0:
    q=va+(vb-va)*(da/(da-db))
    if not any((q-p).length<1e-8 for p in hits):hits.append(q)
  if len(hits)==2:segments.append(hits)
 return segments
def lines(name,segments,color):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=.00027;cu.bevel_resolution=1;cu.resolution_u=1
 for a,b in segments:
  sp=cu.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
 ob=bpy.data.objects.new(name,cu);s.collection.objects.link(ob);ob.color=(*color,1);return ob
sections={};equipment('hidden');o.hide_render=True
cd=bpy.data.cameras.new('BW5_Actual_Section_Camera');cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);cd.type='ORTHO';cd.ortho_scale=.16
for name,x in [('index',.027),('middle',.003),('ring',-.019),('little',-.039)]:
 segs=section_segments(o,x);hs=section_segments(bpy.data.objects['BW4_SelectedSword_handle'],x);gs=section_segments(bpy.data.objects['BW4_SelectedSword_guard'],x)
 sections[name]={'plane_x_m':x,'normal':[1,0,0],'glove_evaluated_segments_m':[[list(a),list(b)] for a,b in segs],'actual_handle_segments_m':[[list(a),list(b)] for a,b in hs],'actual_guard_segments_m':[[list(a),list(b)] for a,b in gs]}
 objects=[lines('BW5_Glove_Cut',segs,(.22,.74,.90)),lines('BW5_Actual_Octagonal_Hilt_Cut',hs,(1,.52,.12))]
 if gs:objects.append(lines('BW5_Guard_Cut',gs,(.88,.2,.22)))
 aim=Vector((x,.059,.025));cam.location=aim+Vector((-.5,0,0));cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam;render('retained_actual_section_'+name+'.png')
 for ob in objects:bpy.data.objects.remove(ob,do_unlink=True)
(OUT/'records/actual_transverse_sections.json').write_text(json.dumps({'source':str(frozen),'source_sha256':frozenhash,'space':'metres in retained BW4 hand coordinate frame','scope':'Actual evaluated mesh triangles, fixed planes normal to hilt axis. Guard retained in full 3D query; guard lies outside these X planes.','sections':sections},indent=2))
o.hide_render=False;equipment('hilt')
# Local inspection motion is explicitly static geometry with a moving review camera.
motion=OUT/'motion';frames=motion/'frames';frames.mkdir(parents=True,exist_ok=True)
cam.data.ortho_scale=.26;s.camera=cam;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100
matrices=[];target=Vector((0,.06,.025))
for f in range(1,49):
 a=2*math.pi*(f-1)/48;cam.location=target+Vector((.35*math.cos(a),.35*math.sin(a),.22));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(frames/f'frame_{f:04}.png');bpy.ops.render.render(write_still=True);matrices.append([list(r) for r in cam.matrix_world])
files=sorted(frames.glob('frame_*.png'));video=bpy.data.scenes.new('BW5_LOCAL_STATIC_GLOVE_INSPECTION');bpy.context.window.scene=video
video.frame_start=1;video.frame_end=48;video.render.resolution_x=800;video.render.resolution_y=800;video.render.resolution_percentage=100;video.render.fps=24;video.render.fps_base=1
video.render.image_settings.media_type='VIDEO';video.render.image_settings.file_format='FFMPEG';video.render.ffmpeg.format='MPEG4';video.render.ffmpeg.codec='H264';video.render.ffmpeg.constant_rate_factor='MEDIUM';video.render.ffmpeg.audio_codec='NONE'
movie=motion/'BW5_HAND_ART_REVISE_STATIC_INSPECTION_NOT_GAME_CLIPS.mp4';video.render.filepath=str(movie);video.view_settings.view_transform='Standard';video.view_settings.look='None';ed=video.sequence_editor_create();strip=ed.strips.new_image('Native static candidate review frames',str(files[0]),channel=1,frame_start=1)
for p in files[1:]:strip.elements.append(p.name)
label=ed.strips.new_effect('Scope',type='TEXT',channel=2,frame_start=1,length=48);label.text='BW5 HAND / ART_REVISE\nSTATIC CONSTRUCTION TURNTABLE - NOT GAME CLIPS\nGuard/blade hidden visually; included in geometry checks';label.font_size=18;label.location=(.5,.94);label.color=(1,1,1,1);label.use_shadow=True
video.render.use_sequencer=True;bpy.ops.render.render(animation=True,scene=video.name)
manifest['motion']={'path':str(movie),'sha256':sha(movie),'frames':48,'fps':24,'camera_matrices':matrices,'scope':'Static glove/hilt with rotating diagnostic camera; NOT candidate animation or wrist integration'}
(OUT/'records/capture_manifest.json').write_text(json.dumps(manifest,indent=2))
print('BW5_RETAINED_FROZEN',frozenhash,flush=True)
