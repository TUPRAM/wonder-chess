from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json
root=Path(__file__).resolve().parent
clips=['Idle','Move','Attack','Active','Hit','Defeat','Victory']
rows=[]
for batch, selection in enumerate((clips[:4],clips[4:])):
    dst=root/f'actual-pose-grid-{batch+1}.png'
    if dst.exists(): raise FileExistsError(dst)
    sheet=Image.new('RGB',(960,344*len(selection)),(242,242,242)); draw=ImageDraw.Draw(sheet)
    for row,clip in enumerate(selection):
        for col,label in enumerate(('start','release','end')):
            path=root/f'{clip}-{label}.png'
            with Image.open(path) as image:
                assert image.size==(320,320)
                sheet.paste(image.convert('RGB'),(col*320,row*344+24))
            draw.text((col*320+8,row*344+5),clip+' / '+label,fill=(20,20,20))
            rows.append({'clip':clip,'sample':label,'source':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    sheet.save(dst)
(root/'actual-pose-grid-inputs.json').write_text(json.dumps({'kind':'montage of actual rendered sparse pose samples','continuous_review':False,'images':rows},indent=2))
