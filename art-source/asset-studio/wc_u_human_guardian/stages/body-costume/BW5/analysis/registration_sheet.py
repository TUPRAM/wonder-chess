import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).parent;reg=json.loads((R/'registration_body_anchors.json').read_text())
refpath=Path('C:/Users/iputu/Documents/Wonder Chess/production/asset-studio/supplements/BW5/Wonder_Chess_Proportion_Fit_BW5/references/Ada_supplied_turnaround.png');modelpath=R.parent/'armor/captures/reference_pose_front.png'
ref=Image.open(refpath).convert('RGB');model=Image.open(modelpath).convert('RGB');q=reg['uniform_model_to_reference_transform'];k=q['scale_xy_same'];tx,ty=q['translation_px']
box=(100,145,405,390);w,h=box[2]-box[0],box[3]-box[1]
# Inverse sampling preserves a single uniform scale, including fractional translation.
aligned=model.transform((w,h),Image.Transform.AFFINE,(1/k,0,(box[0]-tx)/k,0,1/k,(box[1]-ty)/k),resample=Image.Resampling.BICUBIC,fillcolor=(50,50,50))
crop=ref.crop(box);scale=2.8;size=(round(w*scale),round(h*scale));canvas=Image.new('RGB',(1830,1000),'#f5f2ec');draw=ImageDraw.Draw(canvas);font=lambda n:ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',n)
draw.text((40,23),'ADA | approximate registration using body landmarks',fill='#193440',font=font(33))
draw.text((40,74),'One uniform scale + translation. Hidden anatomical proxies carry explicit uncertainty; no armor-corner fit.',fill='#42525d',font=font(23))
for im,x,title in [(crop,40,'REFERENCE | supplied pixels'),(aligned,940,'BW5 RETAINED | ART_REVISE')]:
 draw.text((x,124),title,fill='#193440',font=font(25));canvas.paste(im.resize(size,Image.Resampling.LANCZOS),(x,171))
 for i,(name,a) in enumerate(reg['anchors'].items()):
  px,py=a['reference_proxy_px'];ux,uy=a['reference_uncertainty_px'];cx=x+(px-box[0])*scale;cy=171+(py-box[1])*scale;c='#12aab4' if i==0 else '#e6b536'
  draw.rectangle((cx-ux*scale,cy-uy*scale,cx+ux*scale,cy+uy*scale),outline=c,width=2);draw.line((cx-11,cy,cx+11,cy),fill=c,width=3);draw.line((cx,cy-11,cx,cy+11),fill=c,width=3)
  label='clavicle proxy' if i==0 else 'waist proxy';draw.text((x+15,cy-13),label,fill=c,font=font(20))
draw.text((40,887),'Cyan: inferred clavicle location, +/-12 source pixels vertically. Gold: inferred natural waist, +/-8 pixels.',fill='#42525d',font=font(22))
draw.text((40,925),'Retained collar and shoulders are unresolved BW4 context. This broad comparison is not exact likeness, fit or motion approval.',fill='#42525d',font=font(22))
canvas.save(R/'BW5_body_anchored_reference_comparison.png')
reg['image_sources']={'reference':{'path':str(refpath),'sha256':hashlib.sha256(refpath.read_bytes()).hexdigest(),'native_size':list(ref.size)},'model':{'path':str(modelpath),'sha256':hashlib.sha256(modelpath.read_bytes()).hexdigest(),'native_size':list(model.size)}};reg['display']={'reference_crop_xyxy':box,'display_enlargement_same_both_panels':scale,'output':str(R/'BW5_body_anchored_reference_comparison.png'),'interpolation':'Bicubic uniform registration, Lanczos display enlargement; no redraw or generated visual content.'}
(R/'registration_body_anchors.json').write_text(json.dumps(reg,indent=2))
