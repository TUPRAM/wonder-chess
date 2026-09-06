from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[2]
ids=['wc_u_elf_ranger','wc_u_elf_priest','wc_u_dwarf_guardian','wc_u_dwarf_ranger','wc_u_dwarf_warrior']
units={u['id']:u for u in json.loads((root/'data/units.json').read_text())['units']}
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',13)
sheet=Image.new('RGB',(9*180,5*215),(21,30,43));draw=ImageDraw.Draw(sheet)
for row,uid in enumerate(ids):
    for ci,clip in enumerate(('Move','Attack','Active')):
        for si,stage in enumerate(('anticipation','release','recovery')):
            x=(ci*3+si)*180;y=row*215
            shot=Image.open(root/f'reports/WC-330/{uid}/contact_{clip}_{stage}.png').convert('RGB');shot.thumbnail((180,180));sheet.paste(shot,(x,y))
            draw.text((x+4,y+180),units[uid]['name'],font=font,fill=(234,225,205))
            draw.text((x+4,y+196),clip+' '+stage,font=font,fill=(234,225,205))
sheet.save(root/'reports/WC-330/roster/support_motion_contact_sheet.png')
print('Assembled 45 actual sampled support-hand pose renders.')
