import bpy, json, hashlib, ast, re
from pathlib import Path
from collections import Counter
import numpy as np
from mathutils import Matrix
from mathutils.bvhtree import BVHTree

out=Path(__file__).parent
source=out.parent/'grip_integrated_contact_r001.blend'
sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert sha=='9509750f833cec0c8cac90cd866215a732baed67571d1d444c7b718f441f877d'
s=bpy.context.scene
r=bpy.data.objects['BW1_Temporary_Pose_Rig']
rec=json.loads(s['BW2_hand_contract'])
Fi=Matrix(rec['frame_world']).inverted()
deform={b.name for b in r.data.bones if b.use_deform}
tree=ast.parse((out/'audit_integrated_geometry.py').read_text())
defs=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('segment_triangle','self_audit')],type_ignores=[])
exec(compile(defs,str(out/'audit_integrated_geometry.py'),'exec'),globals())

def weights(ob,v):
    return {ob.vertex_groups[g.group].name:float(g.weight) for g in v.groups if ob.vertex_groups[g.group].name in deform and g.weight>1e-7}

def region(w):
    groups={'thumb':0.,'index':0.,'middle':0.,'ring':0.,'little':0.,'palm_wrist':0.}
    for n,v in w.items():
        mt=re.match(r'finger([1-5])-',n)
        if mt:groups[['thumb','index','middle','ring','little'][int(mt.group(1))-1]]+=v
        else:groups['palm_wrist']+=v
    return max(groups,key=groups.get)

def geometry(ob):
    bpy.context.view_layer.update()
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me=ev.to_mesh();me.calc_loop_triangles()
    transform=Fi@ev.matrix_world
    q=np.array([list(transform@v.co) for v in me.vertices])
    w=[weights(ob,v) for v in me.vertices]
    tris=[(t.index,tuple(t.vertices)) for t in me.loop_triangles]
    ev.to_mesh_clear()
    return q,w,tris

