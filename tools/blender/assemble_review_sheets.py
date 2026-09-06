"""Assemble labeled contact sheets from actual Blender renders; no synthetic poses."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[2]
ids=json.loads((root/'data/rules.alpha.json').read_text())['alpha_unit_ids']
units={u['id']:u for u in json.loads((root/'data/units.json').read_text())['units']}
output=root/'reports/WC-330/roster';output.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',14)
portraits=Image.new('RGB',(1024,900),(21,30,43));draw=ImageDraw.Draw(portraits)
clips=('Idle','Move','Attack','Active','Hit','Defeat','Victory')
grid=Image.new('RGB',(1260,12*216),(21,30,43));gd=ImageDraw.Draw(grid)
for index,uid in enumerate(ids):
    directory=root/f'reports/WC-330/{uid}'
    portrait=Image.open(root/f'exports/heroes/{uid}/portrait.png').convert('RGB')
    portrait.thumbnail((256,256));x=(index%4)*256;y=(index//4)*300
    portraits.paste(portrait,(x,y));draw.text((x+12,y+263),units[uid]['name'],font=font,fill=(234,225,205))
    # This preview is generated from the same actual model render.
    tiny=portrait.copy();tiny.thumbnail((96,96));tiny.save(directory/'preview_96px.png')
    gd.text((8,index*216),units[uid]['name']+' | actual Blender key-pose renders',font=small,fill=(234,225,205))
    for ci,clip in enumerate(clips):
        path=directory/f'clip_{clip}.png'
        if not path.is_file():raise FileNotFoundError(path)
        shot=Image.open(path).convert('RGB');shot.thumbnail((180,180));grid.paste(shot,(ci*180,index*216+20))
        gd.text((ci*180+8,index*216+198),clip,font=small,fill=(234,225,205))
portraits.save(output/'twelve_hero_portraits.png');grid.save(output/'84_key_pose_contact_sheet.png')
print('Assembled 12 model-render portraits and 84 actual key-pose render references. This is not continuous animation acceptance.')
