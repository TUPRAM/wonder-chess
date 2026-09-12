from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',27)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
board=Image.new('RGB',(2000,2120),(28,33,40));d=ImageDraw.Draw(board);sources=[]
for row,view in enumerate(['back','profile']):
 for col,(prefix,title) in enumerate([('baseline_pair','Recut-neck source / backplate before'),('retained_pair','BW6 rebuilt upper back + connected edge bands')]):
  p=R/'captures'/f'{prefix}_{view}.png';im=Image.open(p).convert('RGB');assert im.size==(1000,1000);x=col*1000;y=row*1060;board.paste(im,(x,y+60));d.text((x+20,y+10),title+' / '+view,font=font,fill='white');sources.append({'path':str(p),'sha256':sha(p)})
board.save(R/'captures/BW6_BACKPLATE_BEFORE_AFTER.png')
section=Image.new('RGB',(2000,1600),(28,33,40));d=ImageDraw.Draw(section)
for i,z in enumerate([1.405,1.445,1.465]):
 p=R/'captures'/f'actual_posterior_section_z{z:.3f}_f49.png';x=(i%2)*1000;y=(i//2)*780;section.paste(Image.open(p).convert('RGB'),(x,y+70));d.text((x+20,y+10),f'Actual posterior section / Z {z:.3f} m / frame49',font=font,fill='white');sources.append({'path':str(p),'sha256':sha(p)})
d.text((1020,860),'Blue = body\nGold = evaluated padded coat\nGrey = outer and inner backplate\n\nLocal sections, not a body-fit approval.\n3.5 mm shell wall preserved.\nNo human or runtime approval.',font=font,fill='white',spacing=14)
section.save(R/'captures/BW6_BACKPLATE_SECTION_BOARD.png')
(R/'records/comparison_composition.json').write_text(json.dumps({'method':'Native Blender pixels pasted without scale change, labels outside source pixels','sources':sources,'baseline_sha256':'c9db4556de382b5a7670c38f060d1b0648c8aa6e02db0c9c65f5a6c08a33ae04','candidate_sha256':'9081f10ab60f36b29d8400b33056efc4e1bfbfa881e42438683fa56db378ec75'},indent=2));print('BACKPLATE_COMPARISON_READY')
