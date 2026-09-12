"""Prepared native BW2 movie renderer; do not run before the final candidate decision.

Adapted from BW1/r001/motion-r003/render_motion.py. Run in fresh background
Blender with the chosen saved file already open and --disable-autoexec.
After -- supply --render-authorized --source-sha256 HASH --output-dir NEW_DIR.
No blend is saved. Requires a new output directory under BW2/r001.
"""
import argparse
import bpy
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render-authorized', action='store_true', required=True)
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--camera', default='BW2_cam_carry_close')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    assert bpy.app.background
    source = Path(bpy.data.filepath).resolve()
    assert source.parent == ROOT
    expected = args.source_sha256.lower()
    assert sha(source) == expected
    output = args.output_dir.resolve()
    assert output.parent == ROOT and not output.exists(), 'Use a new BW2/r001 child output directory'
    output.mkdir()
    frames = output / 'frames'
    frames.mkdir()
    scene = bpy.data.scenes['BW2_RIGHT_GRIP']
    bpy.context.window.scene = scene
    scene.camera = bpy.data.objects[args.camera]
    scene.camera.data.ortho_scale = .32
    rig = bpy.data.objects['BW1_Temporary_Pose_Rig']
    spec = json.loads(scene['BW2_carry_spec'])
    assert spec['frame_count'] == 145 and spec['held_frames'] == [25, 145]
    scene.frame_start = 1
    scene.frame_end = 145
    scene.frame_step = 1
    scene.render.fps = 24
    scene.render.fps_base = 1
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'SINGLE'
    scene.display.shading.single_color = (.55, .55, .55)
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = 'BOTH'
    scene.display.shading.show_specular_highlight = True
    scene.display.shading.background_type = 'WORLD'
    scene.world.color = (.09, .09, .09)
    scene.render.resolution_x = 800
    scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.filepath = str(frames / 'frame_')
    scene.render.use_file_extension = True
    scene.render.film_transparent = False
    scene.use_nodes = False
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    camera_frames = []
    for frame in range(1, 146):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        camera_frames.append({'frame': frame, 'matrix_world': [list(row) for row in scene.camera.matrix_world]})
    scene.frame_set(1)
    bpy.context.view_layer.update()
    metadata = {
        'status': 'RENDERING', 'source': str(source), 'source_sha256': expected,
        'script_sha256': sha(__file__), 'blender_version': bpy.app.version_string,
        'scene': scene.name, 'camera': scene.camera.name,
        'camera_policy': spec['camera_policy'],
        'camera_projection': {'type': scene.camera.data.type, 'ortho_scale_m': scene.camera.data.ortho_scale,
                              'lens_mm': scene.camera.data.lens, 'clip_start': scene.camera.data.clip_start,
                              'clip_end': scene.camera.data.clip_end},
        'camera_matrices_every_frame': camera_frames,
        'action': rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None,
        'frame_range': [1, 145], 'held_frames': [25, 145], 'frame_count': 145,
        'fps': 24, 'encoded_duration_seconds': 145 / 24, 'keyframe_time_span_seconds': 144 / 24,
        'resolution': [800, 800], 'engine': 'BLENDER_WORKBENCH', 'single_clay_color': [.55, .55, .55],
        'lighting': {'light': 'STUDIO', 'studio_light': scene.display.shading.studiolight_rotate_z,
                     'shadows': True, 'cavity': 'BOTH', 'specular_highlight': True,
                     'background_world_rgb': list(scene.world.color)},
        'view_settings': {'view_transform': scene.view_settings.view_transform,
                          'look': scene.view_settings.look, 'exposure': 0, 'gamma': 1},
        'source_visible_object_names_at_frame1': [obj.name for obj in scene.objects if obj.visible_get()],
        'review_status': 'ART_REVISE',
        'reported_blocker': 'Root reported375 confirmed glove self-crossing pairs in thumb/web; numeric fixed-handle contact screens do not establish G02 success.',
        'source_visibility_preserved': True, 'art_approval': False, 'source_saved': False,
        'media_boundary': 'Actual Blender authoring carry action. No actual-game motion, runtime import, collision certification, or human approval is implied.',
        'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }
    record = output / 'metadata.json'
    record.write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    started = time.perf_counter()
    bpy.ops.render.render(animation=True, scene=scene.name)
    metadata['render_seconds'] = time.perf_counter() - started
    metadata['rendered_frames'] = len(list(frames.glob('frame_*.png')))
    assert metadata['rendered_frames'] == 145
    metadata['status'] = 'FRAMES_RENDERED'
    record.write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')

    # Encode the real frames with Blender's native VSE in an unsaved temporary scene.
    video = bpy.data.scenes.new('BW2_TEMP_VIDEO_ENCODING')
    bpy.context.window.scene = video
    video.render.resolution_x = 800
    video.render.resolution_y = 800
    video.render.resolution_percentage = 100
    video.render.fps = 24
    video.render.fps_base = 1
    video.frame_start = 1
    video.frame_end = 145
    video.render.image_settings.media_type = 'VIDEO'
    video.render.image_settings.file_format = 'FFMPEG'
    video.render.ffmpeg.format = 'MPEG4'
    video.render.ffmpeg.codec = 'H264'
    video.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    video.render.ffmpeg.ffmpeg_preset = 'GOOD'
    video.render.ffmpeg.audio_codec = 'NONE'
    movie = output / 'ada_bw2_fixed_handle_ART_REVISE.mp4'
    video.render.filepath = str(movie)
    video.view_settings.view_transform = 'Standard'
    video.view_settings.exposure = 0
    video.view_settings.gamma = 1
    editor = video.sequence_editor_create()
    strip = editor.strips.new_image('Actual rendered frames', str(frames / 'frame_0001.png'), channel=1, frame_start=1)
    for frame in range(2, 146):
        strip.elements.append(f'frame_{frame:04}.png')
    video.render.use_sequencer = True
    bpy.ops.render.render(animation=True, scene=video.name)
    metadata['status'] = 'VIDEO_ENCODED'
    metadata['video_file'] = str(movie)
    metadata['video_sha256'] = sha(movie)
    metadata['encoding'] = 'Blender native VSE; H264 MPEG4; no audio'
    metadata['source_sha256_after'] = sha(source)
    assert metadata['source_sha256_after'] == expected
    metadata['finished_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    record.write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    print('BW2_NATIVE_VIDEO_DONE', json.dumps(metadata), flush=True)


if __name__ == '__main__':
    main()
