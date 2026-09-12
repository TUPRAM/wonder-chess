import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];SOURCE=R/'ada_bw6_bracer_checkpoint_r002_REVIEW_CANDIDATE.blend';sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False);s=bpy.data.scenes['BW6_RIGHT_BRACER_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
rig=bpy.data.objects['BW6_Bracer_Independent_Rig'];frame=json.loads(s['BW6_bracer_frame']);W=Vector(frame['wrist']);A=Vector(frame['proximal']);D=Vector(frame['dorsal']);T=Vector(frame['transverse'])
root=R/'motion/r002';root.mkdir(parents=True,exist_ok=True)
contexts=[bpy.data.objects[n] for n in json.loads(s['BW6_bracer_context'])];masks=[]
for o in contexts:
 vg=o.vertex_groups.new(name='BW6_TEMP_FOREARM_DISPLAY')
 for v in o.data.vertices:
  q=o.matrix_world@v.co-W;t=q.dot(A);r=(q-A*t).length
  if -.22<t<.29 and r<.145:vg.add([v.index],1,'REPLACE')
 m=o.modifiers.new('Temporary tracked view crop','MASK');m.vertex_group=vg.name;masks.append(m)
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.53,.53,.53);s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world.color=(.06,.06,.06)
s.render.resolution_x=560;s.render.resolution_y=560;s.render.resolution_percentage=100;s.render.film_transparent=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.use_sequencer=False;s.use_nodes=False;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0
cam=bpy.data.objects['BW6_Bracer_Camera_ThreeQuarter'];basecam=cam.matrix_world.copy();restbone=(rig.matrix_world@rig.pose.bones['lowerarm02.R'].matrix).copy();matrices=[]
folder=root/'tracked';folder.mkdir(exist_ok=True)
for fr in range(1,98):
 s.frame_set(fr);bpy.context.view_layer.update();current=rig.matrix_world@rig.pose.bones['lowerarm02.R'].matrix;cam.matrix_world=current@restbone.inverted()@basecam;s.camera=cam;s.render.filepath=str(folder/f'frame_{fr:04}.png');bpy.ops.render.render(write_still=True)
 matrices.append({'frame':fr,'forearm_world':[list(x) for x in current],'camera_world':[list(x) for x in cam.matrix_world]})
for m in masks:m.show_render=False
data=bpy.data.cameras.new('BW6_TEMP_FIXED_ARM_CONTEXT');data.type='ORTHO';data.ortho_scale=.91;fixed=bpy.data.objects.new(data.name,data);s.collection.objects.link(fixed);fixed.location=(1.65,2.2,1.62);fixed.rotation_euler=(Vector((.25,.045,1.30))-fixed.location).to_track_quat('-Z','Y').to_euler();s.camera=fixed
folder=root/'context';folder.mkdir(exist_ok=True)
for fr in range(1,98):s.frame_set(fr);s.render.filepath=str(folder/f'frame_{fr:04}.png');bpy.ops.render.render(write_still=True)
video=bpy.data.scenes.new('BW6_TEMP_BRACER_SOURCE_VIDEO');bpy.context.window.scene=video;video.frame_start=1;video.frame_end=97;video.render.resolution_x=1120;video.render.resolution_y=560;video.render.resolution_percentage=100;video.render.fps=24;video.render.image_settings.media_type='VIDEO';video.render.image_settings.file_format='FFMPEG';video.render.ffmpeg.format='MPEG4';video.render.ffmpeg.codec='H264';video.render.ffmpeg.constant_rate_factor='MEDIUM';video.render.ffmpeg.audio_codec='NONE';video.view_settings.view_transform='Standard';video.view_settings.look='None'
movie=root/'BW6_BRACER_97_AUTHORING_FRAMES_NOT_GAME_CLIPS.mp4';video.render.filepath=str(movie);ed=video.sequence_editor_create()
for channel,view,x in [(1,'tracked',-280),(2,'context',280)]:
 files=[root/view/f'frame_{f:04}.png' for f in range(1,98)];assert all(p.exists() for p in files);strip=ed.strips.new_image(view,str(files[0]),channel=channel,frame_start=1)
 for p in files[1:]:strip.elements.append(p.name)
 strip.transform.offset_x=x
label=ed.strips.new_effect('Scope',type='TEXT',channel=3,frame_start=1,length=97);label.text='BW6 BRACER  |  TRACKED CLOSEUP / FIXED CONTEXT  |  AUTHORING ONLY';label.font_size=18;label.location=(.5,.97);label.color=(1,1,1,1);label.use_shadow=True;video.render.use_sequencer=True;bpy.ops.render.render(animation=True,scene=video.name)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==sha
(root/'source_record.json').write_text(json.dumps({'source':str(SOURCE),'sha256':sha,'movie':str(movie),'movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'frames':97,'fps':24,'dimensions':[1120,560],'rig_action':rig.animation_data.action.name,'tracked_camera_matrices':matrices,'fixed_camera_matrix':[list(x) for x in fixed.matrix_world],'scope':'Actual source-bound renders at all 97 integer frames. Tracked forearm camera isolates local construction; fixed camera shows actual authoring arm motion. No seven game clips, engine or continuous-collision claim.'},indent=2));print('BRACER_SOURCE_MOTION_DONE')
