"""Compose unaltered native Blender pixels into labeled review sheets."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
OUT=Path(__file__).resolve().parents[1];BW5=OUT.parents[1]/'BW5/hand'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',28);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
manifest=json.loads((OUT/'records/capture_manifest.json').read_text());old=json.loads((BW5/'records/capture_manifest.json').read_text())
oldhash={Path(item['path']).name:item['sha256'] for item in old['captures']}
newhash={Path(item['path']).name:item['sha256'] for item in manifest['captures']}
sources=[]
sheet=Image.new('RGB',(2000,3180),(27,31,38));d=ImageDraw.Draw(sheet)
for row,(kind,view) in enumerate([('equipment_hidden','palm'),('equipment_hidden','oblique'),('hilt_only','side')]):
 for col,(root,label,checks) in enumerate([(BW5,'BW5 retained / ART_REVISE',oldhash),(OUT,'BW6 new anatomical surface / ART_REVISE',newhash)]):
  p=root/'captures'/f'retained_{kind}_{view}.png';assert sha(p)==checks[p.name]
  im=Image.open(p).convert('RGB');assert im.size==(1000,1000)
  y=row*1060;sheet.paste(im,(col*1000,y+60));d.text((col*1000+20,y+8),label+' - '+view,font=font,fill=(240,243,249));sources.append({'path':str(p),'sha256':sha(p)})
sheet.save(OUT/'captures/BW5_vs_BW6_ANATOMICAL_HAND_ART_REVISE.png')
sections=Image.new('RGB',(2000,2140),(27,31,38));d=ImageDraw.Draw(sections)
for i,name in enumerate(('index','middle','ring','little')):
 p=OUT/'captures'/f'retained_actual_section_{name}.png';assert sha(p)==newhash[p.name];x=(i%2)*1000;y=(i//2)*1060
 sections.paste(Image.open(p).convert('RGB'),(x,y+60));d.text((x+20,y+8),name+' / actual evaluated transverse section',font=font,fill=(240,243,249));sources.append({'path':str(p),'sha256':sha(p)})
d.text((20,2120),'Blue = glove; orange = actual octagonal hilt. Open wrist ends are intentional. No contact pass.',font=small,fill=(240,243,249))
sections.save(OUT/'captures/BW6_ACTUAL_GRIP_CHANNEL_SECTIONS.png')
plate=Image.new('RGB',(2000,2140),(27,31,38));d=ImageDraw.Draw(plate)
items=[('retained_equipment_hidden_oblique.png','New anatomical mass construction'),('retained_actual_cage_oblique.png','Actual editable cage / same camera'),('retained_uniform_clay_key.png','Uniform clay / area key'),('retained_uniform_clay_reversed_key.png','Same geometry / reversed key')]
for i,(name,title) in enumerate(items):
 p=OUT/'captures'/name;assert sha(p)==newhash[p.name];x=(i%2)*1000;y=(i//2)*1060;plate.paste(Image.open(p).convert('RGB'),(x,y+60));d.text((x+20,y+8),title,font=font,fill=(240,243,249))
plate.save(OUT/'captures/BW6_CAGE_AND_REVERSED_LIGHT_ART_REVISE.png')
(OUT/'records/comparison_composition.json').write_text(json.dumps({'method':'Native 1000x1000 Blender source pixels pasted without resizing or geometry retouching; labels outside source regions','sources':sources,'BW5_frozen_sha256':old['frozen_sha256'],'BW6_frozen_sha256':manifest['frozen_sha256'],'cameras_equal':True,'no_art_approval':True},indent=2))
print('BW6_REVIEW_SHEETS_WRITTEN')
