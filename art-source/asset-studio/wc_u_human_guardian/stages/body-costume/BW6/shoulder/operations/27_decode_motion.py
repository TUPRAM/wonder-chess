import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'motion/r002';v=R/'BW6_SHOULDER_DUAL_VIEW_AUTHORING_NOT_GAME_CLIPS.mp4';out=R/'decoded';out.mkdir(exist_ok=True)
s=bpy.context.scene;e=s.sequence_editor_create();strip=e.strips.new_movie('Actual encoded BW6 shoulder movie',str(v),channel=1,frame_start=1)
assert strip.frame_duration==97 and abs(strip.fps-24)<.001;assert strip.elements[0].orig_width==1280 and strip.elements[0].orig_height==640
s.frame_start=1;s.frame_end=97;s.frame_step=1;s.render.fps=24;s.render.resolution_x=1280;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.filepath=str(out/'frame_');s.render.use_sequencer=True;s.view_settings.view_transform='Standard';s.view_settings.look='None';bpy.ops.render.render(animation=True,scene=s.name)
files=[out/f'frame_{f:04}.png' for f in range(1,98)];assert all(p.exists() for p in files)
(R/'video_verification.json').write_text(json.dumps({'source_movie':str(v),'sha256':hashlib.sha256(v.read_bytes()).hexdigest(),'frames_decoded':97,'dimensions':[1280,640],'fps':24,'method':'Native Blender VSE reopened encoded MP4 and decoded every integer frame to PNG in fresh factory scene. No real-time playback claim.','status':'DECODED_NOT_ART_APPROVED','decoded_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},indent=2));print('ALL97_DUALVIEW_DECODED')
