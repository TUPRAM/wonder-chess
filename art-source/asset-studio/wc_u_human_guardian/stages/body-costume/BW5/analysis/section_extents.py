import json
from pathlib import Path
R=Path(__file__).parent;d=json.loads((R/'bw4_sections_and_conflicts.json').read_text());out=[]
for st in d['stations']:
 row={'name':st['name'],'z_m':st['z_m'],'layers':{}}
 for k,lines in st['section_lines_xy_m'].items():
  if not lines:row['layers'][k]=None;continue
  adj={};pos={}
  for a,b in lines:
   ka=tuple(round(v,5) for v in a);kb=tuple(round(v,5) for v in b)
   adj.setdefault(ka,set()).add(kb);adj.setdefault(kb,set()).add(ka);pos[ka]=a;pos[kb]=b
  seen=set();components=[]
  for seed in adj:
   if seed in seen:continue
   stack=[seed];seen.add(seed);c=[]
   while stack:
    p=stack.pop();c.append(pos[p])
    for q in adj[p]-seen:seen.add(q);stack.append(q)
   if len(c)>2:components.append(c)
  center=[c for c in components if min(p[0] for p in c)<=0<=max(p[0] for p in c)]
  selected=max(center,key=lambda c:(max(p[0] for p in c)-min(p[0] for p in c))*(max(p[1] for p in c)-min(p[1] for p in c))) if center else [p for c in components for p in c]
  row['layers'][k]={'component_count':len(components),'selected_points':len(selected),'width_mm':(max(p[0] for p in selected)-min(p[0] for p in selected))*1000,'min_x_m':min(p[0] for p in selected),'max_x_m':max(p[0] for p in selected),'front_y_m':max(p[1] for p in selected),'back_y_m':min(p[1] for p in selected),'has_center_component':bool(center),'selection':'Largest center-spanning component if present, otherwise union of separated wings. At shoulder merge this includes connected shoulder/arm surface, not hidden torso-only circumference.'}
 out.append(row)
(R/'bw4_section_extents.json').write_text(json.dumps({'scope':'Frame1 section line components, 10micrometer endpoint merging. Not a global object bounding box. Final thin shell section may have connected front/back faces; rays record inner/outer separately.','stations':out},indent=2))
print(json.dumps(out,indent=2))
