import bpy,json,hashlib,time
from pathlib import Path
out=Path(__file__).parent;frames=out/'frames';frames.mkdir(exist_ok=True)
source=out.parent/'ada_body_costume_checkpoint_r001_ART_REVISE.blend'
expected='7e71cdf5b737779d84231866e5559cd2950bbf4a65b13430658d957370bbc443'
actual=hashlib.sha256(source.read_bytes()).hexdigest()
assert actual==expected,(actual,expected)
scene=bpy.data.scenes['BW1_BODY_COSTUME'];bpy.context.window.scene=scene
scene.camera=bpy.data.objects['BW1_Camera_three_quarter']
rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
scene.frame_start=1;scene.frame_end=169;scene.frame_step=1
scene.render.fps=24;scene.render.fps_base=1
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.55,.55,.55)
scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH'
scene.display.shading.show_specular_highlight=True
scene.display.shading.background_type='WORLD';scene.world.color=(.09,.09,.09)
scene.render.resolution_x=680;scene.render.resolution_y=880;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
scene.render.filepath=str(frames/'frame_');scene.render.use_file_extension=True
scene.render.film_transparent=False;scene.use_nodes=False
scene.view_settings.view_transform='Standard';scene.view_settings.exposure=0;scene.view_settings.gamma=1
metadata={'status':'RENDERING','source_file':str(source),'source_sha256':actual,'blender_version':bpy.app.version_string,'scene':scene.name,'camera':scene.camera.name,'camera_matrix_world':[list(r) for r in scene.camera.matrix_world],'camera_type':scene.camera.data.type,'ortho_scale':scene.camera.data.ortho_scale,'action':rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None,'nla_tracks':len(rig.animation_data.nla_tracks) if rig.animation_data else 0,'frame_start':1,'frame_end':169,'frame_count':169,'fps':24,'duration_seconds':169/24,'resolution':[680,880],'engine':'BLENDER_WORKBENCH','single_clay_color':[.55,.55,.55],'shadows':True,'cavity':'BOTH','media_boundary':'Blender authoring diagnostic action only; not actual game playback, exported animation, human approval or runtime compatibility evidence.','started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
(out/'metadata.json').write_text(json.dumps(metadata,indent=2))
started=time.perf_counter()
bpy.ops.render.render(animation=True,scene=scene.name)
metadata['render_seconds']=time.perf_counter()-started
metadata['rendered_frames']=len(list(frames.glob('frame_*.png')))
metadata['status']='FRAMES_RENDERED'
(out/'metadata.json').write_text(json.dumps(metadata,indent=2))
print('MOTION_FRAMES_DONE',json.dumps(metadata))

# Native VSE encodes the actual sequence in an unsaved temporary scene.
video=bpy.data.scenes.new('BW1_TEMP_VIDEO_ENCODING');bpy.context.window.scene=video
video.render.resolution_x=680;video.render.resolution_y=880;video.render.resolution_percentage=100
video.render.fps=24;video.render.fps_base=1;video.frame_start=1;video.frame_end=169
video.render.image_settings.media_type='VIDEO';video.render.image_settings.file_format='FFMPEG'
video.render.ffmpeg.format='MPEG4';video.render.ffmpeg.codec='H264';video.render.ffmpeg.constant_rate_factor='MEDIUM';video.render.ffmpeg.ffmpeg_preset='GOOD';video.render.ffmpeg.audio_codec='NONE'
video.render.filepath=str(out/'ada_bw1_articulation_review.mp4')
video.view_settings.view_transform='Standard';video.view_settings.exposure=0;video.view_settings.gamma=1
seq=video.sequence_editor_create();strip=seq.strips.new_image('Actual rendered frames',str(frames/'frame_0001.png'),channel=1,frame_start=1)
for frame in range(2,170):strip.elements.append(f'frame_{frame:04}.png')
video.render.use_sequencer=True
bpy.ops.render.render(animation=True,scene=video.name)
metadata['status']='VIDEO_ENCODED';metadata['video_file']=str(out/'ada_bw1_articulation_review.mp4');metadata['encoding']='Blender native VSE, H264 in MPEG4, no audio';metadata['source_sha256_after']=hashlib.sha256(source.read_bytes()).hexdigest();metadata['finished_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
(out/'metadata.json').write_text(json.dumps(metadata,indent=2))
print('MOTION_VIDEO_DONE',json.dumps(metadata))
