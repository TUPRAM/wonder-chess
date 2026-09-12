from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parents[1];CAP=OUT/'captures'
def font(size):return ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',size)
def text(draw,xy,value,size=20,fill='#ecece7'):draw.text(xy,value,font=font(size),fill=fill)
def tile(canvas,path,x,y,w):
 im=Image.open(path).convert('RGB');im.thumbnail((w,w),Image.Resampling.LANCZOS);canvas.paste(im,(x,y));return im.size
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
records=[]
# Matching source cameras and unchanged hilt registration. Original source frames
# are preserved separately at 1000 px; this sheet is only a labeled comparison.
im=Image.new('RGB',(1240,2050),'#202327');dr=ImageDraw.Draw(im)
text(dr,(24,16),'BW5 HAND / RETAINED CORRECTION 1 / ART_REVISE',28)
text(dr,(24,56),'Same BW4 cameras; same 30 x 26 mm hilt, 110 mm exposed; guard included in geometry queries.',19)
text(dr,(24,96),'BW4 frozen baseline',24);text(dr,(640,96),'BW5 retained: local channel clear; art/contact fail',22)
for row,view in enumerate(('palm','oblique','axial')):
 y=140+row*630;tile(im,CAP/f'bw4_fresh_hilt_only_{view}.png',16,y,600);tile(im,CAP/f'retained_hilt_only_{view}.png',624,y,600)
 text(dr,(24,y+599),view.upper()+' / hilt only',18);text(dr,(640,y+599),view.upper()+' / hilt only',18)
path=CAP/'BW4_vs_BW5_HAND_ART_REVISE.png';im.save(path);records.append(path)
# Actual transverse section geometry, consistently scaled in saved diagnostic camera.
im=Image.new('RGB',(1240,1420),'#202327');dr=ImageDraw.Draw(im)
text(dr,(24,16),'ACTUAL HILT CHANNEL SECTIONS / RETAINED BW5 CANDIDATE',26)
text(dr,(24,55),'Blue: evaluated glove triangles. Orange: actual octagonal hilt. Empty space is visible; contact remains loose.',19)
for i,(name,xmm) in enumerate((('index',27),('middle',3),('ring',-19),('little',-39))):
 x=16+(i%2)*608;y=105+(i//2)*640;tile(im,CAP/f'retained_actual_section_{name}.png',x,y,600)
 text(dr,(x+8,y+6),f'{name.upper()}  |  X = {xmm:+g} mm',22)
 # 10 mm in the square 160 mm orthographic section, downsampled to 600 px.
 dr.line((x+450,y+558,x+487.5,y+558),fill='#eeeeee',width=3);text(dr,(x+444,y+565),'10 mm',16)
text(dr,(24,1380),'These four planes do not intersect the guard; the unchanged guard is checked in the complete 3D surface query.',17)
path=CAP/'BW5_HAND_ACTUAL_SECTIONS.png';im.save(path);records.append(path)
# Anatomical digit registration proof with the actual guard visible.
im=Image.new('RGB',(1350,1100),'#202327');im.paste(Image.open(CAP/'retained_full_palm.png').convert('RGB'),(0,100));dr=ImageDraw.Draw(im)
text(dr,(24,14),'ANATOMICAL-RIGHT REGISTRATION / ACTUAL GUARD VISIBLE',27)
text(dr,(24,54),'Guardward = local +X. Index and thumb are on that end; little finger is toward the grip end.',19)
projection=json.loads((OUT/'records/anatomical_label_projection.json').read_text())
for i,p in enumerate(projection['labels']):
 x,y=p['image_xy'];y+=100;target=(1040,175+i*75);dr.line((x,y,target[0]-12,target[1]+12),fill='#4ad6e8',width=2);dr.ellipse((x-4,y-4,x+4,y+4),fill='#4ad6e8');text(dr,target,p['label'],20)
for i,line in enumerate(['Selected handle unchanged:','30 x 26 mm octagonal','110 mm exposed span','154.4 mm total length','','Original guard and blade','No pommel assumed','','Local glove only','No wrist integration pass','No game clip pass','No human approval']):text(dr,(1030,610+i*28),line,18)
path=CAP/'BW5_HAND_DIGIT_REGISTRATION.png';im.save(path);records.append(path)
# Rejected second correction stays plainly visible alongside its raw cage.
im=Image.new('RGB',(1240,760),'#202327');dr=ImageDraw.Draw(im);text(dr,(24,15),'REJECTED CORRECTION 2 / PALM-WEB REGRESSION',28)
text(dr,(24,55),'12 raw / 28 evaluated self crossings; 30 boundary edges. Retain correction 1 instead.',20)
tile(im,CAP/'correction2_hilt_only_palm.png',16,112,600);tile(im,CAP/'rejected_correction2_actual_cage.png',624,112,600)
text(dr,(24,720),'Closed-hand silhouette',19);text(dr,(640,720),'Actual raw cage: failed new palm/web transition',19)
path=CAP/'BW5_HAND_REJECTED_CORRECTION2.png';im.save(path);records.append(path)
# Actual encoded video frames, reopened and decoded by Blender in a fresh process.
im=Image.new('RGB',(1240,950),'#202327');dr=ImageDraw.Draw(im);text(dr,(22,16),'ACTUAL MP4 DECODE / STATIC REVIEW TURNTABLE / ART_REVISE',24)
text(dr,(22,53),'All 48 encoded frames decoded. Eight selected temporal views shown; no seven-game-action claim.',18)
sample=(1,7,13,19,25,31,37,43)
for i,frame in enumerate(sample):
 x=12+(i%4)*307;y=100+(i//4)*420;tile(im,OUT/'motion/decoded'/f'frame_{frame:04}.png',x,y,300);text(dr,(x+6,y+307),f'Decoded frame {frame} / 48',17)
path=OUT/'motion/decoded_8_sample_review.png';im.save(path);records.append(path)
(OUT/'records/review_sheet_manifest.json').write_text(json.dumps({'method':'Pillow labels and composition of actual native Blender renders; no geometry or rendered pixels repainted','files':[{'path':str(p),'sha256':sha(p)} for p in records],'decoded_samples':list(sample)},indent=2))
