import bpy,json,hashlib
import numpy as np
from pathlib import Path
from collections import Counter,defaultdict
OUT=Path(__file__).resolve().parents[1]
BW4=OUT.parents[1]/'BW4/r001'
src=BW4/'ada_fixed_hand_checkpoint_ART_REVISE.blend'
bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
o=bpy.data.objects['BW4_ClosedGlove_Correction2']
d=json.loads((BW4/'records/open_glove_geometry.json').read_text())
v=np.array(d['vertices_m']);current=np.array([list(a.co) for a in o.data.vertices])
def loops(faces):
 c=Counter(tuple(sorted((a,b))) for f in faces for a,b in zip(f,f[1:]+f[:1]));adj=defaultdict(list)
 for (a,b),n in c.items():
  if n==1:adj[a].append(b);adj[b].append(a)
 seq=[]
 while adj:
  a=next(iter(adj));lp=[a];prev=None
  for _ in range(1000):
   opts=adj.get(a,[]);nxt=next((x for x in opts if x!=prev),None)
   if nxt is None:break
   prev,a=a,nxt
   if a==lp[0]:break
   lp.append(a)
  for a in lp:adj.pop(a,None)
  seq.append(lp)
 return seq
parts={}
for n in range(1,6):
 w=np.array([sum(t.get(f'finger{n}-{j}.R',0) for j in (1,2,3)) for t in d['weights']])
 faces=[f for f in d['faces'] if min(w[f])>.95]
 lp=loops(faces)
 parts[n]={'faces':faces,'loops':lp,'loop_coords_open':[[v[i].tolist() for i in a] for a in lp], 'loop_coords_bw4':[[current[i].tolist() for i in a] for a in lp]}
 print(n,'faces',len(faces),'loops',[(len(a),np.round(np.mean(current[a],axis=0)*1000,2).tolist()) for a in lp],flush=True)
print('BOUNDS',current.min(axis=0),current.max(axis=0))
record={'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'parts':parts,'bw4_vertices':current.tolist()}
(OUT/'records/root_inspection.json').write_text(json.dumps(record,indent=2))
