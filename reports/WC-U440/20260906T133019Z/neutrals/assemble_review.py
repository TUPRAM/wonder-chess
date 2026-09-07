"""Assemble actual rendered poses with explicit sparse-review labels."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(r'C:/Users/iputu/Documents/Wonder Chess')
REPORT=Path(__file__).resolve().parent
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',21)
records=json.loads((REPORT/'pose-samples/index.json').read_text())
names=sorted({r['creature'] for r in records})
for name in names:
    clips=list(dict.fromkeys(r['clip'] for r in records if r['creature']==name))
    canvas=Image.new('RGB',(1000,70+len(clips)*228),'#192634')
    draw=ImageDraw.Draw(canvas)
    draw.text((12,9),name+' | Blender sparse poses',font=title,fill='white')
    draw.text((12,39),'Five sampled frames per clip; not continuous visual or Unreal approval.',font=font,fill='#c2d1df')
    for row,clip in enumerate(clips):
        for record in [r for r in records if r['creature']==name and r['clip']==clip]:
            image=Image.open(record['path']).convert('RGB').resize((196,196),Image.Resampling.LANCZOS)
            x=record['column']*200+2;y=70+row*228
            canvas.paste(image,(x,y))
            draw.text((x+3,y+198),clip+' frame '+str(record['frame']),font=font,fill='white')
    canvas.save(REPORT/(name+'_pose_sheet.png'))
canvas=Image.new('RGB',(1040,660),'#192634')
draw=ImageDraw.Draw(canvas)
draw.text((12,8),'Wonder Chess | Seven original neutral candidates',font=title,fill='white')
draw.text((12,39),'Actual Blender portraits. Unreal import, motion approval, FX and audio remain separate.',font=font,fill='#c2d1df')
for i,name in enumerate(names):
    image=Image.open(ROOT/'exports/neutrals'/name/'portrait.png').convert('RGB').resize((248,248),Image.Resampling.LANCZOS)
    x=8+(i%4)*258;y=76+(i//4)*290
    canvas.paste(image,(x,y))
    draw.text((x+4,y+253),name.removeprefix('wc_n_').title(),font=title,fill='white')
canvas.save(REPORT/'neutral_portrait_contact_sheet.png')
print('Assembled seven sparse pose sheets and seven-portrait contact sheet')
