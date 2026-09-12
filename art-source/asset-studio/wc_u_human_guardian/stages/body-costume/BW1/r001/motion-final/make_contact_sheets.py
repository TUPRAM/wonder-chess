from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
out=Path(__file__).parent;frame_dir=out/'frames';sheets=out/'contact-sheets';sheets.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
headerfont=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24)
images=[frame_dir/f'frame_{n:04}.png' for n in range(1,170)]
assert all(p.is_file() for p in images)
tile_w,tile_h,label_h,header_h=255,330,26,52
inventory=[]
for start in range(1,170,16):
    end=min(start+15,169);canvas=Image.new('RGB',(tile_w*4,(tile_h+label_h)*4+header_h),(28,30,33));draw=ImageDraw.Draw(canvas)
    draw.text((12,11),f'BW1 actual motion: frames {start:03}-{end:03} | 24 fps | ART_REVISE',font=headerfont,fill=(238,238,238))
    for offset,n in enumerate(range(start,end+1)):
        col=offset%4;row=offset//4;x=col*tile_w;y=header_h+row*(tile_h+label_h)
        with Image.open(frame_dir/f'frame_{n:04}.png') as im:
            assert im.size==(680,880),im.size
            im=im.convert('RGB');im.thumbnail((tile_w,tile_h),Image.Resampling.LANCZOS);canvas.paste(im,(x+(tile_w-im.width)//2,y))
        draw.text((x+9,y+tile_h+2),f'Frame {n:03}  |  {(n-1)/24:0.3f} s',font=font,fill=(240,240,240))
    path=sheets/f'frames_{start:03}_{end:03}.jpg';canvas.save(path,quality=91,subsampling=0)
    inventory.append({'file':str(path),'first_frame':start,'last_frame':end,'frame_count':end-start+1,'dimensions':list(canvas.size)})
manifest={'status':'COMPLETE','source':'Actual unchanged Blender PNG frames; uniformly downsampled 680x880 to 255x330; labels added outside image pixels; no warped artwork','total_frames':169,'sheet_count':len(inventory),'sheets':inventory,'png_frames':[{'frame':n,'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for n,p in enumerate(images,1)]}
(out/'contact_sheet_manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'sheets':len(inventory),'frames':sum(i['frame_count'] for i in inventory)}))
