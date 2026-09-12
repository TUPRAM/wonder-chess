from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path('C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW4/r001/armor');selected=[1,13,20,25,37,49,61,73,97]
im=Image.new('RGB',(1200,1320),(26,28,30));d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
d.text((15,10),'BW4 ARMOR | DECODED MOVIE SAMPLES | ART_REVISE',font=font,fill='white');d.text((15,36),'97 integer frames rendered + decoded. These 9 samples are local MPFB diagnostic poses, not game clips.',font=small,fill=(240,197,135))
for k,fr in enumerate(selected):
 src=R/'motion/decoded'/f'frame_{fr:04}.png';pic=Image.open(src).convert('RGB').resize((400,400),Image.Resampling.LANCZOS);x=(k%3)*400;y=65+(k//3)*418;im.paste(pic,(x,y));d.text((x+8,y+402),f'Frame {fr}',font=small,fill='white')
path=R/'motion/decoded_motion_review_9_samples.png';im.save(path);print(path)
