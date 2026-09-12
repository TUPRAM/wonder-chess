import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;v=R.parents[1]/'armor/motion/BW5_ARMOR_AUTHORING_DIAGNOSTIC_NOT_GAME_CLIPS.mp4';out=R/'decoded';out.mkdir(exist_ok=True)
s=bpy.context.scene;e=s.sequence_editor_create();strip=e.strips.new_movie('Actual encoded BW5 shoulder movie',str(v),channel=1,frame_start=1)
assert strip.frame_duration==97 and abs(strip.fps-24)<.001;assert strip.elements[0].orig_width==800 and strip.elements[0].orig_height==800
s.frame_start=1;s.frame_end=97;s.frame_step=1;s.render.fps=24;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.filepath=str(out/'frame_');s.render.use_sequencer=True;s.view_settings.view_transform='Standard';s.view_settings.look='None'
bpy.ops.render.render(animation=True,scene=s.name)
files=[out/f'frame_{f:04}.png' for f in range(1,98)];assert all(p.exists() for p in files)
(R/'video_verification.json').write_text(json.dumps({'source_movie':str(v),'sha256':hashlib.sha256(v.read_bytes()).hexdigest(),'frames_decoded':97,'dimensions':[800,800],'fps':24,'method':'Native Blender VSE reopen and decode every integer frame to PNG, fresh factory scene.','status':'DECODED_NOT_ART_APPROVED','decoded_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},indent=2))
print('ALL97_DECODED')
