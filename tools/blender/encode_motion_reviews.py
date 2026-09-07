"""Encode actual render frames at their declared playback speed and verify them."""
import argparse, json, math
from pathlib import Path
from PIL import Image, ImageDraw

parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
out=parser.parse_args().output.resolve()
sequence=json.loads((out/'motion-sequences.json').read_text())
records=[]
for clip in sequence['clips']:
    images=[]
    for index,path in enumerate(sorted(Path(clip['frames_directory']).glob('*.png'))):
        source=Image.open(path).convert('RGB')
        framed=Image.new('RGB',(source.width,source.height+24),'#121820');framed.paste(source,(0,0))
        ImageDraw.Draw(framed).text((8,source.height+5),f"{clip['clip']} | source frame {clip['source_frames'][index]} | 1x",fill='white')
        images.append(framed)
    assert len(images)==clip['frame_count']
    gif=out/f"{clip['clip']}-normal-speed.gif"
    if gif.exists():raise RuntimeError('Preserve existing review media')
    images[0].save(gif,save_all=True,append_images=images[1:],duration=50,loop=0,optimize=False,disposal=2)
    decoded=Image.open(gif);durations=[]
    for index in range(decoded.n_frames):decoded.seek(index);durations.append(decoded.info['duration'])
    assert decoded.n_frames==len(images) and sum(durations)==clip['duration_ms']
    size=192;columns=min(7,len(images));rows=math.ceil(len(images)/columns)
    sheet=Image.new('RGB',(columns*size,rows*(size+24)),'#121820')
    for index,frame in enumerate(images):
        thumbnail=frame.resize((size,size+24),Image.Resampling.LANCZOS)
        sheet.paste(thumbnail,((index%columns)*size,(index//columns)*(size+24)))
    contact=out/f"{clip['clip']}-all-samples.png";sheet.save(contact)
    records.append({'clip':clip['clip'],'frames':decoded.n_frames,'duration_ms':sum(durations),
                    'gif':str(gif),'contact_sheet':str(contact)})
(out/'normal-speed-evidence.json').write_text(json.dumps({'status':'ACTUAL_FRAME_PLAYBACK_ENCODING_VERIFIED',
    'playback_fps':20,'speed_multiplier':1,'clips':records,
    'limits':['Rendered 20Hz source samples, not Unreal playback','Encoding verification does not certify continuous visual review']},indent=2)+'\n')
print(json.dumps(records,indent=2))
