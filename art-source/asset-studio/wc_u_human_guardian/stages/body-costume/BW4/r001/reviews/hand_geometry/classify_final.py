"""Classify the already measured final crossings; no asset edit or additional fit."""
import ast
import json
import re
from collections import Counter
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
source=json.loads((ROOT/'records/open_glove_geometry.json').read_text())
report=json.loads((OUT/'correction2_geometry.json').read_text())
bw2=ROOT.parents[1]/'BW2/r001/integrated-independent/audit_integrated_geometry.py'
tree=ast.parse(bw2.read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='segment_triangle']
exec(compile(ast.Module(body=defs,type_ignores=[]),str(bw2),'exec'),globals())
names={1:'thumb',2:'index',3:'middle',4:'ring',5:'little'}
def label(ids):
    if any(i>=len(source['weights']) for i in ids):return 'reconstructed web'
    weights=Counter()
    for index in ids:
        for group,w in source['weights'][index].items():
            match=re.match(r'finger([1-5])-',group)
            weights[names[int(match.group(1))] if match else 'palm/base transition']+=w/len(ids)
    return weights.most_common(1)[0][0]

summary={};counts=Counter();examples={};details=[]
for mode,record in report['modes'].items():
    records=[]
    for pair in record['self']['pairs']:
        ta,tb=[np.array(v) for v in pair['triangle_points_m']]
        hits=[]
        for seg,tri in [(ta,tb),(tb,ta)]:
            for i in range(3):
                p=segment_triangle(seg[i],seg[(i+1)%3],tri)
                if p is not None:hits.append(p)
        span=max(np.linalg.norm(a-b) for a in hits for b in hits)*1000
        na=np.cross(ta[1]-ta[0],ta[2]-ta[0]);nb=np.cross(tb[1]-tb[0],tb[2]-tb[0])
        angle=np.degrees(np.arccos(np.clip(abs(np.dot(na,nb)/(np.linalg.norm(na)*np.linalg.norm(nb))),0,1)))
        item={'triangles':pair['triangles'],'intersection_span_mm':float(span),'acute_plane_angle_degrees':float(angle),
              'point_m':pair['intersection_hand_m'],'vertices':pair['vertices']}
        if mode=='raw':
            category=' / '.join(sorted(label(ids) for ids in pair['vertices']))
            item['approximate_source_region']=category;counts[category]+=1;examples.setdefault(category,item)
        records.append(item)
    summary[mode]={'confirmed_pairs':len(records),
        'minimum_plane_angle_degrees':min(r['acute_plane_angle_degrees'] for r in records),
        'minimum_intersection_span_mm':min(r['intersection_span_mm'] for r in records),
        'maximum_intersection_span_mm':max(r['intersection_span_mm'] for r in records),
        'pairs_with_span_above_0_01mm_and_angle_above1degree':sum(r['intersection_span_mm']>.01 and r['acute_plane_angle_degrees']>1 for r in records),
        'pairs':records}
idx=709
output={'status':'CONFIRMED_MAJOR_CROSSINGS_ART_REVISE',
 'source_sha256':report['source_sha256_before'],
 'raw_region_counts':dict(counts),'raw_region_examples':examples,
 'crossing_span_and_angle':summary,
 'worst_handle_vertex_source':{'candidate_index':idx,'original_full_glove_vertex_index':source['source_vertex_ids'][idx],
   'original_open_point_m':source['vertices_m'][idx],'original_weights':source['weights'][idx],
   'final_raw_point_m':report['modes']['raw']['handle_vertex_distance']['worst_point_m'],
   'final_evaluated_point_m':report['modes']['evaluated']['handle_vertex_distance']['worst_point_m'],
   'region_inference':'Middle proximal finger / metacarpal transition. Not one of the predeclared distal-pad regions.'},
 'classification_limits':['Raw region names aggregate original MPFB weights; they are anatomical approximations, not exact semantic segmentation.',
   'A triangle containing newly inserted web vertices is labeled reconstructed web.',
   'Evaluated subdivision indices are not reused as original source vertex IDs; exact region classification is therefore reported for the raw cage only.',
   'The reused segment-triangle test rejects parallel/coplanar determinant cases; coplanar and tangential overlap is unclassified rather than certified clear.']}
(OUT/'correction2_failure_regions.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'raw_region_counts':dict(counts),'span_and_angle':{m:{k:v for k,v in s.items() if k!='pairs'} for m,s in summary.items()}},indent=2))