audit=json.loads((out/'integrated_geometry_audit.json').read_text())
result={'source_sha256':sha,'method':'Read-only existing deform weights, evaluated crossing ownership, and unsmoothed base-cage transverse intersections. No weights or poses changed. Broad transition selections are diagnostic ownership, not proposed edit masks.','objects':{}}
for name in ['BW1_Glove_Pair_SourceFit','BW1_IndexedBody']:
    ob=bpy.data.objects[name]
    q,ew,tris=geometry(ob)
    linear=next(v for v in audit['variants'] if v['mode']=='linear' and v['object']==name)
    classified=[];counts=Counter()
    for pair in linear['self_intersections']['pairs']:
        owners=[]
        for ids in pair['vertices']:
            avg={}
            for i in ids:
                for n,w in ew[i].items():avg[n]=avg.get(n,0.)+w/3
            owners.append(region(avg))
        key='/'.join(sorted(owners));counts[key]+=1
        classified.append({**pair,'dominant_deform_region':owners})
    state=[(m,m.show_viewport) for m in ob.modifiers]
    for m,_ in state:
        if m.type!='ARMATURE':m.show_viewport=False
    bq,bw,bt=geometry(ob)
    assert len(bq)==len(ob.data.vertices)
    if name=='BW1_IndexedBody':
        gi=ob.vertex_groups['body'].index
        bodyids={v.index for v in ob.data.vertices if any(g.group==gi and g.weight>.5 for g in v.groups)}
    else:bodyids=set(range(len(bq)))
    ids={i for i in bodyids if -.025<bq[i,1]<.24 and abs(bq[i,0])<.135 and abs(bq[i,2])<.14}
    bt=[(index,vs) for index,vs in bt if all(i in ids for i in vs)]
    rawself=self_audit(bq,bt)
    thumb=lambda w:sum(v for n,v in w.items() if n.startswith('finger1-') and n.endswith('.R'))
    wrist=lambda w:sum(v for n,v in w.items() if not n.startswith('finger') and n.endswith('.R'))
    # Exact existing CMC/hand transition membership; no nearest-surface mapping.
    mixed={i for i in ids if bw[i].get('finger1-1.R',0)>1e-5 and wrist(bw[i])>1e-5}
    edgejumps=[]
    for e in ob.data.edges:
        a,b=e.vertices
        if a not in ids or b not in ids or (a not in mixed and b not in mixed):continue
        jump=abs(thumb(bw[a])-thumb(bw[b]))
        if jump>.1:edgejumps.append({'vertices':[a,b],'thumb_weight_jump':jump,'posed_edge_length_mm':float(np.linalg.norm(bq[a]-bq[b])*1000)})
    edgejumps.sort(key=lambda e:e['thumb_weight_jump'],reverse=True)
    crossing_ids=sorted({i for p in rawself['pairs'] for tri in p['vertices'] for i in tri})
    sourceattr=ob.data.attributes.get('mpfb_source_index')
    selected=sorted(mixed|set(crossing_ids))
    rows=[]
    for i in selected:
        rows.append({'base_vertex':i,'source_vertex':int(sourceattr.data[i].value) if sourceattr else (i if name=='BW1_IndexedBody' else None),'posed_hand_m':bq[i].tolist(),'weights':bw[i],'mixed_CMC_wrist':i in mixed,'raw_cage_crossing':i in crossing_ids})
    data={'linear_evaluated_crossing_region_counts':dict(counts),'classified_evaluated_crossings':classified,'right_hand_base_vertices':sorted(ids),'mixed_CMC_wrist_base_vertices':sorted(mixed),'raw_cage_intersections':rawself,'raw_cage_crossing_base_vertices':crossing_ids,'largest_existing_transition_edge_jumps':edgejumps[:50],'vertex_records':rows}
    if name=='BW1_Glove_Pair_SourceFit':
        data['frozen_pad_existing_evaluated_deform_weights']={digit:[{'evaluated_vertex':i,'weights':ew[i]} for i in p['indices']] for digit,p in rec['patches'].items()}
        folder=out.parents[2]/'BW1/r001/source-quarantine/selected/clothes/toigo_gloves_short'
        mhclo=folder/'toigo_gloves_short.mhclo';objfile=folder/'gloves_hand.obj'
        mapping=[];reading=False
        for line in mhclo.read_text().splitlines():
            line=line.strip()
            if line.startswith('verts '):reading=True;continue
            if not reading or not line or line.startswith('#'):continue
            parts=line.split()
            if not parts[0].lstrip('-').isdigit():break
            if len(parts)==1:mapping.append({'indices':[int(parts[0])],'coefficients':[1.]})
            elif len(parts)==9:mapping.append({'indices':list(map(int,parts[:3])),'coefficients':list(map(float,parts[3:6]))})
            else:raise ValueError(line)
        sourcefaces=[]
        for line in objfile.read_text().splitlines():
            if line.startswith('f '):sourcefaces.append(tuple(int(v.split('/')[0])-1 for v in line.split()[1:]))
        canonical=lambda faces:sorted(tuple(sorted(f)) for f in faces)
        assert len(mapping)==len(ob.data.vertices)
        assert canonical(sourcefaces)==canonical([p.vertices for p in ob.data.polygons])
        data['mapping_provenance']={'path':str(mhclo),'sha256':hashlib.sha256(mhclo.read_bytes()).hexdigest(),'rows':len(mapping),'source_OBJ_indexed_face_sets_match_live_base_mesh':True,'note':'Native glove uses MHCLO barycentric correspondence, not a one-source-index helper attribute. Coefficients are fitting data, distinct from skeletal groups.'}
        body=bpy.data.objects['BW1_IndexedBody']
        for row in rows:
            mm=mapping[row['base_vertex']];row['mhclo_source_mapping']=mm
            row['source_body_weights']=[{'base_vertex':i,'weights':weights(body,body.data.vertices[i])} for i in mm['indices']]
    result['objects'][name]=data
    for m,flag in state:m.show_viewport=flag
    print(name,'regions',dict(counts),'mixed',len(mixed),'raw_pairs',rawself['confirmed_nonadjacent_transverse_pairs'],'maxjump',edgejumps[:2],flush=True)
result['source_sha256_after']=hashlib.sha256(source.read_bytes()).hexdigest()
assert result['source_sha256_after']==sha
(out/'web_weight_diagnosis.json').write_text(json.dumps(result,indent=2))
