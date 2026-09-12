import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];source=OUT/'ada_fixed_hand_correction2.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
s=bpy.context.scene;o=bpy.data.objects['BW4_ClosedGlove_Correction2'];s.name='BW4_FIXED_HAND_ART_REVISE'
s['BW4_scope']='ART_REVISE after initial + 2 substantive corrections; no cuff/runtime/approval pass'
s['BW4_equipment_selection']='User: Use the narrower handle proposal; selected candidate only'
s['BW4_remaining_defects']='Confirmed web/thumb/palm crossings; middle base inside handle; guard crossing; contact incomplete'
s['BW4_export_allowlist']=json.dumps([])
s['BW4_study_allowlist']=json.dumps([o.name]+[ob.name for ob in s.objects if ob.name.startswith('BW4_SelectedSword_')])
s['BW4_actual_seven_new_candidate_clips']='NOT_RUN_LOCAL_CONSTRUCTION_FAILED'
s['BW4_engine']='NOT_RUN'
for ob in s.objects:
 if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=False
s.camera=bpy.data.objects['BW4_oblique']
work=OUT/'ada_fixed_hand_work.blend';frozen=OUT/'ada_fixed_hand_checkpoint_ART_REVISE.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(work));bpy.ops.wm.save_as_mainfile(filepath=str(frozen),copy=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sources={str(p):sha(p) for p in [source,work,frozen]}
# Additional hilt-only and bare-glove evidence in unchanged saved cameras.
for name in ['side','palm','axial']:
 s.camera=bpy.data.objects['BW4_'+name]
 for ob in s.objects:
  if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=not ob.name.endswith('handle')
 s.render.filepath=str(OUT/'captures'/('final_selected_hilt_only_'+name+'.png'));bpy.ops.render.render(write_still=True)
# Uniform clay lighting diagnostic. Both images share geometry, camera, fill and exposure.
s.camera=bpy.data.objects['BW4_oblique']
for ob in s.objects:
 if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=True
mat=bpy.data.materials.new('BW4_Diagnostic_Clay');mat.diffuse_color=(.34,.32,.29,1);mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.34,.32,.29,1);bs.inputs['Roughness'].default_value=.7;o.data.materials.clear();o.data.materials.append(mat)
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=4
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.12,.12,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
def area(name,pos,energy,size):
 d=bpy.data.lights.new(name,'AREA');ob=bpy.data.objects.new(name,d);s.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((0,.065,.025))-ob.location).to_track_quat('-Z','Y').to_euler();d.energy=energy;d.shape='DISK';d.size=size;return ob
key=area('BW4_Key',( .16,.06,.30),12,.22);fill=area('BW4_Fill',(-.22,.05,.18),2,.25)
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.filepath=str(OUT/'captures/final_uniform_clay_key.png');bpy.ops.render.render(write_still=True)
key.location=(-.16,.06,.30);key.rotation_euler=(Vector((0,.065,.025))-key.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(OUT/'captures/final_uniform_clay_reversed_key.png');bpy.ops.render.render(write_still=True)
# Source-bound LOCAL inspection turntable, explicitly not the actual seven game clips.
s.render.engine='BLENDER_WORKBENCH';s.view_settings.view_transform='Standard';s.view_settings.look='None'
s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100
for ob in s.objects:
 if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=not ob.name.endswith('handle')
motion=OUT/'motion';motion.mkdir(exist_ok=True);frames=motion/'local_turntable_frames';frames.mkdir(exist_ok=True)
cam=s.camera;cam.data.ortho_scale=.26;target=Vector((0,.07,.025));camera_matrices=[]
for f in range(1,97):
 a=2*math.pi*(f-1)/96;cam.location=target+Vector((.35*math.cos(a),.35*math.sin(a),.22));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(frames/f'frame_{f:04}.png');bpy.ops.render.render(write_still=True);camera_matrices.append([list(row) for row in cam.matrix_world])
files=sorted(frames.glob('frame_*.png'))
video=bpy.data.scenes.new('BW4_LOCAL_INSPECTION_VIDEO');bpy.context.window.scene=video
video.frame_start=1;video.frame_end=96;video.render.resolution_x=800;video.render.resolution_y=800;video.render.resolution_percentage=100;video.render.fps=24;video.render.fps_base=1
video.render.image_settings.media_type='VIDEO';video.render.image_settings.file_format='FFMPEG';video.render.ffmpeg.format='MPEG4';video.render.ffmpeg.codec='H264';video.render.ffmpeg.constant_rate_factor='MEDIUM';video.render.ffmpeg.audio_codec='NONE'
movie=motion/'BW4_fixed_hand_LOCAL_TURNTABLE_ART_REVISE.mp4';video.render.filepath=str(movie);video.view_settings.view_transform='Standard';video.view_settings.look='None';ed=video.sequence_editor_create();strip=ed.strips.new_image('Native source-bound diagnostic frames',str(files[0]),channel=1,frame_start=1)
for p in files[1:]:strip.elements.append(p.name)
label=ed.strips.new_effect('Scope label',type='TEXT',channel=2,frame_start=1,length=96);label.text='BW4 FIXED HAND / ART_REVISE\nLOCAL TURNTABLE - NOT SEVEN GAME CLIPS\nSelected hilt only; guard/blade hidden for inspection';label.font_size=18;label.location=(.5,.94);label.color=(1,1,1,1);label.use_shadow=True
video.render.use_sequencer=True;bpy.ops.render.render(animation=True,scene=video.name)
record={'status':'ART_REVISE','geometry_sources':sources,'geometry_edited_during_capture':False,'camera_matrices':camera_matrices,'local_turntable':{'frames':96,'fps':24,'pixels':[800,800],'source':str(frozen),'sha256':sources[str(frozen)],'movie':str(movie),'movie_sha256':sha(movie)},'actual_seven_candidate_clips':'NOT_RUN_LOCAL_GATE_FAILED','engine':'NOT_RUN','forms_approval':False}
(OUT/'records/final_capture_manifest.json').write_text(json.dumps(record,indent=2))
print('FROZEN_HAND_AND_LOCAL_VIDEO',json.dumps(sources))
