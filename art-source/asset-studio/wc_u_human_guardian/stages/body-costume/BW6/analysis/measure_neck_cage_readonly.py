import bpy,json,numpy as np,collections,hashlib
from pathlib import Path
R=Path(__file__).parent;source=R.parent/'armor/ada_bw6_upper_combined_r001.blend';bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);o=bpy.data.objects['BW6_PaddedCoat_Tailored'];me=o.data;uses=collections.Counter()
for f in me.polygons:
 for e in f.edge_keys:uses[tuple(sorted(e))]+=1
rows=[]
for e in me.edges:
 a,b=[me.vertices[i] for i in e.vertices]
 if uses[tuple(sorted(e.vertices))]==1 and min(a.co.z,b.co.z)>1.54:rows.append({'vertices':list(e.vertices),'length_mm':(a.co-b.co).length*1000})
lengths=[r['length_mm'] for r in rows];out={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'top_boundary_edges':len(rows),'length_percentiles_mm':np.percentile(lengths,[0,10,25,50,75,90,100]).tolist(),'shorter_than_1_5mm_wall':sum(x<1.5 for x in lengths),'edges':rows};(R/'neck_cage_spacing.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k!='edges'})
