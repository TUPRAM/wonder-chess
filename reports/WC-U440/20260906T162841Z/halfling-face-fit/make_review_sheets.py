from pathlib import Path
from PIL import Image,ImageDraw
import json
root=Path(__file__).resolve().parent
for hero in ('finn','nella','milo'):
    source=root/hero
    if not (source/'completed.json').exists(): continue
    for name,labels,columns,cell in [('views-review',('front','side','back','three-quarter','face','game-angle'),3,320),('sparse-clips-review',tuple(f'{clip}-{phase}' for phase in ('start','release','end') for clip in ('Idle','Move','Attack','Active','Hit','Defeat','Victory')),7,280)]:
        output=root/(hero+'-'+name+'.png')
        if output.exists(): continue
        image=Image.new('RGB',(columns*cell,((len(labels)+columns-1)//columns)*(cell+26)),(235,235,235));draw=ImageDraw.Draw(image)
        for index,label in enumerate(labels):
            with Image.open(source/(label+'.png')) as frame:
                frame=frame.convert('RGB');frame.thumbnail((cell,cell));x=(index%columns)*cell;y=(index//columns)*(cell+26);image.paste(frame,(x,y+26));draw.text((x+4,y+5),label,fill=(15,15,15))
        image.save(output)
    print(hero+' ACTUAL_SPARSE_RENDER_CONTACT_SHEETS_NOT_CONTINUOUS_REVIEW')
