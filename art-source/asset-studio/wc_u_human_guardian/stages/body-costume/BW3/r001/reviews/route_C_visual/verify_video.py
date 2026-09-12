"""Native Blender VSE reopen and full145-frame decode; never saves a blend."""
import bpy
import hashlib
import json
from pathlib import Path
import time

out = Path(__file__).resolve().parent
video = out / 'BW3_C_thumb_approach_OTHER_FINGERS_OPEN_NOT_A_GRIP.mp4'
expected = '587e738750da2212fd1a3c87b3be18de9e4515017c68f5e1c457136054bd1df0'
digest = hashlib.sha256(video.read_bytes()).hexdigest()
assert bpy.app.background and digest == expected
decoded = out / 'decoded-verification'
decoded.mkdir(exist_ok=False)
scene = bpy.context.scene
editor = scene.sequence_editor_create()
strip = editor.strips.new_movie('Verify actual encoded MP4', str(video), channel=1, frame_start=1)
data = {'file': str(video), 'bytes': video.stat().st_size, 'sha256': digest,
        'frame_duration': strip.frame_duration, 'fps': strip.fps,
        'dimensions': [strip.elements[0].orig_width, strip.elements[0].orig_height],
        'native_png_count': len(list((out / 'frames').glob('frame_*.png'))),
        'method': 'Existing BW1 native Blender VSE movie-strip reopening, extended to actually decode every frame into PNG in a fresh factory-startup process.',
        'source_saved': False, 'art_approval': False}
assert data['frame_duration'] == 145
assert data['dimensions'] == [800, 800]
assert abs(data['fps'] - 24) < .001
scene.frame_start = 1
scene.frame_end = 145
scene.frame_step = 1
scene.render.fps = 24
scene.render.fps_base = 1
scene.render.resolution_x = 800
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.media_type = 'IMAGE'
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.filepath = str(decoded / 'frame_')
scene.render.use_file_extension = True
scene.render.use_sequencer = True
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1
started = time.perf_counter()
bpy.ops.render.render(animation=True, scene=scene.name)
files = [decoded / f'frame_{frame:04}.png' for frame in range(1, 146)]
assert all(path.is_file() for path in files)
data['decoded_frames'] = len(files)
data['decode_seconds'] = time.perf_counter() - started
data['decoded_frame_hashes'] = [
    {'frame': frame, 'file': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    for frame, path in enumerate(files, 1)]
data['sha256_after'] = hashlib.sha256(video.read_bytes()).hexdigest()
assert data['sha256_after'] == expected
data['status'] = 'ALL145_FRAMES_DECODED_24FPS_800x800'
with (out / 'video_verification.json').open('x', encoding='utf-8') as stream:
    json.dump(data, stream, indent=2)
    stream.write('\n')
print(json.dumps({key: value for key, value in data.items() if key != 'decoded_frame_hashes'}, indent=2))

