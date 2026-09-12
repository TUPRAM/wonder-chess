from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path('C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW4/r001/armor');C=R/'captures'
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
canvas=Image.new('RGB',(1280,4*690+95),(28,29,32));d=ImageDraw.Draw(canvas)
d.text((18,14),'ADA BW4 ARMOR | MATCHED r003 TO FINAL CANDIDATE',font=font,fill='white')
d.text((18,44),'ART_REVISE | New chest/back + one right shoulder; head/cuff/other context pending',font=small,fill=(235,190,115))
d.text((18,68),'Same saved cameras, neutral light, frame1. Display panels reduced from 960px to 640px.',font=small,fill=(190,195,205))
records=[]
for row,cam in enumerate(['front','three_quarter','profile','back']):
 for col,(prefix,label) in enumerate([('matched_r003_','BW1 frozen r003'),('review_final_','BW4 final / ART_REVISE')]):
  p=C/(prefix+cam+'.png');im=Image.open(p).convert('RGB');canvas.paste(im.resize((640,640),Image.Resampling.LANCZOS),(col*640,95+row*690+36));d.text((col*640+12,95+row*690+8),label+' | '+cam.replace('_',' '),font=font,fill='white');records.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out=C/'BW1_r003_vs_BW4_FINAL_ART_REVISE.png';canvas.save(out)
(R/'records/comparison_provenance.json').write_text(json.dumps({'comparison':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'operations':'Unmodified image contents reduced proportionally and labeled; no retouching or registration warp.','panels':records},indent=2))
print(out)
