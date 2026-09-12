import bpy,json,hashlib
from pathlib import Path
out=Path(__file__).parent;video=out/'ada_bw1_articulation_r003_review.mp4'
scene=bpy.context.scene;seq=scene.sequence_editor_create();strip=seq.strips.new_movie('Verify encoded MP4',str(video),channel=1,frame_start=1)
data={'media_type':'VIDEO','file':str(video),'bytes':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'frame_duration':strip.frame_duration,'fps':strip.fps,'dimensions':[strip.elements[0].orig_width,strip.elements[0].orig_height],'png_count':len(list((out/'frames').glob('frame_*.png'))),'verification':'Native Blender video strip reopened encoded MP4 in fresh factory-startup process; no .blend saved.'}
assert data['frame_duration']==169,data
assert data['dimensions']==[680,880],data
assert abs(data['fps']-24)<.001,data
(out/'video_verification.json').write_text(json.dumps(data,indent=2));print(json.dumps(data))
