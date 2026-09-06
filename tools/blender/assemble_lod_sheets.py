"""Label and compare actual LOD renders without altering their geometry."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[2]
ids=json.loads((root/'data/rules.alpha.json').read_text())['alpha_unit_ids']
units={u['id']:u for u in json.loads((root/'data/units.json').read_text())['units']}
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
for section in range(2):
    sheet=Image.new('RGB',(576,6*220),(21,30,43));draw=ImageDraw.Draw(sheet)
    for row,uid in enumerate(ids[section*6:(section+1)*6]):
        for lod in (0,1,2):
            shot=Image.open(root/f'reports/WC-330/{uid}/LOD{lod}_192px.png').convert('RGB')
            sheet.paste(shot,(lod*192,row*220))
            draw.text((lod*192+6,row*220+195),f'{units[uid]["name"]} LOD{lod}',font=font,fill=(234,225,205))
    sheet.save(root/f'reports/WC-330/roster/lod_comparison_{section+1}.png')
print('Assembled 36 actual small-scale LOD renders.')
