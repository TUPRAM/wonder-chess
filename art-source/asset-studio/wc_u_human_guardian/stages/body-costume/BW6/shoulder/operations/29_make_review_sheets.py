from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];review=R/'review/r002';review.mkdir(parents=True,exist_ok=True);motion=R/'motion/r002';record=json.loads((motion/'video_verification.json').read_text());assert hashlib.sha256(Path(record['source_movie']).read_bytes()).hexdigest()==record['sha256'];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14);sheets=[]
for batch,start in enumerate(range(1,98,20),1):
 image=Image.new('RGB',(1600,1170),'#202226');draw=ImageDraw.Draw(image);draw.text((15,12),f'BW6 r002 actual encoded dual-view frames {start}-{min(start+19,97)} / AUTHORING ONLY',font=font,fill='white')
 for k,fr in enumerate(range(start,min(start+20,98))):
  path=motion/'decoded'/f'frame_{fr:04}.png';assert hashlib.sha256(path.read_bytes()).hexdigest()==record['decoded_hashes'][path.name];x=(k%4)*400;y=48+(k//4)*222;im=Image.open(path).convert('RGB');im.thumbnail((400,200),Image.Resampling.LANCZOS);image.paste(im,(x,y));draw.text((x+8,y+202),f'Frame {fr}  /  {((fr-1)/24):.3f}s',font=small,fill='white')
 target=review/f'chronological_dualview_{batch}.png';image.save(target);sheets.append(str(target))
comparison=Image.new('RGB',(1600,1720),'#202226');draw=ImageDraw.Draw(comparison)
pairs=[('baseline_bw5r003_shoulder_lowered.png','r002_combined_shoulder_lowered.png'),('baseline_bw5r003_rear_three_quarter_73.png','r002_combined_rear_three_quarter_73.png')]
for row,pair in enumerate(pairs):
 for col,name in enumerate(pair):
  im=Image.open(R/'captures'/name).convert('RGB');comparison.paste(im,(col*800,60+row*830));draw.text((col*800+12,20+row*830),('BW5 r003 baseline context' if col==0 else 'BW6 r002 combined context')+(' / lowered' if row==0 else ' / frame73'),font=font,fill='white')
comparison.save(review/'matched_baseline_comparison.png');(review/'source_binding.json').write_text(json.dumps({'movie_sha256':record['sha256'],'all_encoded_frames':97,'review_sheets':sheets,'scope':'Chronological reduced contact sheets for broad motion review; native images are retained separately. Front/rear paired source cameras. Comparison uses same saved cameras but explicitly different torso/coat context.'},indent=2))
print('SHEETS',sheets)
