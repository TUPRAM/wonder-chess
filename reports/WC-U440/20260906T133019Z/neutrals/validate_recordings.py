"""Read back actual Blender movie files; this is metadata validation, not visual approval."""
import bpy
import hashlib
import json
from pathlib import Path

ROOT=Path(r'C:/Users/iputu/Documents/Wonder Chess')
REPORT=Path(__file__).resolve().parent
records=[]
errors=[]
for out in sorted((ROOT/'exports/neutrals').glob('wc_n_*')):
    manifest=json.loads((out/'export_manifest.json').read_text())
    source=ROOT/'art-source/neutrals'/out.name/(out.name+'.blend')
    if hashlib.sha256(source.read_bytes()).hexdigest()!=manifest['source_sha256']:
        errors.append(out.name+' source hash mismatch')
    for filename,digest in manifest['files'].items():
        if hashlib.sha256((out/filename).read_bytes()).hexdigest()!=digest:
            errors.append(out.name+'/'+filename+' export hash mismatch')
    for name,clip in manifest['clips'].items():
        path=Path(manifest['review_path'])/('continuous_'+name+'.mp4')
        video=bpy.data.movieclips.load(str(path))
        record={'creature':out.name,'clip':name,'path':str(path),'fps':video.fps,
                'frames':video.frame_duration,'resolution':list(video.size),
                'duration_seconds':video.frame_duration/video.fps,
                'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        if video.fps!=60 or video.frame_duration!=clip['frames'][1] or list(video.size)!=[384,384]:
            errors.append(out.name+'/'+name+' duration/rate/resolution mismatch')
        records.append(record)
if len(records)!=40:errors.append('Expected 40 recordings, saw '+str(len(records)))
summary={'status':'PASS_VIDEO_METADATA_AND_SOURCE_EXPORT_HASHES' if not errors else 'FAIL',
         'blender_version':bpy.app.version_string,'recording_count':len(records),
         'recorded_frames':sum(r['frames'] for r in records),
         'recorded_duration_seconds':sum(r['duration_seconds'] for r in records),
         'records':records,'errors':errors,
         'limitations':['Metadata readback is not continuous visual acceptance.',
                       'No Unreal import or frame-time measurement is implied.']}
(REPORT/'recording-validation.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='records'},indent=2))
if errors:raise RuntimeError('; '.join(errors))
