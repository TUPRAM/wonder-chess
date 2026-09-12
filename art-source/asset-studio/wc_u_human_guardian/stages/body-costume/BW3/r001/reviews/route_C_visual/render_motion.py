"""Bounded adaptation of BW2's native render/VSE path; no blend saves."""
import bpy
import hashlib
import json
from pathlib import Path
import time

OUT = Path(__file__).resolve().parent
SOURCE = OUT.parents[1] / 'thumb_route_C_final_method_input.blend'
EXPECTED = '2dad0803a3e8bfd1974b3bf86dbf5377cd462807f02fb9e76f45463205ba2a1d'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert bpy.app.background and Path(bpy.data.filepath).resolve() == SOURCE and sha(SOURCE) == EXPECTED
frames = OUT / 'frames'
frames.mkdir(exist_ok=False)
s = bpy.context.scene
rig = bpy.data.objects['BW3_Derived_Rig']
action_name = rig.animation_data.action.name
s.camera = bpy.data.objects['BW3_cam_carry_close']
s.frame_start = 1
s.frame_end = 145
s.frame_step = 1
s.render.fps = 24
s.render.fps_base = 1
s.render.engine = 'BLENDER_WORKBENCH'
shade = s.display.shading
shade.light = 'STUDIO'
shade.color_type = 'SINGLE'
shade.single_color = (.55, .55, .55)
shade.show_shadows = True
shade.show_cavity = True
shade.cavity_type = 'BOTH'
shade.show_specular_highlight = True
shade.background_type = 'WORLD'
s.world.color = (.09, .09, .09)
s.render.resolution_x = 800
s.render.resolution_y = 800
s.render.resolution_percentage = 100
s.render.image_settings.media_type = 'IMAGE'
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGB'
s.render.filepath = str(frames / 'frame_')
s.render.use_file_extension = True
s.render.film_transparent = False
s.use_nodes = False
s.render.use_sequencer = False
s.view_settings.view_transform = 'Standard'
s.view_settings.look = 'None'
s.view_settings.exposure = 0
s.view_settings.gamma = 1
camera_frames = []
for frame in range(1, 146):
    s.frame_set(frame)
    bpy.context.view_layer.update()
    camera_frames.append({'frame': frame, 'matrix_world': [list(row) for row in s.camera.matrix_world]})
s.frame_set(1)
metadata = {'status': 'RENDERING', 'source': str(SOURCE), 'source_sha256': EXPECTED, 'action': action_name, 'camera': s.camera.name, 'camera_projection': {'type': s.camera.data.type, 'ortho_scale': s.camera.data.ortho_scale}, 'camera_matrices_every_frame': camera_frames, 'frame_range': [1,145], 'frame_count':145, 'fps':24, 'dimensions':[800,800], 'engine':s.render.engine, 'studio_light':shade.studio_light, 'studiolight_rotation':shade.studiolight_rotate_z, 'shadows':True, 'cavity':'BOTH', 'single_clay_color':[.55,.55,.55], 'label':'THUMB APPROACH STUDY / OTHER FINGERS OPEN / NOT A GRIP', 'phases':{'1-25':'authored thumb approach with digits2-5 OPEN','26-145':'retained thumb pose during copied wrist/arm carry with digits2-5 OPEN'}, 'fixture':'unchanged fixed-hand-frame diagnostic cylinder, not actual sword', 'source_saved':False, 'art_approval':False}
record = OUT / 'motion_metadata.json'
record.write_text(json.dumps(metadata,indent=2)+'\n')
started = time.perf_counter()
bpy.ops.render.render(animation=True, scene=s.name)
files = [frames / f'frame_{f:04}.png' for f in range(1,146)]
assert all(p.is_file() for p in files)
metadata['render_seconds'] = time.perf_counter()-started
metadata['native_frames'] = [{'frame':f,'path':str(p),'sha256':sha(p)} for f,p in enumerate(files,1)]
video = bpy.data.scenes.new('BW3_TEMP_THUMB_APPROACH_VIDEO')
bpy.context.window.scene = video
video.frame_start = 1
video.frame_end = 145
video.render.resolution_x = 800
video.render.resolution_y = 800
video.render.resolution_percentage = 100
video.render.fps = 24
video.render.fps_base = 1
video.render.image_settings.media_type = 'VIDEO'
video.render.image_settings.file_format = 'FFMPEG'
video.render.ffmpeg.format = 'MPEG4'
video.render.ffmpeg.codec = 'H264'
video.render.ffmpeg.constant_rate_factor = 'MEDIUM'
video.render.ffmpeg.ffmpeg_preset = 'GOOD'
video.render.ffmpeg.audio_codec = 'NONE'
movie = OUT / 'BW3_C_thumb_approach_OTHER_FINGERS_OPEN_NOT_A_GRIP.mp4'
video.render.filepath = str(movie)
video.view_settings.view_transform = 'Standard'
video.view_settings.look = 'None'
video.view_settings.exposure = 0
video.view_settings.gamma = 1
ed = video.sequence_editor_create()
strip = ed.strips.new_image('Actual native thumb study frames',str(files[0]),channel=1,frame_start=1)
for path in files[1:]:
    strip.elements.append(path.name)
label = ed.strips.new_effect('Scope label; not a grip',type='TEXT',channel=2,frame_start=1,length=145)
label.text = 'THUMB APPROACH STUDY\nOTHER FINGERS OPEN / NOT A GRIP'
label.font_size = 22
label.location = (.5,.94)
label.color = (1,1,1,1)
label.use_shadow = True
video.render.use_sequencer = True
bpy.ops.render.render(animation=True,scene=video.name)
metadata['video_file'] = str(movie)
metadata['video_sha256'] = sha(movie)
metadata['status'] = 'ALL145_NATIVE_FRAMES_RENDERED_AND_VIDEO_ENCODED'
metadata['source_sha256_after'] = sha(SOURCE)
metadata['action_name_after'] = rig.animation_data.action.name
assert metadata['source_sha256_after'] == EXPECTED and metadata['action_name_after'] == action_name
record.write_text(json.dumps(metadata,indent=2)+'\n')
print('BW3_C_VIDEO_DONE '+json.dumps({'movie':str(movie),'frames':145,'source_unchanged':True,'action':action_name}))
