"""Lossless native-pixel crops, labeled comparison sheets, and registered mask diagnostics.

No image generation, perspective correction, identity inference, or quality score.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageOps


def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()

def crop_pack(image:Path, boxes:Path, out:Path):
    if out.exists() and any(out.iterdir()):raise ValueError('Output must be new or empty.')
    definitions=json.loads(boxes.read_text(encoding='utf-8'))
    with Image.open(image) as im:
        im.load();w,h=im.size
        records=[]
        for box in definitions['crops']:
            name=box['id'];coords=box['box_xyxy']
            if not re.fullmatch(r'[a-z][a-z0-9_-]+',name):raise ValueError('Invalid crop name.')
            if len(coords)!=4 or any(type(v) is not int for v in coords):raise ValueError('Pixel coordinates must be four integers.')
            x0,y0,x1,y1=coords
            if not (0<=x0<x1<=w and 0<=y0<y1<=h):raise ValueError(f'Out-of-bounds crop: {name}')
            if any(r['id']==name for r in records):raise ValueError('Duplicate crop ID.')
            records.append({'id':name,'box_xyxy':coords,'meaning':box.get('meaning',''), 'notes':box.get('notes','')})
        out.mkdir(parents=True,exist_ok=True)
        for rec in records:
            path=out/(rec['id']+'.png');im.crop(rec['box_xyxy']).save(path)
            rec.update({'path':path.name,'sha256':sha(path),'resampled':False})
        report={'source_file':image.name,'source_sha256':sha(image),'source_dimensions':[w,h],'operation':'native_pixel_crop',
                'status':'reference_crops_not_orthographic_or_approved','crops':records}
        (out/'crops.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        return report

def contact_sheet(inputs:list[Path],out:Path,size:int=420):
    if out.exists():raise ValueError('Refusing to overwrite sheet.')
    if not 96<=size<=2048:raise ValueError('Panel size out of bounds.')
    panels=[]
    for path in inputs:
        with Image.open(path) as src:
            src=ImageOps.exif_transpose(src).convert('RGB');native=src.size
            src.thumbnail((size,size)) # Downsample only; does not invent detail.
            panel=Image.new('RGB',(size,size+46),(232,232,232));panel.paste(src,((size-src.width)//2,(size-src.height)//2))
            d=ImageDraw.Draw(panel);d.text((8,size+4),path.name[:52],fill=(25,25,25));d.text((8,size+21),f'native {native[0]}x{native[1]} | no registration',fill=(25,25,25))
            panels.append(panel)
    if not panels:raise ValueError('No input images.')
    columns=min(3,len(panels));rows=(len(panels)+columns-1)//columns
    sheet=Image.new('RGB',(columns*size,rows*(size+46)),(232,232,232))
    for i,panel in enumerate(panels):sheet.paste(panel,((i%columns)*size,(i//columns)*(size+46)))
    out.parent.mkdir(parents=True,exist_ok=True);sheet.save(out)
    return {'output':str(out),'registered':False,'quality_score':None}

def mask_metrics(a:Path,b:Path,registered:bool):
    if not registered:raise ValueError('Metrics require explicit same-camera, same-pose, same-scale registration acknowledgement.')
    with Image.open(a) as ai,Image.open(b) as bi:
        if ai.size!=bi.size:raise ValueError('Mask dimensions differ; no auto-warp/rescale permitted.')
        av=[v>=128 for v in ai.convert('L').getdata()];bv=[v>=128 for v in bi.convert('L').getdata()]
    union=sum(x or y for x,y in zip(av,bv));intersection=sum(x and y for x,y in zip(av,bv))
    if not union:raise ValueError('Both masks are empty.')
    return {'intersection_over_union':intersection/union,'union_pixels':union,'intersection_pixels':intersection,
            'registered_declared_not_verified':True,'interpretation':'Silhouette overlap only, NOT artistic quality, identity or topology.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    c=sub.add_parser('crop');c.add_argument('--image',type=Path,required=True);c.add_argument('--boxes',type=Path,required=True);c.add_argument('--out',type=Path,required=True)
    c=sub.add_parser('sheet');c.add_argument('--images',type=Path,nargs='+',required=True);c.add_argument('--out',type=Path,required=True);c.add_argument('--size',type=int,default=420)
    c=sub.add_parser('mask-metrics');c.add_argument('--reference',type=Path,required=True);c.add_argument('--candidate',type=Path,required=True);c.add_argument('--registered',action='store_true')
    a=p.parse_args()
    try:
        if a.command=='crop':r=crop_pack(a.image,a.boxes,a.out)
        elif a.command=='sheet':r=contact_sheet(a.images,a.out,a.size)
        else:r=mask_metrics(a.reference,a.candidate,a.registered)
        print(json.dumps(r,indent=2));return 0
    except (ValueError,OSError,KeyError) as exc:print('IMAGE REVIEW ERROR:',exc);return 2
if __name__=='__main__':raise SystemExit(main())
