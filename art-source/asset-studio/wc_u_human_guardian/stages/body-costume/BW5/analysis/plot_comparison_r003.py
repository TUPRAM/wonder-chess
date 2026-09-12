import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).parent;d=json.loads((R/'r003_sections_and_conflicts.json').read_text()); baseline=json.loads((R/'bw4_sections_and_conflicts.json').read_text())
im=Image.new('RGB',(1800,1100),'#f6f3ed');draw=ImageDraw.Draw(im)
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',n)
draw.text((40,23),'BW4 TO BW5 | measured body / padding / plate fit',fill='#172b3a',font=font(32))
draw.text((40,70),'Millimeters, same scale per panel. +Y anterior points up. Frame 1: BW4 frozen baseline and BW5 r003 retained frozen plate shapes.',fill='#364854',font=font(21))
colors={'body':'#6a7380','coat':'#d58119','front':'#127da1','back':'#af4267'}
for i,st in enumerate(d['stations']):
 x0=30+(i%3)*590;y0=125+(i//3)*465
 draw.rounded_rectangle((x0,y0,x0+560,y0+435),14,fill='white',outline='#b8c1c6')
 draw.text((x0+17,y0+11),f"{st['name'].replace('_',' ').upper()} | Z {st['z_m']*1000:.1f} mm",fill='#172b3a',font=font(22))
 center=(x0+280,y0+233);scale=750
 xy=lambda p:(center[0]+p[0]*scale,center[1]-(p[1]+.035)*scale)
 for q in [-.2,-.1,0,.1,.2]:
  draw.line((xy((q,-.24)),xy((q,.24))),fill='#e7ecee',width=1)
  draw.line((xy((-.27,q)),xy((.27,q))),fill='#e7ecee',width=1)
 for k in ['front','back']:
  for a,b in baseline['stations'][i]['section_lines_xy_m'][k]:
   if max(abs(a[0]),abs(b[0]))<.285 and max(abs(a[1]),abs(b[1]))<.24:draw.line((xy(a),xy(b)),fill='#bbc4cc',width=2)
 for k in ['body','coat','front','back']:
  for a,b in st['section_lines_xy_m'][k]:
   # Clip display to the torso panel, actual full section data is retained.
   if max(abs(a[0]),abs(b[0]))<.285 and max(abs(a[1]),abs(b[1]))<.24:draw.line((xy(a),xy(b)),fill=colors[k],width=2 if k=='body' else 3)
 draw.text((x0+20,y0+397),'100 mm',fill='#526773',font=font(15));draw.line((x0+110,y0+410,x0+185,y0+410),fill='#172b3a',width=3)
x0=1210;y0=620
draw.text((x0,y0),'Measured construction relationship',fill='#172b3a',font=font(24))
for i,(k,c) in enumerate(colors.items()):
 draw.rectangle((x0,y0+55+i*43,x0+26,y0+75+i*43),fill=c)
 draw.text((x0+38,y0+46+i*43),{'body':'Unchanged body, evaluated','coat':'Padded coat, final thickness','front':'BW5 front plate, outer / inner','back':'BW5 back plate, outer / inner'}[k],fill='#364854',font=font(21))
notes=['Pale gray outlines = frozen BW4 plate sections.','Full sections may include sleeve components.','Display crop: |X| < 285 mm; complete lines in JSON.','Directional gaps are axial, not surface-normal distance.','A section alone does not certify collision freedom.']
for i,t in enumerate(notes):draw.text((x0,y0+245+i*30),t,fill='#364854',font=font(18))
draw.text((40,1040),'Center depth is reduced. Upper anterior edge still floats; these sections do not clear assembly, collar, waist or motion defects.',fill='#172b3a',font=font(22))
im.save(R/'BW4_vs_BW5_r003_torso_sections.png')
